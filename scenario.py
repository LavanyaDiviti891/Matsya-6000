import asyncio
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
# CO2 Scrubber Failure Scenario
# ─────────────────────────────────────────────────────────────────────────────
async def run_carbondioxide_increase_scenario(app_state, broadcast_fn, ScenarioOverlay_fn):
    """
    Scenario: CO2 SCRUBBER FAILURE
    ─────────────────────────────────────────
    CO2 rises from 800 → 2000 ppm over 60s on both HSSS panels and sidebar.
    Stage 1: 10s countdown, then alarm fires.
    Stage 2: pilot enables co2_scrubber_p switch.
    After switch: CO2 decreases from current value back to 800 ppm over 30s.
    """
    sc = scenario_state
    sw = app_state.switches.state

    # ── initialise ────────────────────────────────────────────────────────────
    sc.active = True
    sc.success = None
    sc.mission_name = "CO2 Scrubber Failure"
    sc.timer_total = 60
    sc.timer_remaining = 60
    sc.result_message = ""
    sc.feedback_msg = "CO2 levels rising..."
    sc.current_stage = 1

    # Reset switch
    sw.co2_scrubber_p = False

    # CO2 rises 800 → 2000 ppm over 60 ticks (~20 ppm/tick)
    CO2_start = 800.0
    CO2_peak  = 2000.0
    CO2_step  = (CO2_peak - CO2_start) / sc.timer_total

    alarm_timer = 10  # alarm fires after 10s in stage 1

    # ── tick loop (rising phase) ───────────────────────────────────────────────
    for elapsed in range(sc.timer_total):
        if not sc.active:
            break

        current_co2 = round(CO2_start + CO2_step * elapsed, 1)

        # Update HSSS port and starboard CO2
        app_state.hsss.p.co2.value = current_co2
        app_state.hsss.s.co2.value = current_co2
        # Update sidebar environment CO2
        app_state.environment.co2.value = current_co2

        sc.timer_remaining = sc.timer_total - elapsed
        sc.blink = not sc.blink

        if sc.current_stage == 1:
            alarm_timer -= 1
            if alarm_timer <= 0:
                sc.feedback_msg = "ALARM: CO2 levels critical! Enable CO2 Scrubber."
                sc.current_stage = 2

        elif sc.current_stage == 2:
            if sw.co2_scrubber_p:
                sc.feedback_msg = "CO2 Scrubber activated. CO2 decreasing..."
                sc.current_stage = 3
                break  # exit rising loop, enter recovery loop

        await broadcast_fn(ScenarioOverlay_fn())
        await asyncio.sleep(1.0)

    # ── check if pilot never responded ────────────────────────────────────────
    if sc.active and sc.success is None and not sw.co2_scrubber_p:
        sc.success = False
        sc.active = False
        sc.result_message = "CO2 levels exceeded safe limits. Mission failed."
        await broadcast_fn(ScenarioOverlay_fn())
        await asyncio.sleep(6)
        reset_scenario(sc)
        await broadcast_fn(ScenarioOverlay_fn())
        return

    # ── recovery loop: CO2 decreases back to 800 ppm over 30 ticks ───────────
    recovery_ticks = 10
    co2_at_recovery = app_state.hsss.p.co2.value
    CO2_recovery_step = (co2_at_recovery - CO2_start) / recovery_ticks

    for tick in range(recovery_ticks):
        if not sc.active:
            break

        recovered_co2 = round(co2_at_recovery - CO2_recovery_step * tick, 1)
        app_state.hsss.p.co2.value   = recovered_co2
        app_state.hsss.s.co2.value   = recovered_co2
        app_state.environment.co2.value = recovered_co2

        sc.timer_remaining = recovery_ticks - tick
        sc.blink = not sc.blink

        await broadcast_fn(ScenarioOverlay_fn())
        await asyncio.sleep(1.0)

    # ── success ───────────────────────────────────────────────────────────────
    sc.success = True
    sc.active = False
    sc.result_message = "CO2 levels normalised. Mission complete."

    await broadcast_fn(ScenarioOverlay_fn())
    await asyncio.sleep(6)
    reset_scenario(sc)
    await broadcast_fn(ScenarioOverlay_fn())
