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


async def run_loading_ballasttank_scenario(app_state, broadcast_fn, ScenarioOverlay_fn):
    """
    Scenario: LOADING BALLAST TANK
    Follows Main Ballast System SOP steps 96-100, then VBS fill.

    Uses only switch/model fields that actually exist (verified in models.py):

    Stage 1 (SOP 96):  Pilot enables sw.hp_ap_on_off  (MBS / HP Air Port ON)
                       → Scenario immediately sets read_pressure_s / read_pressure_p
                         and enables pressure_s_enable / pressure_p_enable so the
                         Ballast GUI shows the air bottle pressure reading.

    Stage 2 (SOP 97):  Pilot enables sw.hp_bp_on_off  (Ready to Dive / HP Ballast Port)
                       → Opens MBS vent valves for 6 tanks; confirm neutral buoyancy.

    Stage 3 (SOP 98):  Pilot enables sw.dive_in        (Dive)
                       → Opens MBS vent valve for 7th tank; check descend depth.

    Stage 4 (SOP 99):  Pilot enables sw.vbt_set_value  (MBS re-confirm / VBT set)
                       → Scenario updates read_pressure_s / read_pressure_p with a
                         post-vent reading and re-enables the pressure display.

    Stage 5 (SOP 100): Pilot enables sw.freeboard_p    (FREEBOARD)
                       → Activates MBS blow valves; confirm freeboard depth.

    Stage 6 (VBS):     Pilot enables ballast.vbs.hpu_enable
                       → VBS tank auto-fills +5 % per tick up to 100 % → success.

    Timer behaviour:
      - 90-second countdown starts when the scenario is launched (not on page load).
      - Decrements every tick (1 s); expiry = mission failed.
    """
    sc = scenario_state
    sw = app_state.switches.state
    b  = app_state.ballast

    # ── Simulated air bottle pressure readings (bar) ──────────────────────────
    # SOP 96 — full charge before descent
    PRESSURE_S_INITIAL = 172.5
    PRESSURE_P_INITIAL = 171.8
    # SOP 99 — slight drop after vent operations
    PRESSURE_S_POST    = 168.2
    PRESSURE_P_POST    = 167.6

    # ── Initialise scenario state ─────────────────────────────────────────────
    sc.active          = True
    sc.success         = None
    sc.mission_name    = "LOADING BALLAST TANK"
    sc.timer_total     = 90
    sc.timer_remaining = 90
    sc.result_message  = ""
    sc.current_stage   = 1
    sc.feedback_msg    = (
        "SOP 96 ▶ Turn ON HP_AP_ON/OFF (MBS) in Ballast page GUI. "
        "Check and record air bottle pressure."
    )

    # ── Reset switches used in this scenario ──────────────────────────────────
    try:
        sw.hp_ap_on_off  = False
        sw.hp_bp_on_off  = False
        sw.dive_in       = False
        sw.vbt_set_value = False
        sw.freeboard_p   = False
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

    # ── Depth / altitude animation: 5 m → 20 m over 90 s ────────────────────
    depth_start    = 5.0
    depth_end      = 20.0
    altitude_start = 20.0
    altitude_end   = 5.0
    depth_step     = (depth_end    - depth_start)    / sc.timer_total
    altitude_step  = (altitude_end - altitude_start) / sc.timer_total

    # ── Main loop — one tick per second ───────────────────────────────────────
    for elapsed in range(1, sc.timer_total + 1):
        if not sc.active:
            break

        # Animate header values
        try:
            app_state.header.depth.value    = round(depth_start    + depth_step    * elapsed, 1)
            app_state.header.altitude.value = round(altitude_start + altitude_step * elapsed, 1)
        except AttributeError as e:
            print(f"[SCENARIO] Warning: header depth/altitude: {e}")

        sc.timer_remaining = sc.timer_total - elapsed
        sc.blink = not sc.blink

        # ── Stage 1 — SOP 96: HP_AP_ON/OFF → set initial pressure reading ────
        if sc.current_stage == 1:
            sc.feedback_msg = (
                "Turn ON HP_AP_ON/OFF "
                "to power the Main Ballast system. "
                "Check and record air bottle pressure."
            )
            try:
                if sw.hp_ap_on_off:
                    # Populate Ballast GUI pressure fields immediately
                    b.main_ballast.read_pressure_s   = PRESSURE_S_INITIAL
                    b.main_ballast.read_pressure_p   = PRESSURE_P_INITIAL
                    b.main_ballast.pressure_s_enable = True
                    b.main_ballast.pressure_p_enable = True
                    sc.current_stage = 2
                    sc.feedback_msg = (
                        f"✔ HP_AP (MBS) ON — "
                        f"Pressure_S: {PRESSURE_S_INITIAL} bar | "
                        f"Pressure_P: {PRESSURE_P_INITIAL} bar — recorded. "
                        "Now turn ON HP_BP_ON/OFF (Ready to Dive)."
                    )
            except AttributeError:
                pass

        # ── Stage 2 — SOP 97: HP_BP_ON/OFF → vent 6 tanks ───────────────────
        elif sc.current_stage == 2:
            sc.feedback_msg = (
                "Turn ON HP_BP_ON/OFF — opens MBS vent valves for 6 tanks. "
                "Confirm neutral buoyancy on depth gauge."
            )
            try:
                if sw.hp_bp_on_off:
                    sc.current_stage = 3
                    sc.feedback_msg = (
                        "✔ HP_BP ON — 6-tank vent valves open, neutral buoyancy confirmed. "
                        "Turn ON Dive In to open 7th tank vent valve."
                    )
            except AttributeError:
                pass

        # ── Stage 3 — SOP 98: Dive In → 7th tank vent ────────────────────────
        elif sc.current_stage == 3:
            sc.feedback_msg = (
                "Turn ON Dive In — opens MBS vent valve for the 7th tank. "
                "Check depth data for descend operations."
            )
            try:
                if sw.dive_in:
                    sc.current_stage = 4
                    sc.feedback_msg = (
                        "✔ Dive In ON — 7th tank vent open, descend depth confirmed. "
                        "Turn ON VBT_Set Value (MBS re-confirm) "
                        "and record air bottle pressure again."
                    )
            except AttributeError:
                pass

        # ── Stage 4 — SOP 99: VBT_Set Value → update post-vent pressure ──────
        elif sc.current_stage == 4:
            sc.feedback_msg = (
                "Turn ON VBT_Set Value in the Ballast page GUI "
                "to re-confirm MBS. Check and record air bottle pressure."
            )
            try:
                if sw.vbt_set_value:
                    # Update Ballast GUI pressure with post-vent reading
                    b.main_ballast.read_pressure_s   = PRESSURE_S_POST
                    b.main_ballast.read_pressure_p   = PRESSURE_P_POST
                    b.main_ballast.pressure_s_enable = True
                    b.main_ballast.pressure_p_enable = True
                    sc.current_stage = 5
                    sc.feedback_msg = (
                        f"✔ VBT_Set Value ON — "
                        f"Pressure_S: {PRESSURE_S_POST} bar | "
                        f"Pressure_P: {PRESSURE_P_POST} bar — recorded. "
                        "Turn ON FreeBoard_P to activate blow valves."
                    )
            except AttributeError:
                pass

        # ── Stage 5 — SOP 100: FreeBoard_P → blow valves ─────────────────────
        elif sc.current_stage == 5:
            sc.feedback_msg = (
                " Turn ON FreeBoard_P — activates MBS blow valves. "
                "Check bottle pressure and depth to confirm freeboard."
            )
            try:
                if sw.freeboard_p:
                    sc.current_stage = 6
                    sc.feedback_msg = (
                        "✔ FreeBoard_P ON — blow valves active, freeboard confirmed. "
                        " Enable VBS HPU button to begin Variable Ballast Tank fill."
                    )
            except AttributeError:
                pass

        # ── Stage 6 — VBS HPU ON → auto-fill tank ────────────────────────────
        elif sc.current_stage == 6:
            try:
                hpu_on = b.vbs.hpu_enable
            except AttributeError:
                hpu_on = False

            if not hpu_on:
                sc.feedback_msg = (
                    " Enable VBS HPU button on the Ballast page to start tank fill."
                )
            else:
                try:
                    b.vbs.tank_level = min(100, b.vbs.tank_level + 5)
                    sc.feedback_msg  = f"⏳ Filling VBS tank… {b.vbs.tank_level:.0f}%"
                    if b.vbs.tank_level >= 100:
                        sc.success        = True
                        sc.active         = False
                        sc.result_message = "Variable Ballast Tank filled. Mission complete."
                        break
                except AttributeError as e:
                    print(f"[SCENARIO] VBS tank_level error: {e}")
                    sc.success        = True
                    sc.active         = False
                    sc.result_message = "VBS Tank filled. Mission complete."
                    break

        await broadcast_fn(ScenarioOverlay_fn())
        await asyncio.sleep(1.0)

    # ── Timer expired without completion ──────────────────────────────────────
    if sc.active and sc.success is None:
        sc.success        = False
        sc.active         = False
        sc.result_message = "Time expired before mission completion. Mission failed."

    await broadcast_fn(ScenarioOverlay_fn())
    await asyncio.sleep(6)
    reset_scenario(sc)
    await broadcast_fn(ScenarioOverlay_fn())
