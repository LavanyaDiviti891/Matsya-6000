from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Set, Optional
import asyncio
import random
import os
import re
import json
import glob
from datetime import datetime

from models import MatsyaUIState
import rule_engine
import sample_scenario
import co2_scenario
import alarm_engine

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------- STATE -----------------
app_state = MatsyaUIState()
connected_clients: Set[WebSocket] = set()


# ----------------- WEBSOCKETS -----------------
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.add(websocket)
    try:
        # Send initial state
        await websocket.send_json(app_state.model_dump())
        while True:
            data = await websocket.receive_text()
            # We can handle client messages here if needed
    except WebSocketDisconnect:
        connected_clients.remove(websocket)


async def broadcast():
    # Recompute the DNV alarm-document thresholds every time we push state.
    # This only ever sets app_state.beep_level / active_alarms -- it does
    # not open any popup; the frontend beeps according to beep_level.
    alarm_engine.update_app_state(app_state)

    if not connected_clients:
        return
    data = app_state.model_dump()
    disconnected = set()
    for client in connected_clients:
        try:
            await client.send_json(data)
        except Exception:
            disconnected.add(client)
    connected_clients.difference_update(disconnected)


# ----------------- APIs & SIMULATION -----------------
simulator_task = None


class SimState:
    command: str = None
    target_dive: int = None
    speed: str = "1"
    paused: bool = False


sim_global = SimState()


async def simulate_data():
    s = app_state

    data_dir = "sim_data_processed"
    if not os.path.exists(data_dir):
        print(f"Data directory {data_dir} not found. Simulation stopped.")
        return

    json_files = glob.glob(os.path.join(data_dir, "*.json"))
    if not json_files:
        print(f"No JSON files found in {data_dir}. Simulation stopped.")
        return

    json_files.sort()

    current_file = json_files[0]
    for jf in json_files:
        m = re.search(r"(?i)dive[_\s]*(\d+)", jf)
        if m and int(m.group(1)) == s.header.dive_num:
            current_file = jf
            break

    m = re.search(r"(?i)dive[_\s]*(\d+)", current_file)
    if m:
        s.header.dive_num = int(m.group(1))

    print(f"Loading simulation data from {current_file} (Dive {s.header.dive_num})")

    try:
        with open(current_file, "r") as f:
            records = json.load(f)
    except Exception as e:
        print(f"Failed to load JSON: {e}")
        return

    if not records:
        return

    idx = 0
    while True:
        state_changed = False
        cmd = sim_global.command
        sim_global.command = None

        if sim_global.target_dive is not None:
            t_dive = sim_global.target_dive
            sim_global.target_dive = None
            for jf in json_files:
                m = re.search(r"(?i)dive[_\s]*(\d+)", jf)
                if m and int(m.group(1)) == t_dive:
                    current_file = jf
                    s.header.dive_num = t_dive
                    try:
                        with open(current_file, "r") as f:
                            records = json.load(f)
                        idx = 0
                        state_changed = True
                        print(f"Switched to {current_file}")
                    except Exception:
                        pass
                    break

        if cmd == "rewind":
            idx = max(0, idx - 10)
            state_changed = True
        elif cmd == "forward":
            idx = min(len(records) - 1, idx + 10)
            state_changed = True
        elif cmd == "start":
            idx = 0
            state_changed = True
        elif cmd == "end":
            idx = max(0, len(records) - 1)
            state_changed = True

        if sim_global.paused and not state_changed:
            await asyncio.sleep(0.1)
            continue

        if idx >= len(records):
            idx = 0

        record = records[idx]

        for var_path, value in record.items():
            if value is None:
                continue

            # While the SAMPLE COLLECTION scenario is running it owns
            # header.depth exclusively (it sets a seabed value and the
            # pilot doesn't expect it to drift back to the dive-tape
            # value mid-mission) -- same behavior as the old UI.
            if app_state.sample_scenario.active and var_path == "header.depth":
                continue

            # While the combined CO2 -> nav-instability -> buoy mission is
            # running it owns depth, altitude, and all three CO2 fields
            # exclusively (see co2_scenario.py's module docstring) -- the
            # live-data simulator must not fight it for these paths.
            if app_state.co2_scenario.active and var_path in (
                "header.depth",
                "header.altitude",
                "hsss.p.co2",
                "hsss.s.co2",
                "environment.co2",
            ):
                continue

            parts = var_path.split(".")
            obj = s
            try:
                for p in parts[:-1]:
                    obj = getattr(obj, p)

                leaf = parts[-1]
                target = getattr(obj, leaf)

                if hasattr(target, "value"):
                    try:
                        target.value = float(value)
                    except ValueError:
                        pass
                else:
                    setattr(obj, leaf, value)
            except AttributeError:
                pass

        if "header.present_time" in record and record["header.present_time"]:
            time_str = str(record["header.present_time"])
            time_str = time_str.replace("_", ":").split(".")[0]
            s.header.present_time = time_str
        else:
            s.header.present_time = datetime.now().strftime("%H:%M:%S")

        if "header.mission_time" not in record or not record["header.mission_time"]:
            s.header.mission_time = datetime.now().strftime("%H:%M:%S")

        await broadcast()

        if not sim_global.paused:
            idx += 1
            sleep_dur = 1.0
            if sim_global.speed == "max":
                sleep_dur = 0.008
            await asyncio.sleep(sleep_dur)
        else:
            await asyncio.sleep(0.1)


