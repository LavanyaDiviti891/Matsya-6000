import asyncio
from dataclasses import dataclass, field
from typing import Optional


# ─────────────────────────────────────────────────────────────────────────────
# Scenario State  (single global instance, imported by main.py)
# ─────────────────────────────────────────────────────────────────────────────
@dataclass
class ScenarioState:
    active: bool = False
    mission_name: str = ""
    timer_total: int = 60          # seconds pilot has to act
    timer_remaining: int = 60
    target_depth: float = 250.0    # depth the sub will descend toward during drill
    depth_rate: float = 3.0        # m/s the depth increases per second of scenario
    success: Optional[bool] = None # None = in-progress | True = won | False = failed
    result_message: str = ""
    blink: bool = False            # toggled every second for flashing UI cues
    current_stage: int = 0         # to track multi-step scenarios
    feedback_msg: str = ""         # for mid-scenario hints/feedback



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
# Core scenario coroutine
# Call this as: asyncio.create_task(run_drop_weight_scenario(app_state, broadcast_fn))
# ─────────────────────────────────────────────────────────────────────────────

# ─────────────────────────────────────────────────────────────────────────────
# Maneuvering Phase Scenario
# ─────────────────────────────────────────────────────────────────────────────
async def run_maneuvering_phase_scenario(app_state, broadcast_fn, ScenarioOverlay_fn):
    """
    Scenario: MANEUVERING PHASE
    ─────────────────────────────────────────
    Pitch and roll fluctuate.
    Pilot enables thrusters, then joystick.
    After 30s from joystick enable, alarm shows "Manipulator in foreign body".
    Pilot must trigger emergency jettisoning manipulator switch.
    """
    import random
    sc = scenario_state
    sw = app_state.switches.state
    sb = app_state.sidebar

    # ── initialise ────────────────────────────────────────────────────────────
    sc.active = True
    sc.success = None
    sc.mission_name = "MANEUVERING PHASE"
    sc.timer_total = 60  # 3 minutes should be enough
    sc.timer_remaining = 60
    sc.result_message = ""
    sc.feedback_msg = "Maneuvering Phase Started"
    sc.current_stage = 1

    # Reset relevant switches
    sb.thrusters_enable = False
    sb.joystick = False
    sw.ej_manipulator_1 = False
    sw.ej_manipulator_2 = False
    sw.ej_manipulator_3 = False
    sw.ej_manipulator_4 = False

    stage3_timer = 10

    # ── tick loop ─────────────────────────────────────────────────────────────
    for elapsed in range(sc.timer_total):
        if not sc.active:
            break

        # Fluctuate pitch and roll
        app_state.imu.pitch.value = round(random.uniform(5, 10) * random.choice([-1, 1]), 1)
        app_state.imu.roll.value = round(random.uniform(20, 30) * random.choice([-1, 1]), 1)

        sc.timer_remaining = sc.timer_total - elapsed
        sc.blink = not sc.blink

        if sc.current_stage == 1:
            if sb.thrusters_enable:
                sc.current_stage = 2
        elif sc.current_stage == 2:
            if sb.joystick:
                sc.current_stage = 3
        elif sc.current_stage == 3:
            stage3_timer -= 1
            if stage3_timer <= 0:
                sc.feedback_msg = "ALARM: Manipulator in foreign body!"
                sc.current_stage = 4
        elif sc.current_stage == 4:
            if (sw.ej_manipulator_1 or sw.ej_manipulator_2 or 
                sw.ej_manipulator_3 or sw.ej_manipulator_4):
                sc.success = True
                sc.active = False
                sc.result_message = "Emergency jettisoning successful. Mission complete."
                break

        await broadcast_fn(ScenarioOverlay_fn())
        await asyncio.sleep(1.0)

    # ── check outcome ─────────────────────────────────────────────────────────
    if sc.active and sc.success is None:
        sc.success = False
        sc.active = False
        sc.result_message = "Time expired before mission completion. Mission failed."

    # show final state
    await broadcast_fn(ScenarioOverlay_fn())
    await asyncio.sleep(6)
    reset_scenario(sc)
    await broadcast_fn(ScenarioOverlay_fn())

