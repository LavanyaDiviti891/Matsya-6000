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
    timer_total: int = 400
    timer_remaining: int = 400
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
# Scenario: POWERING MATSYA (SOP Implementation)
# ─────────────────────────────────────────────────────────────────────────────
async def run_powering_matsya_scenario(app_state, broadcast_fn):
    sc = scenario_state
    sw = app_state.switches

    # ── Initialize ────────────────────────────────────────────────────────────
    sc.active          = True
    sc.success         = None
    sc.mission_name    = "POWERING MATSYA (SOP)"
    sc.timer_total     = 450
    sc.timer_remaining = 450
    sc.result_message  = ""
    sc.feedback_msg    = "POWER THE VEHICLE"
    sc.current_stage   = 1

    # Reset all relevant switch states to OFF / Initial conditions
    sw.p.power_selection_eb = "UB_"
    sw.s.power_selection_eb = "UB_"
    sw.p.power_selection_ub = "MB"
    sw.s.power_selection_ub = "MB"
    sw.p.ub_mcb = False
    sw.s.ub_mcb = False
    sw.p.led_emergency_port = False
    sw.s.led_emergency_port = False
    sw.p.ab_p_bms = False
    sw.s.ab_s_bms = False
    sw.p.ab_p_power_selection = False
    sw.s.ab_s_power_selection = False
    
    
    sw.p.mb_p_bms = False
    sw.p.mb_p_1 = False
    sw.p.mb_p_2 = False
    sw.p.mb_p_3 = False
    sw.p.mb_p_4 = False
    sw.p.mb_p_5 = False
    sw.p.mb_p_pde_p = False

    sw.s.mb_s_bms = False
    sw.s.mb_s_1 = False
    sw.s.mb_s_2 = False
    sw.s.mb_s_3 = False
    sw.s.mb_s_4 = False
    sw.s.mb_s_5 = False
    sw.s.mb_s_pde_s = False

    # Reset display values so panels start at zero
    sw.p.ib_insulation = 0.0
    sw.p.eb_b_status = 0.0
    sw.p.ub_voltage = 0.0
    sw.s.ib_insulation = 0.0
    sw.s.eb_b_status = 0.0
    sw.s.ub_voltage = 0.0

    await broadcast_fn()

    # ── Timer + stage-check loop ──────────────────────────────────────────────
    while sc.active and sc.success is None and sc.timer_remaining > 0:
        await asyncio.sleep(1.0)
        sc.timer_remaining -= 1
        sc.blink = not sc.blink

        if sc.current_stage == 1:
            sc.feedback_msg = "SOP Step 2: Set Power selection EB_P to Emergency Battery (E_Batts) in Switches_P3."
            if sw.p.power_selection_eb == "E_Batts":
                sc.current_stage = 2

        elif sc.current_stage == 2:
            sc.feedback_msg = "SOP Step 3-4: Turn ON toggle switch EMG_LED_P (LED_Emegency_Port) in Switches_P1. Check BATTMAN PRO: Voltage > 25V & SOC > 90%."
            if sw.p.led_emergency_port:
                # BATTMAN PRO shows healthy EB_P voltage once LED is ON
                sw.p.eb_b_status = 26.5
                sc.current_stage = 3

        elif sc.current_stage == 3:
            sc.feedback_msg = "SOP Step 6-7: Confirm EB_P IR >= 1.5 M Ohm. Set UB_P selector to AB in Switches_P3 (Power selection UB rotary)."
            if sw.p.power_selection_ub == "AB":
                # EB_P insulation resistance confirmed >= 1.5 MOhm
                sw.p.ib_insulation = 2.1
                sc.current_stage = 4

        elif sc.current_stage == 4:
            sc.feedback_msg = "SOP Step 8: Turn ON AB_P_BMS toggle in Switches_P1."
            if sw.p.ab_p_bms:
                sc.current_stage = 5

        elif sc.current_stage == 5:
            sc.feedback_msg = "SOP Step 9: Turn ON toggle switch AB_P (AB_P Power selection) in Switches_P1."
            if sw.p.ab_p_power_selection:
                sc.current_stage = 6

        elif sc.current_stage == 6:
            sc.feedback_msg = "SOP Step 10: Turn ON UB MCB in Switches_P3. Confirm Utility Bus Port voltage ~24VDC & UB_P IR >= 1.5 M Ohm."
            if sw.p.ub_mcb:
                # Utility Bus Port energised: voltage ~24VDC, insulation confirmed
                sw.p.ub_voltage = 24.1
                sw.p.ib_insulation = 2.1
                sc.current_stage = 7

        elif sc.current_stage == 7:
            sc.feedback_msg = "SOP Step 13-14: Set EB_P selector to UB_ in Switches_P3. Wait for PLC start-up and check HMI for alarms."
            if sw.p.power_selection_eb == "UB_":
                sc.current_stage = 8

        elif sc.current_stage == 8:
            sc.feedback_msg = "SOP Step 15-17: Switch ON the Pilot Panel PC using the button on the Monitor. Wait for display ON, then load Matsya6000 software. (Auto-advancing in 10s...)"
            await broadcast_fn()
            await asyncio.sleep(10.0)
            sc.current_stage = 9

        elif sc.current_stage == 9:
            sc.feedback_msg = "SOP Step 18: Set Power selection EB_S to Emergency Battery (E_Batts) in Switches_S3."
            if sw.s.power_selection_eb == "E_Batts":
                sc.current_stage = 10

        elif sc.current_stage == 10:
            sc.feedback_msg = "SOP Step 19-20: Turn ON toggle switch EMG_LED_S (LED_Emegency_Port) in Switches_S1. Check BATTMAN PRO: Voltage > 25V & SOC > 90%."
            if sw.s.led_emergency_port:
                # BATTMAN PRO shows healthy EB_S voltage once LED is ON
                sw.s.eb_b_status = 26.5
                sc.current_stage = 11

        elif sc.current_stage == 11:
            sc.feedback_msg = "SOP Step 22-23: Confirm EB_S IR >= 1.5 M Ohm. Set UB_S selector to AB in Switches_S3 (Power selection UB rotary)."
            if sw.s.power_selection_ub == "AB":
                # EB_S insulation resistance confirmed >= 1.5 MOhm
                sw.s.ib_insulation = 2.1
                sc.current_stage = 12

        elif sc.current_stage == 12:
            sc.feedback_msg = "SOP Step 24: Turn ON AB_S_BMS toggle in Switches_S1."
            if sw.s.ab_s_bms:
                sc.current_stage = 13

        elif sc.current_stage == 13:
            sc.feedback_msg = "SOP Step 25: Turn ON toggle switch AB_S (AB_S Power selection) in Switches_S1."
            if sw.s.ab_s_power_selection:
                sc.current_stage = 14

        elif sc.current_stage == 14:
            sc.feedback_msg = "SOP Step 26: Turn ON UB MCB in Switches_S3. Confirm Utility Bus Starboard voltage ~24VDC & UB_S IR >= 1.5 M Ohm."
            if sw.s.ub_mcb:
                # Utility Bus Starboard energised: voltage ~24VDC, insulation confirmed
                sw.s.ub_voltage = 24.1
                sw.s.ib_insulation = 2.1
                sc.current_stage = 15

        elif sc.current_stage == 15:
            sc.feedback_msg = "SOP Step 29-30: Set EB_S selector to UB_ in Switches_S3. Wait for PLC start-up and check HMI for alarms."
            if sw.s.power_selection_eb == "UB_":
                sc.current_stage = 16
                sc.feedback_msg = "SOP Step 31-36: Verifying Co-Pilot PC & Scrubber gas flow. Settling down..."
                await broadcast_fn()
                await asyncio.sleep(5.0)
                sc.current_stage = 17

        elif sc.current_stage == 17:
            sc.feedback_msg = "SOP Step 37: Turn ON MB_P_BMS for Main Battery Port in Switches_P1. Check MB_P SOC > 90% & Temp < 30C."
            if sw.p.mb_p_bms:
                sc.current_stage = 18

        elif sc.current_stage == 18:
            sc.feedback_msg = "SOP Step 41: Turn ON main battery pack switches MB_P_1 through MB_P_5 sequentially in Switches_P1."
            if sw.p.mb_p_1 and sw.p.mb_p_2 and sw.p.mb_p_3 and sw.p.mb_p_4 and sw.p.mb_p_5:
                sc.current_stage = 19

        elif sc.current_stage == 19:
            sc.feedback_msg = "SOP Step 42: Turn ON (Pull UP) contactor MB_P-PDE_P in Switches_P1. Confirm PDE_P_148 status is ON."
            if sw.p.mb_p_pde_p:
                sc.current_stage = 20

        elif sc.current_stage == 20:
            sc.feedback_msg = "SOP Step 47: Turn ON MB_S_BMS for Main Battery Starboard in Switches_S1. Check MB_S SOC > 90% & Temp < 30C."
            if sw.s.mb_s_bms:
                sc.current_stage = 21

        elif sc.current_stage == 21:
            sc.feedback_msg = "SOP Step 51: Turn ON main battery pack switches MB_S_1 through MB_S_5 sequentially in Switches_S1."
            if sw.s.mb_s_1 and sw.s.mb_s_2 and sw.s.mb_s_3 and sw.s.mb_s_4 and sw.s.mb_s_5:
                sc.current_stage = 22

        elif sc.current_stage == 22:
            sc.feedback_msg = "SOP Step 52: Turn ON (Pull UP) contactor MB_S-PDE_S in Switches_S1."
            if sw.s.mb_s_pde_s:
                sc.current_stage = 23

        elif sc.current_stage == 23:
            sc.feedback_msg = "SOP Step 59: Change Power selection EB_P & EB_S from UB to EB (set selectors to E_Batts) in Switches_P3 & Switches_S3."
            if sw.p.power_selection_eb == "E_Batts" and sw.s.power_selection_eb == "E_Batts":
                sc.current_stage = 24

        elif sc.current_stage == 24:
            sc.feedback_msg = "SOP Step 60: Change Utility Bus UB_P & UB_S from AB to MB (set selectors to MB) in Switches_P3 & Switches_S3."
            if sw.p.power_selection_ub == "MB" and sw.s.power_selection_ub == "MB":
                sc.success        = True
                sc.active         = False
                sc.result_message = "Vehicle powered successfully!"
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
        sc.result_message = "Time expired. Power up sequence failed."

    await broadcast_fn()
    await asyncio.sleep(6)
    reset_scenario(sc)
    await broadcast_fn()
