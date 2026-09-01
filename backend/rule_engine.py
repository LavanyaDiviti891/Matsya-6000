"""
MATSYA 6000 Power-Up Rule Engine
================================
State-based SOP classifier and telemetry manager implementing the MATSYA 6000
Power-Up SOP & Logic specification.
"""

import datetime
import random

def _blank_sequence_state():
    return {
        "eb_pos_confirmed": False,
        "emg_led_on": False,
        "scrubber_done": False,
        "ub_pos_confirmed": False,
        "ab_bms_on": False,
        "ab_power_on": False,
        "ub_mcb_on": False,
        "emcs_powered": False,
        "eb_ub_changeover_done": False,
        # SOP Step 59: EB selector reverted back to EB position
        "eb_reverted": False,
        # SOP Step 60: UB selector changed over from AB to Main Battery (MB)
        "ub_mb_changeover_done": False,
    }


_sequence_state = {"P": _blank_sequence_state(), "S": _blank_sequence_state()}

_active_side = ""

# ── Training fault-injection state (Medium & Hard scenarios, scoped to the
#    Main Battery power-up phase / SOP steps ~51 and ~60) ───────────────────
_fault_state = {
    "medium_triggered": False,   # Medium: MB_S_3 insulation fault has fired once
    "medium_active": False,      # True while the IR fault is unresolved
    "hard_triggered": False,     # Hard: UB_P changeover blackout has fired once
    "hard_active_p": False,      # True while the Port blackout is unresolved
}

# Monotonic counter, unique per event_log entry. The frontend uses this
# (not the 1-second-resolution `timestamp` string) to dedupe voice-over.
_event_seq = 0

# The live scenario is intentionally scoped to Main Battery power-up (SOP
# Steps 1-60). Flip this to True to re-enable the Imaging -> Sensors ->
# Comms -> Ballast -> Propulsion driver (SOP steps 63-108) again later.
ENABLE_POST_MAIN_BATTERY_PHASES = False


def start_scenario(app_state):
    """Activates the SOP-driven power-up scenario and resets all tracking
    state so the operator starts from SOP Step 1 -- no fault is armed
    until the pilot actually works their way through the real sequence."""
    reset_engine(app_state)
    sc = app_state.scenario
    sc.active = True
    sc.feedback_msg = (
        "SOP Monitor active. Toggle any PORT or STARBOARD switch to begin "
        "Step 1 — whichever side you touch first becomes the active side."
    )
    recompute_derived_flags(app_state)


def stop_scenario(app_state):
    sc = app_state.scenario
    sc.active = False
    sc.feedback_msg = "Awaiting power-up sequence start."
    reset_engine(app_state)


def reset_engine(app_state=None):
    global _active_side, _event_seq
    _active_side = ""
    _event_seq = 0
    _fault_state["medium_triggered"] = False
    _fault_state["medium_active"] = False
    _fault_state["hard_triggered"] = False
    _fault_state["hard_active_p"] = False
    for side in ("P", "S"):
        _sequence_state[side] = _blank_sequence_state()
        if app_state:
            _clear_eb_readings(app_state, side)
            _clear_ub_readings(app_state, side)
    if app_state:
        app_state.scenario.alarm_active = False
        app_state.scenario.alarm_message = ""
        app_state.scenario.fault_type = ""
        app_state.scenario.clear_message = ""
        app_state.scenario.next_step_final = ""
        app_state.scenario.main_battery_complete = False
        refresh_telemetry_displays(app_state)


FIELD_MAP = {
    # Port Emergency Bus Selection & Emergency Switches
    "switches.p.e_batts":            ("P", "EB_P_SELECT", "eb_position"),
    "switches.p.power_selection_eb": ("P", "EB_P_SELECT", "eb_position"),
    "switches.p.emg_led_p":          ("P", "EMG_LED_P", "flexible_pair"),
    "switches.p.led_emergency_port": ("P", "EMG_LED_P", "flexible_pair"),
    "switches.p.co2_scrubber_p":     ("P", "SCRUBBER_CO2_P", "flexible_pair"),
    # Frontend alias quirk: the actual EMG_LED_P / INT_LED_P / CO2_P toggle
    # switches shown on the Switches_S page write to switches.s.*_p, not
    # switches.p.*_p (see models.py "Frontend aliases" section). Map those
    # real, live field paths too -- side is still P, the physical Port
    # light -- or these toggles never get classified/advance the SOP.
    "switches.s.emg_led_p":          ("P", "EMG_LED_P", "flexible_pair"),
    "switches.s.int_led_p":          ("P", "INT_LED_P", "aux_seq_late"),
    "switches.s.co2_p":              ("P", "SCRUBBER_CO2_P", "flexible_pair"),

    # Port Utility Bus Selection & Aux Battery
    "switches.p.ab_p":               ("P", "UB_P_SELECT", "ub_position"),
    "switches.p.power_selection_ub": ("P", "UB_P_SELECT", "ub_position"),
    "switches.p.ab_p_bms":           ("P", "AB_P_BMS", "aux_seq"),
    "switches.p.ab_p_power":         ("P", "AB_P_POWER", "aux_seq"),
    "switches.p.ab_p_power_selection": ("P", "AB_P_POWER", "aux_seq"),
    "switches.p.ub_p_mcb":           ("P", "UB_P_MCB", "aux_seq"),
    "switches.p.ub_mcb":             ("P", "UB_P_MCB", "aux_seq"),
    "switches.p.ub_p_mcb2":          ("P", "UB_P_MCB", "aux_seq"),
    "switches.p.int_led_p":          ("P", "INT_LED_P", "aux_seq_late"),
    "switches.p.wago_p":             ("P", "WAGO_P", "aux_seq"),

    # Port PDE / IDE  (SOP steps 37-46)
    "switches.p.mb_p_bms":           ("P", "MB_P_BMS", "mb_bms"),
    "switches.p.oim_p":              ("P", "PDE_P_OIM", "pde_oim"),
    "switches.p.pde_p_olr":          ("P", "PDE_P_OLR", "pde_olr"),
    "switches.p.pde_p_148":          ("P", "PDE_P_148", "pde_148"),
    "switches.p.mb_p_1":             ("P", "MB_P_1", "mb_packs"),
    "switches.p.mb_p_2":             ("P", "MB_P_2", "mb_packs"),
    "switches.p.mb_p_3":             ("P", "MB_P_3", "mb_packs"),
    "switches.p.mb_p_4":             ("P", "MB_P_4", "mb_packs"),
    "switches.p.mb_p_5":             ("P", "MB_P_5", "mb_packs"),
    # NOTE: the port panel's actual MB_P1_EN..MB_P5_EN switches are wired
    # to switches.p.mb_1..mb_5 (see SwitchesLayout.jsx), NOT to the
    # mb_p_1..mb_p_5 fields above -- those exist in models.py but nothing
    # in the UI ever sets them, so the mappings above never fire. Map the
    # real, live field paths here so the SOP actually advances.
    "switches.p.mb_1":               ("P", "MB_P_1", "mb_packs"),
    "switches.p.mb_2":               ("P", "MB_P_2", "mb_packs"),
    "switches.p.mb_3":               ("P", "MB_P_3", "mb_packs"),
    "switches.p.mb_4":               ("P", "MB_P_4", "mb_packs"),
    "switches.p.mb_5":               ("P", "MB_P_5", "mb_packs"),
    "switches.p.mb_p_pde_p":         ("P", "MB_P-PDE_P", "main_contactor"),
    # SwitchesLayout.jsx actually wires the "Pull UP MB-PDE Main Contactor"
    # toggle to switches.p.pde_p_24v (labelled "SECONDARY/PRIMARY PDE-P 24V
    # CONTROL" on the panel) -- mb_p_pde_p exists in models.py but nothing
    # in the UI ever sets it, so map the real, live field path here.
    "switches.p.pde_p_24v":          ("P", "MB_P-PDE_P", "main_contactor"),
    "switches.p.pde_p_24v_main":     ("P", "24V_Main_P", "conv_24v"),
    "switches.p.ide_p_1":            ("P", "IDE1_P", "ide"),

    # Starboard Emergency Bus Selection & Emergency Switches
    "switches.s.e_batts":            ("S", "EB_S_SELECT", "eb_position"),
    "switches.s.e_batt_s":           ("S", "EB_S_SELECT", "eb_position"),
    "switches.s.power_selection_eb": ("S", "EB_S_SELECT", "eb_position"),
    "switches.s.emg_led_s":          ("S", "EMG_LED_S", "flexible_pair"),
    "switches.s.co2_scrubber_s":     ("S", "SCRUBBER_CO2_S", "flexible_pair"),
    "switches.s.co2_s":              ("S", "SCRUBBER_CO2_S", "flexible_pair"),

    # Starboard Utility Bus Selection & Aux Battery
    "switches.s.ab_s":               ("S", "UB_S_SELECT", "ub_position"),
    "switches.s.ub_s":               ("S", "UB_S_SELECT", "ub_position"),
    "switches.s.power_selection_ub": ("S", "UB_S_SELECT", "ub_position"),
    "switches.s.ab_s_bms":           ("S", "AB_S_BMS", "aux_seq"),
    "switches.s.ab_s_power":         ("S", "AB_S_POWER", "aux_seq"),
    "switches.s.ab_s_power_selection": ("S", "AB_S_POWER", "aux_seq"),
    "switches.s.ub_s_mcb":           ("S", "UB_S_MCB", "aux_seq"),
    "switches.s.ub_mcb":             ("S", "UB_S_MCB", "aux_seq"),
    "switches.s.ub_s_mcb2":          ("S", "UB_S_MCB", "aux_seq"),
    "switches.s.int_led_s":          ("S", "INT_LED_S", "aux_seq_late"),
    "switches.s.wago":               ("S", "WAGO_S", "aux_seq"),

    # Starboard PDE / IDE  (SOP steps 47-56)
    "switches.s.mb_s_bms":           ("S", "MB_S_BMS", "mb_bms"),
    "switches.s.pde_s_oim":          ("S", "PDE_S_OIM", "pde_oim"),
    "switches.s.oim":                ("S", "PDE_S_OIM", "pde_oim"),
    "switches.s.pde_s_olr":          ("S", "PDE_S_OLR", "pde_olr"),
    "switches.s.pde_s_148":          ("S", "PDE_S_148", "pde_148"),
    "switches.s.mb_s_1":             ("S", "MB_S_1", "mb_packs"),
    "switches.s.mb_s_2":             ("S", "MB_S_2", "mb_packs"),
    "switches.s.mb_s_3":             ("S", "MB_S_3", "mb_packs"),
    "switches.s.mb_s_4":             ("S", "MB_S_4", "mb_packs"),
    "switches.s.mb_s_5":             ("S", "MB_S_5", "mb_packs"),
    "switches.s.mb_s_pde_s":         ("S", "MB_S-PDE_S", "main_contactor"),
    "switches.s.main_24_s":          ("S", "24V_Main_S", "conv_24v"),
    "switches.s.ide_s_1":            ("S", "IDE1_S", "ide"),
}

