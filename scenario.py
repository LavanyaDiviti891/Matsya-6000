import asyncio
import random
from dataclasses import dataclass
from typing import Optional


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
    Stage 1: pilot enables sw.dive_in
    Stage 2: pilot enables sw.vbt_set_value AND sw.freeboard_p
    Stage 3: pilot clicks VBS HPU button → b.vbs.hpu_enable = True
    Stage 4: tank auto-fills +5% per tick to 100% → success
    """
    sc = scenario_state
    sw = app_state.switches.state

    sc.active          = True
    sc.success         = None
    sc.mission_name    = "LOADING BALLAST TANK"
    sc.timer_total     = 60
    sc.timer_remaining = 60
    sc.result_message  = ""
    sc.feedback_msg    = "Descend Phase Started. Enable Dive In."
    sc.current_stage   = 1

    # Reset only confirmed sw fields (these exist — verified in main.py lines 989-992)
    sw.dive_in         = False
    sw.vbt_set_value   = False
    sw.freeboard_p     = False

    # VBS fields — wrap in try/except to avoid silent crash if model differs
    b = app_state.ballast
    try:
        b.vbs.hpu_enable = False
        b.vbs.tank_level = 0
    except AttributeError as e:
        print(f"[SCENARIO] Warning: could not reset VBS fields: {e}")

    depth_start    = 5.0
    depth_step     = (20.0 - 5.0) / 60   # +0.25m per tick
    altitude_start = 20.0
    altitude_step  = (20.0 - 5.0) / 60   # -0.25m per tick

    for elapsed in range(1, sc.timer_total + 1):
        if not sc.active:
            break

        try:
            app_state.header.depth.value    = round(depth_start    + depth_step    * elapsed, 1)
            app_state.header.altitude.value = round(altitude_start - altitude_step * elapsed, 1)
        except AttributeError as e:
            print(f"[SCENARIO] Warning: header depth/altitude: {e}")

        sc.timer_remaining = sc.timer_total - elapsed
        sc.blink = not sc.blink

        if sc.current_stage == 1:
            sc.feedback_msg = "Close hatch,complete the pre-dive checks and mention it. Enable Dive In."
            if sw.dive_in:
                sc.current_stage = 2
                sc.feedback_msg  = "Dive In enabled. Set VBT value and enable FreeBoard_P."

        elif sc.current_stage == 2:
            if sw.vbt_set_value and sw.freeboard_p:
                sc.current_stage = 3
                sc.feedback_msg  = "Life support checks done and mention the checks done. Enable VBS HPU."

        elif sc.current_stage == 3:
            try:
                hpu_on = b.vbs.hpu_enable
            except AttributeError:
                hpu_on = False
            if hpu_on:
                sc.current_stage = 4
                sc.feedback_msg  = "HPU ON. VBS tank filling..."

        elif sc.current_stage == 4:
            try:
                current = b.vbs.tank_level
                b.vbs.tank_level = min(100, current + 5)
                sc.feedback_msg  = f"Filling VBS tank... {b.vbs.tank_level}%"
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

    if sc.active and sc.success is None:
        sc.success        = False
        sc.active         = False
        sc.result_message = "Time expired before mission completion. Mission failed."

    await broadcast_fn(ScenarioOverlay_fn())
    await asyncio.sleep(6)
    reset_scenario(sc)
    await broadcast_fn(ScenarioOverlay_fn())
