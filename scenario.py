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
async def run_emergency_buoy_scenario(app_state, broadcast_fn, ScenarioOverlay_fn):
    """
    Scenario: EMERGENCY BUOY DEPLOYEMENT
    
    """
    sc = scenario_state
    pd = app_state.propulsion_detail
    sb = app_state.sidebar
    sw = app_state.switches.state

    # ── initialise ────────────────────────────────────────────────────────────
    sc.active = True
    sc.success = None
    sc.mission_name = "EMERGENCY BUOY DEPLOYMENT"
    sc.timer_total = 60
    sc.timer_remaining = 60
    sc.result_message = ""
    sc.feedback_msg = "NAVIGATION INSTABILITY DETECTED"
    sc.current_stage = 1

    # Reset switches
    pd.t1.power = False;  pd.t1.enable = False
    pd.t3.power = False;  pd.t3.enable = False
    pd.t5.power = False;  pd.t5.enable = False
    pd.t7.power = False;  pd.t7.enable = False
    sb.thrusters_enable = False
    
    sw.heading_trim = False
    sw.surface_ins = False
    sw.em_buoy_release_1 = False
    sw.em_buoy_release_2 = False

    # Randomise RPMs to show mismatch immediately
    app_state.imu.pitch.value = round(random.uniform(-15, 15), 1)
    app_state.imu.roll.value = round(random.uniform(-20, 20), 1)
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
                sc.feedback_msg = "ALARM: NAVIGATION INSTABILITY DETECTED"
                sc.current_stage = 2

        elif sc.current_stage == 2:
            if sw.surface_ins and sw.heading_trim:
                sc.current_stage = 3
                sc.feedback_msg = "PROPULSION RESPONSE DEGRADED"

        
        elif sc.current_stage == 3:
            if pd.t3.power and pd.t3.enable and pd.t5.power and pd.t5.enable and pd.t7.power and pd.t7.enable and pd.t1.power and pd.t1.enable :
                sc.current_stage = 4
                sc.feedback_msg = "Recovery failed, Deploy BUOY"

        elif sc.current_stage == 4:
            if sw.em_buoy_release_1 or sw.em_buoy_release_2:
                sc.current_stage = 5
                sc.feedback_msg = "Emergency Buoy Released"

                await broadcast_fn(ScenarioOverlay_fn())
                break  # → recovery loop

        await broadcast_fn(ScenarioOverlay_fn())
        await asyncio.sleep(1.0)

    # ── timeout ───────────────────────────────────────────────────────────────
    if sc.active and sc.success is None and sc.current_stage != 5:
        sc.success = False
        sc.active = False
        sc.result_message = "Time expired before mission completion. Mission failed."
        await broadcast_fn(ScenarioOverlay_fn())
        await asyncio.sleep(6)
        reset_scenario(sc)
        await broadcast_fn(ScenarioOverlay_fn())
        return

   
    # ── success ───────────────────────────────────────────────────────────────
    sc.success = True
    sc.active = False
    sc.result_message = "Emergency Buoy Released, Mission complete."
    await broadcast_fn(ScenarioOverlay_fn())
    await asyncio.sleep(6)
    reset_scenario(sc)
    await broadcast_fn(ScenarioOverlay_fn())