# ── PDE/IDE group vs. "early" (EB/UB/EMCS) group ───────────────────────────
# The early group (EB position -> ... -> EB/UB changeover) must be done
# fully on one side before the other side may start it (SOP steps 2-33,
# PORT first, then STARBOARD).
#
# The PDE/Battery/IDE group (SOP steps 37-46 for P, 47-56 for S) only opens
# up once BOTH sides have finished their early group. Per the SOP document
# this group is ALSO strictly side-locked, PORT first: STARBOARD's
# PDE/Battery/IDE work (steps 47-56) may not begin until PORT's (steps
# 37-46) is fully complete. Imaging (steps 63+) remains gated on BOTH sides
# finishing their PDE/Battery/IDE work.
PDE_PHASES = {"mb_bms", "pde_oim", "pde_olr", "pde_148", "mb_packs", "main_contactor", "conv_24v", "ide"}

STEP_ORDER = [
    ("eb_pos",             "Set EB Power Selector to EM position"),
    ("first_actions",      "Turn ON EMG_LED and run Scrubber/CO2 check"),
    ("ub_pos",             "Set Utility Bus Selector to AB position"),
    ("aux_seq:ab_bms",     "Turn ON Auxiliary Battery BMS"),
    ("aux_seq:ab",         "Turn ON Auxiliary Battery Power"),
    ("aux_seq:ub_mcb",     "Turn ON Utility Bus MCB in PDPP"),
    ("aux_seq_late",       "Turn ON Internal Light INT_LED"),
    ("eb_ub_changeover",   "Change EB selector from EB position back to UB position"),
    ("mb_bms",             "Turn ON MB_BMS for Main Battery BMS"),
    ("pde_oim",            "Turn ON PDE OIM (then verify 148V insulation IR manually, no auto GO/NO-GO gate)"),
    ("pde_olr",            "Turn ON PDE OLR"),
    ("mb_packs",           "Sequentially power up Main Battery packs 1-5"),
    ("main_contactor",     "Pull UP MB-PDE Main Contactor (148V bus)"),
    ("conv_24v",           "Turn ON 24V_Main Converter"),
    ("ide",                "Turn ON IDE1"),
]

# Steps that belong to the side-locked "early" (EB/UB/EMCS) group -- i.e.
# everything in STEP_ORDER that is not part of the flexible PDE/IDE group.
EARLY_STEP_ORDER = [(k, l) for k, l in STEP_ORDER if k not in (
    "mb_bms", "pde_oim", "pde_olr", "mb_packs", "main_contactor", "conv_24v", "ide",
)]


def _now():
    return datetime.datetime.now().strftime("%H:%M:%S")


def _inject_eb_readings(app_state, side):
    pw = app_state.power
    battery = pw.aux_p if side == "P" else pw.aux_s
    sw = getattr(app_state.switches, side.lower())

    if getattr(sw, "eb_b_status", 0.0) == 0.0 or battery.voltage.value == 0.0:
        voltage = round(random.uniform(25.5, 26.8), 2)
        soc = round(random.uniform(92.0, 98.0), 1)
        insulation = round(random.uniform(1.8, 2.5), 2)

        battery.voltage.value = voltage
        battery.soc.value = soc
        setattr(sw, "eb_b_status", voltage)
        setattr(sw, "ib_insulation", insulation)


def _clear_eb_readings(app_state, side):
    pw = app_state.power
    battery = pw.aux_p if side == "P" else pw.aux_s
    sw = getattr(app_state.switches, side.lower())

    battery.voltage.value = 0.0
    battery.soc.value = 0.0
    setattr(sw, "eb_b_status", 0.0)
    setattr(sw, "ib_insulation", 0.0)