@app.post("/api/toggle_power")
async def toggle_power():
    global simulator_task
    app_state.is_powered_on = not app_state.is_powered_on
    if app_state.is_powered_on:
        if simulator_task is None or simulator_task.done():
            simulator_task = asyncio.create_task(simulate_data())
    else:
        if simulator_task and not simulator_task.done():
            simulator_task.cancel()
            simulator_task = None

    await broadcast()
    return {"status": "ok"}


@app.post("/api/toggle_joystick")
async def toggle_joystick():
    s = app_state.sidebar
    s.joystick = not s.joystick
    await broadcast()
    return {"status": "ok"}


@app.post("/api/toggle_thrusters_enable")
async def toggle_thrusters_enable():
    s = app_state.sidebar
    s.thrusters_enable = not s.thrusters_enable
    await broadcast()
    return {"status": "ok"}


@app.post("/api/toggle_high_speed")
async def toggle_high_speed():
    s = app_state.sidebar
    s.high_speed = not s.high_speed
    await broadcast()
    return {"status": "ok"}


@app.post("/api/toggle/{state_path:path}")
async def generic_toggle(state_path: str, val: Optional[str] = Form(None)):
    parts = state_path.split(".")
    obj = app_state
    for p in parts[:-1]:
        obj = getattr(obj, p)

    previous_val = getattr(obj, parts[-1])
    if val is not None:
        setattr(obj, parts[-1], val)
        new_val = val
    else:
        new_val = not previous_val
        setattr(obj, parts[-1], new_val)

    # Let the SOP rule engine (if the training scenario is active) classify
    # this exact switch action against the real MATSYA power-up sequence --
    # this is what gates alarms/faults behind the actual step order instead
    # of firing them the instant a "medium/high" mode is picked.
    if app_state.scenario.active:
        rule_engine.evaluate_action(app_state, state_path, previous_val, new_val)
        rule_engine.recompute_derived_flags(app_state)

    # Thruster POWER/ENABLE switches (Propulsion tab) previously toggled
    # with no visible effect -- RPM/Voltage/Current/Temp stayed at 0.00
    # forever because nothing ever wrote to propulsion_detail.tN's other
    # fields. Synthesize plausible telemetry the moment a thruster's
    # power/enable state changes so the gauges actually move.
    if len(parts) == 3 and parts[0] == "propulsion_detail" and parts[2] in ("power", "enable"):
        _sync_thruster_telemetry(app_state, parts[1])

    await broadcast()
    return {"status": "ok"}


