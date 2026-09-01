"""
co2_scenario.py — combined "CO2 SCRUBBER FAILURE -> NAVIGATION INSTABILITY
-> EMERGENCY BUOY DEPLOYMENT" training mission.

This merges what used to be two separate missions (co2_scenario.py and
emergency_buoy_scenario.py) into one, in the order requested: the CO2
failure runs first: full descent, weight drop, CO2 alarm + recovery --
then, once CO2 recovers, navigation instability follows immediately and
the mission ends with the emergency buoy release. One scenario, one
Start/Reset pair (`/api/scenario/co2/start`, `/api/scenario/co2/reset` --
unchanged, so nothing on the frontend needs to know the routes moved).

  Stage 1  DESCENDING          scripted depth ramp toward seabed-approach
  Stage 2  APPROACHING         scripted altitude closure toward seabed
  Stage 3  WAIT_WEIGHTS        waits for 2 x 50kg service-drop weights
  Stage 4  CO2_RISING          CO2 climbing toward peak
  Stage 5  CO2_ALARM           CO2 alarm - waits for both scrubbers on
  Stage 6  CO2_RECOVERY        CO2 easing back to baseline
  Stage 7  NAV_INSTABILITY     (new) short delay, then instability begins
  Stage 8  NAV_CONFIRM         waits for SW-3 HEADING_CTRL + LATERAL TRIM
  Stage 9  BUOY_RELEASE        waits for any SW-3 MB EJ P/S switch
  Stage 10 COMPLETE            success (or failure, from stage 5's timeout)

Only stages 3, 8, and 9 wait indefinitely on real pilot action; every
other stage is scripted/timed so the mission always progresses.

ALARM / BEEP BEHAVIOUR (per this iteration's requirement):
  Neither the CO2 alarm nor the navigation-instability alarm drives any
  pop-up/banner. Both only ever set `sc.beep_level` to "" / "warning" /
  "critical":
    - CO2_ALARM (stage 5)        -> "critical" (continuous beep) until
                                     both scrubbers are on.
    - NAV_INSTABILITY (stage 7)  -> "critical" (continuous beep) until
                                     HEADING_CTRL + LATERAL TRIM are both
                                     engaged (stage 8 -> 9).
  `sc.feedback_msg` still carries the plain-text instruction for whatever
  already reads it (e.g. a Main-2 status line) -- that's just pilot
  guidance text, not an alarm widget, and is left as-is.

Field-path notes (unchanged from the original co2_scenario.py):
  - Weight-drop switches: ALL "Service Drop Weight" switches -- both
    PORT- and STARBOARD-labelled -- POST to `switches.p.sdwp_<n>` /
    `switches.p.sdws_<n>` (frontend quirk, not something to "fix" here).
    Only sdwp_1-4 / sdws_6-9 are the 50kg ones.
  - CO2 scrubber switches: `switches.s.co2_s` and `switches.s.co2_p`,
    both required (AND).
  - CO2 readings mirrored across: `hsss.p.co2`, `hsss.s.co2`,
    `environment.co2`.
  - Navigation-instability confirmation: SW-3 tab, `switches.sw3.heading_ctrl`
    and `switches.sw3.lat_trim` (KnobToggleSwitch "HEADING_CTRL" /
    "LATERAL TRIM"). These are real, clickable SW-3 controls.
  - Emergency buoy release: SW-3 tab, any of `switches.sw3.mb_ej_p1..p4`
    / `switches.sw3.mb_ej_s1..s4` (the Marker/Emergency-Buoy ejection
    3-way switches). Also real, clickable SW-3 controls.
  - While this scenario is active it owns `header.depth`,
    `header.altitude`, and all three CO2 fields exclusively -- main.py's
    live-data simulator must skip those paths (see the
    `app_state.co2_scenario.active` guard in simulate_data()) --
    unchanged from before.

Usage from main.py (unchanged -- same import name, same routes):

    import co2_scenario

    co2_scenario_task = None

    @app.post("/api/scenario/co2/start")
    async def co2_scenario_start():
        global co2_scenario_task
        if co2_scenario_task is None or co2_scenario_task.done():
            co2_scenario_task = asyncio.create_task(
                co2_scenario.run(app_state, broadcast)
            )
        return {"status": "ok"}

    @app.post("/api/scenario/co2/reset")
    async def co2_scenario_reset():
        global co2_scenario_task
        if co2_scenario_task and not co2_scenario_task.done():
            co2_scenario_task.cancel()
        co2_scenario.reset(app_state)
        await broadcast()
        return {"status": "ok"}
"""