def _inject_ub_reading(app_state, side):
    pw = app_state.power
    ub = pw.ub_port if side == "P" else pw.ub_stbd
    sw = getattr(app_state.switches, side.lower())

    if getattr(sw, "ub_voltage", 0.0) == 0.0 or ub.voltage.value == 0.0:
        voltage = round(random.uniform(23.8, 24.5), 2)
        ir = round(random.uniform(1.7, 2.3), 2)

        ub.voltage.value = voltage
        ub.ir.value = ir
        setattr(sw, "ub_voltage", voltage)


def _clear_ub_readings(app_state, side):
    pw = app_state.power
    ub = pw.ub_port if side == "P" else pw.ub_stbd
    sw = getattr(app_state.switches, side.lower())

    ub.voltage.value = 0.0
    ub.ir.value = 0.0
    setattr(sw, "ub_voltage", 0.0)


def _get_measured(app_state, side):
    pw = app_state.power
    battery = pw.aux_p if side == "P" else pw.aux_s
    mb = pw.mb_p if side == "P" else pw.mb_s
    enclosure = pw.pde_p if side == "P" else pw.pde_s
    return {
        "voltage": battery.voltage.value,
        "soc": battery.soc.value,
        "temperature": mb.temp.value,
        "ir": enclosure.ir.value,
    }


def _emit(app_state, side, switch, field_path, prev, new, expected, action_type, warning, go_no_go="", alarm_status="NONE"):
    global _event_seq
    m = _get_measured(app_state, side)
    from models import EventLogEntry
    _event_seq += 1
    entry = EventLogEntry(
        timestamp=_now(),
        side={"P": "PORT", "S": "STARBOARD"}.get(side, "GLOBAL"),
        switch=switch,
        field_path=field_path,
        previous_state=str(prev),
        new_state=str(new),
        expected_action=expected,
        action_type=action_type,
        warning=warning,
        go_no_go=go_no_go,
        measured_voltage=m["voltage"],
        measured_soc=m["soc"],
        measured_temperature=m["temperature"],
        measured_ir=m["ir"],
        alarm_status=alarm_status,
        seq=_event_seq,
    )

    sc = app_state.scenario
    sc.event_log.append(entry)
    sc.event_log[:] = sc.event_log[-100:]
    sc.last_action_type = action_type
    sc.last_warning = warning
    if go_no_go:
        sc.last_go_no_go = go_no_go

    sc.last_result = f"{switch}: {warning}" if warning else f"{switch}: ACCEPTED."
    # NOTE: feedback_msg is intentionally left untouched here — it holds the
    # current "next step" instruction (or a phase/handover message) and is
    # rendered in its own banner box alongside last_result. Overwriting it
    # with the same text as last_result caused every toggle to be announced
    # twice (once as "next step" / feedback_msg, once as "Last action").
    return entry


def _is_side_complete(app_state, side) -> bool:
    """True once every STEP_ORDER check for `side` is satisfied."""
    return compute_next_step(app_state, side).endswith("All power-up steps complete.")


def _maybe_auto_advance_side(app_state):
    """
    Once the active side finishes its EARLY (EB/UB/EMCS, steps 2-17 / 18-33)
    sequence, release the session lock and hand control to the other side
    automatically (if that side hasn't already finished its early sequence
    too). This lets the operator move straight from PORT's early sequence
    into STARBOARD's, with no manual "unlock" step required.

    Once BOTH sides have cleared the early gate, this also drives the
    PORT-then-STARBOARD handover for the PDE/Battery/IDE group (SOP steps
    37-46 then 47-56): PORT becomes (or stays) active until its
    PDE/Battery/IDE work is fully complete, then control is handed to
    STARBOARD. The actual gating that blocks out-of-order toggles lives in
    evaluate_action (checked directly against side completion so there's no
    one-toggle lag); this function only keeps `_active_side` -- and the
    banner's "Active Side / Next Step" display and feedback message -- in
    sync with that same PORT-first rule.
    """
    global _active_side
    if _active_side == "":
        return

    other_side = "S" if _active_side == "P" else "P"

    if _is_early_complete(app_state, _active_side) and not _is_early_complete(app_state, other_side):
        completed = "PORT" if _active_side == "P" else "STARBOARD"
        upcoming = "STARBOARD" if other_side == "S" else "PORT"
        _active_side = other_side
        app_state.scenario.feedback_msg = (
            f"{completed} side early (EB/UB/EMCS) sequence complete. "
            f"Control automatically handed to {upcoming} side — proceed with the same steps. "
            f"PDE/Battery power-up will unlock, PORT first, once {upcoming} finishes its early sequence too."
        )
        return

    both_early_done = _is_early_complete(app_state, "P") and _is_early_complete(app_state, "S")
    if not both_early_done:
        return

    if not _is_side_complete(app_state, "P"):
        if _active_side != "P":
            _active_side = "P"
            app_state.scenario.feedback_msg = (
                "PORT and STARBOARD early (EB/UB/EMCS) sequence complete. "
                "Proceed with PORT Main Battery/PDE/IDE power-up (SOP steps 37-46)."
            )
    elif not _is_side_complete(app_state, "S"):
        if _active_side != "S":
            _active_side = "S"
            app_state.scenario.feedback_msg = (
                "PORT Main Battery/PDE/IDE power-up complete (SOP steps 37-46). "
                "Control handed to STARBOARD — proceed with Main Battery/PDE/IDE sequence (steps 47-56)."
            )


