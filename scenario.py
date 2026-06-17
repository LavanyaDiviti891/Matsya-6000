import asyncio
import random
from dataclasses import dataclass
from typing import Optional


@dataclass
class ScenarioState:
    active: bool = False
    mission_name: str = ""
    timer_total: int = 600
    timer_remaining: int = 600
    target_depth: float = 250.0
    depth_rate: float = 3.0
    success: Optional[bool] = None
    result_message: str = ""
    blink: bool = False
    current_stage: int = 0
    feedback_msg: str = ""


scenario_state = ScenarioState()

# Dot-paths (matching simulate_data's record keys, e.g. "header.depth.value")
# that the scenario has just injected a reading into. While a path is in
# this set, the JSON-replay simulator (simulate_data in main.py) skips
# overwriting it, so the participant has time to observe/record the value
# instead of it being clobbered on the next replay tick.
scenario_locked_paths: set[str] = set()


def reset_scenario(sc: ScenarioState) -> None:
    sc.active = False
    sc.success = None
    sc.mission_name = ""
    sc.result_message = ""
    sc.feedback_msg = ""
    sc.blink = False
    sc.current_stage = 0
    sc.timer_remaining = sc.timer_total
    scenario_locked_paths.clear()


async def run_loading_ballast_scenario(app_state, broadcast_fn):
    """
    Scenario: UNDERWATER IMAGING & SENSORS (SOP Steps 63–92)

    Covers:
      Imaging  — VHS recorders, HD/SD cameras, LED lights, Obstacle SONAR
      Science  — CTD_P (CTDO), Dissolved O2
      Nav      — Surface INS, Depth Primary, INS, DVL, Altimeter

    Field paths (new models.py):
      switches.p  → SwitchesCategory_P   switches.s → SwitchesCategory_S
      imaging.*   → ImagingState
      sensors.toggles.* → SensorsToggles

    READING_PAUSE_SECS — seconds banner holds the ✔ confirmation so
    participants can observe and record values before next instruction.

    Stage map (18 stages total):
      1  SOP 64  switches.p.vhs_power_p          Switches_P1
      2  SOP 65  switches.s.vhs_power_s          Switches_S1
      3  SOP 66  imaging.hd_camera_p             Imaging page
      4  SOP 67  imaging.hd_sdi_p3               Imaging page (SD Cam P3)
      5  SOP 68  imaging.hd_sdi_p4               Imaging page (SD Cam P4)
      6  SOP 69  imaging.hd_camera_s             Imaging page
      7  SOP 70  imaging.hd_sdi_s2               Imaging page (SD Cam S3)
      8  SOP 71  imaging.hd_sdi_s3               Imaging page (SD Cam S4)
      9  SOP 72  imaging.led_p2.power            Imaging page (LED P2)
     10  SOP 73  imaging.led_p3.power            Imaging page (LED P3)
     11  SOP 75  switches.p.led_emergency_port   Switches_P1 (LED Light P1)
     12  SOP 76  imaging.led_s2.power            Imaging page (LED S2)
     13  SOP 77  imaging.led_s3.power            Imaging page (LED S3)
     14  SOP 79  switches.s.led_emergency_port   Switches_S1 (LED Light S1)
     15  SOP 80  switches.p.sonar                Switches_P1 (Obstacle SONAR)
     16  SOP 84  sensors.toggles.ctdo            Sensors page (CTD_P)
     17  SOP 85  sensors.toggles.dissolved_o2    Sensors page (DO_S)
     18  SOP 86  switches.p.surface_ins          Switches_P1 (Surface INS)
     19  SOP 89  sensors.toggles.depth_sensor_pri Sensors page
     20  SOP 90  sensors.toggles.ins             Sensors page (INS_P)
     21  SOP 91  sensors.toggles.dvl             Sensors page (DVL_P)
     22  SOP 92  sensors.toggles.altimeter       Sensors page (Altimeter_S)
    """
    sc      = scenario_state
    sw_p    = app_state.switches.p
    sw_s    = app_state.switches.s
    img     = app_state.imaging
    sens    = app_state.sensors.toggles
    sens_st = app_state.sensors          # full SensorsState (scientific, surface_ins, redt_depth)
    hdr     = app_state.header           # HeaderTelemetry (depth, altitude, etc.)

    READING_PAUSE_SECS = 8   # seconds to hold ✔ message so participants can record values
    TOTAL_STAGES       = 22

    # ── Helper: generate a plausible reading the instant a switch/sensor is
    #            turned ON, so the corresponding display shows a live value
    #            for the participant to check/record (per SOP instruction).
    #            Paths written are added to scenario_locked_paths so the
    #            JSON-replay simulator (simulate_data, in main.py) does not
    #            immediately overwrite the value on its next tick. ──────────
    def inject_reading(name: str):
        """Populate the relevant telemetry field(s) with a realistic random value."""
        writes = {}   # dot-path -> value, matching simulate_data's record key format
        try:
            if name == "ctdo":
                sci = sens_st.scientific
                writes = {
                    "sensors.scientific.conductivity.port":  round(random.uniform(3.0, 5.5), 3),
                    "sensors.scientific.conductivity.stbd":  round(random.uniform(3.0, 5.5), 3),
                    "sensors.scientific.ctd_temp.port":      round(random.uniform(2.0, 28.0), 2),
                    "sensors.scientific.ctd_temp.stbd":      round(random.uniform(2.0, 28.0), 2),
                    "sensors.scientific.salinity.port":      round(random.uniform(33.0, 37.0), 2),
                    "sensors.scientific.salinity.stbd":      round(random.uniform(33.0, 37.0), 2),
                    "sensors.scientific.turbidity.port":     round(random.uniform(0.1, 5.0), 2),
                    "sensors.scientific.turbidity.stbd":     round(random.uniform(0.1, 5.0), 2),
                    "sensors.scientific.pressure.port":      round(random.uniform(1.0, 300.0), 1),
                    "sensors.scientific.pressure.stbd":      round(random.uniform(1.0, 300.0), 1),
                    "sensors.scientific.water_density.port": round(random.uniform(1020.0, 1028.0), 2),
                    "sensors.scientific.water_density.stbd": round(random.uniform(1020.0, 1028.0), 2),
                    "sensors.scientific.ph.port":            round(random.uniform(7.6, 8.3), 2),
                    "sensors.scientific.ph.stbd":             round(random.uniform(7.6, 8.3), 2),
                    "sensors.scientific.orp.port":            round(random.uniform(150.0, 350.0), 1),
                    "sensors.scientific.orp.stbd":            round(random.uniform(150.0, 350.0), 1),
                    "header.depth.value":                     round(random.uniform(50.0, 3000.0), 1),
                }

            elif name == "dissolved_o2":
                writes = {
                    "sensors.scientific.dissolved_oxygen.port": round(random.uniform(150.0, 300.0), 1),
                    "sensors.scientific.dissolved_oxygen.stbd": round(random.uniform(150.0, 300.0), 1),
                    "sensors.scientific.ctd_temp.port":          round(random.uniform(2.0, 28.0), 2),
                    "sensors.scientific.ctd_temp.stbd":          round(random.uniform(2.0, 28.0), 2),
                }

            elif name == "surface_ins":
                writes = {
                    "sensors.surface_ins.s_roll":      round(random.uniform(-5.0, 5.0), 2),
                    "sensors.surface_ins.s_pitch":      round(random.uniform(-5.0, 5.0), 2),
                    "sensors.surface_ins.s_heading":    round(random.uniform(0.0, 359.9), 1),
                    "sensors.surface_ins.s_speed1":     round(random.uniform(0.0, 3.0), 2),
                    "sensors.surface_ins.s_speed2":     round(random.uniform(0.0, 3.0), 2),
                    "sensors.surface_ins.s_speed3":     round(random.uniform(0.0, 3.0), 2),
                    "sensors.surface_ins.s_latitude":   round(random.uniform(8.0, 13.0), 6),
                    "sensors.surface_ins.s_longitude":  round(random.uniform(72.0, 80.0), 6),
                }

            elif name == "depth_sensor_pri":
                writes = {
                    "header.depth.value":           round(random.uniform(50.0, 3000.0), 1),
                    "sensors.redt_depth.s_depth":    round(random.uniform(50.0, 3000.0), 1),
                }

            elif name == "ins":
                writes = {
                    "sensors.surface_ins.s_heading": round(random.uniform(0.0, 359.9), 1),
                    "sensors.surface_ins.s_roll":    round(random.uniform(-5.0, 5.0), 2),
                    "sensors.surface_ins.s_pitch":   round(random.uniform(-5.0, 5.0), 2),
                }

            elif name == "dvl":
                writes = {
                    "bottom.east_speed.value":  round(random.uniform(-2.0, 2.0), 2),
                    "bottom.north_speed.value": round(random.uniform(-2.0, 2.0), 2),
                    "bottom.vert_speed.value":  round(random.uniform(-1.0, 1.0), 2),
                }

            elif name == "altimeter":
                # Kept under 90 m per SOP 92 ("data shall be received when altitude < 90 m")
                writes = {
                    "header.altitude.value": round(random.uniform(5.0, 89.0), 1),
                }

            # Apply the writes to app_state and lock the paths so the
            # JSON-replay simulator skips them while the reading is on screen.
            for path, value in writes.items():
                parts = path.split(".")
                obj = app_state
                for p in parts[:-1]:
                    obj = getattr(obj, p)
                leaf = parts[-1]
                setattr(obj, leaf, value)
                scenario_locked_paths.add(path)

        except AttributeError as e:
            print(f"[SCENARIO] Warning: inject_reading({name}): {e}")

    # ── Initialise scenario state ─────────────────────────────────────────────
    sc.active          = True
    sc.success         = None
    sc.mission_name    = "UNDERWATER IMAGING & SENSORS"
    sc.timer_total     = 600   # 10 minutes for 22 stages
    sc.timer_remaining = 600
    sc.result_message  = ""
    sc.current_stage   = 1
    scenario_locked_paths.clear()
    sc.feedback_msg    = (
        "SOP 64 ▶ Go to Switches_P1 → General Control Switches. "
        "Turn ON VHS_Power_P to power the Port video recorder. "
        "Check Video display and VHS_P status."
    )

    # ── Reset all fields used in this scenario ────────────────────────────────
    resets = [
        (sw_p, "vhs_power_p"),
        (sw_s, "vhs_power_s"),
        (sw_p, "led_emergency_port"),
        (sw_s, "led_emergency_port"),
        (sw_p, "sonar"),
        (sw_p, "surface_ins"),
        (img,  "hd_camera_p"),
        (img,  "hd_camera_s"),
        (img,  "hd_sdi_p3"),
        (img,  "hd_sdi_p4"),
        (img,  "hd_sdi_s2"),
        (img,  "hd_sdi_s3"),
        (sens, "ctdo"),
        (sens, "dissolved_o2"),
        (sens, "depth_sensor_pri"),
        (sens, "ins"),
        (sens, "dvl"),
        (sens, "altimeter"),
    ]
    for obj, field in resets:
        try:
            setattr(obj, field, False)
        except AttributeError as e:
            print(f"[SCENARIO] Warning: reset {field}: {e}")

    # Reset LED power fields
    for led in [img.led_p2, img.led_p3, img.led_s2, img.led_s3]:
        try:
            led.power = False
        except AttributeError:
            pass

    # Reset readings/telemetry fields touched by this scenario so stale
    # values from a previous run don't linger before the relevant switch
    # is turned ON again.
    try:
        sci = sens_st.scientific
        for row in [sci.conductivity, sci.ctd_temp, sci.salinity, sci.turbidity,
                    sci.pressure, sci.water_density, sci.ph, sci.orp, sci.dissolved_oxygen]:
            row.port = 0.0
            row.stbd = 0.0
        surf = sens_st.surface_ins
        surf.s_roll = surf.s_pitch = surf.s_heading = 0.0
        surf.s_speed1 = surf.s_speed2 = surf.s_speed3 = 0.0
        surf.s_latitude = surf.s_longitude = 0.0
        sens_st.redt_depth.s_depth = 0.0
        hdr.depth.value = 0.0
        hdr.altitude.value = 0.0
        app_state.bottom.east_speed.value = 0.0
        app_state.bottom.north_speed.value = 0.0
        app_state.bottom.vert_speed.value = 0.0
    except AttributeError as e:
        print(f"[SCENARIO] Warning: reset readings: {e}")

    # ── Helper: hold banner for reading_pause seconds ─────────────────────────
    async def reading_pause(seconds: int):
        for _ in range(seconds):
            if not sc.active:
                return
            sc.timer_remaining = max(0, sc.timer_remaining - 1)
            sc.blink = not sc.blink
            await broadcast_fn()
            await asyncio.sleep(1.0)

    # ── Helper: advance stage with confirmation pause then set next message ───
    async def confirm_and_advance(confirm_msg: str, next_msg: str, next_stage: int):
        sc.feedback_msg = confirm_msg
        await broadcast_fn()
        await reading_pause(READING_PAUSE_SECS)
        sc.current_stage = next_stage
        sc.feedback_msg  = next_msg

    # ── Main loop — one tick per second ───────────────────────────────────────
    for elapsed in range(1, sc.timer_total + 1):
        if not sc.active:
            break

        sc.timer_remaining = sc.timer_total - elapsed
        sc.blink = not sc.blink

        # ── Stage 1 — SOP 64: VHS_Power_P ────────────────────────────────────
        if sc.current_stage == 1:
            sc.feedback_msg = (
                "SOP 64 ▶ Switches_P1 → General Control Switches. "
                "Turn ON VHS_Power_P — powers Port video recorder. "
                "Check Video display and VHS_P status."
            )
            try:
                if sw_p.vhs_power_p:
                    await confirm_and_advance(
                        "✔ VHS_Power_P ON — Port video recorder powered. "
                        f"Check Video display. Moving to SOP 65 in {READING_PAUSE_SECS}s…",
                        "SOP 65 ▶ Switches_S1 → General Control Switches. "
                        "Turn ON VHS_Power_S — powers Stbd video recorder. "
                        "Check Video display and VHS_S status.",
                        2
                    )
            except AttributeError:
                pass

        # ── Stage 2 — SOP 65: VHS_Power_S ────────────────────────────────────
        elif sc.current_stage == 2:
            try:
                if sw_s.vhs_power_s:
                    await confirm_and_advance(
                        "✔ VHS_Power_S ON — Stbd video recorder powered. "
                        f"Check Video display. Moving to SOP 66 in {READING_PAUSE_SECS}s…",
                        "SOP 66 ▶ Imaging page → Turn ON HD CAM1_P (HD camera P). "
                        "Check video in Video Monitor. Verify zoom, focus, iris.",
                        3
                    )
            except AttributeError:
                pass

        # ── Stage 3 — SOP 66: HD Camera Port ─────────────────────────────────
        elif sc.current_stage == 3:
            try:
                if img.hd_camera_p:
                    await confirm_and_advance(
                        "✔ HD CAM1_P ON — Port HD camera powered. "
                        f"Check Video Monitor, zoom/focus/iris. Moving to SOP 67 in {READING_PAUSE_SECS}s…",
                        "SOP 67 ▶ Imaging page → Turn ON HD SDI_P3 (SD Camera P3 — landing). "
                        "Check video in Video Monitor.",
                        4
                    )
            except AttributeError:
                pass

        # ── Stage 4 — SOP 67: SD Camera P3 ───────────────────────────────────
        elif sc.current_stage == 4:
            try:
                if img.hd_sdi_p3:
                    await confirm_and_advance(
                        "✔ SD Camera P3 ON — Port landing camera powered. "
                        f"Check Video Monitor. Moving to SOP 68 in {READING_PAUSE_SECS}s…",
                        "SOP 68 ▶ Imaging page → Turn ON HD SDI_P4 (SD Camera P4 — fixed). "
                        "Check video in Video Monitor.",
                        5
                    )
            except AttributeError:
                pass

        # ── Stage 5 — SOP 68: SD Camera P4 ───────────────────────────────────
        elif sc.current_stage == 5:
            try:
                if img.hd_sdi_p4:
                    await confirm_and_advance(
                        "✔ SD Camera P4 ON — Port fixed camera powered. "
                        f"Check Video Monitor. Moving to SOP 69 in {READING_PAUSE_SECS}s…",
                        "SOP 69 ▶ Imaging page → Turn ON HD CAM1_S (HD camera S). "
                        "Check video in Video Monitor. Verify zoom, focus, iris.",
                        6
                    )
            except AttributeError:
                pass

        # ── Stage 6 — SOP 69: HD Camera Stbd ─────────────────────────────────
        elif sc.current_stage == 6:
            try:
                if img.hd_camera_s:
                    await confirm_and_advance(
                        "✔ HD CAM1_S ON — Stbd HD camera powered. "
                        f"Check Video Monitor, zoom/focus/iris. Moving to SOP 70 in {READING_PAUSE_SECS}s…",
                        "SOP 70 ▶ Imaging page → Turn ON HD SDI_S2 (SD Camera S3 — landing stbd). "
                        "Check video in Video Monitor.",
                        7
                    )
            except AttributeError:
                pass

        # ── Stage 7 — SOP 70: SD Camera S3 (→ hd_sdi_s2) ────────────────────
        elif sc.current_stage == 7:
            try:
                if img.hd_sdi_s2:
                    await confirm_and_advance(
                        "✔ SD Camera S3 ON — Stbd landing camera powered. "
                        f"Check Video Monitor. Moving to SOP 71 in {READING_PAUSE_SECS}s…",
                        "SOP 71 ▶ Imaging page → Turn ON HD SDI_S3 (SD Camera S4 — fixed stbd). "
                        "Check video in Video Monitor.",
                        8
                    )
            except AttributeError:
                pass

        # ── Stage 8 — SOP 71: SD Camera S4 (→ hd_sdi_s3) ────────────────────
        elif sc.current_stage == 8:
            try:
                if img.hd_sdi_s3:
                    await confirm_and_advance(
                        "✔ SD Camera S4 ON — Stbd fixed camera powered. "
                        f"Check Video Monitor. Moving to SOP 72 in {READING_PAUSE_SECS}s…",
                        "SOP 72 ▶ Imaging page → Turn ON LED Light P2 (LED_P2). "
                        "Check illumination change in Video Monitor.",
                        9
                    )
            except AttributeError:
                pass

        # ── Stage 9 — SOP 72: LED Light P2 ───────────────────────────────────
        elif sc.current_stage == 9:
            try:
                if img.led_p2.power:
                    await confirm_and_advance(
                        "✔ LED Light P2 ON — Port front LED 2 illuminated. "
                        f"Observe illumination in video. Moving to SOP 73 in {READING_PAUSE_SECS}s…",
                        "SOP 73 ▶ Imaging page → Turn ON LED Light P3 (LED_P3). "
                        "Check illumination change in Video Monitor.",
                        10
                    )
            except AttributeError:
                pass

        # ── Stage 10 — SOP 73: LED Light P3 ──────────────────────────────────
        elif sc.current_stage == 10:
            try:
                if img.led_p3.power:
                    await confirm_and_advance(
                        "✔ LED Light P3 ON — Port front LED 3 illuminated. "
                        f"Observe illumination in video. Moving to SOP 75 in {READING_PAUSE_SECS}s…",
                        "SOP 75 ▶ Switches_P1 → General Control Switches. "
                        "Turn ON LED_Emergency_Port (LED Light P1 toggle switch). "
                        "Check illumination change in video.",
                        11
                    )
            except AttributeError:
                pass

        # ── Stage 11 — SOP 75: LED Light P1 (toggle switch) ──────────────────
        elif sc.current_stage == 11:
            try:
                if sw_p.led_emergency_port:
                    await confirm_and_advance(
                        "✔ LED Light P1 ON — Port front LED 1 illuminated via toggle switch. "
                        f"Observe illumination in video. Moving to SOP 76 in {READING_PAUSE_SECS}s…",
                        "SOP 76 ▶ Imaging page → Turn ON LED Light S2 (LED_S2). "
                        "Check illumination change in Video Monitor.",
                        12
                    )
            except AttributeError:
                pass

        # ── Stage 12 — SOP 76: LED Light S2 ──────────────────────────────────
        elif sc.current_stage == 12:
            try:
                if img.led_s2.power:
                    await confirm_and_advance(
                        "✔ LED Light S2 ON — Stbd front LED 2 illuminated. "
                        f"Observe illumination in video. Moving to SOP 77 in {READING_PAUSE_SECS}s…",
                        "SOP 77 ▶ Imaging page → Turn ON LED Light S3 (LED_S3). "
                        "Check illumination change in Video Monitor.",
                        13
                    )
            except AttributeError:
                pass

        # ── Stage 13 — SOP 77: LED Light S3 ──────────────────────────────────
        elif sc.current_stage == 13:
            try:
                if img.led_s3.power:
                    await confirm_and_advance(
                        "✔ LED Light S3 ON — Stbd front LED 3 illuminated. "
                        f"Observe illumination in video. Moving to SOP 79 in {READING_PAUSE_SECS}s…",
                        "SOP 79 ▶ Switches_S1 → General Control Switches. "
                        "Turn ON LED_Emergency_Port (LED Light S1 toggle switch). "
                        "Check illumination change in video.",
                        14
                    )
            except AttributeError:
                pass

        # ── Stage 14 — SOP 79: LED Light S1 (toggle switch) ──────────────────
        elif sc.current_stage == 14:
            try:
                if sw_s.led_emergency_port:
                    await confirm_and_advance(
                        "✔ LED Light S1 ON — Stbd front LED 1 illuminated via toggle switch. "
                        f"Observe illumination in video. Moving to SOP 80 in {READING_PAUSE_SECS}s…",
                        "SOP 80 ▶ Switches_P1 → General Control Switches. "
                        "Turn ON SONAR (Obstacle Avoidance Sonar). "
                        "Run 837A software in NAV_PC. Check data and adjust gain if required. "
                        "Switch OFF during descend/ascend operations.",
                        15
                    )
            except AttributeError:
                pass

        # ── Stage 15 — SOP 80: Obstacle SONAR ────────────────────────────────
        # (No numeric sonar telemetry field exists in models.py — 837A
        #  software/gain data lives outside app_state, so nothing to inject.)
        elif sc.current_stage == 15:
            try:
                if sw_p.sonar:
                    await confirm_and_advance(
                        "✔ Obstacle SONAR ON — Check 837A software in NAV_PC. "
                        f"Verify sonar data and adjust gain. Moving to SOP 84 in {READING_PAUSE_SECS}s…",
                        "SOP 84 ▶ Sensors page → Turn ON CTDO (CTD_P). "
                        "Check Conductivity, Temperature, Depth, Salinity, Turbidity data "
                        "in the Sensor page and record values.",
                        16
                    )
            except AttributeError:
                pass

        # ── Stage 16 — SOP 84: CTD_P (→ ctdo) ───────────────────────────────
        elif sc.current_stage == 16:
            try:
                if sens.ctdo:
                    inject_reading("ctdo")
                    await confirm_and_advance(
                        "✔ CTDO (CTD_P) ON — Check and record: Conductivity, Temperature, "
                        f"Depth, Salinity, Turbidity in Sensors page. Moving to SOP 85 in {READING_PAUSE_SECS}s…",
                        "SOP 85 ▶ Sensors page → Turn ON Dissolved O2 (DO_S). "
                        "Check and record Dissolved Oxygen and Temperature in Sensor page.",
                        17
                    )
            except AttributeError:
                pass

        # ── Stage 17 — SOP 85: Dissolved O2 ─────────────────────────────────
        elif sc.current_stage == 17:
            try:
                if sens.dissolved_o2:
                    inject_reading("dissolved_o2")
                    await confirm_and_advance(
                        "✔ Dissolved O2 (DO_S) ON — Check and record Dissolved Oxygen "
                        f"and Temp in Sensors page. Moving to SOP 86 in {READING_PAUSE_SECS}s…",
                        "SOP 86 ▶ Switches_P1 → General Control Switches. "
                        "Turn ON Surface_INS — powers Surface INS in PS. "
                        "Check data in Sensor GUI and verify INS navigation mode.",
                        18
                    )
            except AttributeError:
                pass

        # ── Stage 18 — SOP 86: Surface INS ───────────────────────────────────
        elif sc.current_stage == 18:
            try:
                if sw_p.surface_ins:
                    inject_reading("surface_ins")
                    await confirm_and_advance(
                        "✔ Surface_INS ON — Check INS data in Sensor GUI. "
                        f"Verify navigation mode on web page. Moving to SOP 89 in {READING_PAUSE_SECS}s…",
                        "SOP 89 ▶ Sensors page → Turn ON Depth Sensor Pri (Depth_Primary). "
                        "Check depth data in Main GUI.",
                        19
                    )
            except AttributeError:
                pass

        # ── Stage 19 — SOP 89: Depth Sensor Primary ──────────────────────────
        elif sc.current_stage == 19:
            try:
                if sens.depth_sensor_pri:
                    inject_reading("depth_sensor_pri")
                    await confirm_and_advance(
                        "✔ Depth Sensor Pri ON — Check depth data in Main GUI header. "
                        f"Moving to SOP 90 in {READING_PAUSE_SECS}s…",
                        "SOP 90 ▶ Sensors page → Turn ON INS (INS_P). "
                        "Check INS-DVL data in Main GUI. Verify INS navigation mode on web page.",
                        20
                    )
            except AttributeError:
                pass

        # ── Stage 20 — SOP 90: INS_P ─────────────────────────────────────────
        elif sc.current_stage == 20:
            try:
                if sens.ins:
                    inject_reading("ins")
                    await confirm_and_advance(
                        "✔ INS_P ON — Check INS-DVL data in Main GUI. "
                        f"Verify navigation mode on web page. Moving to SOP 91 in {READING_PAUSE_SECS}s…",
                        "SOP 91 ▶ Sensors page → Turn ON DVL (DVL_P). "
                        "Check x, y, z speed data in Main GUI.",
                        21
                    )
            except AttributeError:
                pass

        # ── Stage 21 — SOP 91: DVL_P ─────────────────────────────────────────
        elif sc.current_stage == 21:
            try:
                if sens.dvl:
                    inject_reading("dvl")
                    await confirm_and_advance(
                        "✔ DVL_P ON — Check x, y, z speed data in Main GUI bottom strip. "
                        f"Moving to SOP 92 in {READING_PAUSE_SECS}s…",
                        "SOP 92 ▶ Sensors page → Turn ON Altimeter (Altimeter_S). "
                        "Check altitude data in Main GUI. "
                        "Data shall be received when altitude < 90 m.",
                        22
                    )
            except AttributeError:
                pass

        # ── Stage 22 — SOP 92: Altimeter_S ───────────────────────────────────
        elif sc.current_stage == 22:
            try:
                if sens.altimeter:
                    inject_reading("altimeter")
                    sc.feedback_msg = (
                        "✔ Altimeter_S ON — Check altitude data in Main GUI header. "
                        f"Data valid when altitude < 90 m. "
                        f"Verifying all systems for {READING_PAUSE_SECS}s…"
                    )
                    await broadcast_fn()
                    await reading_pause(READING_PAUSE_SECS)
                    sc.success        = True
                    sc.active         = False
                    sc.result_message = (
                        "✅ All imaging & sensor systems online. "
                        "SOP Steps 64–92 complete. Mission complete!"
                    )
                    break
            except AttributeError:
                pass

        await broadcast_fn()
        await asyncio.sleep(1.0)

    # ── Timer expired without completion ──────────────────────────────────────
    if sc.active and sc.success is None:
        sc.success        = False
        sc.active         = False
        sc.result_message = (
            f"⏰ Time expired at Stage {sc.current_stage}/{TOTAL_STAGES}. Mission failed."
        )

    await broadcast_fn()
    await asyncio.sleep(8)
    reset_scenario(sc)
    await broadcast_fn()
