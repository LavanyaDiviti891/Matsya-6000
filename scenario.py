import asyncio
from dataclasses import dataclass
from typing import Optional


@dataclass
class ScenarioState:
    active: bool = False
    mission_name: str = ""
    timer_total: int = 90
    timer_remaining: int = 90
    target_depth: float = 250.0
    depth_rate: float = 3.0
    success: Optional[bool] = None
    result_message: str = ""
    blink: bool = False
    current_stage: int = 0
    feedback_msg: str = ""


scenario_state = ScenarioState()


def reset_scenario(sc: ScenarioState) -> None:
    sc.active = False
    sc.success = None
    sc.mission_name = ""
    sc.result_message = ""
    sc.feedback_msg = ""
    sc.blink = False
    sc.current_stage = 0
    sc.timer_remaining = sc.timer_total


async def run_loading_ballast_scenario(app_state, broadcast_fn):
    """
    Scenario: LOADING BALLAST TANK
    Follows Main Ballast System SOP steps 96-100, then VBS fill.

    Switch fields live under:
        app_state.switches.p  →  SwitchesCategory_P   (was switches.state)
        app_state.switches.s  →  SwitchesCategory_S

    Ballast fields are unchanged:
        app_state.ballast.main_ballast  →  MainBallastState
        app_state.ballast.vbs           →  VBSTelemetry

    Stage 1 (SOP 96):  Pilot enables switches.p.hp_ap_on_off
                       → Populates Ballast GUI pressure readings.

    Stage 2 (SOP 97):  Pilot enables switches.p.hp_bp_on_off
                       → Opens MBS vent valves for 6 tanks.

    Stage 3 (SOP 98):  Pilot enables switches.p.dive_in
                       → Opens MBS vent valve for 7th tank.

    Stage 4 (SOP 99):  Pilot enables switches.p.vbt_set_value
                       → Updates pressure readings with post-vent values.

    Stage 5 (SOP 100): Pilot enables switches.p.freeboard_p
                       → Activates MBS blow valves; confirm freeboard.

    Stage 6 (VBS):     Pilot enables ballast.vbs.hpu_enable
                       → VBS tank auto-fills +5 % per tick up to 100 % → success.

    Timer: 90-second countdown. Expiry = mission failed.
    """
    sc   = scenario_state
    sw_p = app_state.switches.p   # SwitchesCategory_P (was app_state.switches.state)
    b    = app_state.ballast

    # ── Simulated air bottle pressure readings (bar) ──────────────────────────
    PRESSURE_S_INITIAL = 172.5   # SOP 96 — full charge
    PRESSURE_P_INITIAL = 171.8
    PRESSURE_S_POST    = 168.2   # SOP 99 — slight drop after vent
    PRESSURE_P_POST    = 167.6

    # ── Reading pause: seconds participants get to observe values ─────────────
    READING_PAUSE_SECS = 8

    # ── Initialise scenario state ─────────────────────────────────────────────
    sc.active          = True
    sc.success         = None
    sc.mission_name    = "LOADING BALLAST TANK"
    sc.timer_total     = 180      # 3 minutes — enough time for all 6 stages
    sc.timer_remaining = 180
    sc.result_message  = ""
    sc.current_stage   = 1
    sc.feedback_msg    = (
        "SOP 96 ▶ Turn ON HP_AP_ON/OFF in Switches_P1 (BATS Control) "
        "to power the Main Ballast system. "
        "Check and record air bottle pressure in Ballast page."
    )

    # ── Reset switches used in this scenario ──────────────────────────────────
    try:
        sw_p.hp_ap_on_off  = False
        sw_p.hp_bp_on_off  = False
        sw_p.dive_in       = False
        sw_p.vbt_set_value = False
        sw_p.freeboard_p   = False
    except AttributeError as e:
        print(f"[SCENARIO] Warning: could not reset switch fields: {e}")

    # ── Reset VBS fields ──────────────────────────────────────────────────────
    try:
        b.vbs.hpu_enable = False
        b.vbs.tank_level = 0
    except AttributeError as e:
        print(f"[SCENARIO] Warning: could not reset VBS fields: {e}")

    # ── Reset pressure display in Ballast GUI ─────────────────────────────────
    try:
        b.main_ballast.read_pressure_s   = 0.0
        b.main_ballast.read_pressure_p   = 0.0
        b.main_ballast.pressure_s_enable = False
        b.main_ballast.pressure_p_enable = False
    except AttributeError as e:
        print(f"[SCENARIO] Warning: could not reset pressure fields: {e}")

    # ── Depth / altitude animation: 5 m → 20 m over 180 s ───────────────────
    depth_start    = 5.0
    depth_end      = 6000
    altitude_start = 20.0
    altitude_end   = 5.0
    depth_step     = (depth_end    - depth_start)    / sc.timer_total
    altitude_step  = (altitude_end - altitude_start) / sc.timer_total

    # ── Helper: pause loop that keeps timer ticking & banner updating ─────────
    async def reading_pause(seconds: int):
        """Hold the current feedback message for `seconds` ticks so participants
        can observe and record the displayed values before the next instruction."""
        for _ in range(seconds):
            if not sc.active:
                return
            sc.timer_remaining = max(0, sc.timer_remaining - 1)
            sc.blink = not sc.blink
            await broadcast_fn()
            await asyncio.sleep(1.0)

    # ── Main loop — one tick per second ───────────────────────────────────────
    for elapsed in range(1, sc.timer_total + 1):
        if not sc.active:
            break

        # Animate header depth/altitude
        try:
            app_state.header.depth.value    = round(depth_start    + depth_step    * elapsed, 1)
            app_state.header.altitude.value = round(altitude_start + altitude_step * elapsed, 1)
        except AttributeError as e:
            print(f"[SCENARIO] Warning: header depth/altitude: {e}")

        sc.timer_remaining = sc.timer_total - elapsed
        sc.blink = not sc.blink

        # ── Stage 1 — SOP 96: HP_AP_ON/OFF → initial pressure reading ────────
        if sc.current_stage == 1:
            sc.feedback_msg = (
                " Turn ON HP_AP_ON/OFF in Switches_P1 (BATS Control) "
                "to power the Main Ballast system. "
                "Check and record air bottle pressure in Ballast page."
            )
            try:
                if sw_p.hp_ap_on_off:
                    b.main_ballast.read_pressure_s   = PRESSURE_S_INITIAL
                    b.main_ballast.read_pressure_p   = PRESSURE_P_INITIAL
                    b.main_ballast.pressure_s_enable = True
                    b.main_ballast.pressure_p_enable = True
                    sc.feedback_msg = (
                        f"HP_AP ON — Pressure_S: {PRESSURE_S_INITIAL} bar | "
                        f"Pressure_P: {PRESSURE_P_INITIAL} bar — "
                        f"Record these values now.  {READING_PAUSE_SECS}s…"
                    )
                    await broadcast_fn()
                    await reading_pause(READING_PAUSE_SECS)
                    sc.current_stage = 2
                    sc.feedback_msg = (
                        "Turn ON HP_BP_ON/OFF in Switches_P1 (BATS Control) — "
                        "opens MBS vent valves for 6 tanks. "
                        "Confirm neutral buoyancy on depth gauge."
                    )
            except AttributeError:
                pass

        # ── Stage 2 — SOP 97: HP_BP_ON/OFF → vent 6 tanks ───────────────────
        elif sc.current_stage == 2:
            try:
                if sw_p.hp_bp_on_off:
                    sc.feedback_msg = (
                        f"HP_BP ON — 6-tank vent valves open. "
                        f"Check depth gauge for neutral buoyancy. "
                        f"Proceeding to SOP 98 in {READING_PAUSE_SECS}s…"
                    )
                    await broadcast_fn()
                    await reading_pause(READING_PAUSE_SECS)
                    sc.current_stage = 3
                    sc.feedback_msg = (
                        "Turn ON Dive In in Switches_P1 (BATS Control) — "
                        "opens MBS vent valve for the 7th tank. "
                        "Check depth data for descend operations."
                    )
            except AttributeError:
                pass

        # ── Stage 3 — SOP 98: Dive In → 7th tank vent ────────────────────────
        elif sc.current_stage == 3:
            try:
                if sw_p.dive_in:
                    sc.feedback_msg = (
                        f"Dive In ON — 7th tank vent open. "
                        f"Check depth gauge — confirm vessel is descending. "
                        f"{READING_PAUSE_SECS}s…"
                    )
                    await broadcast_fn()
                    await reading_pause(READING_PAUSE_SECS)
                    sc.current_stage = 4
                    sc.feedback_msg = (
                        "Turn ON VBT_Set Value in Switches_P1 (BATS Control) "
                        "to re-confirm MBS. Check and record air bottle pressure in Ballast page."
                    )
            except AttributeError:
                pass

        # ── Stage 4 — SOP 99: VBT_Set Value → post-vent pressure reading ─────
        elif sc.current_stage == 4:
            try:
                if sw_p.vbt_set_value:
                    b.main_ballast.read_pressure_s   = PRESSURE_S_POST
                    b.main_ballast.read_pressure_p   = PRESSURE_P_POST
                    b.main_ballast.pressure_s_enable = True
                    b.main_ballast.pressure_p_enable = True
                    sc.feedback_msg = (
                        f"✔ VBT_Set Value ON — Pressure_S: {PRESSURE_S_POST} bar | "
                        f"Pressure_P: {PRESSURE_P_POST} bar — "
                        f"Record these post-vent values now {READING_PAUSE_SECS}s…"
                    )
                    await broadcast_fn()
                    await reading_pause(READING_PAUSE_SECS)
                    sc.current_stage = 5
                    sc.feedback_msg = (
                        "Turn ON FreeBoard_P in Switches_P1 (BATS Control) — "
                        "activates MBS blow valves. "
                        "Check bottle pressure and depth to confirm freeboard."
                    )
            except AttributeError:
                pass

        # ── Stage 5 — SOP 100: FreeBoard_P → blow valves ─────────────────────
        elif sc.current_stage == 5:
            try:
                if sw_p.freeboard_p:
                    sc.feedback_msg = (
                        f"✔ FreeBoard_P ON — blow valves active. "
                        f"Check depth gauge and confirm freeboard. "
                        f"Proceeding to VBS fill in {READING_PAUSE_SECS}s…"
                    )
                    await broadcast_fn()
                    await reading_pause(READING_PAUSE_SECS)
                    sc.current_stage = 6
                    sc.feedback_msg = (
                        "Go to Ballast page and click the HPU OFF button "
                        "to enable VBS HPU and begin Variable Ballast Tank fill."
                    )
            except AttributeError:
                pass

        # ── Stage 6 — VBS HPU ON → auto-fill tank to 100 % ──────────────────
        elif sc.current_stage == 6:
            try:
                hpu_on = b.vbs.hpu_enable
            except AttributeError:
                hpu_on = False

            if not hpu_on:
                sc.feedback_msg = (
                    "Go to Ballast page and click the HPU OFF button "
                    "to enable VBS HPU and begin Variable Ballast Tank fill."
                )
            else:
                try:
                    b.vbs.tank_level = min(100, b.vbs.tank_level + 5)
                    sc.feedback_msg  = f"Filling VBS tank… {b.vbs.tank_level:.0f}% — observe tank gauge in Ballast page."
                    if b.vbs.tank_level >= 100:
                        sc.success        = True
                        sc.active         = False
                        sc.result_message = "Variable Ballast Tank filled to 100%. Mission complete!"
                        break
                except AttributeError as e:
                    print(f"[SCENARIO] VBS tank_level error: {e}")
                    sc.success        = True
                    sc.active         = False
                    sc.result_message = "VBS Tank filled. Mission complete!"
                    break

        await broadcast_fn()
        await asyncio.sleep(1.0)

    # ── Timer expired without completion ──────────────────────────────────────
    if sc.active and sc.success is None:
        sc.success        = False
        sc.active         = False
        sc.result_message = " Time expired before mission completion. Mission failed."

    await broadcast_fn()
    await asyncio.sleep(8)
    reset_scenario(sc)
    await broadcast_fn()