def evaluate_action(app_state, switch_path: str, previous_value, new_value):
    mapping = FIELD_MAP.get(switch_path)
    if mapping is None:
        return None

    side, name, phase = mapping
    sw = getattr(app_state.switches, side.lower())
    sc = app_state.scenario

    both_ide_complete = _is_side_complete(app_state, "P") and _is_side_complete(app_state, "S")

    # Once both sides have finished their Main Battery/PDE/IDE sequence
    # (SOP steps 37-56), any further EB/UB selector toggles belong to the
    # final phase (SOP steps 59-60: EB revert, then UB AB->MB changeover)
    # rather than the initial power-up gating above.
    if both_ide_complete and phase in ("eb_position", "ub_position"):
        return _classify_final_phase(app_state, side, name, phase, switch_path, previous_value, new_value, sw)

    turning_on = bool(new_value) and not bool(previous_value)
    if not turning_on:
        # SOP Step 14/30: after the aux battery sequence is done, the EB
        # selector is switched back from EB position to UB position
        # (e_batts True -> False). Track that explicitly so it shows up
        # as its own completed step rather than a generic "OFF" toggle.
        if name in ("EB_P_SELECT", "EB_S_SELECT") and bool(previous_value) and not bool(new_value):
            _sequence_state[side]["eb_ub_changeover_done"] = True
            return _emit(app_state, side, name, switch_path, previous_value, new_value,
                         expected="Change EB selector from EB to UB position",
                         action_type="CORRECT",
                         warning="Emergency Bus changed over to Utility Bus.")

        # ── MEDIUM SCENARIO recovery: MB_S_3 turned back OFF to isolate
        #    an active insulation fault (see _classify's "mb_packs" branch).
        if name == "MB_S_3" and _fault_state["medium_active"]:
            _fault_state["medium_active"] = False
            app_state.power.pde_s.ir.value = round(random.uniform(1.9, 2.3), 2)
            sc.alarm_active = False
            sc.fault_type = ""
            sc.clear_message = (
                "Insulation fault isolated. IR recovered to healthy range on Starboard Main Battery pack 3. "
                "Co-Pilot confirms Starboard Life Support (HSSS-S) oxygen, C O2, and humidity held stable "
                "throughout. Resume MB_S_3 power-up when ready."
            )
            return _emit(app_state, side, name, switch_path, previous_value, new_value,
                         expected="Isolate MB_S_3 and confirm IR recovery >= 1.5 M Ohm",
                         action_type="CORRECT", warning=sc.clear_message, alarm_status="CLEARED")

        return _emit(app_state, side, name, switch_path, previous_value, new_value,
                     expected=name, action_type="CORRECT", warning="")

    global _active_side

    if phase in PDE_PHASES:
        # PDE/Battery/IDE group (SOP steps 37-46 for P, 47-56 for S) is
        # gated on BOTH sides having finished their early EB/UB/EMCS
        # sequence first.
        if not (_is_early_complete(app_state, "P") and _is_early_complete(app_state, "S")):
            warning = "Complete the EB/UB power-up sequence on BOTH Port and Starboard before starting PDE/Battery power-up."
            return _emit(app_state, side, name, switch_path, previous_value, new_value,
                         expected="Finish early power-up sequence on both sides first",
                         action_type="OUT_OF_ORDER", warning=warning)

        # Per the SOP document this group is strictly PORT-then-STARBOARD
        # (steps 37-46 before 47-56) -- unlike the early group, the two
        # sides are NOT interleaved freely here. Checked directly against
        # PORT's completion (rather than via the `_active_side` lock) so
        # there's no one-toggle lag between this check and the state that
        # was just written to app_state.switches by the caller.
        if side == "S" and not _is_side_complete(app_state, "P"):
            warning = "Complete PORT Main Battery/PDE/IDE power-up (SOP steps 37-46) before starting STARBOARD."
            return _emit(app_state, side, name, switch_path, previous_value, new_value,
                         expected="Finish PORT Main Battery/PDE/IDE sequence first",
                         action_type="OUT_OF_ORDER", warning=warning)

        _active_side = "S" if _is_side_complete(app_state, "P") else "P"
        return _classify(app_state, side, name, phase, switch_path, previous_value, new_value, sw)

    # NOTE: auto-advance is handled in recompute_derived_flags (called right
    # after this function on every toggle), not here. Doing it here would
    # read the switch that's *currently being classified* as already flipped
    # (its new value is applied before evaluate_action runs), which would
    # make a side look "complete" one action early and misclassify the very
    # action that completes it as OUT_OF_ORDER.

    if _active_side == "":
        _active_side = side
    elif _active_side != side:
        other = "PORT" if side == "S" else "STARBOARD"
        warning = f"Operation on {side} while {other} side power-up is active."
        return _emit(app_state, side, name, switch_path, previous_value, new_value,
                     expected=f"Finish {other} side active power-up first",
                     action_type="OUT_OF_ORDER", warning=warning)

    return _classify(app_state, side, name, phase, switch_path, previous_value, new_value, sw)


def _classify(app_state, side, name, phase, switch_path, previous_value, new_value, sw):
    seq = _sequence_state[side]

    if phase == "eb_position":
        seq["eb_pos_confirmed"] = True
        return _emit(app_state, side, name, switch_path, previous_value, new_value,
                     expected="Set EB power selection to EM position",
                     action_type="CORRECT", warning="")

    if phase == "flexible_pair":
        if name.startswith("EMG_LED"):
            seq["emg_led_on"] = True
        else:
            seq["scrubber_done"] = True

        _inject_eb_readings(app_state, side)
        return _emit(app_state, side, name, switch_path, previous_value, new_value,
                     expected="Interchangeable step P-03A / P-03B",
                     action_type="FLEXIBLE_ORDER", warning="")

    if phase == "ub_position":
        seq["ub_pos_confirmed"] = True
        return _emit(app_state, side, name, switch_path, previous_value, new_value,
                     expected="Set UB power selection to AB position",
                     action_type="CORRECT", warning="")

    if phase == "aux_seq" or phase == "aux_seq_late":
        # SOP rule: ONLY EMG_LED and the CO2 Scrubber (flexible_pair, above)
        # are allowed to run while still in E_BATTS position. Everything
        # else in this group — AB_BMS, AB_POWER, UB_MCB, and INT_LED — must
        # wait until the UB position selector has been switched over.
        # Warn (don't block) if the operator jumps ahead; the operator is
        # expected to set the position switch and continue.
        # NOTE: the warning text deliberately does NOT restate the switch
        # name/code — the voice-over layer already announces which switch
        # was toggled, so repeating it here caused every warning to be
        # spoken twice (once as the switch name, once embedded in the
        # message text).
        position_warning = ""
        if not seq.get("ub_pos_confirmed", False):
            position_warning = "Please change to UB position first — this can lead to battery drain if skipped."

        if phase == "aux_seq":
            if name.endswith("BMS"):
                seq["ab_bms_on"] = True
            elif "POWER" in name or name in ("AB_P", "AB_S"):
                seq["ab_power_on"] = True
            elif "MCB" in name:
                seq["ub_mcb_on"] = True
            expected = "Auxiliary battery power sequence"
        else:
            expected = "Turn ON Internal Light, then power Pilot PC & WAGO PC"

        if position_warning:
            return _emit(app_state, side, name, switch_path, previous_value, new_value,
                         expected=expected, action_type="WARNING", warning=position_warning)

        if phase == "aux_seq_late":
            # Correct-order reminder: no code names, just the next action.
            reminder = "Next, power ON the Pilot PC and the WAGO PC."
            return _emit(app_state, side, name, switch_path, previous_value, new_value,
                         expected=expected, action_type="CORRECT", warning=reminder)

        return _emit(app_state, side, name, switch_path, previous_value, new_value,
                     expected=expected, action_type="CORRECT", warning="")

    # ── Enforce SOP Step 41/51: battery packs MUST be closed strictly in
    #    order (pack N only after pack N-1 is already ON). This is what
    #    keeps the training scenario from "jumping straight to the alarm"
    #    -- MB_S_3 (and the fault check below) is only reachable once
    #    MB_S_1 and MB_S_2 have genuinely been switched on first, exactly
    #    as the SOP requires ("Sequentially power up the five battery
    #    packs").
    if phase == "mb_packs":
        pack_num = int(name.rsplit("_", 1)[-1])
        field_prefix = "mb" if side == "P" else "mb_s"
        for i in range(1, pack_num):
            prev_field = f"{field_prefix}_{i}"
            if not getattr(sw, prev_field, False):
                prev_name = f"MB_{side}_{i}" if side == "S" else f"MB_P_{i}"
                warning = f"Power up battery packs sequentially — {prev_name} must be closed before {name}."
                return _emit(app_state, side, name, switch_path, previous_value, new_value,
                             expected=f"Close {prev_name} before {name}",
                             action_type="OUT_OF_ORDER", warning=warning)

    # ── MEDIUM SCENARIO: Insulation Fault During Sequential MB_S Power-Up ──
    # Fires exactly once, the first time MB_S_3 is energized AFTER MB_S_1
    # and MB_S_2 are confirmed ON (enforced above): IR on the Starboard
    # 148V enclosure drops from a healthy ~2.0 M Ohm to ~1.2 M Ohm (below
    # the 1.5 M Ohm GO/NO-GO limit). Recovery is handled above, in
    # evaluate_action's "not turning_on" branch, when the operator isolates
    # the pack by turning MB_S_3 back OFF.
    if phase == "mb_packs" and side == "S" and name == "MB_S_3" and not _fault_state["medium_triggered"]:
        _fault_state["medium_triggered"] = True
        _fault_state["medium_active"] = True
        app_state.power.pde_s.ir.value = round(random.uniform(1.1, 1.3), 2)
        app_state.scenario.alarm_active = True
        app_state.scenario.fault_type = "IR_FAULT_MB_S3"
        app_state.scenario.alarm_message = (
            f"NO-GO: Insulation Resistance dropped to {app_state.power.pde_s.ir.value} M Ohm on MB_S_3 "
            "(limit >= 1.5 M Ohm). Turn MB_S_3 OFF to isolate the fault and confirm IR recovers before "
            "continuing to MB_S_4. Co-Pilot: verify Starboard Life Support (HSSS-S) O2/C O2/Humidity "
            "remain stable despite the anomaly."
        )
        return _emit(app_state, side, name, switch_path, previous_value, new_value,
                     expected="Power up MB_S_3", action_type="NO_GO",
                     warning=app_state.scenario.alarm_message, go_no_go="NO_GO", alarm_status="ALARM")

    if phase == "mb_packs":
        return _emit(app_state, side, name, switch_path, previous_value, new_value,
                     expected=f"Power up {name}", action_type="CORRECT", warning="")

    return _emit(app_state, side, name, switch_path, previous_value, new_value,
                 expected="SOP Step", action_type="CORRECT", warning="")


