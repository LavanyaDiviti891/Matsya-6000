"""
alarm_engine.py — threshold engine for
"ALARM DOCUMENT FOR 500m DEPTH RATED HUMAN SUBMERSIBLE -- MATSYA500"
(NIOT/DST/S&GH/MANSUB/CMS/AS/99/V0, Rev R0, Feb 2026).

This module ONLY decides two things, every tick:
  1. Which documented parameters are currently in Warning/Advisory or
     Critical territory (`evaluate(app_state) -> list[Alarm]`).
  2. What that means for the audible cue (`beep_level(alarms) -> str`),
     per the document's Table "Definition":
        Critical         -> continuous beep until acknowledged
        Warning/Advisory  -> single beep
        (neither)         -> silent

Per the user's requirement, this deliberately does NOT drive any visual
pop-up/banner/modal. `app_state.active_alarms` is populated purely so a
status page *could* list what's active if wanted, but nothing here forces
a UI element on screen -- the frontend only reacts to `beep_level` to
decide whether/how to beep (see hooks/useAlarmBeep.js).

Each entry in THRESHOLDS is:
    key: (getter, warning_low, warning_high, critical_low, critical_high)
`None` means "NW"/"NA" (not defined) for that bound in the document.
`getter(app_state) -> float | bool | None` reads the live value.
For boolean "Y/NA" style rows (e.g. water ingress), warning bounds are
None and the critical bound is treated as "true means alarm".
"""

from dataclasses import dataclass
from typing import Callable, Optional, List


@dataclass
class Alarm:
    key: str
    label: str
    level: str          # "warning" | "critical"
    value: float


def _v(numeric_telemetry):
    """Pull .value off a NumericTelemetry-shaped object, else return as-is."""
    if numeric_telemetry is None:
        return None
    return getattr(numeric_telemetry, "value", numeric_telemetry)


def _safe(fn, app_state):
    try:
        return fn(app_state)
    except AttributeError:
        return None


