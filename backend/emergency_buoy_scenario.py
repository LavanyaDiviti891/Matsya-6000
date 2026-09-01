"""
emergency_buoy_scenario.py — EMERGENCY BUOY DEPLOYMENT training mission.

Ported from the old FastHTML/HTMX UI's scenario.py (run_emergency_buoy_scenario)
to this codebase's async-task / websocket-broadcast style (see sample_scenario.py
for the pattern this follows).

No timer: the old UI's 60s countdown / fail-on-timeout was removed (it made
the alarm fire almost immediately and gave the pilot no real time to react
before the mission was declared failed). Each stage now waits indefinitely
for its condition, exactly like sample_scenario.py.

Stage logic (minus the timer, and minus the old "turn thrusters on" step):
  Stage 1: navigation instability builds, alarm fires after a short delay
  Stage 2: pilot confirms navigation on the SW-3 tab: HEADING_CTRL +
           LATERAL TRIM knobs both engaged
  Stage 3: pilot releases the EMERGENCY BUOY on the SW-3 tab (any
           MB EJ P1-P4 / MB EJ S1-S4 switch) -> mission complete

NOTE -- the old Stage 3 ("bring T1/T3/T5/T7 to POWER + ENABLE") has been
removed. The UI now starts every dive with thrusters already powered and
enabled (see models.py ThrusterTelemetry / SidebarControls defaults) --
the vehicle is assumed to already be underway, not freshly powered on.
Asking the pilot to "turn on" thrusters that are already on had no real
action to perform, so that stage is gone; navigation confirmation now
leads straight to the buoy release.

IMPORTANT -- why this doesn't use switches.p.heading_trim / surface_ins /
em_buoy_release_*:
  Those fields exist in models.py but SwitchesLayout.jsx never renders a
  control for them -- there is no button/knob anywhere in the UI that sets
  them, so a scenario gated on them can NEVER be completed by clicking
  anything on screen. Per instruction, SwitchesLayout.jsx is NOT being
  modified to add new controls. Instead this scenario is gated on fields
  that are ALREADY wired to real, clickable controls on the existing SW-3
  tab:
    - switches.sw3.heading_ctrl / switches.sw3.lat_trim  (KnobToggleSwitch
      "HEADING_CTRL" / "LATERAL TRIM")
    - switches.sw3.mb_ej_p1..p4 / switches.sw3.mb_ej_s1..s4  (the
      Marker/Emergency-Buoy ejection 3-way switches)
  Thrusters (t1/t3/t5/t7 power+enable) and sidebar.thrusters_enable are
  no longer part of this scenario's stage gating -- they default to ON
  (vehicle already underway) and this mission no longer asks the pilot
  to toggle them.

Usage from main.py:

    import emergency_buoy_scenario

    buoy_scenario_task = None

    @app.post("/api/scenario/buoy/start")
    async def buoy_scenario_start():
        global buoy_scenario_task
        if buoy_scenario_task is None or buoy_scenario_task.done():
            buoy_scenario_task = asyncio.create_task(
                emergency_buoy_scenario.run(app_state, broadcast)
            )
        return {"status": "ok"}

    @app.post("/api/scenario/buoy/reset")
    async def buoy_scenario_reset():
        global buoy_scenario_task
        if buoy_scenario_task and not buoy_scenario_task.done():
            buoy_scenario_task.cancel()
        emergency_buoy_scenario.reset(app_state)
        await broadcast()
        return {"status": "ok"}
"""

import asyncio
import random

# How many 0.2s ticks to wait in stage 1 before the alarm fires
# (0.2s * 15 = ~3s -- gives a beat before the alarm, without the
# old UI's fast 1s-tick / 8-tick-early-fire feel).
ALARM_DELAY_TICKS = 15


def reset(app_state) -> None:
    """Return the buoy-deployment scenario to idle."""
    bs = app_state.buoy_scenario
    bs.active = False
    bs.success = None
    bs.mission_name = ""
    bs.result_message = ""
    bs.feedback_msg = ""
    bs.blink = False
    bs.current_stage = 0
    bs.alarm_active = False
    bs.alarm_message = ""


def _side_confirmed(sw_side) -> bool:
    """True if this ONE side (p or s) has both heading_trim + surface_ins on."""
    return bool(sw_side.heading_trim and sw_side.surface_ins)


def _navigation_confirmed(app_state) -> bool:
    """
    SW-3 tab: HEADING_CTRL and LATERAL TRIM knobs both engaged.
    (switches.p/s.heading_trim + surface_ins have no on-screen control --
    see the module docstring -- so this scenario is gated on the SW-3
    knobs that are actually clickable instead.)
    """
    sw3 = app_state.switches.sw3
    return bool(sw3.heading_ctrl and sw3.lat_trim)