def _classify_final_phase(app_state, side, name, phase, switch_path, previous_value, new_value, sw):
    """
    Handles SOP Steps 59-60, reached only once BOTH sides have finished
    their Main Battery/PDE/IDE sequence (steps 37-56):
      Step 59: EB selector reverted back to EB position (both sides)
      Step 60: UB selector changed over from AB to Main Battery -- MB
               (both sides). HARD SCENARIO: Port's changeover triggers a
               Main Power Contactor failure / blackout the first time it's
               attempted.
    This is where the "till Main Battery" scenario ends: no Imaging/
    Sensors/Comms/Ballast/Propulsion phases follow.
    """
    sc = app_state.scenario
    seq = _sequence_state[side]
    turning_on = bool(new_value) and not bool(previous_value)
    turning_off = bool(previous_value) and not bool(new_value)

    # ── Step 59: EB selector back to EB position ──
    if phase == "eb_position":
        if turning_on:
            seq["eb_reverted"] = True
            both = _sequence_state["P"]["eb_reverted"] and _sequence_state["S"]["eb_reverted"]
            warning = ("EB selector confirmed back in EB position." if not both else
                       "Emergency Bus selectors reverted on both sides (SOP Step 59). "
                       "Proceed to the Utility Bus AB -> Main Battery changeover (SOP Step 60).")
            return _emit(app_state, side, name, switch_path, previous_value, new_value,
                         expected="Revert EB selector to EB position (SOP Step 59)",
                         action_type="CORRECT", warning=warning)
        return _emit(app_state, side, name, switch_path, previous_value, new_value,
                     expected="EB selector", action_type="CORRECT", warning="")

    # ── Step 60: UB selector AB -> Main Battery (MB) changeover ──
    if phase == "ub_position":
        eb_ready = _sequence_state["P"]["eb_reverted"] and _sequence_state["S"]["eb_reverted"]
        if not eb_ready:
            warning = "Complete Step 59 (EB selectors back to EB, both sides) before the UB AB -> MB changeover."
            return _emit(app_state, side, name, switch_path, previous_value, new_value,
                         expected="Revert EB selectors to EB position on both sides first",
                         action_type="OUT_OF_ORDER", warning=warning)

        going_to_mb = turning_off   # AB (True) -> MB (False)
        going_to_ab = turning_on    # MB (False) -> AB (True): recovery / retry path

        if side == "P":
            # ── HARD SCENARIO: Bus Changeover Failure & System Blackout ──
            if going_to_mb:
                if not _fault_state["hard_triggered"]:
                    _fault_state["hard_triggered"] = True
                    _fault_state["hard_active_p"] = True
                    seq["ub_mb_changeover_done"] = False
                    sc.alarm_active = True
                    sc.fault_type = "BLACKOUT_UB_P"
                    sc.alarm_message = (
                        "NO-GO: Port Main Power Contactor failed during the UB_P changeover. Utility Bus PORT "
                        "has lost all power -- Internal Lights, Pilot Panel PC, and HSSS-HMI-P are DOWN. "
                        "Move the UB_P selector back to AB to restore emergency power, then retry the "
                        "changeover to Main Battery."
                    )
                    return _emit(app_state, side, name, switch_path, previous_value, new_value,
                                 expected="UB_P selector AB -> MB changeover",
                                 action_type="NO_GO", warning=sc.alarm_message,
                                 go_no_go="NO_GO", alarm_status="ALARM")
                seq["ub_mb_changeover_done"] = True
                return _emit(app_state, side, name, switch_path, previous_value, new_value,
                             expected="UB_P selector AB -> MB changeover",
                             action_type="CORRECT",
                             warning="Uninterrupted power shift to Main Battery Port confirmed. Contactor holding.")

            if going_to_ab and _fault_state["hard_active_p"]:
                _fault_state["hard_active_p"] = False
                sc.alarm_active = False
                sc.fault_type = ""
                sc.clear_message = (
                    "Port emergency power restored via the AB position. Internal Lights and the Pilot Panel PC "
                    "are back online, and Starboard HSSS confirms cabin atmosphere held steady throughout. "
                    "Retry the UB_P changeover to Main Battery when ready."
                )
                return _emit(app_state, side, name, switch_path, previous_value, new_value,
                             expected="Revert UB_P selector to AB position (emergency recovery)",
                             action_type="CORRECT", warning=sc.clear_message, alarm_status="CLEARED")

            return _emit(app_state, side, name, switch_path, previous_value, new_value,
                         expected="UB_P selector", action_type="CORRECT", warning="")

        # side == "S" -- clean changeover, no fault modeled here
        if going_to_mb:
            seq["ub_mb_changeover_done"] = True
            return _emit(app_state, side, name, switch_path, previous_value, new_value,
                         expected="UB_S selector AB -> MB changeover",
                         action_type="CORRECT",
                         warning="Uninterrupted power shift to Main Battery Starboard confirmed.")
        return _emit(app_state, side, name, switch_path, previous_value, new_value,
                     expected="UB_S selector", action_type="CORRECT", warning="")

    return _emit(app_state, side, name, switch_path, previous_value, new_value,
                 expected="Final phase step", action_type="CORRECT", warning="")


