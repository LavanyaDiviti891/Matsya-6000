import asyncio
import random
from dataclasses import dataclass
from typing import Optional


# ─────────────────────────────────────────────────────────────────────────────
# Scenario State  (single global instance, imported by main.py)
# ─────────────────────────────────────────────────────────────────────────────
@dataclass
class ScenarioState:
    active: bool = False
    mission_name: str = ""
    timer_total: int = 60
    timer_remaining: int = 60
    target_depth: float = 250.0
    depth_rate: float = 3.0
    success: Optional[bool] = None
    result_message: str = ""
    blink: bool = False
    current_stage: int = 0
    feedback_msg: str = ""


scenario_state = ScenarioState()


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────
def reset_scenario(sc: ScenarioState) -> None:
    """Return scenario to idle without touching app_state."""
    sc.active = False
    sc.success = None
    sc.mission_name = ""
    sc.result_message = ""
    sc.feedback_msg = ""
    sc.blink = False
    sc.current_stage = 0
    sc.timer_remaining = sc.timer_total


# ─────────────────────────────────────────────────────────────────────────────
# Thruster Vector Mismatch Scenario
# ─────────────────────────────────────────────────────────────────────────────
async def run_thruster_mismatch_scenario(app_state, broadcast_fn, ScenarioOverlay_fn):
    """
    Scenario: THRUSTER VECTOR MISMATCH
    ─────────────────────────────────────────
    T1, T3, T5, T7 RPMs randomised to simulate desynchronisation.
    Stage 1: 8s countdown → alarm fires
    Stage 2: pilot enables T1 power + T1 enable  → stage 3
    Stage 3: pilot enables T3 power + T3 enable  → stage 4
    Stage 4: pilot enables T5 power + T5 enable  → stage 5
    Stage 5: pilot enables T7 power + T7 enable  → stage 6
    Stage 6: pilot enables lateral_trim AND heading_trim → success
    Recovery: RPMs ramp back to 0 over 10 ticks.
    """
    sc = scenario_state
    pd = app_state.propulsion_detail
    sb = app_state.sidebar
    sw = app_state.switches.state

    # ── initialise ────────────────────────────────────────────────────────────
    sc.active = True
    sc.success = None
    sc.mission_name = "THRUSTER VECTOR MISMATCH"
    sc.timer_total = 60
    sc.timer_remaining = 60
    sc.result_message = ""
    sc.feedback_msg = "Thrusters desynchronised. Stand by..."
    sc.current_stage = 1

    # Reset switches
    pd.t1.power = False;  pd.t1.enable = False
    pd.t3.power = False;  pd.t3.enable = False
    pd.t5.power = False;  pd.t5.enable = False
    pd.t7.power = False;  pd.t7.enable = False
    sb.thrusters_enable = False
    sw.lateral_trim = False
    sw.heading_trim = False

    # Randomise RPMs to show mismatch immediately
    app_state.propulsion.t1_rpm = round(random.uniform(300, 1000), 1)
    app_state.propulsion.t3_rpm = round(random.uniform(300, 1000), 1)
    app_state.propulsion.t5_rpm = round(random.uniform(300, 1000), 1)
    app_state.propulsion.t7_rpm = round(random.uniform(300, 1000), 1)

    alarm_timer = 8  # alarm fires 8 ticks into stage 1

    # ── tick loop ─────────────────────────────────────────────────────────────
    for elapsed in range(1, sc.timer_total + 1):  # start at 1 so timer counts down visibly
        if not sc.active:
            break

        sc.timer_remaining = sc.timer_total - elapsed
        sc.blink = not sc.blink

        if sc.current_stage == 1:
            alarm_timer -= 1
            if alarm_timer <= 0:
                sc.feedback_msg = "ALARM: Thruster vector mismatch!"
                sc.current_stage = 2

        elif sc.current_stage == 2:
            if pd.t1.power and pd.t1.enable:
                sc.current_stage = 3
                sc.feedback_msg = "T1 restored."

        elif sc.current_stage == 3:
            if pd.t3.power and pd.t3.enable:
                sc.current_stage = 4
                sc.feedback_msg = "T3 restored."

        elif sc.current_stage == 4:
            if pd.t5.power and pd.t5.enable:
                sc.current_stage = 5
                sc.feedback_msg = "T5 restored."

        elif sc.current_stage == 5:
            if pd.t7.power and pd.t7.enable:
                sc.current_stage = 6
                sc.feedback_msg = "T7 restored."

        elif sc.current_stage == 6:
            if sw.lateral_trim and sw.heading_trim:
                sc.feedback_msg = "Trims set. Synchronising thrusters..."
                sc.current_stage = 7
                await broadcast_fn(ScenarioOverlay_fn())
                break  # → recovery loop

        await broadcast_fn(ScenarioOverlay_fn())
        await asyncio.sleep(1.0)

    # ── timeout ───────────────────────────────────────────────────────────────
    if sc.active and sc.success is None and sc.current_stage != 7:
        sc.success = False
        sc.active = False
        sc.result_message = "Time expired before mission completion. Mission failed."
        await broadcast_fn(ScenarioOverlay_fn())
        await asyncio.sleep(6)
        reset_scenario(sc)
        await broadcast_fn(ScenarioOverlay_fn())
        return

    # ── recovery: RPMs ramp to 0 over 10 ticks ────────────────────────────────
    recovery_ticks = 10
    t1_start = app_state.propulsion.t1_rpm
    t3_start = app_state.propulsion.t3_rpm
    t5_start = app_state.propulsion.t5_rpm
    t7_start = app_state.propulsion.t7_rpm

    for tick in range(recovery_ticks + 1):
        frac = tick / recovery_ticks
        app_state.propulsion.t1_rpm = round(t1_start * (1 - frac), 1)
        app_state.propulsion.t3_rpm = round(t3_start * (1 - frac), 1)
        app_state.propulsion.t5_rpm = round(t5_start * (1 - frac), 1)
        app_state.propulsion.t7_rpm = round(t7_start * (1 - frac), 1)
        sc.timer_remaining = recovery_ticks - tick
        sc.blink = not sc.blink
        await broadcast_fn(ScenarioOverlay_fn())
        await asyncio.sleep(1.0)

    # ── success ───────────────────────────────────────────────────────────────
    sc.success = True
    sc.active = False
    sc.result_message = "Thrusters synchronised. Mission complete."
    await broadcast_fn(ScenarioOverlay_fn())
    await asyncio.sleep(6)
    reset_scenario(sc)
    await broadcast_fn(ScenarioOverlay_fn())
