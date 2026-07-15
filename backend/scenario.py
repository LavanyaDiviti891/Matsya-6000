import asyncio
import random
import traceback
from dataclasses import dataclass
from typing import Optional

# ─────────────────────────────────────────────────────────────────────────────
# Scenario State
# ─────────────────────────────────────────────────────────────────────────────
@dataclass
class ScenarioState:
    active: bool = False
    mission_name: str = ""
    timer_total: int = 900
    timer_remaining: int = 900
    target_depth: float = 250.0
    depth_rate: float = 3.0
    success: Optional[bool] = None
    result_message: str = ""
    blink: bool = False
    current_stage: int = 1
    feedback_msg: str = ""

scenario_state = ScenarioState()
scenario_locked_paths: set[str] = set()

def reset_scenario(sc: ScenarioState) -> None:
    sc.active = False
    sc.success = None
    sc.mission_name = ""
    sc.result_message = ""
    sc.feedback_msg = ""
    sc.blink = False
    sc.current_stage = 1
    sc.timer_remaining = sc.timer_total
    scenario_locked_paths.clear()

# ─────────────────────────────────────────────────────────────────────────────
# Main Scenario Process
# ─────────────────────────────────────────────────────────────────────────────
async def run_poweringup_scenario(app_state, broadcast_fn):
    try:
        sc   = scenario_state
        sw_p = app_state.switches.p
        sw_s = app_state.switches.s
        pwr  = app_state.power

        # Config
        READING_PAUSE_SECS = 6   
        TOTAL_STAGES       = 62  # Matches all 62 steps of the SOP perfectly

        # ── Telemetry Injection Logic ──
        def inject_reading(name: str):
            writes = {}   
            if name == "eb_p":
                writes = {
                    "power.aux_p.voltage.value": round(random.uniform(25.5, 27.0), 2),
                    "power.aux_p.soc.value": round(random.uniform(92.0, 98.0), 1),
                    "switches.p.eb_b_status": round(random.uniform(25.5, 27.0), 2),
                }
            elif name == "eb_p_ir":
                writes = {
                    "switches.p.ib_insulation": round(random.uniform(1.8, 2.5), 2),
                }
            elif name == "ub_p":
                writes = {
                    "power.ub_port.voltage.value": round(random.uniform(24.0, 24.5), 2),
                    "power.ub_port.ir.value": round(random.uniform(1.6, 2.2), 2),
                    "switches.p.ub_voltage": round(random.uniform(24.0, 24.5), 2),
                }
            elif name == "eb_s":
                writes = {
                    "power.aux_s.voltage.value": round(random.uniform(25.5, 27.0), 2),
                    "power.aux_s.soc.value": round(random.uniform(92.0, 98.0), 1),
                    "switches.s.eb_s_status": round(random.uniform(25.5, 27.0), 2),
                }
            elif name == "eb_s_ir":
                writes = {
                    "switches.s.eb_s_insulation": round(random.uniform(1.8, 2.5), 2),
                }
            elif name == "ub_s":
                writes = {
                    "power.ub_stbd.voltage.value": round(random.uniform(24.0, 24.5), 2),
                    "power.ub_stbd.ir.value": round(random.uniform(1.6, 2.2), 2),
                    "switches.s.ub_voltage": round(random.uniform(24.0, 24.5), 2),
                }
            elif name == "hsss":
                writes = {
                    "hsss.p.oxygen.value": round(random.uniform(20.8, 21.2), 1),
                    "hsss.p.co2.value": round(random.uniform(380.0, 440.0), 1),
                    "hsss.s.oxygen.value": round(random.uniform(20.8, 21.2), 1),
                    "hsss.s.co2.value": round(random.uniform(380.0, 440.0), 1),
                }
            elif name == "mb_p":
                writes = {
                    "power.mb_p.voltage.value": round(random.uniform(163.0, 165.0), 2),
                    "power.mb_p.soc.value": round(random.uniform(94.0, 99.0), 1),
                    "power.mb_p.temp.value": round(random.uniform(23.0, 26.5), 1),
                    "header.mb_p_soc.value": round(random.uniform(94.0, 99.0), 1),
                }
            elif name == "pde_p_ir":
                writes = {
                    "power.pde_p.ir.value": round(random.uniform(1.8, 3.5), 2),
                    "power.pde_p.ir_148.value": round(random.uniform(1.8, 3.5), 2),
                }
            elif name == "pde_p":
                writes = {
                    "power.pde_p.voltage.value": round(random.uniform(147.5, 148.8), 2),
                    "power.pde_p.current.value": round(random.uniform(1.2, 2.8), 2),
                    "power.pde_p.ir_24.value": round(random.uniform(24.0, 24.2), 2),
                }
            elif name == "ide_p":
                writes = {
                    "power.ide_p.voltage.value": round(random.uniform(24.0, 24.4), 2),
                    "power.ide_p.current.value": round(random.uniform(0.8, 1.9), 2),
                    "power.ide_p.ir.value": round(random.uniform(1.6, 2.8), 2),
                }
            elif name == "mb_s":
                writes = {
                    "power.mb_s.voltage.value": round(random.uniform(163.0, 165.0), 2),
                    "power.mb_s.soc.value": round(random.uniform(94.0, 99.0), 1),
                    "power.mb_s.temp.value": round(random.uniform(23.0, 26.5), 1),
                    "header.mb_s_soc.value": round(random.uniform(94.0, 99.0), 1),
                }
            elif name == "pde_s_ir":
                writes = {
                    "power.pde_s.ir.value": round(random.uniform(1.8, 3.5), 2),
                    "power.pde_s.ir_148.value": round(random.uniform(1.8, 3.5), 2),
                }
            elif name == "pde_s":
                writes = {
                    "power.pde_s.voltage.value": round(random.uniform(147.5, 148.8), 2),
                    "power.pde_s.current.value": round(random.uniform(1.2, 2.8), 2),
                    "power.pde_s.ir_24.value": round(random.uniform(24.0, 24.2), 2),
                }
            elif name == "ide_s":
                writes = {
                    "power.ide_s.voltage.value": round(random.uniform(24.0, 24.4), 2),
                    "power.ide_s.current.value": round(random.uniform(0.8, 1.9), 2),
                    "power.ide_s.ir.value": round(random.uniform(1.6, 2.8), 2),
                }

            for path, val in writes.items():
                try:
                    parts = path.split('.')
                    target = app_state
                    for part in parts[:-1]:
                        target = getattr(target, part)
                    setattr(target, parts[-1], val)
                    scenario_locked_paths.add(path)
                except Exception as e:
                    print(f"[SCENARIO ERROR] Path failure on {path}: {e}")

        async def confirm_and_advance(msg: str, inject_key: str = None, pause_time: int = READING_PAUSE_SECS):
            if inject_key:
                inject_reading(inject_key)
            sc.feedback_msg = msg
            await broadcast_fn() 
            await asyncio.sleep(pause_time)
            sc.current_stage += 1
            await broadcast_fn()

        # ── Initialize State ──────────────────────────────────────────────────
        sc.active          = True
        sc.success         = None
        sc.mission_name    = "POWERING MATSYA (FULL 62-STEP SOP)"
        sc.timer_total     = 900
        sc.timer_remaining = 900
        sc.result_message  = ""
        sc.current_stage   = 1
        await broadcast_fn()

        # ── Main Control Loop ─────────────────────────────────────────────────
        while sc.active and sc.success is None and sc.timer_remaining > 0:
            try:
                sc.timer_remaining -= 1
                sc.blink = not sc.blink

                # ── PORT SIDE SYSTEM POWER UP SEQUENCE ──
                if sc.current_stage == 1:
                    sc.feedback_msg = "SOP Step 1: Visual Inspection - Confirm all switches are OFF before starting."
                    await confirm_and_advance("✅ Initial conditions verified.", None, 3)

                elif sc.current_stage == 2:
                    sc.feedback_msg = "SOP Step 2: Set Power selection EB_P to Emergency Battery (E_Batts)."
                    if getattr(sw_p, "e_batts", False) is True:
                        await confirm_and_advance("✅ EB_P Position Confirmed.", None, 2)

                elif sc.current_stage == 3:
                    sc.feedback_msg = "SOP Step 3: Turn ON MCB-1 for Emergency Battery Port."
                    await confirm_and_advance("✅ MCB-1 status active and hold condition clear.", None, 2)

                elif sc.current_stage == 4:
                    sc.feedback_msg = "SOP Step 4: Turn ON toggle switch EMG_LED_P for Emergency Light."
                    if getattr(sw_p, "emg_led_p", False):
                        await confirm_and_advance("✅ Emergency Light Port Active.", None, 2)

                elif sc.current_stage == 5:
                    sc.feedback_msg = "SOP Step 5: Validating EB_P Voltage >25V & SOC >90%..."
                    await confirm_and_advance("📈 Telemetry Loaded. Limits verified.", "eb_p", READING_PAUSE_SECS)

                elif sc.current_stage == 6:
                    sc.feedback_msg = "SOP Step 6: Validating EB_P Insulation IR >= 1.5 M Ohm..."
                    await confirm_and_advance("📈 Insulation status loaded via Bender isoRW425.", "eb_p_ir", READING_PAUSE_SECS)

                elif sc.current_stage == 7:
                    sc.feedback_msg = "SOP Step 7: Set Utility Bus change over switch UB_P to Auxiliary Battery (AB_P)."
                    if getattr(sw_p, "ab_p", False) is True:
                        await confirm_and_advance("✅ Utility Bus selector set to AB_P.", None, 2)

                elif sc.current_stage == 8:
                    sc.feedback_msg = "SOP Step 8: Turn ON toggle switch AB_P_BMS for Auxiliary battery BMS."
                    if getattr(sw_p, "ab_p_bms", False):
                        await confirm_and_advance("✅ AB_P BMS Active.", None, 2)

                elif sc.current_stage == 9:
                    sc.feedback_msg = "SOP Step 9: Turn ON toggle switch AB_P for Auxiliary battery port power."
                    if getattr(sw_p, "ab_p_power", False):
                        await confirm_and_advance("✅ AB_P Main Output Powered.", None, 2)

                elif sc.current_stage == 10:
                    sc.feedback_msg = "SOP Step 10: Turn ON UB_P MCB for Utility bus port power."
                    if getattr(sw_p, "ub_mcb", False):
                        await confirm_and_advance("✅ UB_P MCB Active.", None, 2)

                elif sc.current_stage == 11:
                    sc.feedback_msg = "SOP Step 11: Observe Utility Bus Port voltage display UB_P_VOLTAGE (~24VDC)."
                    await confirm_and_advance("📈 Port Utility voltage validated via MECO meter.", "ub_p", READING_PAUSE_SECS)

                elif sc.current_stage == 12:
                    sc.feedback_msg = "SOP Step 12: Check insulation status of UB_P bus (IR ≥ 1.5 M Ohm)."
                    await confirm_and_advance("✅ OIM Insulation values validated.", None, 3)

                elif sc.current_stage == 13:
                    sc.feedback_msg = "SOP Step 13: Turn ON Toggle switch INT_LED_P for Internal Lights."
                    if getattr(sw_p, "int_led_p", False):
                        await confirm_and_advance("✅ Internal Lights Port ON.", None, 2)

                elif sc.current_stage == 14:
                    sc.feedback_msg = "SOP Step 14: Change Emergency Bus change over switch EB_P from EB_P to UB_P."
                    if getattr(sw_p, "e_batts", True) is False:
                        await confirm_and_advance("✅ Emergency Bus changed over to UB_P successfully.", None, 2)

                elif sc.current_stage == 15:
                    sc.feedback_msg = "SOP Step 15: Verifying EMCS portside, HSSS-HMI-P and HMI-P status..."
                    await confirm_and_advance("⏰ Waiting for PLC startup routines...", None, 5)

                elif sc.current_stage == 16:
                    sc.feedback_msg = "SOP Step 16: Switch ON the Pilot Panel PC using the monitor power button."
                    await confirm_and_advance("🖥️ Pilot Panel PC boot process initiated.", None, 4)

                elif sc.current_stage == 17:
                    sc.feedback_msg = "SOP Step 17: Load Matsya6000 software on Pilot PC and read parameters."
                    await confirm_and_advance("✅ Data acquisition links to PS_P established.", None, 3)

                # ── STARBOARD SIDE SYSTEM POWER UP SEQUENCE ──
                elif sc.current_stage == 18:
                    sc.feedback_msg = "SOP Step 18: Set Power selection EB_S to Emergency Battery (E_Batts)."
                    if getattr(sw_s, "e_batt_s", False) is True:
                        await confirm_and_advance("✅ EB_S Position Confirmed.", None, 2)

                elif sc.current_stage == 19:
                    sc.feedback_msg = "SOP Step 19: Turn ON MCB-2 for Emergency Battery Starboard."
                    await confirm_and_advance("✅ MCB-2 status active.", None, 2)

                elif sc.current_stage == 20:
                    sc.feedback_msg = "SOP Step 20: Turn ON toggle switch EMG_LED_S for Emergency Light."
                    if getattr(sw_s, "emg_led_s", False):
                        await confirm_and_advance("✅ Emergency Light Starboard Active.", None, 2)

                elif sc.current_stage == 21:
                    sc.feedback_msg = "SOP Step 21: Validating EB_S Voltage >25V & SOC >90%..."
                    await confirm_and_advance("📈 Telemetry Loaded. Limits verified.", "eb_s", READING_PAUSE_SECS)

                elif sc.current_stage == 22:
                    sc.feedback_msg = "SOP Step 22: Validating EB_S Insulation IR >= 1.5 M Ohm..."
                    await confirm_and_advance("📈 Insulation status loaded via Bender isoRW425.", "eb_s_ir", READING_PAUSE_SECS)

                elif sc.current_stage == 23:
                    sc.feedback_msg = "SOP Step 23: Set Utility Bus change over switch UB_S to Auxiliary Battery (AB_S)."
                    if getattr(sw_s, "ab_s", False) is True:
                        await confirm_and_advance("✅ Utility Bus selector set to AB_S.", None, 2)

                elif sc.current_stage == 24:
                    sc.feedback_msg = "SOP Step 24: Turn ON toggle switch AB_S_BMS for Auxiliary battery BMS."
                    if getattr(sw_s, "ab_s_bms", False):
                        await confirm_and_advance("✅ AB_S BMS Active.", None, 2)

                elif sc.current_stage == 25:
                    sc.feedback_msg = "SOP Step 25: Turn ON toggle switch AB_S for Auxiliary battery starboard power."
                    if getattr(sw_s, "ab_s_power", False):
                        await confirm_and_advance("✅ AB_S Main Output Powered.", None, 2)

                elif sc.current_stage == 26:
                    sc.feedback_msg = "SOP Step 26: Turn ON UB_S MCB for Utility Bus Starboard."
                    if getattr(sw_s, "ub_mcb", False):
                        await confirm_and_advance("✅ UB_S MCB Active.", None, 2)

                elif sc.current_stage == 27:
                    sc.feedback_msg = "SOP Step 27: Observe Utility Bus starboard voltage display UB_S VOLTAGE (~24VDC)."
                    await confirm_and_advance("📈 Starboard Utility voltage validated via MECO meter.", "ub_s", READING_PAUSE_SECS)

                elif sc.current_stage == 28:
                    sc.feedback_msg = "SOP Step 28: Check insulation status of UB_S bus (IR ≥ 1.5 M Ohm)."
                    await confirm_and_advance("✅ OIM Insulation values validated.", None, 3)

                elif sc.current_stage == 29:
                    sc.feedback_msg = "SOP Step 29: Turn ON Toggle switch INT_LED_S for Internal Lights."
                    if getattr(sw_s, "int_led_s", False):
                        await confirm_and_advance("✅ Internal Lights Starboard ON.", None, 2)

                elif sc.current_stage == 30:
                    sc.feedback_msg = "SOP Step 30: Change Emergency Bus change over switch EB_S from EB_S to UB_S."
                    if getattr(sw_s, "e_batt_s", True) is False:
                        await confirm_and_advance("✅ Emergency Bus changed over to UB_S successfully.", None, 2)

                elif sc.current_stage == 31:
                    sc.feedback_msg = "SOP Step 31: Verifying EMCS starboard, HSSS-HMI-S and HMI-S display ON."
                    await confirm_and_advance("⏰ Waiting for Starboard PLC routines to settle...", None, 4)

                elif sc.current_stage == 32:
                    sc.feedback_msg = "SOP Step 32: Switch ON the Co-Pilot Panel PC and Navigation PCs."
                    await confirm_and_advance("🖥️ Co-Pilot and Navigation systems boot sequences initialized.", None, 4)

                elif sc.current_stage == 33:
                    sc.feedback_msg = "SOP Step 33: Load Matsya6000 software on Co-Pilot PC desktop."
                    await confirm_and_advance("✅ Communication link check to PS_S completed.", None, 3)

                elif sc.current_stage == 34:
                    sc.feedback_msg = "SOP Step 34: Confirm Life Support Scrubber is operational and gas flow stabilizes."
                    await confirm_and_advance("💨 Gas Scrubber airflow loop functional.", None, 4)

                elif sc.current_stage == 35:
                    sc.feedback_msg = "SOP Step 35: Record Oxygen, CO2, pressure, and humidity from HSSS display."
                    await confirm_and_advance("📈 Environment parameters pushed to GUI.", "hsss", READING_PAUSE_SECS)

                elif sc.current_stage == 36:
                    sc.feedback_msg = "SOP Step 36: Check and adjust the flow meter and Regulator for oxygen."
                    await confirm_and_advance("✅ Flow parameters confirmed in limits.", None, 3)

                # ── PORT SIDE HIGH POWER (PDE / IDE) SEQUENCE ──
                elif sc.current_stage == 37:
                    sc.feedback_msg = "SOP Step 37: Turn ON toggle switch MB_P_BMS for Main Battery Port BMS."
                    if getattr(sw_p, "mb_p_bms", False):
                        await confirm_and_advance("✅ MB_P BMS initialized.", None, 2)

                elif sc.current_stage == 38:
                    sc.feedback_msg = "SOP Step 38: Record voltage, temperature and SOC of MB_P in GUI."
                    await confirm_and_advance("📈 Main battery packs telemetry online.", "mb_p", READING_PAUSE_SECS)

                elif sc.current_stage == 39:
                    sc.feedback_msg = "SOP Step 39: Turn ON toggle switch PDE_P_OIM for Port PDE OIM Power."
                    if getattr(sw_p, "pde_p_oim", False):
                        await confirm_and_advance("📈 Checking 148V insulation IR parameters.", "pde_p_ir", READING_PAUSE_SECS)

                elif sc.current_stage == 40:
                    sc.feedback_msg = "SOP Step 40: Turn ON toggle switch PDE_P_OLR for Overload Relay Port."
                    if getattr(sw_p, "pde_p_olr", False):
                        await confirm_and_advance("✅ PDE-P-OLR Status confirmed.", None, 2)

                elif sc.current_stage == 41:
                    sc.feedback_msg = "SOP Step 41: Sequentially power UP Main Battery packs MB_P_1 through MB_P_5."
                    if (getattr(sw_p, "mb_1", False) and getattr(sw_p, "mb_2", False) and 
                        getattr(sw_p, "mb_3", False) and getattr(sw_p, "mb_4", False) and getattr(sw_p, "mb_5", False)):
                        await confirm_and_advance("✅ All 5 Port Battery packs online.", None, 3)

                elif sc.current_stage == 42:
                    sc.feedback_msg = "SOP Step 42: Turn ON (Pull UP) the contactor switch MB_P-PDE_P."
                    if getattr(sw_p, "pde_p_148", False):
                        await confirm_and_advance("📈 148V High Voltage Bus energized to Port Enclosures.", "pde_p", READING_PAUSE_SECS)

                elif sc.current_stage == 43:
                    sc.feedback_msg = "SOP Step 43: Turn ON toggle switch 24V_Main_P for internal DC-DC Converter."
                    if getattr(sw_p, "pde_p_24v_main", False) or getattr(sw_p, "pde_p_24v", False):
                        await confirm_and_advance("✅ 24V Main Port Regulator functional.", None, 2)

                elif sc.current_stage == 44:
                    sc.feedback_msg = "SOP Step 44: Verify communication status between PDE_P and Propulsion System."
                    await confirm_and_advance("✅ Telemetry data loops operational.", None, 3)

                elif sc.current_stage == 45:
                    sc.feedback_msg = "SOP Step 45: Turn ON toggle switch IDE1_P for powering IDE_P."
                    if getattr(sw_p, "ide_p_1", False):
                        await confirm_and_advance("📈 IDE_P internal bus diagnostic telemetry active.", "ide_p", READING_PAUSE_SECS)

                elif sc.current_stage == 46:
                    sc.feedback_msg = "SOP Step 46: Verify telemetry and water ingress status loops for IDE_P."
                    await confirm_and_advance("✅ IDE_P data structures stable.", None, 3)

                # ── STARBOARD SIDE HIGH POWER (PDE / IDE) SEQUENCE ──
                elif sc.current_stage == 47:
                    sc.feedback_msg = "SOP Step 47: Turn ON toggle switch MB_S_BMS for Main Battery Starboard BMS."
                    if getattr(sw_s, "mb_s_bms", False):
                        await confirm_and_advance("✅ MB_S BMS initialized.", None, 2)

                elif sc.current_stage == 48:
                    sc.feedback_msg = "SOP Step 48: Record voltage, temperature and SOC of MB_S in GUI."
                    await confirm_and_advance("📈 Starboard Main battery pack telemetry online.", "mb_s", READING_PAUSE_SECS)

                elif sc.current_stage == 49:
                    sc.feedback_msg = "SOP Step 49: Turn ON toggle switch PDE_S_OIM for Starboard PDE OIM Power."
                    if getattr(sw_s, "pde_s_oim", False):
                        await confirm_and_advance("📈 Checking 148V insulation IR parameters.", "pde_s_ir", READING_PAUSE_SECS)

                elif sc.current_stage == 50:
                    sc.feedback_msg = "SOP Step 50: Turn ON toggle switch PDE_S_OLR for Overload Relay Starboard."
                    if getattr(sw_s, "pde_s_olr", False):
                        await confirm_and_advance("✅ PDE-S-OLR Status confirmed.", None, 2)

                elif sc.current_stage == 51:
                    sc.feedback_msg = "SOP Step 51: Sequentially power UP Main Battery packs MB_S_1 through MB_S_5."
                    if (getattr(sw_s, "mb_s_1", False) and getattr(sw_s, "mb_s_2", False) and 
                        getattr(sw_s, "mb_s_3", False) and getattr(sw_s, "mb_s_4", False) and getattr(sw_s, "mb_s_5", False)):
                        await confirm_and_advance("✅ All 5 Starboard Battery packs online.", None, 3)

                elif sc.current_stage == 52:
                    sc.feedback_msg = "SOP Step 52: Turn ON (Pull UP) the contactor switch MB_S-PDE_S."
                    if getattr(sw_s, "mb_s_pde_s", False):
                        await confirm_and_advance("📈 148V High Voltage Bus energized to Starboard Enclosures.", "pde_s", READING_PAUSE_SECS)

                elif sc.current_stage == 53:
                    sc.feedback_msg = "SOP Step 53: Turn ON toggle switch 24V_Main_S for internal DC-DC Converter."
                    if getattr(sw_s, "main_24_s", False):
                        await confirm_and_advance("✅ 24V Main Starboard Regulator functional.", None, 2)

                elif sc.current_stage == 54:
                    sc.feedback_msg = "SOP Step 54: Verify communication status between PDE_S and Propulsion System."
                    await confirm_and_advance("✅ Telemetry data loops operational.", None, 3)

                elif sc.current_stage == 55:
                    sc.feedback_msg = "SOP Step 55: Turn ON toggle switch IDE1_S for powering IDE_S."
                    if getattr(sw_s, "ide_s_1", False):
                        await confirm_and_advance("📈 IDE_S internal bus diagnostic telemetry active.", "ide_s", READING_PAUSE_SECS)

                elif sc.current_stage == 56:
                    sc.feedback_msg = "SOP Step 56: Verify telemetry and water ingress status loops for IDE_S."
                    await confirm_and_advance("✅ IDE_S data structures stable.", None, 3)

                # ── CRITICAL FINAL CHANGEOVERS ──
                elif sc.current_stage == 57:
                    sc.feedback_msg = "SOP Step 57: Comprehensive communication validation across all units (PS_P, PS_S, IDEs, PDEs)."
                    await confirm_and_advance("✅ All active links report OK status.", None, 3)

                elif sc.current_stage == 58:
                    sc.feedback_msg = "SOP Step 58: Cross checking SOC of Auxiliary Batteries before changeover."
                    await confirm_and_advance("✅ Threshold check pass.", None, 3)

                elif sc.current_stage == 59:
                    sc.feedback_msg = "SOP Step 59: Change Position of Emergency Bus change over selectors EB_P & EB_S back to EB (E_Batts)."
                    if getattr(sw_p, "e_batts", False) is True and getattr(sw_s, "e_batt_s", False) is True:
                        await confirm_and_advance("✅ Emergency Bus switchover confirmed.", None, 3)

                elif sc.current_stage == 60:
                    sc.feedback_msg = "SOP Step 60: Change position of Utility Bus selectors UB_P & UB_S from AB to Main Battery (MB)."
                    if getattr(sw_p, "ab_p", True) is False and getattr(sw_s, "ab_s", True) is False:
                        await confirm_and_advance("✅ Uninterrupted power shift to Main Internal Battery Banks confirmed.", None, 3)

                elif sc.current_stage == 61:
                    sc.feedback_msg = "SOP Step 61: Verify Main Battery banks hold SOC > 25% for deployment."
                    await confirm_and_advance("✅ Main power reserve parameters look healthy.", None, 3)

                elif sc.current_stage == 62:
                    sc.feedback_msg = "SOP Step 62: Confirm Power and Control system is ready for Operational checks."
                    sc.success = True
                    sc.active = False
                    sc.result_message = "✅ Vehicle powered successfully! All 62 Steps Complete."
                    await broadcast_fn()
                    await asyncio.sleep(8)
                    reset_scenario(sc)
                    await broadcast_fn()
                    return

                try:
                    await broadcast_fn()
                except Exception as b_e:
                    print(f"[SCENARIO] Broadcast failed in main loop: {b_e}")

                await asyncio.sleep(1.0)

            except Exception as stage_e:
                print(f"[SCENARIO] Error during stage {sc.current_stage} logic: {stage_e}")
                sc.feedback_msg = f"⚠️ Internal error at Stage {sc.current_stage}: {stage_e}"
                try:
                    await broadcast_fn()
                except Exception:
                    pass
                await asyncio.sleep(1.0) 

        # ── Timer expired without completion ──────────────────────────────────────
        if sc.active and sc.success is None:
            sc.success        = False
            sc.active         = False
            sc.result_message = f"⏰ Time expired at Stage {sc.current_stage}/{TOTAL_STAGES}. Mission failed."

        await broadcast_fn()
        await asyncio.sleep(8)
        reset_scenario(sc)
        await broadcast_fn()

    except Exception as e:
        print("\n" + "="*50)
        print("🚨 SCENARIO TASK CRASHED! 🚨")
        traceback.print_exc()
        print("="*50 + "\n")
        scenario_state.active = False
        scenario_state.result_message = f"CRASH: {str(e)}"
        try:
            await broadcast_fn()
        except:
            pass