def compute_next_step(app_state, side):
    sw = getattr(app_state.switches, side.lower())
    # The EMG_LED_P / INT_LED_P / CO2_P toggle switches physically shown on
    # the Switches_S page write to switches.s.*_p (frontend alias quirk --
    # see FIELD_MAP above), so Port's "first_actions"/"aux_seq_late" checks
    # need to read from switches.s, not switches.p.
    sw_s = app_state.switches.s
    p = side.lower()
    seq = _sequence_state[side]

    checks = {
        # Stateful (not a live switch read): once EB_P_SELECT/EB_S_SELECT has
        # been confirmed ON at least once, this stays satisfied even after
        # the later EB->UB changeover step (Step 14/30) flips it back off.
        "eb_pos": lambda: bool(seq.get("eb_pos_confirmed", False)),
        "first_actions": lambda: bool(
            getattr(sw, f"emg_led_{p}", False) or getattr(sw, "led_emergency_port" if side == "P" else "emg_led_s", False)
            or (side == "P" and getattr(sw_s, "emg_led_p", False))
        ) or bool(
            getattr(sw, f"co2_scrubber_{p}", False) or getattr(sw, "co2_s" if side == "S" else "co2_scrubber_p", False)
            or (side == "P" and getattr(sw_s, "co2_p", False))
        ),
        "ub_pos": lambda: bool(getattr(sw, f"ab_{p}", False) or getattr(sw, "ub_s" if side == "S" else "ab_p", False)),
        "aux_seq:ab_bms": lambda: bool(getattr(sw, f"ab_{p}_bms", False)),
        "aux_seq:ab": lambda: bool(getattr(sw, f"ab_{p}_power", False) or getattr(sw, f"ab_{p}_power_selection", False)),
        "aux_seq:ub_mcb": lambda: bool(getattr(sw, f"ub_{p}_mcb", False) or getattr(sw, "ub_mcb", False)),
        "aux_seq_late": lambda: bool(getattr(sw, f"int_led_{p}", False) or (side == "P" and getattr(sw_s, "int_led_p", False))),
        "eb_ub_changeover": lambda: bool(seq.get("eb_ub_changeover_done", False)),
        "mb_bms": lambda: bool(getattr(sw, "mb_p_bms" if side == "P" else "mb_s_bms", False)),
        "pde_oim": lambda: bool(getattr(sw, "oim_p" if side == "P" else "pde_s_oim", False) or getattr(sw, "oim", False)),
        "pde_olr": lambda: bool(getattr(sw, f"pde_{p}_olr", False)),
        "pde_148": lambda: bool(getattr(sw, f"pde_{p}_148", False) or getattr(sw, "mb_s_pde_s" if side == "S" else "pde_p_148", False)),
        "mb_packs": lambda: bool(
            getattr(sw, "mb_1", False) and getattr(sw, "mb_2", False) and
            getattr(sw, "mb_3", False) and getattr(sw, "mb_4", False) and
            getattr(sw, "mb_5", False)
        ) if side == "P" else bool(
            getattr(sw, "mb_s_1", False) and getattr(sw, "mb_s_2", False) and
            getattr(sw, "mb_s_3", False) and getattr(sw, "mb_s_4", False) and
            getattr(sw, "mb_s_5", False)
        ),
        "main_contactor": lambda: bool(getattr(sw, "mb_p_pde_p" if side == "P" else "mb_s_pde_s", False) or (side == "P" and getattr(sw, "pde_p_24v", False))),
        "conv_24v": lambda: bool(getattr(sw, "pde_p_24v_main" if side == "P" else "main_24_s", False)),
        "ide": lambda: bool(getattr(sw, "ide_p_1" if side == "P" else "ide_s_1", False) or getattr(sw, "ide_2", False)),
    }

    for key, label in STEP_ORDER:
        check_fn = checks.get(key)
        if check_fn and not check_fn():
            return f"[{side}] {label}"

    return f"[{side}] All power-up steps complete."


def _is_early_complete(app_state, side) -> bool:
    """
    True once the side-locked "early" group (EB position through the
    EB->UB changeover, SOP steps 2-33) is finished for `side`. This is the
    gate that must pass on BOTH sides before either side's PDE/Battery/IDE
    group (steps 37+) is allowed to proceed in flexible order.
    """
    next_step = compute_next_step(app_state, side)
    early_labels = {f"[{side}] {label}" for _, label in EARLY_STEP_ORDER}
    return next_step not in early_labels


# ── Post Power-Up Phases (both sides complete) ─────────────────────────────
# Runs, in SOP document order, once BOTH Port and Starboard power-up
# sequences finish (SOP steps 63-108):
#   1) IMAGING     (steps 63-83: fiber mux/VHS, HD/SD cameras, LED lights, sonar)
#   2) SENSORS     (steps 84-92: CTD, DO, DVL, Altimeter)
#   3) COMMS       (steps 93-95: Acoustic modem, VHF, SUAT/UWT)
#   4) MAIN BALLAST (steps 96-100: Dive-In, MBS)
#   5) PROPULSION  (steps 101-108: 148VDC contactor, thruster enable/power, joystick)
# Each phase only starts once the previous one is complete.

IMAGING_STEP_ORDER = [
    ("vhs_p",  "Turn ON toggle switch VHS_Pow_P for Port video recorder power"),
    ("vhs_s",  "Turn ON toggle switch VHS_Pow_S for Starboard video recorder power"),
    ("cam_p",  "Turn ON HD Camera Port (HD CAM1_P) in imaging page GUI"),
    ("sdi_p3", "Turn ON SD Camera P3 (landing) in imaging page GUI"),
    ("sdi_p4", "Turn ON SD Camera P4 (fixed) in imaging page GUI"),
    ("cam_s",  "Turn ON HD Camera Starboard (HD CAM1_S) in imaging page GUI"),
    ("sdi_s2", "Turn ON SD Camera S3 (landing) in imaging page GUI"),
    ("sdi_s3", "Turn ON SD Camera S4 (fixed) in imaging page GUI"),
    ("led_p2", "Turn ON soft control LED Light P2 in imaging page GUI"),
    ("led_p3", "Turn ON soft control LED Light P3 in imaging page GUI"),
    ("led_p1", "Turn ON toggle switch LED Light P1 (UW_CAM_P) in general switches"),
    ("led_s2", "Turn ON soft control LED Light S2 in imaging page GUI"),
    ("led_s3", "Turn ON soft control LED Light S3 in imaging page GUI"),
    ("led_s1", "Turn ON toggle switch LED Light S1 (UW_CAM_S) in general switches"),
    ("sonar",  "Switch ON Obstacle Avoidance Sonar in imaging page GUI"),
]

SENSORS_STEP_ORDER = [
    ("ctd_p",         "Turn ON soft control CTD_P in Sensor page GUI"),
    ("do_s",          "Turn ON soft control DO_S (Dissolved Oxygen) in Sensor page GUI"),
    ("ins",           "Turn ON soft control INS in Sensor page GUI (Port side) for powering the Surface INS"),
    ("depth_primary", "Turn ON soft control Depth Sensor Pri in Sensor page GUI (Port side) for powering the Primary depth sensor in IDE_P"),
    ("dvl_p",         "Turn ON soft control DVL_P in Sensor page GUI"),
    ("altimeter_s",   "Turn ON soft control Altimeter_S in Sensor page GUI"),
]

COMMS_STEP_ORDER = [
    ("acoustic_modem", "Turn ON toggle switch APS-2 (Acoustic modem) under SWITCHES_S tab \u2192 General Control Switch"),
    ("vhf",            "Turn ON subsea VHF receiver (VHF PWR_S) under SWITCHES_S tab \u2192 General Control Switch"),
    ("uwt",             "Turn ON shallow water acoustic telephone (UWT PWR_S) under SWITCHES_S tab \u2192 General Control Switch"),
]

BALLAST_STEP_ORDER = [
    ("mbs", "Turn ON soft control button (MBS) in Sensor page GUI (Starboard side) — powers Main Ballast System in IDE_S"),
    ("ready_to_dive", "Turn ON toggle switch DIVE-IN-ON (SW3) — vents six tanks, confirms neutral buoyancy"),
    ("freeboard", "Turn ON toggle switches FREEBOARD_P and FREEBOARD_S (SW3) — blow valves, confirm free board"),
]

PROPULSION_STEP_ORDER = [
    ("main_148vdc", "Verify 148 VDC contactor is ON for Port & Stbd (MB_P-PDE_P / MB_S-PDE_S)"),
    ("thrusters_enable", "Enable the Thruster Enable interlock in Main GUI"),
    ("thrusters_power", "Power & Enable Thrusters (T1) — operate at 60-70 RPM"),
    ("joystick", "Enable the Joystick in the Main GUI"),
]


