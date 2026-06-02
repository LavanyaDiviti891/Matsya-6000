import asyncio
from dataclasses import dataclass
from typing import Optional


# ─────────────────────────────────────────────────────────────────────────────
# SOP GO-CRITERIA THRESHOLDS (from "Powering Matsya" SOP document)
# ─────────────────────────────────────────────────────────────────────────────
EB_VOLTAGE_MIN   = 25.0    # V   — steps 5, 21
EB_SOC_MIN       = 90.0    # %   — steps 5, 21
IR_GO_MIN        = 1.5     # MOhm — steps 6, 12, 22, 28, 39, 42, 43, 45, 49, 52, 53, 55
UB_VOLTAGE_NOM   = 24.0    # V   — steps 11, 27  (approx ±2 V tolerance)
UB_VOLTAGE_TOL   = 2.0     # V
MB_VOLTAGE_MIN   = 160.0   # V   — steps 38, 48
MB_SOC_MIN       = 90.0    # %   — steps 38, 48
MB_TEMP_MAX      = 30.0    # °C  — steps 38, 48
MB_PACK_V_MIN    = 162.0   # V   — step 41 per-pack check


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
    wait_ticks: int = 0


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
    sc.wait_ticks = 0


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────
def _eb_go(eb_state) -> bool:
    return (eb_state.voltage.value > EB_VOLTAGE_MIN and eb_state.soc.value > EB_SOC_MIN)

def _ir_go(ir_value: float) -> bool:
    return ir_value >= IR_GO_MIN

def _ub_voltage_go(ub_state) -> bool:
    v = ub_state.voltage.value
    return abs(v - UB_VOLTAGE_NOM) <= UB_VOLTAGE_TOL

def _mb_go(mb_state) -> bool:
    return (mb_state.voltage.value > MB_VOLTAGE_MIN and mb_state.soc.value > MB_SOC_MIN and mb_state.temp.value < MB_TEMP_MAX)

def _mb_pack_go(mb_state) -> bool:
    return (mb_state.voltage.value > MB_PACK_V_MIN and mb_state.soc.value > MB_SOC_MIN and mb_state.temp.value < MB_TEMP_MAX)


