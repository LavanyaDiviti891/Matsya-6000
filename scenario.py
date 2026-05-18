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
async def run_drop_weight_scenario(app_state, broadcast_fn, ScenarioOverlay_fn):
    """
    Scenario: DROP WEIGHT — EMERGENCY ASCENT
    ─────────────────────────────────────────
    Depth begins increasing at `depth_rate` m/s.
    Pilot must flip either  em_drop_weight_p1_sc  OR  em_drop_weight_p2_pc
    in the Switches panel before the timer hits zero.

    Win  → switch flipped in time      → "MISSION COMPLETE"
    Fail → timer reaches zero           → "MISSION FAILED"
    """
    sc = scenario_state
    sw = app_state.switches.state

    # ── initialise ────────────────────────────────────────────────────────────
    sc.active = True
    sc.success = None
    sc.mission_name = "DROP WEIGHT — EMERGENCY ASCENT"
    sc.timer_remaining = sc.timer_total
    sc.result_message = ""

    # reset the two relevant switches so the pilot has to actively flip them
    sw.em_drop_weight_p1_sc = False
    sw.em_drop_weight_p2_pc = False

    start_depth = app_state.header.depth.value

    # ── tick loop ─────────────────────────────────────────────────────────────
    for elapsed in range(sc.timer_total):
        # update depth (sub is sinking)
        app_state.header.depth.value = round(start_depth + elapsed * sc.depth_rate, 1)
        sc.timer_remaining = sc.timer_total - elapsed
        sc.blink = not sc.blink          # toggle every second for flashing effect

        # push updated overlay to every connected client
        await broadcast_fn(ScenarioOverlay_fn())

        # check win condition
        if sw.em_drop_weight_p1_sc or sw.em_drop_weight_p2_pc:
            sc.success = True
            sc.active = False
            sc.result_message = (
                f"Drop weight released at {app_state.header.depth.value:.1f} m — "
                "Ascent initiated. Well done!"
            )
            await broadcast_fn(ScenarioOverlay_fn())
            await asyncio.sleep(6)       # show result for 6 s then auto-clear
            reset_scenario(sc)
            await broadcast_fn(ScenarioOverlay_fn())
            return

        await asyncio.sleep(1.0)

    # ── time expired ──────────────────────────────────────────────────────────
    sc.success = False
    sc.active = False
    sc.result_message = (
        f"No action taken at {app_state.header.depth.value:.1f} m — "
        "Sub exceeded safe depth. Mission failed."
    )
    await broadcast_fn(ScenarioOverlay_fn())
    await asyncio.sleep(6)
    reset_scenario(sc)
    await broadcast_fn(ScenarioOverlay_fn())


# ─────────────────────────────────────────────────────────────────────────────
# Sequential Drop Scenario (2 minutes)
# ─────────────────────────────────────────────────────────────────────────────
async def run_sequential_drop_scenario(app_state, broadcast_fn, ScenarioOverlay_fn):
    """
    Scenario: SEQUENTIAL DROP DRILL
    ─────────────────────────────────────────
    Depth increases.
    At >= 50m, user must drop Port Side SDW 1.
    At >= 100m, user must drop Port Side SDW 2.
    Timer: 120 seconds.
    """
    sc = scenario_state
    sw = app_state.switches.state

    # ── initialise ────────────────────────────────────────────────────────────
    sc.active = True
    sc.success = None
    sc.mission_name = "SEQUENTIAL DROP DRILL"
    sc.timer_total = 120
    sc.timer_remaining = 120
    sc.result_message = ""
    sc.feedback_msg = "TASK 1: Descend initialized. Prepare to drop weight 1 at 50m."
    sc.current_stage = 1

    # Reset relevant switches
    sw.port_side_sdw_1 = False
    sw.port_side_sdw_2 = False

    start_depth = 0.0 # start at surface
    app_state.header.depth.value = start_depth

    # Speed: we have 120s total. Let's reach 50m at 40s (1.25m/s), 100m at 80s, give them time to react.
    sc.depth_rate = 1.25

    # ── tick loop ─────────────────────────────────────────────────────────────
    for elapsed in range(sc.timer_total):
        if not sc.active:
            break

        # update depth
        app_state.header.depth.value = round(start_depth + elapsed * sc.depth_rate, 1)
        current_depth = app_state.header.depth.value
        sc.timer_remaining = sc.timer_total - elapsed
        sc.blink = not sc.blink

        # logic for stage 1 (50m)
        if sc.current_stage == 1:
            if current_depth < 50.0:
                sc.feedback_msg = f"TASK 1: Descending... Current: {current_depth:.1f}m. Target: 50m"
                if sw.port_side_sdw_1 or sw.port_side_sdw_2:
                    sc.success = False
                    sc.active = False
                    sc.result_message = "Weight dropped too early! Mission failed."
                    break
            else:
                sc.feedback_msg = "TASK 1: Depth ≥ 50m! DROP WEIGHT 1 (Port Side SDW 1) NOW!"
                if sw.port_side_sdw_2:
                    sc.success = False
                    sc.active = False
                    sc.result_message = "Wrong weight dropped! Expected SDW 1. Mission failed."
                    break
                elif sw.port_side_sdw_1:
                    sc.feedback_msg = "TASK 1: Weight 1 Dropped. Descending to 100m..."
                    sc.current_stage = 2
                    sw.port_side_sdw_1 = False # user has flipped it, we acknowledge

        # logic for stage 2 (100m)
        elif sc.current_stage == 2:
            if current_depth < 100.0:
                sc.feedback_msg = f"TASK 2: Descending... Current: {current_depth:.1f}m. Target: 100m"
                if sw.port_side_sdw_2:
                    sc.success = False
                    sc.active = False
                    sc.result_message = "Weight 2 dropped too early! Mission failed."
                    break
            else:
                sc.feedback_msg = "TASK 2: Depth ≥ 100m! DROP WEIGHT 2 (Port Side SDW 2) NOW!"
                if sw.port_side_sdw_2:
                    sc.success = True
                    sc.active = False
                    sc.result_message = "Both weights dropped correctly. Ascent initiated. Well done!"
                    break

        await broadcast_fn(ScenarioOverlay_fn())
        await asyncio.sleep(1.0)

    # ── check outcome ─────────────────────────────────────────────────────────
    if sc.active and sc.success is None:
        # timer expired
        sc.success = False
        sc.active = False
        sc.result_message = "Time expired before mission completion. Mission failed."

    # show final state
    await broadcast_fn(ScenarioOverlay_fn())
    await asyncio.sleep(6)
    reset_scenario(sc)
    await broadcast_fn(ScenarioOverlay_fn())

