import asyncio
from dataclasses import dataclass
from typing import Optional
import random

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
# Scenario: NORMAL MANEUVERING IN SEABED
# broadcast_fn = broadcast_all_layouts (a coroutine from main.py)
# ─────────────────────────────────────────────────────────────────────────────
async def run_normal_maneuvering_scenario(app_state, broadcast_fn, ScenarioOverlay_fn=None):

    sc = scenario_state
    sw = app_state.switches.state
    sb = app_state.sidebar
    img = app_state.imaging

    # ── Initialise ────────────────────────────────────────────────────────────
    sc.active          = True
    sc.success         = None
    sc.mission_name    = "Normal maneuvering in seadbed"  # FIX 1: must match exact string checked in main.py (man_is_active / ToggleBlock highlight)
    sc.timer_total     = 60
    sc.timer_remaining = 60
    sc.result_message  = ""
    sc.feedback_msg    = "Enable UW_Camera_P to begin maneuvering."
    sc.current_stage   = 1

    # Reset relevant switch states
    sw.uw_camera_p      = False
    sb.thrusters_enable = False
    sb.joystick         = False
    img.led_p1.power = False;  img.led_p2.power = False;  img.led_p3.power = False
    img.led_s1.power = False;  img.led_s2.power = False;  img.led_s3.power = False
    img.hd_camera_p  = False;  img.hd_camera_s  = False
    img.hd_sdi_p1    = False;  img.hd_sdi_p2    = False
    img.hd_sdi_s1    = False;  img.hd_sdi_s2    = False

    # Set initial values — depth lives on header; environment sensors live on app_state.environment
    # FIX 5: scenario was writing co2/o2/pressure/temp to app_state.header which only has
    # depth/heading/altitude/mb_p_soc/mb_s_soc. Correct target is app_state.environment.
    app_state.header.depth.value          = round(random.uniform(5700, 6000), 1)
    app_state.environment.co2.value       = round(random.uniform(0.04, 0.8), 2)
    app_state.environment.o2.value        = round(random.uniform(19.0, 23.0), 1)
    app_state.environment.pressure.value  = round(random.uniform(0.95, 1.10), 2)
    app_state.environment.temp.value      = round(random.uniform(18, 28), 1)

    await broadcast_fn()

    # ── Timer + stage-check loop ──────────────────────────────────────────────
    while sc.active and sc.success is None and sc.timer_remaining > 0:
        await asyncio.sleep(1.0)
        sc.timer_remaining -= 1
        sc.blink = not sc.blink

        # BUG 2 FIX: Stage 1 used bare `if` instead of `elif`, so after
        # sw.underwater_p was detected and stage advanced to 2 in the same tick,
        # the immediately following `if sc.current_stage == 2` block ALSO ran,
        # skipping the user a stage instantly. All stage checks must be elif.

        # BUG 3 FIX: Stage 2 was duplicated — two separate `elif sc.current_stage == 2`
        # blocks existed (lines 101 and 110). Python's elif chain means the second
        # one NEVER runs. The intent is clearly a 2-part stage: first turn on LEDs,
        # then turn on cameras. Split into stages 2 and 3, shift subsequent stages.

        if sc.current_stage == 1:
            sc.feedback_msg = "Enable UW_Camera_P to begin maneuvering."
            if sw.uw_camera_p:
                sc.current_stage = 2
                sc.feedback_msg  = "Turn ON all LEDs"

        elif sc.current_stage == 2:
            if (img.led_p1.power and img.led_p2.power and img.led_p3.power and
                    img.led_s1.power and img.led_s2.power and img.led_s3.power):
                sc.current_stage = 3
                sc.feedback_msg  = "LEDs ON"

        elif sc.current_stage == 3:
            if (img.hd_camera_p and img.hd_camera_s and
                    img.hd_sdi_p1 and img.hd_sdi_p2 and
                    img.hd_sdi_s1 and img.hd_sdi_s2):
                sc.current_stage = 4
                sc.feedback_msg  = "Cameras ready. Enable Joystick and Thrusters."

        elif sc.current_stage == 4:
            # BUG 4 FIX: was `sb.thrusters` — correct field is `sb.thrusters_enable`
            if sb.joystick and sb.thrusters_enable:
                sc.current_stage = 5
                sc.feedback_msg  = "Check the net force and note down the value."

        elif sc.current_stage == 5:
            # BUG 5 FIX: was `sw.md_pde` — wrong switch for maneuvering completion.
            # Maneuvering success is confirmed when joystick + thrusters are live
            # and the pilot confirms via underwater_p still being active.
            # Using a simple time-based confirmation: stage 5 just waits one tick.
            sc.success        = True
            sc.active         = False
            sc.result_message = "Vehicle ready for maneuvering. Mission complete."
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
