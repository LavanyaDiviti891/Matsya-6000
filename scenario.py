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
# Sample Collection Scenario
# ─────────────────────────────────────────────────────────────────────────────
async def run_sample_collection_scenario(app_state, broadcast_fn, ScenarioOverlay_fn):
    """
    Scenario: SAMPLE COLLECTION
    Stage 1: pilot enables all LEDs (P1-P3, S1-S3)
    Stage 2: pilot enables HD cameras and SDI outputs
    Stage 3: pilot enables joystick
    Stage 4: pilot enables Manipulator_1 or Manipulator_2
    Stage 5: pilot triggers ej_sampling_basket_1 → success
    """
    sc = scenario_state
    img = app_state.imaging
    sw = app_state.switches.state

    # ── initialise ────────────────────────────────────────────────────────────
    sc.active = True
    sc.success = None
    sc.mission_name = "SAMPLE COLLECTION"
    sc.timer_total = 60
    sc.timer_remaining = 60
    sc.result_message = ""
    sc.feedback_msg = "Sea bed reached. Enable all LEDs."
    sc.current_stage = 1

    # Reset imaging switches
    img.led_p1.power = False;  img.led_p2.power = False;  img.led_p3.power = False
    img.led_s1.power = False;  img.led_s2.power = False;  img.led_s3.power = False
    img.hd_camera_p  = False;  img.hd_camera_s  = False
    img.hd_sdi_p1    = False;  img.hd_sdi_p2    = False
    img.hd_sdi_s1    = False;  img.hd_sdi_s2    = False
    sw.joystick_enable      = False
    sw.ej_manipulator_1     = False
    sw.ej_manipulator_2     = False
    sw.ej_sampling_basket_1 = False

    # Set depth to seabed value
    app_state.header.depth.value = round(random.uniform(5700, 6000), 1)

    # ── tick loop ─────────────────────────────────────────────────────────────
    for elapsed in range(1, sc.timer_total + 1):
        if not sc.active:
            break

        sc.timer_remaining = sc.timer_total - elapsed
        sc.blink = not sc.blink

        if sc.current_stage == 1:
            # All 6 LEDs must be on
            if (img.led_p1.power and img.led_p2.power and img.led_p3.power and
                    img.led_s1.power and img.led_s2.power and img.led_s3.power):
                sc.current_stage = 2
                sc.feedback_msg = "LEDs on. Enable HD cameras and SDI outputs."

        elif sc.current_stage == 2:
            # Both cameras and SDI outputs on
            if (img.hd_camera_p and img.hd_camera_s and
                    img.hd_sdi_p1 and img.hd_sdi_p2 and
                    img.hd_sdi_s1 and img.hd_sdi_s2):
                sc.current_stage = 3
                sc.feedback_msg = "Cameras ready. Enable joystick."

        elif sc.current_stage == 3:
            if sw.joystick_enable:
                sc.current_stage = 4
                sc.feedback_msg = "Joystick enabled. Manipulator entangled."

        elif sc.current_stage == 4:
            if sw.ej_manipulator_1 or sw.ej_manipulator_2:
                sc.current_stage = 5
                sc.feedback_msg = "Sample basket entangled"

        elif sc.current_stage == 5:
            if sw.ej_sampling_basket_1:
                sc.current_stage = 6
                sc.feedback_msg = "Sample basket released!"
                await broadcast_fn(ScenarioOverlay_fn())
                break

        await broadcast_fn(ScenarioOverlay_fn())
        await asyncio.sleep(1.0)

    # ── timeout ───────────────────────────────────────────────────────────────
    if sc.active and sc.success is None and sc.current_stage != 6:
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
    sc.result_message = "Sample collected. Mission complete."
    await broadcast_fn(ScenarioOverlay_fn())
    await asyncio.sleep(6)
    reset_scenario(sc)
    await broadcast_fn(ScenarioOverlay_fn())
