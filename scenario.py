import asyncio
from dataclasses import dataclass, field
from typing import Optional
import time

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
# Emergency Drop Weights Scenario
# ─────────────────────────────────────────────────────────────────────────────
async def run_emg_dropweights_scenario(app_state, broadcast_fn, ScenarioOverlay_fn):
    """
    Scenario: EMERGENCY DROP WEIGHTS
    ─────────────────────────────────────────
    Sub ascends: depth decreases gradually from 1000m → 510m over 60s.
    Altitude increases inversely from 30m → 100m.
    Pilot must enable port_side_sdw_1, then starboard_side_sdw_1.
    After 10s in stage 3 without action, alarm fires.
    Pilot must trigger em_drop_weight_p1_sc or em_drop_weight_p2_pc to succeed.
    """
    sc = scenario_state
    sw = app_state.switches.state
    sb = app_state.sidebar

    # ── initialise ────────────────────────────────────────────────────────────
    sc.active = True
    sc.success = None
    sc.mission_name = "Emergency Drop weights"
    sc.timer_total = 60
    sc.timer_remaining = 60
    sc.result_message = ""
    sc.feedback_msg = "Ascend Phase Started"
    sc.current_stage = 1

    # Reset relevant switches
    sw.port_side_sdw_1 = False
    sw.starboard_side_sdw_1 = False
    sw.em_drop_weight_p1_sc = False
    sw.em_drop_weight_p2_pc = False

    # Depth decreases from 1000m → 510m over 60s (~8.17m per tick)
    depth_start    = 1000.0
    depth_end      = 510.0
    depth_step     = (depth_start - depth_end) / sc.timer_total

    # Altitude increases inversely from 30m → 100m over 60s (~1.17m per tick)
    altitude_start = 30.0
    altitude_end   = 100.0
    altitude_step  = (altitude_end - altitude_start) / sc.timer_total

    stage3_timer = 10

    # ── tick loop ─────────────────────────────────────────────────────────────
    for elapsed in range(sc.timer_total):
        if not sc.active:
            break

        # Gradually decrease depth and increase altitude each tick
        app_state.header.depth.value    = round(depth_start    - depth_step    * elapsed, 1)
        app_state.header.altitude.value = round(altitude_start + altitude_step * elapsed, 1)

        sc.timer_remaining = sc.timer_total - elapsed
        sc.blink = not sc.blink

        if sc.current_stage == 1:
            if sw.port_side_sdw_1:
                sc.current_stage = 2
        elif sc.current_stage == 2:
            if sw.starboard_side_sdw_1:
                sc.current_stage = 3
        elif sc.current_stage == 3:
            stage3_timer -= 1
            if stage3_timer <= 0:
                sc.feedback_msg = "ALARM: Drop weights are not being triggered!"
                sc.current_stage = 4
        elif sc.current_stage == 4:
            if (sw.em_drop_weight_p1_sc or sw.em_drop_weight_p2_pc):
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


 

 


# ─────────────────────────────────────────────────────────────────────────────
# ASCEND SOP
# ─────────────────────────────────────────────────────────────────────────────

class AscendScenario:

    def __init__(self):

        self.phase = 0
        self.popup = ""

        self.completed = False
        self.failed = False

        self.step_start_time = None
        self.time_limit = 20

    # ============================================================
    # POPUP HELPERS
    # ============================================================

    def show_popup(self, msg):
        self.popup = msg

    def clear_popup(self):
        self.popup = ""

    def get_popup(self):
        return self.popup

    # ============================================================
    # MAIN UPDATE
    # ============================================================

    def update(self, depth, sw):

        # --------------------------------------------------------
        # STOP IF DONE
        # --------------------------------------------------------

        if self.completed or self.failed:
            return

     

        # ============================================================
        # WRONG ORDER PROTECTION
        # ============================================================

        if self.phase == 0:

            # Ballast should not be activated early

            if sw.freeboard_p:

                self.failed = True

                self.show_popup(
                    "ASCEND PHASE\n\n"
                    "✗ WRONG SOP ORDER"
                )

                return

        # ============================================================
        # STEP 1 — RELEASE 300kg WEIGHTS
        # ============================================================

        if self.phase == 0:

            if self.step_start_time is None:
                self.step_start_time = time.time()

            self.show_popup(
                "ASCEND PHASE\n\n"
                "Release 300kg Weights"
            )

            if (
                sw.port_side_sdw_3 and
                sw.starboard_side_sdw_3
            ):

                self.phase = 1

                self.step_start_time = None

                self.show_popup(
                    "ASCEND PHASE\n\n"
                    "✓ 300kg WEIGHTS RELEASED"
                )

        # ============================================================
        # STEP 2 — EMPTY MAIN BALLAST
        # ============================================================

        elif self.phase == 1 and depth <= 20:

            if self.step_start_time is None:
                self.step_start_time = time.time()

            self.show_popup(
                "ASCEND PHASE\n\n"
                "EMPTY MAIN BALLAST TANKs"
            )

            if sw.freeboard_p:

                self.phase = 2

                self.step_start_time = None

                self.show_popup(
                    "ASCEND PHASE\n\n"
                    "✓ MAIN BALLAST CLEARED"
                )

        # ============================================================
        # STEP 3 — TURN OFF SONAR & UW LIGHTS
        # ============================================================

        elif self.phase == 2 and depth <= 20:

            if self.step_start_time is None:
                self.step_start_time = time.time()

            self.show_popup(
                "ASCEND PHASE\n\n"
                "TURN OFF SONAR & EXTERNAL LIGHTS"
            )

            if (
                not sw.sonar and
                not sw.uw_led_p and
                not sw.uw_led_s
            ):

                self.phase = 3

                self.completed = True

                self.step_start_time = time.time()

                self.show_popup(
                    "ASCEND PHASE\n\n"
                    "✓ ASCEND SOP COMPLETED"
                )

        # ============================================================
        # TIMEOUT
        # ============================================================

        if (
            self.step_start_time is not None and
            not self.completed and
            (time.time() - self.step_start_time) > self.time_limit
        ):

            self.failed = True

            self.show_popup(
                "ASCEND PHASE\n\n"
                "✗ SOP FAILED\n"
                "TIME LIMIT EXCEEDED"
            )

        # ============================================================
        # AUTO CLEAR SUCCESS POPUP
        # ============================================================

        if (
            self.completed and
            self.step_start_time is not None and
            (time.time() - self.step_start_time) > 5
        ):

            self.clear_popup()