"""
sample_scenario.py — SAMPLE COLLECTION training mission.

Ported from the old FastHTML/HTMX UI's scenario.py + main.py wiring.

No timer: the mission just waits for each stage's condition and advances
whenever the pilot completes it, however long that takes. (The old UI had
a 60s countdown/fail-on-timeout; that's intentionally removed here.)

Stage logic (unchanged from the old UI):
  Stage 1: pilot enables all 6 imaging LEDs (P1-P3, S1-S3)
  Stage 2: pilot enables both HD cameras + both port/stbd SDI outputs
  Stage 3: pilot enables the joystick
  Stage 4: pilot engages Manipulator 1 or 2
  Stage 5: pilot triggers the sample basket release -> mission complete

Field-path notes:
  - Joystick: the pilot's "Joystick" toggle in the sidebar (the one wired
    to POST /api/toggle_joystick) flips `app_state.sidebar.joystick` --
    NOT `switches.p/s.joystick_enable` (those are separate, unrelated
    fields on the switch panels that this toggle never touches). Stage 3
    must check `sidebar.joystick`.
  - Manipulator / sample basket: old UI used a single flat
    `switches.state.<field>`; new UI splits Port/Starboard, so a switch
    counts as "on" if it's on EITHER panel.

Usage from main.py:

    import sample_scenario

    sample_scenario_task = None

    @app.post("/api/scenario/sample/start")
    async def sample_scenario_start():
        global sample_scenario_task
        if sample_scenario_task is None or sample_scenario_task.done():
            sample_scenario_task = asyncio.create_task(
                sample_scenario.run(app_state, broadcast)
            )
        return {"status": "ok"}

    @app.post("/api/scenario/sample/reset")
    async def sample_scenario_reset():
        global sample_scenario_task
        if sample_scenario_task and not sample_scenario_task.done():
            sample_scenario_task.cancel()
        sample_scenario.reset(app_state)
        await broadcast()
        return {"status": "ok"}
"""

import asyncio
import random


def reset(app_state) -> None:
    """Return the sample-collection scenario to idle."""
    sc = app_state.sample_scenario
    sc.active = False
    sc.success = None
    sc.mission_name = ""
    sc.result_message = ""
    sc.feedback_msg = ""
    sc.current_stage = 0


def _joystick_on(app_state) -> bool:
    return bool(app_state.sidebar.joystick)


def _manipulator_on(app_state) -> bool:
    sw3 = app_state.switches.sw3
    return bool(
        sw3.ejm_p1 or sw3.ejm_p2 or sw3.ejm_p3 or sw3.ejm_p4
        or sw3.ejm_s1 or sw3.ejm_s2 or sw3.ejm_s3 or sw3.ejm_s4
    )


def _basket_released(app_state) -> bool:
    sw3 = app_state.switches.sw3
    return bool(sw3.ejs_p1 or sw3.ejs_p2 or sw3.ejs_s1 or sw3.ejs_s2)


async def run(app_state, broadcast_fn):
    """
    Run the SAMPLE COLLECTION scenario to completion (or cancel).
    No timer/timeout -- each stage waits indefinitely for its condition.
    """
    sc = app_state.sample_scenario
    img = app_state.imaging

    # ── initialise ──────────────────────────────────────────────────────
    sc.active = True
    sc.success = None
    sc.mission_name = "SAMPLE COLLECTION"
    sc.result_message = ""
    sc.feedback_msg = "Sea bed reached. Enable all LEDs."
    sc.current_stage = 1

    # Reset imaging switches
    img.led_p1.power = False
    img.led_p2.power = False
    img.led_p3.power = False
    img.led_s1.power = False
    img.led_s2.power = False
    img.led_s3.power = False
    img.hd_camera_p = False
    img.hd_camera_s = False
    img.hd_sdi_p1 = False
    img.hd_sdi_p2 = False
    img.hd_sdi_s1 = False
    img.hd_sdi_s2 = False
    app_state.sidebar.joystick = False
    sw3 = app_state.switches.sw3
    sw3.ejm_p1 = sw3.ejm_p2 = sw3.ejm_p3 = sw3.ejm_p4 = False
    sw3.ejm_s1 = sw3.ejm_s2 = sw3.ejm_s3 = sw3.ejm_s4 = False
    sw3.ejs_p1 = sw3.ejs_p2 = sw3.ejs_s1 = sw3.ejs_s2 = False

    # Set depth to a seabed value, same range as the old UI
    app_state.header.depth.value = round(random.uniform(5700, 6000), 1)

    try:
        # ── event loop (no countdown) ───────────────────────────────────
        while sc.active:
            if sc.current_stage == 1:
                if (img.led_p1.power and img.led_p2.power and img.led_p3.power
                        and img.led_s1.power and img.led_s2.power and img.led_s3.power):
                    sc.current_stage = 2
                    sc.feedback_msg = "LEDs on. Enable HD cameras and SDI outputs."

            elif sc.current_stage == 2:
                if (img.hd_camera_p and img.hd_camera_s
                        and img.hd_sdi_p1 and img.hd_sdi_p2
                        and img.hd_sdi_s1 and img.hd_sdi_s2):
                    sc.current_stage = 3
                    sc.feedback_msg = "Cameras ready. Enable joystick."

            elif sc.current_stage == 3:
                if _joystick_on(app_state):
                    sc.current_stage = 4
                    sc.feedback_msg = "Joystick enabled. Manipulator entangled."

            elif sc.current_stage == 4:
                if _manipulator_on(app_state):
                    sc.current_stage = 5
                    sc.feedback_msg = "Sample basket entangled"

            elif sc.current_stage == 5:
                if _basket_released(app_state):
                    sc.current_stage = 6
                    sc.feedback_msg = "Sample basket released!"
                    await broadcast_fn()
                    break

            await broadcast_fn()
            await asyncio.sleep(0.2)

        # ── success ─────────────────────────────────────────────────────
        sc.success = True
        sc.active = False
        sc.result_message = "Sample collected. Mission complete."
        await broadcast_fn()
        await asyncio.sleep(6)
        reset(app_state)
        await broadcast_fn()

    except asyncio.CancelledError:
        # /api/scenario/sample/reset cancelled us mid-flight -- the caller
        # is responsible for calling reset(app_state) + broadcast_fn().
        raise
