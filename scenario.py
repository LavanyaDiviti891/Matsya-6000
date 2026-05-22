import asyncio
from dataclasses import dataclass
from typing import Optional


# ─────────────────────────────────────────────────────────────────────────────
# Scenario State
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


def reset_scenario(sc: ScenarioState) -> None:
    sc.active = False
    sc.success = None
    sc.mission_name = ""
    sc.result_message = ""
    sc.feedback_msg = ""
    sc.blink = False
    sc.current_stage = 0
    sc.timer_remaining = sc.timer_total


# ─────────────────────────────────────────────────────────────────────────────
# Scenario: POWERING MATSYA
# broadcast_fn = broadcast_all_layouts (a coroutine from main.py)
# ScenarioOverlay_fn is unused — overlay is embedded in AppLayout directly
# ─────────────────────────────────────────────────────────────────────────────
async def run_powering_matsya_scenario(app_state, broadcast_fn, ScenarioOverlay_fn=None):
    """
    Stage 1: Turn ON ab_p + e_batts
    Stage 2: Turn ON mcb + ab_p_bms + ab_b
    Stage 3: Turn ON mb_p_1 through mb_p_5
    Stage 4: Turn ON md_pde  →  Mission complete
    """
    sc = scenario_state
    sw = app_state.switches.state

    # ── Initialise ────────────────────────────────────────────────────────────
    sc.active          = True
    sc.success         = None
    sc.mission_name    = "POWERING MATSYA"
    sc.timer_total     = 60
    sc.timer_remaining = 60
    sc.result_message  = ""
    sc.feedback_msg    = "POWER THE VEHICLE: Turn ON AB_P and E_BATTS"
    sc.current_stage   = 1

    # Reset relevant switch states
    sw.ab_p     = False
    sw.e_batts  = False
    sw.mcb      = False
    sw.ab_p_bms = False
    sw.ab_b     = False
    sw.mb_p_1   = False
    sw.mb_p_2   = False
    sw.mb_p_3   = False
    sw.mb_p_4   = False
    sw.mb_p_5   = False
    sw.mb_p_pde = False
    sw.md_pde   = False

    await broadcast_fn()

    # ── Timer + stage-check loop ──────────────────────────────────────────────
    while sc.active and sc.success is None and sc.timer_remaining > 0:
        await asyncio.sleep(1.0)
        sc.timer_remaining -= 1
        sc.blink = not sc.blink

        if sc.current_stage == 1:
            if sw.ab_p and sw.e_batts:
                sc.current_stage = 2
                sc.feedback_msg = "Note down the insulation value and based on that take a call on further powering"

        elif sc.current_stage == 2:
            if sw.mcb and sw.ab_p_bms and sw.ab_b:
                sc.current_stage = 3
                sc.feedback_msg = "Switch ON the PC"

        elif sc.current_stage == 3:
            if sw.mb_p_1 and sw.mb_p_2 and sw.mb_p_3 and sw.mb_p_4 and sw.mb_p_5:
                sc.current_stage = 4
                sc.feedback_msg = "Now distribute the power"

        elif sc.current_stage == 4:
            if sw.md_pde:
                sc.success        = True
                sc.active         = False
                sc.result_message = "Vehicle powered successfully. Switch ON the LED."
                await broadcast_fn()
                await asyncio.sleep(6)
                reset_scenario(sc)
                await broadcast_fn()
                return

        await broadcast_fn()

    # ── Timer expired ─────────────────────────────────────────────────────────
    if sc.active and sc.success is None:
        sc.success        = False
        sc.active         = False
        sc.result_message = "Time expired before mission completion. Mission failed."

    await broadcast_fn()
    await asyncio.sleep(6)
    reset_scenario(sc)
    await broadcast_fn()
