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
    rule_engine.recompute_derived_flags(app_state)
    await broadcast()
    return {"status": "ok"}


@app.post("/api/toggle_thrusters_enable")
async def toggle_thrusters_enable():
    s = app_state.sidebar
    s.thrusters_enable = not s.thrusters_enable
    rule_engine.recompute_derived_flags(app_state)
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
    else:
        setattr(obj, parts[-1], not previous_val)

    new_val = getattr(obj, parts[-1])

    # Route switch actions through the SOP rule engine's classifier — this
    # generates the ACCEPTED/WARNING/OUT_OF_ORDER event-log entries and is
    # only meaningful for actual power-up switches.
    result = None
    if state_path.startswith("switches."):
        result = rule_engine.evaluate_action(app_state, state_path, previous_val, new_val)
        print(f"[SOP] toggled: {state_path} = {new_val} | "
              f"classified: {result.action_type if result else 'NOT IN FIELD_MAP'} | "
              f"next_step_p: {app_state.scenario.next_step_p}")

    # Recompute the post-power-up phase state (Imaging -> Sensors -> Comms ->
    # Ballast -> Propulsion) on EVERY toggle, not just switches.* ones — the
    # phase checks read imaging.*, sensors.*, propulsion_detail.*, etc, so
    # skipping this for those paths left the "next step" banner frozen even
    # after the operator flipped the correct switch (e.g. HD Camera P).
    rule_engine.recompute_derived_flags(app_state)

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


# ----------------- SOP RULE-ENGINE SCENARIO -----------------
@app.post("/api/scenario/poweringup/start")
async def start_poweringup_scenario():
    app_state.scenario.active = True
    app_state.scenario.feedback_msg = "Power-up SOP active. Operate switches; the rule engine will classify each action."
    rule_engine.recompute_derived_flags(app_state)
    await broadcast()
    return {"status": "Scenario started"}


@app.post("/api/scenario/poweringup/stop")
async def stop_poweringup_scenario():
    app_state.scenario.active = False
    app_state.scenario.feedback_msg = "Power-up SOP stopped."
    rule_engine.reset_engine(app_state)  # Resets telemetry & clears screen power
    app_state.scenario.event_log = []
    await broadcast()
    return {"status": "Scenario stopped"}