def compute_imaging_step(app_state) -> str:
    img = app_state.imaging
    sen = app_state.sensors.toggles
    sw_p = app_state.switches.p
    sw_s = app_state.switches.s

    checks = {
        "vhs_p":  lambda: bool(getattr(sw_p, "vhs_power_p", False)),
        "vhs_s":  lambda: bool(getattr(sw_s, "vhs_power_s", False)),
        "cam_p":  lambda: bool(getattr(img, "hd_camera_p", False)),
        "sdi_p3": lambda: bool(getattr(img, "hd_sdi_p3", False)),
        "sdi_p4": lambda: bool(getattr(img, "hd_sdi_p4", False)),
        "cam_s":  lambda: bool(getattr(img, "hd_camera_s", False)),
        "sdi_s2": lambda: bool(getattr(img, "hd_sdi_s2", False)),
        "sdi_s3": lambda: bool(getattr(img, "hd_sdi_s3", False)),
        "led_p2": lambda: bool(getattr(img.led_p2, "power", False)),
        "led_p3": lambda: bool(getattr(img.led_p3, "power", False)),
        "led_p1": lambda: bool(getattr(sw_p, "uw_camera_p", False)),
        "led_s2": lambda: bool(getattr(img.led_s2, "power", False)),
        "led_s3": lambda: bool(getattr(img.led_s3, "power", False)),
        "led_s1": lambda: bool(getattr(sw_s, "uw_camera_s", False)),
        "sonar":  lambda: bool(getattr(sen, "img_sonar", False)),
    }
    for key, label in IMAGING_STEP_ORDER:
        if not checks[key]():
            return f"[IMAGING] {label}"
    return "[IMAGING] All imaging checks complete. Ready to proceed to Sensors."


def compute_sensors_step(app_state) -> str:
    sen = app_state.sensors.toggles

    checks = {
        "ctd_p":         lambda: bool(getattr(sen, "ctdo", False)),
        "do_s":          lambda: bool(getattr(sen, "dissolved_o2", False)),
        "ins":           lambda: bool(getattr(sen, "ins", False)),
        "depth_primary": lambda: bool(getattr(sen, "depth_sensor_pri", False)),
        "dvl_p":         lambda: bool(getattr(sen, "dvl", False)),
        "altimeter_s":   lambda: bool(getattr(sen, "altimeter", False)),
    }
    for key, label in SENSORS_STEP_ORDER:
        if not checks[key]():
            return f"[SENSORS] {label}"
    return "[SENSORS] All scientific/navigation sensors online. Ready to proceed to Comms."


def compute_comms_step(app_state) -> str:
    sw_s = app_state.switches.s

    checks = {
        "acoustic_modem": lambda: bool(getattr(sw_s, "aps_2", False)),
        "vhf":            lambda: bool(getattr(sw_s, "vhf", False)),
        "uwt":            lambda: bool(getattr(sw_s, "uwt", False)),
    }
    for key, label in COMMS_STEP_ORDER:
        if not checks[key]():
            return f"[COMMS] {label}"
    return "[COMMS] Acoustic & voice communication checks complete. Ready to proceed to Main Ballast."


def compute_ballast_step(app_state) -> str:
    sen = app_state.sensors.toggles
    sw3 = app_state.switches.sw3

    checks = {
        "mbs": lambda: bool(getattr(sen, "mbs", False)),
        "ready_to_dive": lambda: bool(getattr(sw3, "dive_in_on", False)),
        "freeboard": lambda: bool(getattr(sw3, "freeboard_p", False) and getattr(sw3, "freeboard_s", False)),
    }
    for key, label in BALLAST_STEP_ORDER:
        if not checks[key]():
            return f"[BALLAST] {label}"
    return "[BALLAST] Main ballast powered. Ready to proceed to Propulsion."


def compute_propulsion_step(app_state) -> str:
    sw_p = app_state.switches.p
    sw_s = app_state.switches.s
    sidebar = app_state.sidebar
    pd = getattr(app_state, "propulsion_detail", None)
    t1 = getattr(pd, "t1", None) if pd else None

    checks = {
        "main_148vdc": lambda: bool((getattr(sw_p, "mb_p_pde_p", False) or getattr(sw_p, "pde_p_24v", False)) and getattr(sw_s, "mb_s_pde_s", False)),
        "thrusters_enable": lambda: bool(getattr(sidebar, "thrusters_enable", False)),
        "thrusters_power": lambda: bool(t1 and getattr(t1, "power", False) and getattr(t1, "enable", False)),
        "joystick": lambda: bool(getattr(sidebar, "joystick", False)),
    }

    for key, label in PROPULSION_STEP_ORDER:
        if not checks[key]():
            return f"[PROPULSION] {label}"

    return "[PROPULSION] All propulsion checks complete. Mission systems fully live."


def _update_post_powerup_phases(app_state):
    """
    Once BOTH Port and Starboard power-up sequences are complete, drive the
    SOP-ordered phases that follow (steps 63-108), gating each on the
    previous one: IMAGING -> SENSORS -> COMMS -> MAIN BALLAST -> PROPULSION.
    """
    sc = app_state.scenario
    both_done = _is_side_complete(app_state, "P") and _is_side_complete(app_state, "S")

    def _clear_from_imaging():
        sc.imaging_active = False
        sc.imaging_complete = False
        sc.next_step_imaging = ""
        _clear_from_sensors()

    def _clear_from_sensors():
        sc.sensors_active = False
        sc.sensors_complete = False
        sc.next_step_sensors = ""
        _clear_from_comms()

    def _clear_from_comms():
        sc.comms_active = False
        sc.comms_complete = False
        sc.next_step_comms = ""
        _clear_from_ballast()

    def _clear_from_ballast():
        sc.ballast_active = False
        sc.ballast_complete = False
        sc.next_step_ballast = ""
        sc.propulsion_active = False
        sc.propulsion_complete = False
        sc.next_step_propulsion = ""

    if not both_done:
        _clear_from_imaging()
        return

    # Phase 1: Imaging (steps 63-83)
    sc.imaging_active = True
    imaging_step = compute_imaging_step(app_state)
    sc.next_step_imaging = imaging_step
    sc.imaging_complete = imaging_step.startswith("[IMAGING] All imaging checks complete")
    if not sc.imaging_complete:
        _clear_from_sensors()
        return

    # Phase 2: Sensors (steps 84-92)
    sc.sensors_active = True
    sensors_step = compute_sensors_step(app_state)
    sc.next_step_sensors = sensors_step
    sc.sensors_complete = sensors_step.startswith("[SENSORS] All scientific/navigation sensors online")
    if not sc.sensors_complete:
        _clear_from_comms()
        return

    # Phase 3: Comms (steps 93-95)
    sc.comms_active = True
    comms_step = compute_comms_step(app_state)
    sc.next_step_comms = comms_step
    sc.comms_complete = comms_step.startswith("[COMMS] Acoustic & voice communication checks complete")
    if not sc.comms_complete:
        _clear_from_ballast()
        return

    # Phase 4: Main Ballast (steps 96-100)
    sc.ballast_active = True
    ballast_step = compute_ballast_step(app_state)
    sc.next_step_ballast = ballast_step
    sc.ballast_complete = ballast_step.startswith("[BALLAST] Main ballast powered")
    if not sc.ballast_complete:
        sc.propulsion_active = False
        sc.propulsion_complete = False
        sc.next_step_propulsion = ""
        return

    # Phase 5: Propulsion (steps 101-108, only after Ballast is complete)
    sc.propulsion_active = True
    prop_step = compute_propulsion_step(app_state)
    sc.next_step_propulsion = prop_step
    sc.propulsion_complete = prop_step.startswith("[PROPULSION] All propulsion checks complete")
    if sc.propulsion_complete:
        sc.feedback_msg = "PORT and STARBOARD power-up, Imaging, Sensors, Comms, and Main Ballast complete. Propulsion checks passed — mission systems fully live."


