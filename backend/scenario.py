import asyncio
import random
import traceback

# ─────────────────────────────────────────────────────────────────────────────
# Scenario State
# ─────────────────────────────────────────────────────────────────────────────
# NOTE: The scenario's live state now lives on app_state.scenario itself
# (a ScenarioTelemetry pydantic model defined in models.py), instead of a
# separate module-level dataclass. This means it is automatically included
# in app_state.model_dump() and broadcast to the frontend over the existing
# /ws websocket with zero extra wiring in main.py.
scenario_locked_paths: set[str] = set()

def reset_scenario(sc) -> None:
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
        sc         = app_state.scenario
        sw_p       = app_state.switches.p
        sw_s       = app_state.switches.s
        sw3        = app_state.switches.sw3
        img        = app_state.imaging
        sen        = app_state.sensors.toggles
        mcc        = app_state.mcc.indicators
        mcc_status = app_state.mcc.status     
        pwr        = app_state.power
        ballast    = app_state.ballast        
        prop       = app_state.propulsion     
        pd         = app_state.propulsion_detail
        sidebar    = app_state.sidebar

        # Config
        READING_PAUSE_SECS = 4   
        TOTAL_STAGES       = 113

        # ── Helper Function for 3-Way Switches ──
        def is_pc_on(val):
            # Checks if the switch value matches common 'PC ON' states
            return val in [1, True, "PC_ON", "PC ON", "pc_on", "1"]

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
                writes = {"switches.p.ib_insulation": round(random.uniform(1.8, 2.5), 2)}
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
                writes = {"switches.s.eb_s_insulation": round(random.uniform(1.8, 2.5), 2)}
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
            elif name == "depth_sensor":
                writes = {"header.depth.value": round(random.uniform(0.0, 1.5), 2)}
            elif name == "led_p2":
                writes = {"imaging.led_p2.dim": 75.0}
            elif name == "led_p3":
                writes = {"imaging.led_p3.dim": 80.0}
            elif name == "led_p1_toggle":
                writes = {"imaging.led_p1.dim": 100.0}
            elif name == "led_s2":
                writes = {"imaging.led_s2.dim": 75.0}
            elif name == "led_s3":
                writes = {"imaging.led_s3.dim": 80.0}
            elif name == "led_s1_toggle":
                writes = {"imaging.led_s1.dim": 100.0}
            elif name == "ctd_p":
                writes = {
                    "sensors.scientific.conductivity.port": round(random.uniform(4.2, 4.8), 2),
                    "sensors.scientific.ctd_temp.port": round(random.uniform(22.1, 24.5), 2),
                    "sensors.scientific.pressure.port": round(random.uniform(1.0, 1.2), 2),
                    "sensors.scientific.salinity.port": round(random.uniform(34.1, 35.3), 2),
                    "sensors.scientific.turbidity.port": round(random.uniform(0.1, 0.3), 2),
                }
            elif name == "do_s":
                writes = {
                    "sensors.scientific.dissolved_oxygen.stbd": round(random.uniform(5.1, 5.8), 2),
                }
            elif name == "surface_ins":
                writes = {
                    "sensors.surface_ins.s_roll": round(random.uniform(-0.5, 0.5), 2),
                    "sensors.surface_ins.s_pitch": round(random.uniform(-0.4, 0.4), 2),
                    "sensors.surface_ins.s_heading": round(random.uniform(120.0, 125.0), 2),
                }
            elif name == "subsea_gps":
                writes = {
                    "sensors.subsea_gps.gps_latitude": round(random.uniform(12.9, 13.1), 5),
                    "sensors.subsea_gps.gps_longitude": round(random.uniform(80.2, 80.4), 5),
                }
            elif name == "redt_depth":
                writes = {"sensors.redt_depth.s_depth": round(random.uniform(0.0, 1.5), 2)}
            elif name == "ins_p":
                writes = {"imu.heading_p.value": round(random.uniform(120.0, 125.0), 2)}
            elif name == "dvl_p":
                writes = {
                    "bottom.east_speed.value": 0.0,
                    "bottom.north_speed.value": 0.0,
                    "bottom.vert_speed.value": 0.0,
                }
            elif name == "altimeter_s":
                writes = {"header.altitude.value": 0.0}
            elif name == "acoustic_modem":
                writes = {
                    "mcc.status.ship_latitude": round(random.uniform(12.9, 13.1), 5),
                    "mcc.status.ship_longitude": round(random.uniform(80.2, 80.4), 5),
                }
            elif name == "mbs_active":
                writes = {
                    "ballast.main_ballast.read_pressure_s": round(random.uniform(240.0, 250.0), 1),
                    "ballast.main_ballast.read_pressure_p": round(random.uniform(240.0, 250.0), 1),
                }
            elif name == "ready_to_dive":
                writes = {"header.depth.value": 1.0, "header.altitude.value": 5499.0}
            elif name == "initiate_dive":
                writes = {"header.depth.value": 5.0}
            elif name == "thrusters_spin":
                writes = {
                    "propulsion.t1_rpm": round(random.uniform(60, 70), 1),
                    "propulsion.t2_rpm": round(random.uniform(60, 70), 1),
                    "propulsion.t3_rpm": round(random.uniform(60, 70), 1),
                    "propulsion.t4_rpm": round(random.uniform(60, 70), 1),
                    "propulsion.t5_rpm": round(random.uniform(60, 70), 1),
                    "propulsion.t6_rpm": round(random.uniform(60, 70), 1),
                    "propulsion.t7_rpm": round(random.uniform(60, 70), 1),
                    "propulsion.t8_rpm": round(random.uniform(60, 70), 1),
                }
            elif name == "joystick_fwd":
                writes = {"bottom.north_speed.value": round(random.uniform(1.2, 1.8), 2)}
            elif name == "joystick_vert":
                writes = {"bottom.vert_speed.value": round(random.uniform(0.5, 1.0), 2)}
            elif name == "joystick_lat":
                writes = {"bottom.east_speed.value": round(random.uniform(0.8, 1.2), 2)}
            elif name == "depth_seabed":
                writes = {"header.depth.value": 5450.0}
            elif name == "sampling_seabed":
                writes = {"header.depth.value": 5500.0, "header.altitude.value": 0.5}
            elif name == "ascent_start":
                writes = {"header.depth.value": 5400.0}
            elif name == "surfaced":
                writes = {
                    "header.depth.value": 0.0, 
                    "ballast.main_ballast.read_pressure_s": round(random.uniform(200.0, 210.0), 1)
                }
            elif name == "freeboard":
                writes = {"header.depth.value": -1.5}

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
        sc.mission_name    = "FULL MATSYA SEQUENCE - MANUAL TRIGGERS (113 STEPS)"
        sc.timer_total     = 3600
        sc.timer_remaining = 3600
        sc.result_message  = ""
        sc.current_stage   = 1
        await broadcast_fn()

        # ── Main Control Loop ─────────────────────────────────────────────────
        while sc.active and sc.success is None and sc.timer_remaining > 0:
            try:
                sc.timer_remaining -= 1
                sc.blink = not sc.blink

                # ─────────────────────────────────────────────────────────────
                # POWER UP & OPS CHECKS (Steps 1 to 97)
                # ─────────────────────────────────────────────────────────────
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
                    if (getattr(sw_p, "mb_p_1", False) and getattr(sw_p, "mb_p_2", False) and 
                        getattr(sw_p, "mb_p_3", False) and getattr(sw_p, "mb_p_4", False) and getattr(sw_p, "mb_p_5", False)):
                        await confirm_and_advance("✅ All 5 Port Battery packs online.", None, 3)

                elif sc.current_stage == 42:
                    sc.feedback_msg = "SOP Step 42: Turn ON (Pull UP) the contactor switch MB_P-PDE_P."
                    if getattr(sw_p, "mb_p_pde_p", False):
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

                elif sc.current_stage == 57:
                    sc.feedback_msg = "SOP Step 57: Comprehensive communication validation across all units."
                    await confirm_and_advance("✅ All active links report OK status.", None, 3)

                elif sc.current_stage == 58:
                    sc.feedback_msg = "SOP Step 58: Cross checking SOC of Auxiliary Batteries before changeover."
                    await confirm_and_advance("✅ Threshold check pass.", None, 3)

                elif sc.current_stage == 59:
                    sc.feedback_msg = "SOP Step 59: Change Position of Emergency Bus change over selectors EB_P & EB_S back to EB."
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
                    await confirm_and_advance("✅ Main vehicle initialization complete. Advancing to Subsystem Checks.", None, 3)

                elif sc.current_stage == 63:
                    sc.feedback_msg = "SOP Step 63: Turn ON soft control button Depth_Primary in GUI MCC / Sensors page."
                    if getattr(sen, "depth_sensor_pri", False) or getattr(mcc, "depth_sensor_pri_d", False):
                        await confirm_and_advance("📈 Primary depth sensor online. Fiber optic Multiplexers powered.", "depth_sensor", READING_PAUSE_SECS)

                elif sc.current_stage == 64:
                    sc.feedback_msg = "SOP Step 64: Turn ON toggle switch VHS_Pow_P in General control switches."
                    if getattr(sw_p, "vhs_power_p", False):
                        await confirm_and_advance("✅ Video recorder power active in Port.", None, 2)

                elif sc.current_stage == 65:
                    sc.feedback_msg = "SOP Step 65: Turn ON toggle switch VHS_Pow_S in General control switches."
                    if getattr(sw_s, "vhs_power_s", False):
                        await confirm_and_advance("✅ Video recorder power active in Starboard.", None, 2)

                elif sc.current_stage == 66:
                    sc.feedback_msg = "SOP Step 66: Turn ON soft control button HD CAM1_P in imaging page GUI."
                    if getattr(img, "hd_camera_p", False) or getattr(mcc, "camera_4k_p_d", False):
                        await confirm_and_advance("✅ HD Camera Port active. Zoom, focus, and iris controls verified.", None, 3)

                elif sc.current_stage == 67:
                    sc.feedback_msg = "SOP Step 67: Turn ON soft control button SD Camera P3 in imaging page GUI."
                    if getattr(img, "hd_sdi_p3", False) or getattr(mcc, "hd_camera_p3_d", False):
                        await confirm_and_advance("✅ SD Landing Camera Port active. Video feed verified.", None, 2)

                elif sc.current_stage == 68:
                    sc.feedback_msg = "SOP Step 68: Turn ON soft control button SD Camera P4 in imaging page GUI."
                    if getattr(img, "hd_sdi_p4", False) or getattr(mcc, "sd_camera_p4_d", False):
                        await confirm_and_advance("✅ SD Fixed Camera Port active. Video feed verified.", None, 2)

                elif sc.current_stage == 69:
                    sc.feedback_msg = "SOP Step 69: Turn ON soft control button HD CAM1_S in imaging page GUI."
                    if getattr(img, "hd_camera_s", False) or getattr(mcc, "camera_4k_s_d", False):
                        await confirm_and_advance("✅ HD Camera Starboard active. Lens controls verified.", None, 3)

                elif sc.current_stage == 70:
                    sc.feedback_msg = "SOP Step 70: Turn ON soft control button SD Camera S3 in imaging page GUI."
                    if getattr(img, "hd_sdi_s3", False):
                        await confirm_and_advance("✅ SD Landing Camera Starboard active. Video feed verified.", None, 2)

                elif sc.current_stage == 71:
                    sc.feedback_msg = "SOP Step 71: Turn ON soft control button SD Camera S4 in imaging page GUI."
                    if getattr(img, "hd_sdi_s2", False) or getattr(mcc, "sd_camera_s4_d", False): 
                        await confirm_and_advance("✅ SD Fixed Camera Starboard active. Video feed verified.", None, 2)

                elif sc.current_stage == 72:
                    sc.feedback_msg = "SOP Step 72: Turn ON soft control button LED Light P2 in imaging page GUI."
                    if getattr(img.led_p2, "power", False) or getattr(mcc, "led_light_p2_d", False):
                        await confirm_and_advance("💡 Underwater LED Light Port 2 active.", "led_p2", 2)

                elif sc.current_stage == 73:
                    sc.feedback_msg = "SOP Step 73: Turn ON soft control button LED Light P3 in imaging page GUI."
                    if getattr(img.led_p3, "power", False) or getattr(mcc, "led_light_p3_d", False):
                        await confirm_and_advance("💡 Underwater LED Light Port 3 active.", "led_p3", 2)

                elif sc.current_stage == 74:
                    sc.feedback_msg = "SOP Step 74: Turn ON soft control button LED Light P4 in imaging page GUI."
                    await confirm_and_advance("💡 Underwater LED Light Port 4 active (Auto-advance).", None, 3)

                elif sc.current_stage == 75:
                    sc.feedback_msg = "SOP Step 75: Turn ON toggle switch LED Light P1 in general switches at PS."
                    if getattr(sw_p, "uw_camera_p", False):
                        await confirm_and_advance("💡 Underwater LED Light Port 1 active via switch.", "led_p1_toggle", 2)

                elif sc.current_stage == 76:
                    sc.feedback_msg = "SOP Step 76: Turn ON soft control button LED Light S2 in imaging page GUI."
                    if getattr(img.led_s2, "power", False) or getattr(mcc, "led_light_s2_d", False):
                        await confirm_and_advance("💡 Underwater LED Light Starboard 2 active.", "led_s2", 2)

                elif sc.current_stage == 77:
                    sc.feedback_msg = "SOP Step 77: Turn ON soft control button LED Light S3 in imaging page GUI."
                    if getattr(img.led_s3, "power", False) or getattr(mcc, "led_light_s3_d", False):
                        await confirm_and_advance("💡 Underwater LED Light Starboard 3 active.", "led_s3", 2)

                elif sc.current_stage == 78:
                    sc.feedback_msg = "SOP Step 78: Turn ON soft control button LED Light S4 in imaging page GUI."
                    await confirm_and_advance("💡 Underwater LED Light Starboard 4 active (Auto-advance).", None, 3)

                elif sc.current_stage == 79:
                    sc.feedback_msg = "SOP Step 79: Turn ON toggle switch LED Light S1 in general switches at PS."
                    if getattr(sw_s, "uw_camera_s", False):
                        await confirm_and_advance("💡 Underwater LED Light Starboard 1 active via switch.", "led_s1_toggle", 2)

                elif sc.current_stage == 80:
                    sc.feedback_msg = "SOP Step 80: Switch ON soft control button Obstacle SONAR in imaging page GUI."
                    if getattr(sen, "img_sonar", False):
                        await confirm_and_advance("📡 Obstacle Avoidance Sonar active.", None, 3)

                elif sc.current_stage == 81:
                    sc.feedback_msg = "SOP Step 81: Turn ON/Check recording in HD video recorder in LHS."
                    await confirm_and_advance("✅ HD recording status verified on Video Monitor 1 & 2.", None, 3)

                elif sc.current_stage == 82:
                    sc.feedback_msg = "SOP Step 82: Turn ON/Check recording in Analog video recorder in LHS."
                    await confirm_and_advance("✅ Analog recording status verified on Video Monitor 2.", None, 3)

                elif sc.current_stage == 83:
                    sc.feedback_msg = "SOP Step 83: Check video Overlay status in LHS."
                    await confirm_and_advance("⏱️ Date, time, and INS data alignment verified.", None, 3)

                elif sc.current_stage == 84:
                    sc.feedback_msg = "SOP Step 84: Turn ON soft control button CTD_P in Sensor / MCC page GUI."
                    if getattr(sen, "ctdo", False) or getattr(mcc, "ctdo_d", False):
                        await confirm_and_advance("📈 CTD Port sensor online.", "ctd_p", READING_PAUSE_SECS)

                elif sc.current_stage == 85:
                    sc.feedback_msg = "SOP Step 85: Turn ON soft control button DO_S in sensor / MCC page GUI."
                    if getattr(sen, "dissolved_o2", False) or getattr(mcc, "dissolved_o2_d", False):
                        await confirm_and_advance("📈 Starboard Dissolved Oxygen sensor active.", "do_s", READING_PAUSE_SECS)

                elif sc.current_stage == 86:
                    sc.feedback_msg = "SOP Step 86: Turn ON toggle switch Surface INS in general switches."
                    await confirm_and_advance("📈 Surface INS active (Auto-advance).", "surface_ins", READING_PAUSE_SECS)

                elif sc.current_stage == 87:
                    sc.feedback_msg = "SOP Step 87: Turn ON toggle switch Subsea GPS in general switches."
                    await confirm_and_advance("📈 Subsea GPS powered (Auto-advance).", "subsea_gps", READING_PAUSE_SECS)

                elif sc.current_stage == 88:
                    sc.feedback_msg = "SOP Step 88: Turn ON toggle switch Redt Depth in general switches."
                    await confirm_and_advance("📈 Redundant depth sensor loop verified (Auto-advance).", "redt_depth", READING_PAUSE_SECS)

                elif sc.current_stage == 89:
                    sc.feedback_msg = "SOP Step 89: Turn ON soft control button INS_P in sensors / MCC page GUI."
                    if getattr(sen, "ins", False) or getattr(mcc, "ins_d", False):
                        await confirm_and_advance("📈 INS-DVL powered in IDE_P.", "ins_p", READING_PAUSE_SECS)

                elif sc.current_stage == 90:
                    sc.feedback_msg = "SOP Step 90: Turn ON soft control button DVL_P in sensors / MCC page GUI."
                    if getattr(sen, "dvl", False) or getattr(mcc, "dvl_d", False):
                        await confirm_and_advance("📈 DVL tracking operational.", "dvl_p", READING_PAUSE_SECS)

                elif sc.current_stage == 91:
                    sc.feedback_msg = "SOP Step 91: Turn ON soft control button Altimeter_S in sensors / MCC page GUI."
                    if getattr(sen, "altimeter", False) or getattr(mcc, "altimeter_d", False):
                        await confirm_and_advance("📈 Altimeter operational.", "altimeter_s", READING_PAUSE_SECS)

                elif sc.current_stage == 92:
                    sc.feedback_msg = "SOP Step 92: Power ON soft button Acoustic modem (APS2) in sensors / MCC page GUI."
                    if getattr(sw_s, "aps_2", False) or getattr(mcc_status, "acoustic_comm_auto", False):
                        await confirm_and_advance("📡 Acoustic modem links established.", "acoustic_modem", READING_PAUSE_SECS)

                elif sc.current_stage == 93:
                    sc.feedback_msg = "SOP Step 93: Turn ON subsea VHF receiver in PS for surface voice checks."
                    if getattr(sw_s, "vhf", False):
                        await confirm_and_advance("🔊 Subsea VHF voice loop established.", None, 3)

                elif sc.current_stage == 94:
                    sc.feedback_msg = "SOP Step 94: Turn ON shallow water underwater acoustic telephone (SUAT) in LHS."
                    if getattr(sw_s, "uwt", False):
                        await confirm_and_advance("✅ Subsytem operational checks successfully completed!", None, 2)

                elif sc.current_stage == 95:
                    sc.feedback_msg = "Phase 1: Inspect Penetrator Plates, then turn ON Dive-In switch (SW3)."
                    if getattr(sw3, "dive_in", False):
                        await confirm_and_advance("✅ Dive-In Switch toggled ON. Penetrator plates verified.", None, 2)

                elif sc.current_stage == 96:
                    sc.feedback_msg = "Phase 1: Verify Life Support System fully functional before maneuvering."
                    await confirm_and_advance("✅ Life Support systems holding nominal parameters.", None, 3)

                elif sc.current_stage == 97:
                    sc.feedback_msg = "Phase 1: Power Main Ballast - Turn ON MBS soft control button in Ballast / Sensors GUI."
                    if getattr(sen, "mbs", False) or getattr(sw_s, "mbs_ctrl", False):
                        await confirm_and_advance("📈 Main Ballast powered. Recording air bottle pressure.", "mbs_active", READING_PAUSE_SECS)

                # ─────────────────────────────────────────────────────────────
                # PHASE 2: AUTO-ADVANCING TANK FILLING ANIMATIONS & DESCENT
                # ─────────────────────────────────────────────────────────────
                elif sc.current_stage == 98:
                    sc.feedback_msg = "Phase 2: Auto-Sequence 'Ready to Dive'. Flooding first six tanks..."
                    await broadcast_fn()
                    await asyncio.sleep(2.0)
                    
                    mb = getattr(ballast, "main_ballast", None)
                    
                    for i in range(1, 11):
                        bars = "█" * i + "░" * (10 - i)
                        sc.feedback_msg = f"🌊 Flooding 6 Side Tanks: [{bars}] {i*10}%"
                        
                        slider_val = 150 - (i * 30) 
                        if mb:
                            if hasattr(mb, "act3_pos"): mb.act3_pos = slider_val
                            if hasattr(mb, "act3_pos2"): mb.act3_pos2 = slider_val
                        
                        await broadcast_fn()
                        await asyncio.sleep(0.5) 
                        
                    await confirm_and_advance("✅ Six tanks flooded. Confirming neutral buoyancy and freeboard.", "ready_to_dive", 2)

                elif sc.current_stage == 99:
                    sc.feedback_msg = "Phase 2: Auto-Sequence 'Dive open'. Flooding 7th tank..."
                    await broadcast_fn()
                    await asyncio.sleep(2.0)
                    
                    mb = getattr(ballast, "main_ballast", None)

                    for i in range(1, 11):
                        bars = "█" * i + "░" * (10 - i)
                        sc.feedback_msg = f"⏬ Venting 7th Tank: [{bars}] {i*10}%"
                        
                        slider_val = 150 - (i * 30) 
                        if mb and hasattr(mb, "act3_pos3"): 
                            mb.act3_pos3 = slider_val
                            
                        await broadcast_fn()
                        await asyncio.sleep(0.4)
                        
                    await confirm_and_advance("✅ Negative buoyancy achieved. Beginning descent.", "initiate_dive", 2)

                # ─────────────────────────────────────────────────────────────
                # PROPULSION INTERLOCK CHECKS & SEABED
                # ─────────────────────────────────────────────────────────────
                elif sc.current_stage == 100:
                    sc.feedback_msg = "Propulsion Check: Verify 148 VDC contactor is ON for Port & Stbd."
                    if getattr(sw_p, "mb_p_pde_p", False) and getattr(sw_s, "mb_s_pde_s", False):
                        await confirm_and_advance("✅ 148 VDC Power confirmed active.", None, 2)

                elif sc.current_stage == 101:
                    sc.feedback_msg = "Propulsion Check: Enable the Thruster Enable interlock in Main GUI."
                    if getattr(sidebar, "thrusters_enable", False):
                        await confirm_and_advance("✅ Thruster master interlock ENABLED.", None, 2)

                elif sc.current_stage == 102:
                    sc.feedback_msg = "Propulsion Check: Power & Enable Thrusters. Operate at 60-70 RPM."
                    if getattr(pd.t1, "power", False) and getattr(pd.t1, "enable", False):
                        await confirm_and_advance("✅ Thrusters powered and enabled. RPM feedback verified.", "thrusters_spin", READING_PAUSE_SECS)

                elif sc.current_stage == 103:
                    sc.feedback_msg = "Propulsion Check: Enable the Joystick in the Main GUI."
                    if getattr(sidebar, "joystick", False):
                        await confirm_and_advance("✅ Joystick control ENABLED.", None, 2)

                # ─────────────────────────────────────────────────────────────
                # PHASE 4 & 5: SEABED OPERATIONS & ASCENT (Steps 104 - 106)
                # ─────────────────────────────────────────────────────────────
                elif sc.current_stage == 104:
                    sc.feedback_msg = "Phase 4: Seabed Approach. Set Port 1 & Stbd 1 weights to PC ON."
                    
                    val_p1 = getattr(sw_p, "port_side_sdw_1", None)
                    # FIX: Read sdws_1 from sw_p
                    val_s1 = getattr(sw_p, "starboard_side_sdw_1", None)

                    if sc.timer_remaining % 5 == 0:
                        print(f"[DEBUG Stage 104] Waiting for PC ON. Current -> sdwp_1: {val_p1} | sdws_1: {val_s1}")

                    if is_pc_on(val_p1) and is_pc_on(val_s1):
                        await confirm_and_advance("⚓ Approaching Seabed. 100kg weights dropped. Buoyancy neutralized.", "depth_seabed", 3)

                elif sc.current_stage == 105:
                    sc.feedback_msg = "Phase 4: Seabed Sampling. Set Port 2, 3 & Stbd 2, 3 weights to PC ON."
                    
                    val_p2, val_p3 = getattr(sw_p, "port_side_sdw_2", None), getattr(sw_p, "port_side_sdw_3", None)
                    # FIX: Read sdws_2 and sdws_3 from sw_p
                    val_s2, val_s3 = getattr(sw_p, "starboard_side_sdw_2", None), getattr(sw_p, "starboard_side_sdw_3", None)

                    if sc.timer_remaining % 5 == 0:
                        print(f"[DEBUG Stage 105] Waiting for PC ON. Port 2,3: {val_p2},{val_p3} | Stbd 2,3: {val_s2},{val_s3}")

                    if is_pc_on(val_p2) and is_pc_on(val_p3) and is_pc_on(val_s2) and is_pc_on(val_s3):
                        await confirm_and_advance("🔬 Seabed reached (5500m). Payload sampling complete. 200kg weights dropped.", "sampling_seabed", 3)

                elif sc.current_stage == 106:
                    sc.feedback_msg = "Phase 5: Start Ascent. Set Port 4, 5 & Stbd 4, 5 weights to PC ON."
                    
                    val_p4, val_p5 = getattr(sw_p, "port_side_sdw_4", None), getattr(sw_p, "port_side_sdw_5", None)
                    # FIX: Read sdws_4 and sdws_5 from sw_p
                    val_s4, val_s5 = getattr(sw_p, "starboard_side_sdw_4", None), getattr(sw_p, "starboard_side_sdw_5", None)

                    if sc.timer_remaining % 5 == 0:
                        print(f"[DEBUG Stage 106] Waiting for PC ON. Port 4,5: {val_p4},{val_p5} | Stbd 4,5: {val_s4},{val_s5}")

                    if is_pc_on(val_p4) and is_pc_on(val_p5) and is_pc_on(val_s4) and is_pc_on(val_s5):
                        await confirm_and_advance("🚀 300kg dropped. Positive buoyancy achieved. Beginning ascent.", "ascent_start", 3)

                # ─────────────────────────────────────────────────────────────
                # PHASE 5: AUTO-ADVANCING SURFACING ANIMATIONS
                # ─────────────────────────────────────────────────────────────
                elif sc.current_stage == 107:
                    sc.feedback_msg = "Phase 5: Surface Reached. Auto-Sequence 'Surface open'..."
                    await broadcast_fn()
                    await asyncio.sleep(2.0)
                    
                    mb = getattr(ballast, "main_ballast", None)

                    for i in range(1, 11):
                        bars = "█" * i + "░" * (10 - i)
                        sc.feedback_msg = f"🌊 Blowing Ballast Tanks (Emptying): [{bars}] {i*10}%"
                        
                        slider_val = -150 + (i * 30) 
                        if mb:
                            if hasattr(mb, "act3_pos"): mb.act3_pos = slider_val
                            if hasattr(mb, "act3_pos2"): mb.act3_pos2 = slider_val
                            if hasattr(mb, "act3_pos3"): mb.act3_pos3 = slider_val
                            
                        await broadcast_fn()
                        await asyncio.sleep(0.4)
                        
                    await confirm_and_advance("✅ Surfaced. Main Ballast active.", "surfaced", 2)

                # FIX: Increment numbering (changed from 107 to 108 to fix duplicated elif blocks)
                elif sc.current_stage == 108:
                    sc.feedback_msg = "Phase 5: Blow Ballast (Freeboard). Turn ON FREEBOARD button."
                    if getattr(sw3, "freeboard_p", False) or getattr(sw3, "freeboard_s", False):
                        await confirm_and_advance("💨 Tanks blown. Freeboard established at 1.5m.", "freeboard", READING_PAUSE_SECS)

                # FIX: Increment numbering (changed from 108 to 109)
                elif sc.current_stage == 109:
                    sc.success = True
                    sc.active = False
                    sc.result_message = "✅ FULL MISSION SUCCESS! Powering, Ops Checks, and 5500m Dive complete."
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
        app_state.scenario.active = False
        app_state.scenario.result_message = f"CRASH: {str(e)}"
        try:
            await broadcast_fn()
        except:
            pass