import asyncio
import random

# ── stage constants ──────────────────────────────────────────────────────
STAGE_DESCENDING = 1
STAGE_APPROACHING = 2
STAGE_WAIT_WEIGHTS = 3
STAGE_CO2_RISING = 4
STAGE_CO2_ALARM = 5
STAGE_CO2_RECOVERY = 6
STAGE_NAV_INSTABILITY = 7
STAGE_NAV_CONFIRM = 8
STAGE_BUOY_RELEASE = 9
STAGE_COMPLETE = 10

DEPTH_TARGET_M = 5500.0
DESCENT_SECONDS = 20        # scripted descent pace to seabed-approach depth

ALTITUDE_START_M = 50.0     # where the altitude ramp begins (stage 2)
ALTITUDE_TARGET_M = 4.2     # where it settles (matches idle default)
ALTITUDE_THRESHOLD_M = 5.0  # "close enough" to trigger the weight-drop step
ALTITUDE_SECONDS = 15

WEIGHTS_REQUIRED = 2

CO2_START_PPM = 800.0
CO2_PEAK_PPM = 2000.0
CO2_RISE_SECONDS = 60
CO2_ALARM_AT_S = 10
CO2_RECOVERY_SECONDS = 10

# Short beat before the navigation-instability alarm fires, same idea as
# the old emergency_buoy_scenario.py's ALARM_DELAY_TICKS but expressed in
# whole seconds since this stage loop ticks at 1s (matching the rest of
# this file), not 0.2s.
NAV_INSTABILITY_DELAY_S = 3

WEIGHT_50KG_PORT_FIELDS = ("sdwp_1", "sdwp_2", "sdwp_3", "sdwp_4")
# The starboard row's switches live on their own field range (index+5) so
# they don't collide with the port row's sdwp_1..4/sdws_1..4 -- see
# SwitchesLayout.jsx, where SDW1_S..SDW4_S_50kg post to sdws_6..sdws_9
# (SDW5_S_100kg -> sdws_10 is the 100kg one, excluded here same as port).
WEIGHT_50KG_STBD_FIELDS = ("sdws_6", "sdws_7", "sdws_8", "sdws_9")
WEIGHT_50KG_FIELDS = WEIGHT_50KG_PORT_FIELDS + WEIGHT_50KG_STBD_FIELDS


def reset(app_state) -> None:
    """Return the combined CO2 / nav-instability scenario to idle."""
    sc = app_state.co2_scenario
    sc.active = False
    sc.success = None
    sc.mission_name = ""
    sc.result_message = ""
    sc.feedback_msg = ""
    sc.current_stage = 0
    sc.blink = False
    sc.timer_remaining = sc.timer_total
    sc.beep_level = ""


def _weights_dropped_count(app_state) -> int:
    sw_p = app_state.switches.p
    return sum(1 for f in WEIGHT_50KG_FIELDS if getattr(sw_p, f, False))


def _weights_ready(app_state) -> bool:
    # "2 x 50kg" means one port weight AND one starboard weight dropped.
    sw_p = app_state.switches.p
    port_dropped = any(getattr(sw_p, f, False) for f in WEIGHT_50KG_PORT_FIELDS)
    stbd_dropped = any(getattr(sw_p, f, False) for f in WEIGHT_50KG_STBD_FIELDS)
    return port_dropped and stbd_dropped


def _scrubbers_on(app_state) -> bool:
    # Both required (AND). Both toggles physically live on the S panel.
    sw_s = app_state.switches.s
    return bool(sw_s.co2_s and sw_s.co2_p)


def _navigation_confirmed(app_state) -> bool:
    """SW-3 tab: HEADING_CTRL and LATERAL TRIM knobs both engaged."""
    sw3 = app_state.switches.sw3
    return bool(sw3.heading_ctrl and sw3.lat_trim)


def _buoy_released(app_state) -> bool:
    """SW-3 tab: any Marker/Emergency-Buoy ejection switch."""
    sw3 = app_state.switches.sw3
    return bool(
        sw3.mb_ej_p1 or sw3.mb_ej_p2 or sw3.mb_ej_p3 or sw3.mb_ej_p4
        or sw3.mb_ej_s1 or sw3.mb_ej_s2 or sw3.mb_ej_s3 or sw3.mb_ej_s4
    )


def _set_co2(app_state, value: float) -> None:
    app_state.hsss.p.co2.value = value
    app_state.hsss.s.co2.value = value
    app_state.environment.co2.value = value