def refresh_telemetry_displays(app_state):
    """
    Evaluates current switch positions and updates all telemetry display
    meters (EB Status, EB Insulation, UB Voltage) and screen power status.
    Values remain ZERO until the required switches are toggled ON.
    """
    for side in ("P", "S"):
        sw = getattr(app_state.switches, side.lower())
        sw_s = app_state.switches.s
        p = side.lower()

        # 1. Emergency Bus Dials (Active ONLY when EMG_LED or CO2 Scrubber switch
        #    is ON, AND only up until the EB->UB changeover happens). Once the
        #    Emergency Bus selector has been changed over from EB position back
        #    to UB position (SOP step 14/30), the panel meter is physically
        #    reading the Utility Bus, not the Emergency Bus anymore -- so the
        #    EB voltage/insulation dials stop updating and go blank at that
        #    point, regardless of whether EMG_LED/scrubber are still ON.
        emg_led = bool(
            getattr(sw, f"emg_led_{p}", False) or getattr(sw, "led_emergency_port" if side == "P" else "emg_led_s", False)
            or (side == "P" and getattr(sw_s, "emg_led_p", False))
        )
        scrubber = bool(
            getattr(sw, f"co2_scrubber_{p}", False) or getattr(sw, "co2_s" if side == "S" else "co2_scrubber_p", False)
            or (side == "P" and getattr(sw_s, "co2_p", False))
        )
        changed_over = bool(_sequence_state[side].get("eb_ub_changeover_done", False))

        if (emg_led or scrubber) and not changed_over:
            _inject_eb_readings(app_state, side)
        else:
            _clear_eb_readings(app_state, side)

        # 2. Utility Bus Dial (Active ONLY once UB_MCB is switched ON — or WAGO,
        #    which energizes the same bus directly. AB_BMS + AB_POWER alone do
        #    NOT light up the voltage meter; that only happens after UB_MCB.)
        ub_mcb = bool(getattr(sw, f"ub_{p}_mcb", False) or getattr(sw, "ub_mcb", False))
        wago_on = bool(getattr(sw, "wago_p" if side == "P" else "wago", False))

        # HARD SCENARIO: while the Port blackout fault is unresolved, force
        # UB_P readings to zero regardless of switch state -- otherwise this
        # same recompute would immediately re-inject a healthy reading every
        # broadcast and the "blackout" would never actually show.
        if side == "P" and _fault_state["hard_active_p"]:
            _clear_ub_readings(app_state, side)
        elif ub_mcb or wago_on:
            _inject_ub_reading(app_state, side)
        else:
            _clear_ub_readings(app_state, side)

        # 3. EMCS Display Activation: Utility Bus Position active AND Wago switch ON
        ub_sel = bool(getattr(sw, f"ab_{p}", False) or getattr(sw, "ub_s" if side == "S" else "ab_p", False) or (getattr(sw, "power_selection_ub", "0") != "0"))
        emcs_powered = bool(ub_sel and wago_on)
        _sequence_state[side]["emcs_powered"] = emcs_powered

    # Global comm/screen status flag (kept for anything that only cares
    # "is EMCS up at all" across either side), plus per-side flags so the
    # PORT and STARBOARD switch pages only react to their own WAGO/UB
    # selector state instead of lighting up together.
    app_state.sidebar.comm_status_p = _sequence_state["P"]["emcs_powered"]
    app_state.sidebar.comm_status_s = _sequence_state["S"]["emcs_powered"]
    emcs_active = _sequence_state["P"]["emcs_powered"] or _sequence_state["S"]["emcs_powered"]
    app_state.sidebar.comm_status = emcs_active
    app_state.scenario.communication_system_ready = emcs_active


def recompute_derived_flags(app_state):
    sc = app_state.scenario
    sw_p = app_state.switches.p
    sw_s = app_state.switches.s

    refresh_telemetry_displays(app_state)

    for side, sw in (("P", sw_p), ("S", sw_s)):
        seq = _sequence_state[side]
        ab_bms = getattr(sw, f"ab_{side.lower()}_bms", False)
        ab = getattr(sw, f"ab_{side.lower()}_power", False)
        ub_mcb = getattr(sw, f"ub_{side.lower()}_mcb", False)
        seq["aux_seq_complete"] = bool(ab_bms and ab and ub_mcb)

    sc.global_power_available = (
        _sequence_state["P"]["aux_seq_complete"] or _sequence_state["S"]["aux_seq_complete"]
    )

    mb_p_soc = app_state.power.mb_p.soc.value
    mb_s_soc = app_state.power.mb_s.soc.value
    sc.power_control_system_ready = sc.communication_system_ready and (mb_p_soc >= 25 and mb_s_soc >= 25)

    # Proactively hand control to the other side the moment the active
    # side's sequence completes, even before the next switch toggle comes
    # in (e.g. right after the last PORT step, before any STARBOARD switch
    # has been touched yet).
    _maybe_auto_advance_side(app_state)

    sc.active_side = _active_side
    sc.next_step_p = compute_next_step(app_state, "P")
    sc.next_step_s = compute_next_step(app_state, "S")

    sc.next_step_final = compute_final_phase_step(app_state)
    sc.main_battery_complete = (
        _sequence_state["P"]["ub_mb_changeover_done"] and _sequence_state["S"]["ub_mb_changeover_done"]
    )
    if sc.main_battery_complete and not sc.alarm_active and not sc.feedback_msg.startswith("MAIN BATTERY"):
        sc.feedback_msg = (
            "MAIN BATTERY POWER-UP SEQUENCE COMPLETE (SOP Steps 1-60). Port and Starboard are both on Main "
            "Battery power. This training scenario ends here."
        )

    # This scenario is intentionally scoped to Main Battery power-up
    # (SOP Steps 1-60). The post-power-up phase driver (Imaging -> Sensors
    # -> Comms -> Ballast -> Propulsion, steps 63-108) is disabled -- flip
    # ENABLE_POST_MAIN_BATTERY_PHASES above to re-enable it later.
    if ENABLE_POST_MAIN_BATTERY_PHASES:
        _update_post_powerup_phases(app_state)


def compute_final_phase_step(app_state) -> str:
    """SOP Steps 57-60, only meaningful once both sides finish steps 37-56."""
    if not (_is_side_complete(app_state, "P") and _is_side_complete(app_state, "S")):
        return "[FINAL] Complete Main Battery/PDE/IDE power-up on both sides first (SOP Steps 37-56)."

    p_reverted = _sequence_state["P"]["eb_reverted"]
    s_reverted = _sequence_state["S"]["eb_reverted"]
    if not (p_reverted and s_reverted):
        return "[FINAL] SOP Step 59: Revert EB selectors (Port & Starboard) back to EB position."

    p_mb = _sequence_state["P"]["ub_mb_changeover_done"]
    s_mb = _sequence_state["S"]["ub_mb_changeover_done"]
    if not (p_mb and s_mb):
        return "[FINAL] SOP Step 60: Change UB selectors (Port & Starboard) from AB to Main Battery (MB)."

    return "[FINAL] Main Battery power-up sequence complete (SOP Steps 1-60)."