def _buoy_released(app_state) -> bool:
    """
    SW-3 tab: any Marker/Emergency-Buoy ejection switch (MB EJ P1-P4 /
    MB EJ S1-S4). (switches.p/s.em_buoy_release_1..4 have no on-screen
    control -- see the module docstring -- so this scenario is gated on
    the SW-3 switches that are actually clickable instead.)
    """
    sw3 = app_state.switches.sw3
    return bool(
        sw3.mb_ej_p1 or sw3.mb_ej_p2 or sw3.mb_ej_p3 or sw3.mb_ej_p4
        or sw3.mb_ej_s1 or sw3.mb_ej_s2 or sw3.mb_ej_s3 or sw3.mb_ej_s4
    )


async def run(app_state, broadcast_fn):
    """
    Run the EMERGENCY BUOY DEPLOYMENT scenario to completion (or cancel).
    No timer/timeout -- each stage waits indefinitely for its condition.
    """
    bs = app_state.buoy_scenario
    pd = app_state.propulsion_detail
    sb = app_state.sidebar
    sw3 = app_state.switches.sw3

    # ── initialise ──────────────────────────────────────────────────────
    bs.active = True
    bs.success = None
    bs.mission_name = "EMERGENCY BUOY DEPLOYMENT"
    bs.result_message = ""
    bs.feedback_msg = "NAVIGATION INSTABILITY DETECTED"
    bs.current_stage = 1
    bs.alarm_active = False
    bs.alarm_message = ""
    bs.blink = False

    # Thrusters are intentionally left as-is here (they default to ON --
    # the vehicle is already underway on a dive). This scenario no longer
    # has a "turn thrusters on" stage, so it must not switch them off
    # either, or the pilot would be asked to fix something the mission
    # itself broke.

    sw3.heading_ctrl = False
    sw3.lat_trim = False
    sw3.mb_ej_p1 = sw3.mb_ej_p2 = sw3.mb_ej_p3 = sw3.mb_ej_p4 = False
    sw3.mb_ej_s1 = sw3.mb_ej_s2 = sw3.mb_ej_s3 = sw3.mb_ej_s4 = False

    # Randomise IMU/RPMs to show mismatch immediately, same as old UI
    app_state.imu.pitch.value = round(random.uniform(-15, 15), 1)
    app_state.imu.roll.value = round(random.uniform(-20, 20), 1)
    app_state.propulsion.t1_rpm = round(random.uniform(300, 1000), 1)
    app_state.propulsion.t3_rpm = round(random.uniform(300, 1000), 1)
    app_state.propulsion.t5_rpm = round(random.uniform(300, 1000), 1)
    app_state.propulsion.t7_rpm = round(random.uniform(300, 1000), 1)

    alarm_timer = ALARM_DELAY_TICKS

    try:
        # ── event loop (no countdown) ────────────────────────────────
        while bs.active:
            bs.blink = not bs.blink

            if bs.current_stage == 1:
                alarm_timer -= 1
                if alarm_timer <= 0:
                    bs.alarm_active = True
                    bs.alarm_message = "NAVIGATION INSTABILITY DETECTED"
                    bs.feedback_msg = "ALARM: NAVIGATION INSTABILITY DETECTED. On SW-3, engage HEADING_CTRL and LATERAL TRIM."
                    bs.current_stage = 2

            elif bs.current_stage == 2:
                if _navigation_confirmed(app_state):
                    bs.current_stage = 3
                    bs.feedback_msg = "Navigation recovery failed. On SW-3, release the EMERGENCY BUOY (any MB EJ P1-P4 / MB EJ S1-S4 switch)."

            elif bs.current_stage == 3:
                if _buoy_released(app_state):
                    bs.current_stage = 4
                    bs.feedback_msg = "Emergency Buoy Released"
                    bs.alarm_active = False
                    await broadcast_fn()
                    break

            await broadcast_fn()
            await asyncio.sleep(0.2)

        # ── success ─────────────────────────────────────────────────
        bs.success = True
        bs.active = False
        bs.alarm_active = False
        bs.result_message = "Emergency Buoy Released, Mission complete."
        await broadcast_fn()
        await asyncio.sleep(6)
        reset(app_state)
        await broadcast_fn()

    except asyncio.CancelledError:
        # /api/scenario/buoy/reset cancelled us mid-flight -- the caller
        # is responsible for calling reset(app_state) + broadcast_fn().
        raise