# ─────────────────────────────────────────────────────────────────────────────
# Scenario: POWERING MATSYA
# ─────────────────────────────────────────────────────────────────────────────
async def run_powering_matsya_scenario(app_state, broadcast_fn, ScenarioOverlay_fn=None):
    sc = scenario_state
    sw_p = app_state.switches.p
    sw_s = app_state.switches.s
    pw = app_state.power

    # Initialise
    reset_scenario(sc)
    sc.active          = True
    sc.mission_name    = "POWERING MATSYA"
    sc.timer_total     = 600
    sc.timer_remaining = 600
    sc.current_stage   = 1
    sc.feedback_msg    = (
        "STAGE 1 — PORT: Turn ON e_batts_p (EB_P selector) "
        "then mcb_p (MCB-1) in Switches_P. MCB must not trip."
    )

    # Reset all switches
    sw_p.e_batts_p = sw_p.mcb_p = sw_p.emergency_led_p = sw_p.ab_p_bms = False
    sw_p.ab_p = sw_p.ub_p_mcb = sw_p.int_led_p = sw_p.ub_p = sw_p.mb_p_bms = False
    sw_p.pde_p_oim = sw_p.pde_p_olr = sw_p.mb_p_pde_p = sw_p.ide_p = False
    sw_p.mb_p_1 = sw_p.mb_p_2 = sw_p.mb_p_3 = sw_p.mb_p_4 = sw_p.mb_p_5 = False

    sw_s.e_batts_s = sw_s.mcb_s = sw_s.emergency_led_s = sw_s.ab_s_bms = False
    sw_s.ab_s = sw_s.ub_s_mcb = sw_s.int_led_s = sw_s.ub_s = sw_s.mb_s_bms = False
    sw_s.pde_s_oim = sw_s.pde_s_olr = sw_s.mb_s_pde_s = sw_s.ide_s = False
    sw_s.mb_s_1 = sw_s.mb_s_2 = sw_s.mb_s_3 = sw_s.mb_s_4 = sw_s.mb_s_5 = False

    await broadcast_fn()

    # ── Main Loop ─────────────────────────────────────────────────────────────
    while sc.active and sc.success is None and sc.timer_remaining > 0:
        await asyncio.sleep(1.0)
        sc.timer_remaining -= 1
        sc.blink = not sc.blink

        # ── PORT SIDE ────────────────────────────────────────────────────────

        if sc.current_stage == 1:
            if sw_p.e_batts_p and sw_p.mcb_p:
                sc.current_stage = 2
                sc.feedback_msg = "STAGE 2 — PORT: Turn ON emergency_led_p (EMG_LED_P) in Switches_P."

        elif sc.current_stage == 2:
            if sw_p.emergency_led_p:
                sc.current_stage = 3
                sc.wait_ticks = 0
                sc.feedback_msg = "STAGE 3 — PORT: GO CHECK — Verifying EB_P limits..."

        elif sc.current_stage == 3:
            # Force values every single tick to overpower background simulator resets
            if not _eb_go(pw.eb_p):
                pw.eb_p.voltage.value = EB_VOLTAGE_MIN + 1.0
                pw.eb_p.soc.value = EB_SOC_MIN + 5.0
                
            if sc.wait_ticks == 0:
                sc.wait_ticks = 7
            else:
                sc.wait_ticks -= 1
                sc.feedback_msg = f"STAGE 3 — PORT: Values ready. Note down EB_P Voltage & SOC. (Advancing in {sc.wait_ticks}s...)"
                if sc.wait_ticks <= 0:
                    sc.current_stage = 4
                    sc.wait_ticks = 0
                    sc.feedback_msg = "STAGE 4 — PORT: Set UB_P selector to AB_P position, then turn ON ab_p_bms, ab_p, and ub_p_mcb in Switches_P."

        elif sc.current_stage == 4:
            if sw_p.ab_p_bms and sw_p.ab_p and sw_p.ub_p_mcb:
                sc.current_stage = 5
                sc.wait_ticks = 0
                sc.feedback_msg = "STAGE 5 — PORT: GO CHECK — Verifying UB_PORT limits..."

        elif sc.current_stage == 5:
            # Force values into both ub_port (for UI binding) and ub_p every single tick
            if not (_ub_voltage_go(pw.ub_port) and _ir_go(pw.ub_port.ir.value)):
                pw.ub_port.voltage.value = UB_VOLTAGE_NOM
                pw.ub_port.ir.value = IR_GO_MIN + 1.0
                pw.ub_port.ir_status = "No Leak"
                
            pw.ub_p.voltage.value = UB_VOLTAGE_NOM
            pw.ub_p.ir_instant.value = IR_GO_MIN + 1.0
            pw.ub_p.ir_final.value = IR_GO_MIN + 1.0
                
            if sc.wait_ticks == 0:
                sc.wait_ticks = 7
            else:
                sc.wait_ticks -= 1
                sc.feedback_msg = f"STAGE 5 — PORT: Values ready. Note down UB_PORT Voltage & IR. (Advancing in {sc.wait_ticks}s...)"
                if sc.wait_ticks <= 0:
                    sc.current_stage = 6
                    sc.wait_ticks = 0
                    sc.feedback_msg = "STAGE 6 — PORT: Turn ON int_led_p (INT_LED_P) for internal lights, then set ub_p changeover to UB_P position in Switches_P."

        elif sc.current_stage == 6:
                if sw_p.int_led_p and sw_p.ub_p:
                    sc.current_stage = 7
                    sc.feedback_msg = "STAGE 7 — PORT: Check EMCS PS, wait for PLC. Advance by confirming ub_p remains ON."

        elif sc.current_stage == 7:
                if sw_p.int_led_p and sw_p.ub_p:
                    sc.current_stage = 8
                    sc.feedback_msg = "STAGE 8 — STARBOARD: Turn ON e_batts_s (EB_S selector) then mcb_s (MCB-2) in Switches_S."

        # ── STARBOARD SIDE ───────────────────────────────────────────────────

        elif sc.current_stage == 8:
            if sw_s.e_batts_s and sw_s.mcb_s:
                sc.current_stage = 9
                sc.feedback_msg = "STAGE 9 — STARBOARD: Turn ON emergency_led_s (EMG_LED_S) in Switches_S."

        elif sc.current_stage == 9:
            if sw_s.emergency_led_s:
                sc.current_stage = 10
                sc.wait_ticks = 0
                sc.feedback_msg = "STAGE 10 — STARBOARD: GO CHECK — Verifying EB_S limits..."

        elif sc.current_stage == 10:
            if not _eb_go(pw.eb_s):
                pw.eb_s.voltage.value = EB_VOLTAGE_MIN + 1.0
                pw.eb_s.soc.value = EB_SOC_MIN + 5.0
                
            if sc.wait_ticks == 0:
                sc.wait_ticks = 7
            else:
                sc.wait_ticks -= 1
                sc.feedback_msg = f"STAGE 10 — STARBOARD: Values ready. Note down EB_S Voltage & SOC. (Advancing in {sc.wait_ticks}s...)"
                if sc.wait_ticks <= 0:
                    sc.current_stage = 11
                    sc.wait_ticks = 0
                    sc.feedback_msg = "STAGE 11 — STARBOARD: Set UB_S selector to AB_S position, then turn ON ab_s_bms, ab_s, and ub_s_mcb in Switches_S."

        elif sc.current_stage == 11:
            if sw_s.ab_s_bms and sw_s.ab_s and sw_s.ub_s_mcb:
                sc.current_stage = 12
                sc.wait_ticks = 0
                sc.feedback_msg = "STAGE 12 — STARBOARD: GO CHECK — Verifying UB_STBD limits..."

        elif sc.current_stage == 12:
            # Force values into both ub_stbd (for UI binding) and ub_s every single tick
            if not (_ub_voltage_go(pw.ub_stbd) and _ir_go(pw.ub_stbd.ir.value)):
                pw.ub_stbd.voltage.value = UB_VOLTAGE_NOM
                pw.ub_stbd.ir.value = IR_GO_MIN + 1.0
                pw.ub_stbd.ir_status = "No Leak"
                
            pw.ub_s.voltage.value = UB_VOLTAGE_NOM
            pw.ub_s.ir_instant.value = IR_GO_MIN + 1.0
            pw.ub_s.ir_final.value = IR_GO_MIN + 1.0
                
            if sc.wait_ticks == 0:
                sc.wait_ticks = 7
            else:
                sc.wait_ticks -= 1
                sc.feedback_msg = f"STAGE 12 — STARBOARD: Values ready. Note down UB_STBD Voltage & IR. (Advancing in {sc.wait_ticks}s...)"
                if sc.wait_ticks <= 0:
                    sc.current_stage = 13
                    sc.wait_ticks = 0
                    sc.feedback_msg = "STAGE 13 — STARBOARD: Turn ON int_led_s (INT_LED_S), then set ub_s changeover to UB_S position in Switches_S."

        elif sc.current_stage == 13:
            if sw_s.int_led_s and sw_s.ub_s:
                sc.current_stage = 14
                sc.feedback_msg = "STAGE 14 — STARBOARD: Check EMCS stbd. Advance by keeping ub_s ON."

        elif sc.current_stage == 14:
            if sw_s.int_led_s and sw_s.ub_s:
                sc.current_stage = 15
                sc.feedback_msg = "STAGE 15 — PDE PORT: Turn ON mb_p_bms (MB_P BMS power) in Switches_P."

        # ── PDE/IDE PORT ─────────────────────────────────────────────────────

        elif sc.current_stage == 15:
            if sw_p.mb_p_bms:
                sc.current_stage = 16
                sc.wait_ticks = 0
                sc.feedback_msg = "STAGE 16 — PDE PORT: GO CHECK — Verifying MB_P limits..."

        elif sc.current_stage == 16:
            if not _mb_go(pw.mb_p):
                pw.mb_p.voltage.value = MB_VOLTAGE_MIN + 5.0
                pw.mb_p.soc.value = MB_SOC_MIN + 5.0
                pw.mb_p.temp.value = MB_TEMP_MAX - 5.0
                
            if sc.wait_ticks == 0:
                sc.wait_ticks = 7
            else:
                sc.wait_ticks -= 1
                sc.feedback_msg = f"STAGE 16 — PDE PORT: Values ready. Note down MB_P Voltage, SOC, Temp. (Advancing in {sc.wait_ticks}s...)"
                if sc.wait_ticks <= 0:
                    sc.current_stage = 17
                    sc.wait_ticks = 0
                    sc.feedback_msg = "STAGE 17 — PDE PORT: Turn ON pde_p_oim then pde_p_olr in Switches_P."

        elif sc.current_stage == 17:
            if sw_p.pde_p_oim and sw_p.pde_p_olr:
                if not _ir_go(pw.pde_p.ir_148.value):
                    pw.pde_p.ir_148.value = IR_GO_MIN + 1.0
                    
                if sc.wait_ticks == 0:
                    sc.wait_ticks = 7
                else:
                    sc.wait_ticks -= 1
                    sc.feedback_msg = f"STAGE 17 — PDE PORT: Values ready. Note down PDE_P IR. (Advancing in {sc.wait_ticks}s...)"
                    if sc.wait_ticks <= 0:
                        sc.current_stage = 18
                        sc.wait_ticks = 0
                        sc.feedback_msg = "STAGE 18 — PDE PORT: Sequentially turn ON mb_p_1 through mb_p_5 in Switches_P."
            else:
                sc.wait_ticks = 0
                sc.feedback_msg = "STAGE 17 — PDE PORT: Turn ON pde_p_oim then pde_p_olr in Switches_P."

        elif sc.current_stage == 18:
            all_packs_on = (sw_p.mb_p_1 and sw_p.mb_p_2 and sw_p.mb_p_3 and sw_p.mb_p_4 and sw_p.mb_p_5)
            if all_packs_on:
                if not _mb_pack_go(pw.mb_p):
                    pw.mb_p.voltage.value = MB_PACK_V_MIN + 5.0
                    pw.mb_p.soc.value = MB_SOC_MIN + 5.0
                    pw.mb_p.temp.value = MB_TEMP_MAX - 5.0
                    
                if sc.wait_ticks == 0:
                    sc.wait_ticks = 7
                else:
                    sc.wait_ticks -= 1
                    sc.feedback_msg = f"STAGE 18 — PDE PORT: Values ready. Note down Pack Voltage/SOC/Temp. (Advancing in {sc.wait_ticks}s...)"
                    if sc.wait_ticks <= 0:
                        sc.current_stage = 19
                        sc.wait_ticks = 0
                        sc.feedback_msg = "STAGE 19 — PDE PORT: Turn ON mb_p_pde_p (Main Power Contactor) in Switches_P."
            else:
                sc.wait_ticks = 0
                sc.feedback_msg = "STAGE 18 — PDE PORT: Sequentially turn ON mb_p_1 through mb_p_5 in Switches_P."

        elif sc.current_stage == 19:
            if sw_p.mb_p_pde_p:
                if not _ir_go(pw.pde_p.ir_148.value):
                    pw.pde_p.ir_148.value = IR_GO_MIN + 1.0
                    
                if sc.wait_ticks == 0:
                    sc.wait_ticks = 7
                else:
                    sc.wait_ticks -= 1
                    sc.feedback_msg = f"STAGE 19 — PDE PORT: Values ready. Note down IR. (Advancing in {sc.wait_ticks}s...)"
                    if sc.wait_ticks <= 0:
                        sc.current_stage = 20
                        sc.wait_ticks = 0
                        sc.feedback_msg = "STAGE 20 — IDE PORT: Turn ON ide_p (IDE1_P) in Switches_P."
            else:
                sc.wait_ticks = 0
                sc.feedback_msg = "STAGE 19 — PDE PORT: Turn ON mb_p_pde_p (Main Power Contactor) in Switches_P."

        elif sc.current_stage == 20:
            if sw_p.ide_p:
                if not _ir_go(pw.ide_p.ir_24.value):
                    pw.ide_p.ir_24.value = IR_GO_MIN + 1.0
                    
                if sc.wait_ticks == 0:
                    sc.wait_ticks = 7
                else:
                    sc.wait_ticks -= 1
                    sc.feedback_msg = f"STAGE 20 — IDE PORT: Values ready. Note down IDE_P IR. (Advancing in {sc.wait_ticks}s...)"
                    if sc.wait_ticks <= 0:
                        sc.current_stage = 21
                        sc.wait_ticks = 0
                        sc.feedback_msg = "STAGE 21 — PDE STARBOARD: Turn ON mb_s_bms (MB_S BMS power) in Switches_S."
            else:
                sc.wait_ticks = 0
                sc.feedback_msg = "STAGE 20 — IDE PORT: Turn ON ide_p (IDE1_P) in Switches_P."

        # ── PDE/IDE STARBOARD ────────────────────────────────────────────────

        elif sc.current_stage == 21:
            if sw_s.mb_s_bms:
                sc.current_stage = 22
                sc.wait_ticks = 0
                sc.feedback_msg = "STAGE 22 — PDE STARBOARD: GO CHECK — Verifying MB_S limits..."

        elif sc.current_stage == 22:
            if not _mb_go(pw.mb_s):
                pw.mb_s.voltage.value = MB_VOLTAGE_MIN + 5.0
                pw.mb_s.soc.value = MB_SOC_MIN + 5.0
                pw.mb_s.temp.value = MB_TEMP_MAX - 5.0
                
            if sc.wait_ticks == 0:
                sc.wait_ticks = 7
            else:
                sc.wait_ticks -= 1
                sc.feedback_msg = f"STAGE 22 — PDE STARBOARD: Values ready. Note down MB_S Voltage, SOC, Temp. (Advancing in {sc.wait_ticks}s...)"
                if sc.wait_ticks <= 0:
                    sc.current_stage = 23
                    sc.wait_ticks = 0
                    sc.feedback_msg = "STAGE 23 — PDE STARBOARD: Turn ON pde_s_oim then pde_s_olr in Switches_S."

        elif sc.current_stage == 23:
            if sw_s.pde_s_oim and sw_s.pde_s_olr:
                if not _ir_go(pw.pde_s.ir_148.value):
                    pw.pde_s.ir_148.value = IR_GO_MIN + 1.0
                    
                if sc.wait_ticks == 0:
                    sc.wait_ticks = 7
                else:
                    sc.wait_ticks -= 1
                    sc.feedback_msg = f"STAGE 23 — PDE STARBOARD: Values ready. Note down PDE_S IR. (Advancing in {sc.wait_ticks}s...)"
                    if sc.wait_ticks <= 0:
                        sc.current_stage = 24
                        sc.wait_ticks = 0
                        sc.feedback_msg = "STAGE 24 — PDE STARBOARD: Sequentially turn ON mb_s_1 through mb_s_5 in Switches_S."
            else:
                sc.wait_ticks = 0
                sc.feedback_msg = "STAGE 23 — PDE STARBOARD: Turn ON pde_s_oim then pde_s_olr in Switches_S."

        elif sc.current_stage == 24:
            all_packs_on = (sw_s.mb_s_1 and sw_s.mb_s_2 and sw_s.mb_s_3 and sw_s.mb_s_4 and sw_s.mb_s_5)
            if all_packs_on:
                if not _mb_pack_go(pw.mb_s):
                    pw.mb_s.voltage.value = MB_PACK_V_MIN + 5.0
                    pw.mb_s.soc.value = MB_SOC_MIN + 5.0
                    pw.mb_s.temp.value = MB_TEMP_MAX - 5.0
                    
                if sc.wait_ticks == 0:
                    sc.wait_ticks = 7
                else:
                    sc.wait_ticks -= 1
                    sc.feedback_msg = f"STAGE 24 — PDE STARBOARD: Values ready. Note down Pack Voltage/SOC/Temp. (Advancing in {sc.wait_ticks}s...)"
                    if sc.wait_ticks <= 0:
                        sc.current_stage = 25
                        sc.wait_ticks = 0
                        sc.feedback_msg = "STAGE 25 — PDE STARBOARD: Turn ON mb_s_pde_s (Main Power Contactor) in Switches_S."
            else:
                sc.wait_ticks = 0
                sc.feedback_msg = "STAGE 24 — PDE STARBOARD: Sequentially turn ON mb_s_1 through mb_s_5 in Switches_S."

        elif sc.current_stage == 25:
            if sw_s.mb_s_pde_s:
                if not _ir_go(pw.pde_s.ir_148.value):
                    pw.pde_s.ir_148.value = IR_GO_MIN + 1.0
                    
                if sc.wait_ticks == 0:
                    sc.wait_ticks = 7
                else:
                    sc.wait_ticks -= 1
                    sc.feedback_msg = f"STAGE 25 — PDE STARBOARD: Values ready. Note down IR. (Advancing in {sc.wait_ticks}s...)"
                    if sc.wait_ticks <= 0:
                        sc.current_stage = 26
                        sc.wait_ticks = 0
                        sc.feedback_msg = "STAGE 26 — IDE STARBOARD: Turn ON ide_s (IDE1_S) in Switches_S."
            else:
                sc.wait_ticks = 0
                sc.feedback_msg = "STAGE 25 — PDE STARBOARD: Turn ON mb_s_pde_s (Main Power Contactor) in Switches_S."

        elif sc.current_stage == 26:
            if sw_s.ide_s:
                if not _ir_go(pw.ide_s.ir_24.value):
                    pw.ide_s.ir_24.value = IR_GO_MIN + 1.0
                    
                if sc.wait_ticks == 0:
                    sc.wait_ticks = 7
                else:
                    sc.wait_ticks -= 1
                    sc.feedback_msg = f"STAGE 26 — IDE STARBOARD: Values ready. Note down IDE_S IR. (Advancing in {sc.wait_ticks}s...)"
                    if sc.wait_ticks <= 0:
                        sc.current_stage = 27
                        sc.wait_ticks = 0
                        sc.feedback_msg = "STAGE 27 — FINAL: Verify all comm links in GUI. Ensure ide_s and mb_s_pde_s remain ON."
            else:
                sc.wait_ticks = 0
                sc.feedback_msg = "STAGE 26 — IDE STARBOARD: Turn ON ide_s (IDE1_S) in Switches_S."

        elif sc.current_stage == 27:
            # Check final constraints
            all_on = (sw_p.mb_p_pde_p and sw_p.ide_p and sw_s.mb_s_pde_s and sw_s.ide_s)
            
            # Auto-apply final SOC if failing
            if pw.mb_p.soc.value < 25.0: pw.mb_p.soc.value = 95.0
            if pw.mb_s.soc.value < 25.0: pw.mb_s.soc.value = 95.0
            
            if all_on:
                if sc.wait_ticks == 0:
                    sc.wait_ticks = 7
                else:
                    sc.wait_ticks -= 1
                    sc.feedback_msg = f"STAGE 27 — FINAL: All systems GO! Concluding mission in {sc.wait_ticks}s..."
                    if sc.wait_ticks <= 0:
                        sc.current_stage = 28
            else:
                sc.wait_ticks = 0
                sc.feedback_msg = "STAGE 27 — FINAL: Waiting for operator to confirm final contactors ON."
                
        elif sc.current_stage == 28:
            sc.success        = True
            sc.active         = False
            sc.result_message = " Vehicle powered successfully — all systems GO! Ready for operational checks."
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
        sc.result_message = "⏱ Time expired before mission completion. Mission FAILED."

    await broadcast_fn()
    await asyncio.sleep(6)
    reset_scenario(sc)
    await broadcast_fn()