def _sync_thruster_telemetry(app_state, thruster_key: str) -> None:
    """
    thruster_key is e.g. "t1". Keeps propulsion_detail.<thruster_key>'s
    rpm/voltage/current/temp/ctrl in sync with its power+enable switches,
    and mirrors rpm into the flat propulsion.<thruster_key>_rpm field used
    on the Main tab.
    """
    t = getattr(app_state.propulsion_detail, thruster_key, None)
    if t is None:
        return

    if t.power and t.enable:
        # Running: nominal RPM/voltage/current/temp, only re-roll RPM if
        # it was previously at rest so it doesn't jitter on every toggle.
        if not t.rpm:
            t.rpm = round(random.uniform(750, 1150), 1)
        t.voltage = round(random.uniform(46.0, 50.0), 1)
        t.current = round(random.uniform(12.0, 22.0), 1)
        t.temp = round(random.uniform(28.0, 42.0), 1)
        t.ctrl = round(random.uniform(40.0, 90.0), 1)
    elif t.power and not t.enable:
        # Powered but not enabled: bus voltage present, motor idle.
        t.rpm = 0.0
        t.voltage = round(random.uniform(46.0, 50.0), 1)
        t.current = round(random.uniform(0.3, 1.5), 1)
        t.temp = round(random.uniform(20.0, 25.0), 1)
        t.ctrl = 0.0
    else:
        t.rpm = 0.0
        t.voltage = 0.0
        t.current = 0.0
        t.temp = 0.0
        t.ctrl = 0.0

    rpm_field = f"{thruster_key}_rpm"
    if hasattr(app_state.propulsion, rpm_field):
        setattr(app_state.propulsion, rpm_field, t.rpm)


# ----------------- SAMPLE COLLECTION SCENARIO (ported from old UI) -----------------
sample_scenario_task = None


@app.post("/api/scenario/sample/start")
async def sample_scenario_start():
    global sample_scenario_task
    if sample_scenario_task is None or sample_scenario_task.done():
        sample_scenario_task = asyncio.create_task(
            sample_scenario.run(app_state, broadcast)
        )
    return {"status": "ok"}


@app.post("/api/scenario/sample/reset")
async def sample_scenario_reset():
    global sample_scenario_task
    if sample_scenario_task and not sample_scenario_task.done():
        sample_scenario_task.cancel()
    sample_scenario.reset(app_state)
    await broadcast()
    return {"status": "ok"}


# ----------------- CO2 SCRUBBER FAILURE -> NAV INSTABILITY -> BUOY (combined) -----------------
# Replaces the old separate sample co2_scenario / emergency_buoy_scenario
# pair with the single ordered mission in co2_scenario.py: CO2 alarm first,
# then navigation instability, then buoy release. Routes are unchanged
# (/api/scenario/co2/start, /api/scenario/co2/reset) so nothing else needs
# to move.
co2_scenario_task = None


@app.post("/api/scenario/co2/start")
async def co2_scenario_start():
    global co2_scenario_task
    if co2_scenario_task is None or co2_scenario_task.done():
        co2_scenario_task = asyncio.create_task(
            co2_scenario.run(app_state, broadcast)
        )
    return {"status": "ok"}


@app.post("/api/scenario/co2/reset")
async def co2_scenario_reset():
    global co2_scenario_task
    if co2_scenario_task and not co2_scenario_task.done():
        co2_scenario_task.cancel()
    co2_scenario.reset(app_state)
    await broadcast()
    return {"status": "ok"}


# ----------------- SOP TRAINING SCENARIO -----------------
@app.post("/api/scenario/poweringup/start")
async def scenario_start():
    rule_engine.start_scenario(app_state)
    await broadcast()
    return {"status": "ok"}


@app.post("/api/scenario/poweringup/stop")
async def scenario_stop():
    rule_engine.stop_scenario(app_state)
    await broadcast()
    return {"status": "ok"}


@app.api_route("/api/start_sim", methods=["GET", "POST"])
async def start_sim():
    global simulator_task
    if simulator_task is None or simulator_task.done():
        simulator_task = asyncio.create_task(simulate_data())
        return {"status": "Simulation started"}
    return {"status": "Simulation already running"}


@app.api_route("/api/stop_sim", methods=["GET", "POST"])
async def stop_sim():
    global simulator_task
    if simulator_task and not simulator_task.done():
        simulator_task.cancel()
        simulator_task = None
        return {"status": "Simulation stopped"}
    return {"status": "Simulation not running"}


@app.post("/api/sim/set_dive")
async def set_dive(dive_num: int = Form(...)):
    sim_global.target_dive = dive_num
    app_state.header.dive_num = dive_num
    await broadcast()
    return {"status": "ok"}


@app.post("/api/sim/toggle_pause")
async def toggle_pause():
    sim_global.paused = not sim_global.paused
    await broadcast()
    return {"status": "ok"}


@app.post("/api/sim/set_speed")
async def set_speed(speed: str = Form(...)):
    sim_global.speed = speed
    return {"status": "ok"}


@app.post("/api/sim/{cmd}")
async def sim_command(cmd: str):
    if cmd in ["start", "end"]:
        sim_global.command = cmd
    return {"status": "ok"}