# ---------------------------------------------------------------------------
# THRESHOLDS -- (getter, warn_low, warn_high, crit_low, crit_high)
# Values transcribed from Table 4 (Critical) and Table 5 (Warning/Advisory).
# ---------------------------------------------------------------------------
THRESHOLDS = {
    # -- A) Human Support & Safety System (HSSS) --------------------------
    "o2": dict(
        label="O2 (%V/V)",
        getter=lambda s: _v(s.environment.o2),
        warn_low=20, warn_high=22, crit_low=19.5, crit_high=23.5,
    ),
    "co2": dict(
        label="CO2 (ppm)",
        getter=lambda s: _v(s.environment.co2),
        warn_low=None, warn_high=5000, crit_low=None, crit_high=8000,
    ),
    "cabin_pressure": dict(
        label="Cabin pressure (mbar)",
        getter=lambda s: _v(s.environment.pressure),
        warn_low=850, warn_high=1150, crit_low=750, crit_high=1250,
    ),
    "cabin_temp": dict(
        label="Cabin temperature (deg C)",
        getter=lambda s: _v(s.environment.temp),
        warn_low=None, warn_high=45, crit_low=None, crit_high=None,
    ),

    # -- B) Battery system (Port & Starboard) ------------------------------
    "mb_p_voltage": dict(
        label="Main Battery Port Voltage (V)",
        getter=lambda s: _v(s.power.mb_p.voltage),
        warn_low=140, warn_high=None, crit_low=135, crit_high=None,
    ),
    "mb_p_soc": dict(
        label="Main Battery Port SoC (%)",
        getter=lambda s: _v(s.power.mb_p.soc),
        warn_low=35, warn_high=None, crit_low=30, crit_high=None,
    ),
    "aux_p_voltage": dict(
        label="Auxiliary Battery Port Voltage (V)",
        getter=lambda s: _v(s.power.aux_p.voltage),
        warn_low=28, warn_high=None, crit_low=26, crit_high=None,
    ),
    "aux_p_soc": dict(
        label="Auxiliary Battery Port SoC (%)",
        getter=lambda s: _v(s.power.aux_p.soc),
        warn_low=35, warn_high=None, crit_low=30, crit_high=None,
    ),
    "mb_s_voltage": dict(
        label="Main Battery Stbd Voltage (V)",
        getter=lambda s: _v(s.power.mb_s.voltage),
        warn_low=140, warn_high=None, crit_low=135, crit_high=None,
    ),
    "mb_s_soc": dict(
        label="Main Battery Stbd SoC (%)",
        getter=lambda s: _v(s.power.mb_s.soc),
        warn_low=35, warn_high=None, crit_low=30, crit_high=None,
    ),
    "aux_s_voltage": dict(
        label="Auxiliary Battery Stbd Voltage (V)",
        getter=lambda s: _v(s.power.aux_s.voltage),
        warn_low=28, warn_high=None, crit_low=26, crit_high=None,
    ),
    "aux_s_soc": dict(
        label="Auxiliary Battery Stbd SoC (%)",
        getter=lambda s: _v(s.power.aux_s.soc),
        warn_low=35, warn_high=None, crit_low=30, crit_high=None,
    ),

    # -- C) IDE / PDE enclosures & PS insulation ---------------------------
    "pde_p_ir": dict(
        label="148VDC insulation Port side (kOhm, PDE_P)",
        getter=lambda s: _v(s.power.pde_p.ir_148),
        warn_low=None, warn_high=None, crit_low=500, crit_high=None,
    ),
    "pde_s_ir": dict(
        label="148VDC insulation Stbd side (kOhm, PDE_S)",
        getter=lambda s: _v(s.power.pde_s.ir_148),
        warn_low=None, warn_high=None, crit_low=500, crit_high=None,
    ),
    "ide_p_ir": dict(
        label="24VDC insulation Port side (kOhm, IDE_P)",
        getter=lambda s: _v(s.power.ide_p.ir_24),
        warn_low=None, warn_high=None, crit_low=500, crit_high=None,
    ),
    "ide_s_ir": dict(
        label="24VDC insulation Stbd side (kOhm, IDE_S)",
        getter=lambda s: _v(s.power.ide_s.ir_24),
        warn_low=None, warn_high=None, crit_low=500, crit_high=None,
    ),
    "pde_p_water": dict(
        label="Water ingress - PDE_P",
        getter=lambda s: (s.power.pde_p.water_leak != "No Leak"),
        boolean=True,
    ),
    "pde_s_water": dict(
        label="Water ingress - PDE_S",
        getter=lambda s: (s.power.pde_s.water_leak != "No Leak"),
        boolean=True,
    ),
    "ide_p_water": dict(
        label="Water ingress - IDE_P",
        getter=lambda s: (s.power.ide_p.water_leak != "No Leak"),
        boolean=True,
    ),
    "ide_s_water": dict(
        label="Water ingress - IDE_S",
        getter=lambda s: (s.power.ide_s.water_leak != "No Leak"),
        boolean=True,
    ),

    # -- Comms ---------------------------------------------------------------
    "comm_status": dict(
        label="Communication Status - Submersible network",
        getter=lambda s: (not s.sidebar.comm_status),
        boolean=True,
    ),
    "water_ingress_general": dict(
        label="Water ingress (general alert)",
        getter=lambda s: bool(s.sidebar.water_ingress),
        boolean=True,
    ),

    # -- D) Depth / navigation ------------------------------------------------
    "depth": dict(
        label="Exceeding normal diving depth (m)",
        getter=lambda s: _v(s.header.depth),
        warn_low=None, warn_high=475, crit_low=None, crit_high=500,
    ),
    "altitude": dict(
        label="Altimeter (m)",
        getter=lambda s: _v(s.header.altitude),
        warn_low=5, warn_high=None, crit_low=5, crit_high=None,
    ),
}


def evaluate(app_state) -> List[Alarm]:
    """Return every parameter currently in Warning or Critical territory.
    Critical always takes priority over Warning for the same parameter."""
    alarms: List[Alarm] = []

    for key, spec in THRESHOLDS.items():
        try:
            value = spec["getter"](app_state)
        except Exception:
            continue
        if value is None:
            continue

        if spec.get("boolean"):
            if value:
                alarms.append(Alarm(key, spec["label"], "critical", 1.0))
            continue

        warn_low = spec.get("warn_low")
        warn_high = spec.get("warn_high")
        crit_low = spec.get("crit_low")
        crit_high = spec.get("crit_high")

        if crit_low is not None and value < crit_low:
            alarms.append(Alarm(key, spec["label"], "critical", value))
        elif crit_high is not None and value > crit_high:
            alarms.append(Alarm(key, spec["label"], "critical", value))
        elif warn_low is not None and value < warn_low:
            alarms.append(Alarm(key, spec["label"], "warning", value))
        elif warn_high is not None and value > warn_high:
            alarms.append(Alarm(key, spec["label"], "warning", value))

    return alarms


def beep_level(alarms: List[Alarm]) -> str:
    """Critical beats Warning beats silence."""
    if any(a.level == "critical" for a in alarms):
        return "critical"
    if any(a.level == "warning" for a in alarms):
        return "warning"
    return ""


def update_app_state(app_state) -> None:
    """Call once per simulation/broadcast tick. Sets app_state.beep_level
    and app_state.active_alarms; drives NO popup/banner by itself."""
    alarms = evaluate(app_state)
    app_state.active_alarms = [
        {"key": a.key, "label": a.label, "level": a.level, "value": a.value}
        for a in alarms
    ]
    app_state.beep_level = beep_level(alarms)