async def _ramp(app_state, get_value, set_value, target, seconds, sc, feedback_during=None, broadcast_fn=None):
    """Linearly ramp a scalar from its current value to `target` over
    `seconds`, broadcasting each tick. Returns immediately if already
    at/past target."""
    start = get_value(app_state)
    if seconds <= 0:
        set_value(app_state, target)
        return
    step = (target - start) / seconds
    for i in range(seconds):
        if not sc.active:
            return
        set_value(app_state, round(start + step * (i + 1), 2))
        if feedback_during:
            sc.feedback_msg = feedback_during
        if broadcast_fn:
            await broadcast_fn()
        await asyncio.sleep(1.0)
    set_value(app_state, target)


async def run(app_state, broadcast_fn):
    """Run the full CO2-failure -> navigation-instability -> buoy-release
    mission, in that order."""
    sc = app_state.co2_scenario
    sw3 = app_state.switches.sw3

    # ── initialise ──────────────────────────────────────────────────────
    sc.active = True
    sc.success = None
    sc.mission_name = "CO2 SCRUBBER FAILURE -> EMERGENCY BUOY DEPLOYMENT"
    sc.result_message = ""
    sc.current_stage = STAGE_DESCENDING
    sc.feedback_msg = f"Descending toward seabed-approach depth ({DEPTH_TARGET_M:.0f} m)."
    sc.timer_total = CO2_RISE_SECONDS
    sc.timer_remaining = CO2_RISE_SECONDS
    sc.blink = False
    sc.beep_level = ""

    # Reset scrubber + nav-instability switches at mission start.
    app_state.switches.s.co2_s = False
    app_state.switches.s.co2_p = False
    sw3.heading_ctrl = False
    sw3.lat_trim = False
    sw3.mb_ej_p1 = sw3.mb_ej_p2 = sw3.mb_ej_p3 = sw3.mb_ej_p4 = False
    sw3.mb_ej_s1 = sw3.mb_ej_s2 = sw3.mb_ej_s3 = sw3.mb_ej_s4 = False

    try:
        # ── stage 1: scripted descent to ~5500m ─────────────────────────
        if app_state.header.depth.value < DEPTH_TARGET_M:
            await _ramp(
                app_state,
                get_value=lambda s: s.header.depth.value,
                set_value=lambda s, v: setattr(s.header.depth, "value", v),
                target=DEPTH_TARGET_M,
                seconds=DESCENT_SECONDS,
                sc=sc,
                broadcast_fn=broadcast_fn,
            )
        if not sc.active:
            return
        sc.current_stage = STAGE_APPROACHING
        sc.feedback_msg = "Seabed-approach depth reached. Closing in on the seabed."
        await broadcast_fn()

        # ── stage 2: scripted altitude closure toward seabed ────────────
        app_state.header.altitude.value = ALTITUDE_START_M
        await _ramp(
            app_state,
            get_value=lambda s: s.header.altitude.value,
            set_value=lambda s, v: setattr(s.header.altitude, "value", v),
            target=ALTITUDE_TARGET_M,
            seconds=ALTITUDE_SECONDS,
            sc=sc,
            broadcast_fn=broadcast_fn,
        )
        if not sc.active:
            return
        sc.current_stage = STAGE_WAIT_WEIGHTS
        sc.feedback_msg = "Near seabed. Release 1 port and 1 starboard 50 kg service drop weight."
        await broadcast_fn()

        # ── stage 3: wait for 2 x 50kg weight drop (real pilot action) ──
        while sc.active and sc.current_stage == STAGE_WAIT_WEIGHTS:
            if _weights_ready(app_state):
                sc.current_stage = STAGE_CO2_RISING
                sc.feedback_msg = "Weights released. Trim adjusting. CO2 levels beginning to rise."
            await broadcast_fn()
            await asyncio.sleep(0.3)
        if not sc.active:
            return

        # ── stage 4/5: CO2 rise + alarm, timer-driven ───────────────────
        co2_step = (CO2_PEAK_PPM - CO2_START_PPM) / CO2_RISE_SECONDS
        sc.timer_remaining = CO2_RISE_SECONDS

        for elapsed in range(CO2_RISE_SECONDS):
            if not sc.active:
                return

            _set_co2(app_state, round(CO2_START_PPM + co2_step * elapsed, 1))
            sc.timer_remaining = CO2_RISE_SECONDS - elapsed
            sc.blink = not sc.blink

            if sc.current_stage == STAGE_CO2_RISING and elapsed >= CO2_ALARM_AT_S:
                sc.current_stage = STAGE_CO2_ALARM
                sc.feedback_msg = "CO2 levels critical. Enable both CO2 Scrubbers (Port & Starboard)."
                # Audio only -- continuous beep, no pop-up.
                sc.beep_level = "critical"

            elif sc.current_stage == STAGE_CO2_ALARM and _scrubbers_on(app_state):
                sc.current_stage = STAGE_CO2_RECOVERY
                sc.feedback_msg = "CO2 Scrubbers activated. CO2 decreasing..."
                sc.beep_level = ""
                break

            await broadcast_fn()
            await asyncio.sleep(1.0)

        # ── pilot never responded to the CO2 alarm in time ──────────────
        if sc.active and sc.current_stage != STAGE_CO2_RECOVERY:
            sc.success = False
            sc.active = False
            sc.current_stage = STAGE_COMPLETE
            sc.result_message = "CO2 levels exceeded safe limits. Mission failed."
            sc.beep_level = ""
            await broadcast_fn()
            await asyncio.sleep(6)
            reset(app_state)
            await broadcast_fn()
            return

        # ── stage 6: recovery -- CO2 back down to 800 ppm ───────────────
        co2_at_recovery = app_state.hsss.p.co2.value
        recovery_step = (co2_at_recovery - CO2_START_PPM) / CO2_RECOVERY_SECONDS

        for tick in range(CO2_RECOVERY_SECONDS):
            if not sc.active:
                return

            _set_co2(app_state, round(co2_at_recovery - recovery_step * tick, 1))
            sc.timer_remaining = CO2_RECOVERY_SECONDS - tick
            sc.blink = not sc.blink

            await broadcast_fn()
            await asyncio.sleep(1.0)

        _set_co2(app_state, CO2_START_PPM)

        # ── stage 7: navigation instability begins, beep only ───────────
        if not sc.active:
            return
        sc.current_stage = STAGE_NAV_INSTABILITY
        sc.feedback_msg = "CO2 normalised. Navigation instability detected."
        await broadcast_fn()

        # Randomise IMU/RPMs to show the mismatch, same as the old
        # emergency_buoy_scenario.py -- purely cosmetic telemetry, no
        # alarm widget involved.
        app_state.imu.pitch.value = round(random.uniform(-15, 15), 1)
        app_state.imu.roll.value = round(random.uniform(-20, 20), 1)

        for _ in range(NAV_INSTABILITY_DELAY_S):
            if not sc.active:
                return
            sc.blink = not sc.blink
            await broadcast_fn()
            await asyncio.sleep(1.0)

        if not sc.active:
            return
        sc.current_stage = STAGE_NAV_CONFIRM
        sc.feedback_msg = "On SW-3, engage HEADING_CTRL and LATERAL TRIM."
        # Audio only -- continuous beep, no pop-up/flashing alarm.
        sc.beep_level = "critical"
        await broadcast_fn()

        # ── stage 8: wait for HEADING_CTRL + LATERAL TRIM (real action) ─
        while sc.active and sc.current_stage == STAGE_NAV_CONFIRM:
            if _navigation_confirmed(app_state):
                sc.current_stage = STAGE_BUOY_RELEASE
                sc.feedback_msg = "Navigation recovery failed. On SW-3, release the EMERGENCY BUOY (any MB EJ P1-P4 / MB EJ S1-S4 switch)."
                sc.beep_level = ""
            await broadcast_fn()
            await asyncio.sleep(0.3)
        if not sc.active:
            return

        # ── stage 9: wait for emergency buoy release (real action) ──────
        while sc.active and sc.current_stage == STAGE_BUOY_RELEASE:
            if _buoy_released(app_state):
                sc.current_stage = STAGE_COMPLETE
                sc.feedback_msg = "Emergency Buoy Released"
                break
            await broadcast_fn()
            await asyncio.sleep(0.3)
        if not sc.active:
            return

        # ── stage 10: success ────────────────────────────────────────────
        sc.success = True
        sc.active = False
        sc.beep_level = ""
        sc.result_message = "Emergency Buoy Released. Mission complete."
        await broadcast_fn()
        await asyncio.sleep(6)
        reset(app_state)
        await broadcast_fn()

    except asyncio.CancelledError:
        # /api/scenario/co2/reset cancelled us mid-flight -- the caller
        # is responsible for calling reset(app_state) + broadcast_fn().
        raise
