from fasthtml.common import Div, Span, NotStr, H3, A
import math

def fmt_val(val):
    try:
        return f"{float(val):.2f}"
    except (ValueError, TypeError):
        return str(val)



# ----------------- ICONS (SVG Placeholders via NotStr) -----------------
def IconSettings():
    return NotStr(
        '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path></svg>'
    )


def IconPower():
    return NotStr(
        '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18.36 6.64a9 9 0 1 1-12.73 0"></path><line x1="12" y1="2" x2="12" y2="12"></line></svg>'
    )


def IconHome():
    return NotStr(
        '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path><polyline points="9 22 9 12 15 12 15 22"></polyline></svg>'
    )


def IconChevronDown():
    return NotStr(
        '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"></polyline></svg>'
    )


# ----------------- WIDGETS -----------------


def TopbarInlineMetric(label, value, unit="", id_key=None):
    """Header strip inline key-value pairs"""
    return Div(
        Span(label, cls="topbar-metric-label"),
        Div(
            Span(fmt_val(value), cls="topbar-metric-value"),
            Span(unit, cls="topbar-metric-unit") if unit else None,
            cls="topbar-metric-box",
        ),
        cls="topbar-metric",
        id=id_key,
        hx_swap_oob="true" if id_key else None,
    )


def VerticalGauge(
    label, value, max_val, unit="", low_is_good=False, scale_labels=None, id_key=None
):
    """Tall vertical tracking bar representing Depth or Altitude"""
    percent = min(100, max(0, (value / max_val) * 100))
    fill_cls = (
        "gauge-fill-green"
        if not low_is_good
        else ("gauge-fill-red" if percent > 80 else "gauge-fill-green")
    )

    # Scale labels next to gauge
    labels_children = []
    if scale_labels:
        for lbl in scale_labels:
            labels_children.append(Span(str(lbl), cls="gauge-scale-label"))
    y_axis = Div(*labels_children, cls="gauge-scale")

    return Div(
        Div(
            y_axis,
            Div(
                Div(cls=f"gauge-fill {fill_cls}", style=f"height: {percent}%;"),
                cls="gauge-track",
            ),
            cls="gauge-body",
        ),
        H3(label, cls="gauge-title"),
        Div(
            Span(fmt_val(value), cls="gauge-value"),
            Span(unit, cls="gauge-unit"),
            cls="gauge-readout",
        ),
        cls="gauge-container",
        id=id_key,
        hx_swap_oob="true" if id_key else None,
    )


def SimpleRpmBox(label, value, id_key=None):
    """Specific T1-T8 RPM boxes"""
    return Div(
        Span(label, cls="rpm-label"),
        Div(fmt_val(value), cls="rpm-value"),
        cls="rpm-box",
        id=id_key,
        hx_swap_oob="true" if id_key else None,
    )


def SimpleMetricBox(label, value, unit="", id_key=None):
    """Tiny input-like read-only boxes (used for Roll/Pitch and footers)"""
    return Div(
        Span(label, cls="metric-label"),
        Div(Span(fmt_val(value), cls="metric-value"), cls="metric-input"),
        Span(unit, cls="metric-unit") if unit else None,
        cls="metric-box",
        id=id_key,
        hx_swap_oob="true" if id_key else None,
    )


def CompassBox():
    """The central map box with N, E, S, W indicators"""
    return Div(
        Span("N", cls="compass-label compass-n"),
        Span("S", cls="compass-label compass-s"),
        Span("W", cls="compass-label compass-w"),
        Span("E", cls="compass-label compass-e"),
        Div(cls="compass-inner"),
        cls="compass-box",
    )


def SidebarMetric(label, value, unit="", id_key=None):
    """Right sidebar environmental metrics"""
    return Div(
        Span(label, cls="sidebar-metric-label"),
        Div(
            Span(fmt_val(value), cls="sidebar-metric-value"),
            Span(unit, cls="sidebar-metric-unit"),
            cls="sidebar-metric-readout",
        ),
        cls="sidebar-metric",
        id=id_key,
        hx_swap_oob="true" if id_key else None,
    )


def StatusPill(label, is_ok, ok_text="OK", err_text="ERR", id_key=None):
    """Right sidebar status flags"""
    status_cls = "status-pill-ok" if is_ok else "status-pill-err"
    text = ok_text if is_ok else err_text
    return Div(
        f"{label} {text}",
        cls=f"status-pill {status_cls}",
        id=id_key,
        hx_swap_oob="true" if id_key else None,
    )


def ToggleSwitch(label, is_on, id_key=None, toggle_url=None):
    """Vercel styled pill toggle for right sidebar"""
    toggle_cls = "toggle-on" if is_on else "toggle-off"
    dot_cls = "toggle-dot-on" if is_on else "toggle-dot-off"
    
    attrs = {"cls": "toggle-switch"}
    if id_key:
        attrs["id"] = id_key
        attrs["hx_swap_oob"] = "true"
    if toggle_url:
        attrs["hx_post"] = toggle_url
        attrs["hx_swap"] = "none"
        
    return Div(
        Span(label, cls="toggle-label"),
        Div(
            Span("ON" if is_on else "OFF", cls="toggle-state-text"),
            Div(Div(cls=f"toggle-dot {dot_cls}"), cls=f"toggle-track {toggle_cls}"),
            cls="toggle-controls",
        ),
        **attrs
    )


def BottomTabsNav(tabs, active_tab="Main"):
    """Bottom footer with segmented navigation"""
    nav_links = []
    for t in tabs:
        active_cls = "tab-active" if t == active_tab else "tab-inactive"
        if t == "Main":
            url = "/"
        elif t == "HSSS":
            url = "/hsss"
        elif t == "Ballast":
            url = "/ballast"
        elif t == "Propulsion":
            url = "/propulsion"
        elif t == "POWER":
            url = "/power"
        elif t == "Imaging":
            url = "/imaging"
        elif t == "Sensors":
            url = "/sensors"
        elif t == "Logging":
            url = "/logging"
        elif t == "Status":
            url = "/status"
        elif t == "50 Kwh":
            url = "/50-kwh"
        elif t == "MCC":
            url = "/mcc"
        elif t == "Switches":
            url = "/switches"
        else:
            url = "#"
        nav_links.append(
            A(
                t,
                href=url,
                cls=f"tab-link {active_cls}",
            )
        )
    return Div(*nav_links, cls="bottom-tabs")


def BigNumber(label, value, unit=""):
    """Big prominent readout for the key telemetry values"""
    return Div(
        Span(label, cls="big-number-label"),
        Div(
            Span(fmt_val(value), cls="big-number-value"),
            Span(unit, cls="big-number-unit"),
            cls="big-number-readout",
        ),
        cls="big-number",
    )


def LedPanel(leds, id_key=None):
    """Two rows of 3 LED indicators: PSS/PDS/IDS and PSP/PDP/IDP"""

    def led(label, is_on):
        cls = "led-dot led-on" if is_on else "led-dot led-off"
        return Div(Div(cls=cls), Span(label, cls="led-label"), cls="led-item")

    return Div(
        Div(
            led("PSS", leds.pss),
            led("PDS", leds.pds),
            led("IDS", leds.ids),
            cls="led-row",
        ),
        Div(
            led("PSP", leds.psp),
            led("PDP", leds.pdp),
            led("IDP", leds.idp),
            cls="led-row",
        ),
        cls="led-panel",
        id=id_key,
        hx_swap_oob="true" if id_key else None,
    )


# ----------------- HSSS SPECIFIC WIDGETS -----------------


def SemiCircleGauge(
    label,
    value,
    min_val,
    max_val,
    unit,
    label_sub="",
    scale_labels=None,
    is_oxygen=False,
):
    """A semi-circle CSS gauge for CO2 and Oxygen"""
    percent = (value - min_val) / (max_val - min_val) * 100
    percent = max(0, min(100, percent))
    rotation = (percent / 100) * 180

    # Optional scale labels positions calculated along arc
    labels_divs = []
    if scale_labels:
        n = len(scale_labels)
        for i, sl in enumerate(scale_labels):
            f = i / (n - 1) if n > 1 else 0.5
            angle = math.pi * (1 - f)
            
            r = 120
            cx = 130
            cy = 120
            
            x = cx + r * math.cos(angle)
            y = cy - r * math.sin(angle)
            
            style = f"left: {x}px; top: {y}px; transform: translate(-50%, -50%);"
            labels_divs.append(Span(str(sl), cls="sc-label", style=style))

    gauge_type = "sc-gauge-oxygen" if is_oxygen else "sc-gauge-co2"

    return Div(
        Div(*labels_divs, cls="sc-labels-container"),
        Div(
            Div(
                cls=f"sc-fill {gauge_type}", style=f"transform: rotate({rotation}deg);"
            ),
            Div(cls="sc-cover"),
            cls="sc-track",
        ),
        Div(
            Span(fmt_val(value) if not is_oxygen else fmt_val(value), cls="sc-value"),
            Span(label, cls="sc-title"),
            Span(f"({unit})", cls="sc-unit"),
            cls="sc-readout",
        ),
        cls="semi-circle-gauge",
    )


def HorizontalProgressBar(label, value, min_val, max_val, unit, scale_labels=None):
    """Horizontal progress bar for Pressure, Temp, Humidity"""
    percent = (value - min_val) / (max_val - min_val) * 100
    percent = max(0, min(100, percent))

    labels_row = None
    if scale_labels:
        labels_children = [Span(str(sl), cls="hp-scale-label") for sl in scale_labels]
        labels_row = Div(*labels_children, cls="hp-scale-row")

    return Div(
        Div(
            Span(label, cls="hp-title"),
            Div(fmt_val(value), cls="hp-value-box"),
            cls="hp-header",
        ),
        Div(Div(cls="hp-fill", style=f"width: {percent}%;"), cls="hp-track"),
        labels_row,
        cls="horizontal-progress-bar",
    )


def SensorStatusPill(label, status_text, is_ok):
    """Rectangular block used for indicating Smoke, Flame, and Heat sensor statuses"""
    bg_cls = "sensor-ok" if is_ok else "sensor-err"
    return Div(
        Span(label, cls="sensor-label"),
        Div(status_text, cls=f"sensor-status {bg_cls}"),
        cls="sensor-pill-container",
    )


def HSSSLabelInput(label, value, unit):
    """White box model input display for Hydrogen, LP_L Pressure, etc"""
    return Div(
        Span(label, cls="hsss-input-label"),
        Div(
            Div(fmt_val(value), cls="hsss-input-value"),
            Span(unit, cls="hsss-input-unit"),
            cls="hsss-input-row",
        ),
        cls="hsss-input-container",
    )


# ----------------- BALLAST SPECIFIC WIDGETS -----------------


def BallastActionButton(label):
    """Gray action button for ballast commands (Ready to Dive, Dive open, etc.)"""
    return Div(label, cls="ballast-btn")


def BallastPressureRead(label, value, is_enabled, id_key=None, toggle_url=None):
    """Pressure read row: label + value box + mini toggle switch"""
    toggle_cls = "toggle-on" if is_enabled else "toggle-off"
    dot_cls = "toggle-dot-on" if is_enabled else "toggle-dot-off"
    
    attrs = {"cls": "ballast-pressure-read"}
    if id_key:
        attrs["id"] = id_key
        attrs["hx_swap_oob"] = "true"
    if toggle_url:
        attrs["hx_post"] = toggle_url
        attrs["hx_swap"] = "none"

    return Div(
        Span(label, cls="ballast-pressure-label"),
        Div(
            Div(fmt_val(value), cls="ballast-pressure-value"),
            Div(
                Span("ON" if is_enabled else "OFF", cls="toggle-state-text"),
                Div(
                    Div(cls=f"toggle-dot {dot_cls}"),
                    cls=f"toggle-track {toggle_cls}",
                ),
                cls="toggle-controls",
            ),
            cls="ballast-pressure-right",
        ),
        **attrs
    )


def BallastActSlider(label, value, min_val=-150, max_val=150):
    """ACT position read-only slider: Open <----[thumb]----> Closed with scale"""
    percent = (value - min_val) / (max_val - min_val) * 100
    percent = max(0, min(100, percent))
    scale_labels = ["-150", "-100", "-50", "0", "50", "100", "150"]
    scale_items = [Span(sl, cls="act-scale-label") for sl in scale_labels]
    return Div(
        Span(label, cls="act-slider-title"),
        Div(
            Span("Open", cls="act-slider-side"),
            Div(
                Div(
                    Div(cls="act-thumb", style=f"left: {percent}%;"),
                    cls="act-track",
                ),
                Div(*scale_items, cls="act-scale-row"),
                cls="act-track-wrap",
            ),
            Span("Closed", cls="act-slider-side"),
            cls="act-slider-row",
        ),
        cls="act-slider-container",
    )


def VBSTankGauge(level, max_val=300):
    """Vertical tank gauge for the Variable Ballast System"""
    percent = min(100, max(0, (level / max_val) * 100))
    scale_labels = ["300", "250", "200", "150", "100", "50", "0"]
    labels_children = [Span(str(lbl), cls="vbs-tank-scale-label") for lbl in scale_labels]
    y_axis = Div(*labels_children, cls="vbs-tank-scale")
    return Div(
        Div("VBS Tank", cls="vbs-tank-title"),
        Div(
            y_axis,
            Div(
                Div(cls="vbs-tank-fill", style=f"height: {percent}%;"),
                cls="vbs-tank-track",
            ),
            cls="vbs-tank-body",
        ),
        Div(
            Span(fmt_val(level), cls="vbs-tank-value"),
            Span("L", cls="vbs-tank-unit"),
            cls="vbs-tank-readout",
        ),
        cls="vbs-tank-gauge",
    )


def VBSMetricRow(label, value, unit):
    """Label + value display box + unit for VBS HPU metrics"""
    return Div(
        Span(label, cls="vbs-metric-label"),
        Div(
            Div(fmt_val(value), cls="vbs-metric-value"),
            Span(unit, cls="vbs-metric-unit") if unit else None,
            cls="vbs-metric-right",
        ),
        cls="vbs-metric-row",
    )


def VBSWaterButton(label):
    """Water IN / Water OUT action button"""
    return Div(label, cls="vbs-water-btn")


def VBSSetControl(value):
    """VBS SET control with up/down arrows and current value display"""
    return Div(
        Span("VBS SET", cls="vbs-set-label"),
        Div(
            Div("▲", cls="vbs-set-arrow"),
            Div(fmt_val(value), cls="vbs-set-value"),
            Div("▼", cls="vbs-set-arrow"),
            cls="vbs-set-spinbox",
        ),
        cls="vbs-set-container",
    )


def TrimPositionBar(value, max_val=4500):
    """Horizontal position bar for TRIM showing 0–4500 mm"""
    percent = min(100, max(0, (value / max_val) * 100))
    scale_labels = ["0", "500", "1000", "1500", "2000", "2500", "3000", "3500", "4000", "4500"]
    scale_items = [Span(sl, cls="trim-scale-label") for sl in scale_labels]
    return Div(
        Div(
            Div(
                Div(cls="trim-thumb", style=f"left: {percent}%;"),
                cls="trim-track",
            ),
        ),
        Div(*scale_items, cls="trim-scale-row"),
        cls="trim-position-bar",
    )


def SpeedControlSlider(value, min_val=1, max_val=7):
    """Speed control display slider from 1 to 7"""
    percent = min(100, max(0, ((value - min_val) / (max_val - min_val)) * 100))
    scale_labels = ["1", "2", "3", "4", "5", "6", "7"]
    scale_items = [Span(sl, cls="speed-scale-label") for sl in scale_labels]
    return Div(
        Span("Speed Control", cls="speed-ctrl-label"),
        Div(
            Div(
                Div(cls="speed-thumb", style=f"left: {percent}%;"),
                cls="speed-track",
            ),
            Div(*scale_items, cls="speed-scale-row"),
            cls="speed-track-wrap",
        ),
        cls="speed-control-slider",
    )


def OIMToggleRow(label, is_on, id_key=None, toggle_url=None):
    """Horizontal OIM reset row: label ........ toggle"""
    toggle_cls = "toggle-on" if is_on else "toggle-off"
    dot_cls = "toggle-dot-on" if is_on else "toggle-dot-off"

    attrs = {"cls": "oim-toggle-row"}
    if id_key:
        attrs["id"] = id_key
        attrs["hx_swap_oob"] = "true"
    if toggle_url:
        attrs["hx_post"] = toggle_url
        attrs["hx_swap"] = "none"

    return Div(
        Span(label, cls="oim-toggle-label"),
        Div(
            Span("ON" if is_on else "OFF", cls="toggle-state-text"),
            Div(
                Div(cls=f"toggle-dot {dot_cls}"),
                cls=f"toggle-track {toggle_cls}",
            ),
            cls="toggle-controls",
        ),
        **attrs
    )


# ----------------- PROPULSION SCREEN SPECIFIC WIDGETS -----------------


def ThrusterRPMGauge(label, rpm, max_rpm=1600):
    """Semi-circle RPM gauge for Propulsion screen, styled like original dashboard"""
    percent = min(100, max(0, (rpm / max_rpm) * 100))
    rotation = (percent / 100) * 180  # 0 → 180 deg

    # Arc needle: dark fill rotating from left
    # Scale labels along the arc
    scale_values = [0, 200, 400, 600, 800, 1000, 1200, 1400, 1600]
    labels_divs = []
    n = len(scale_values)
    r = 62
    cx = 70
    cy = 65
    for i, sv in enumerate(scale_values):
        f = i / (n - 1)
        angle = math.pi * (1 - f)
        x = cx + r * math.cos(angle)
        y = cy - r * math.sin(angle)
        style = f"left:{x:.0f}px;top:{y:.0f}px;transform:translate(-50%,-50%);"
        labels_divs.append(Span(str(sv), cls="tg-scale-label", style=style))

    return Div(
        # Labels container
        Div(*labels_divs, cls="tg-labels-container"),
        # Semi-circle track + fill + cover
        Div(
            Div(cls="tg-fill", style=f"transform:rotate({rotation}deg);"),
            Div(cls="tg-cover"),
            cls="tg-track",
        ),
        # Readout below
        Div(
            Span(fmt_val(rpm), cls="tg-rpm-value"),
            cls="tg-readout",
        ),
        Span(label, cls="tg-label"),
        Span("RPM", cls="tg-rpm-unit"),
        cls="thruster-gauge",
    )


def ThrusterPowerEnableToggles(thruster_id, power, enable, toggle_url_p=None, toggle_url_e=None):
    """Compact vertical pair of Power/Enable toggles for Propulsion center column"""
    def mini_toggle(label, is_on, suffix_id, url):
        t_cls = "toggle-on" if is_on else "toggle-off"
        d_cls = "toggle-dot-on" if is_on else "toggle-dot-off"
        
        attrs = {"cls": "prop-toggle-row"}
        if suffix_id:
            attrs["id"] = f"tpet-{thruster_id}-{suffix_id}"
            attrs["hx_swap_oob"] = "true"
        if url:
            attrs["hx_post"] = url
            attrs["hx_swap"] = "none"

        return Div(
            Span(label, cls="prop-toggle-label"),
            Div(
                Div(
                    Div(cls=f"toggle-dot {d_cls}"),
                    cls=f"toggle-track {t_cls}",
                ),
                Span("ON" if is_on else "OFF", cls="prop-toggle-state"),
                cls="prop-toggle-controls",
            ),
            **attrs
        )

    return Div(
        mini_toggle(f"T{thruster_id}_Power", power, "power", toggle_url_p),
        mini_toggle(f"T{thruster_id}_Enable", enable, "enable", toggle_url_e),
        cls="prop-toggle-pair",
    )


def ThrusterPanel(thruster_id, t):
    """Full thruster card: gauge + voltage/current/temp + ctrl + power/enable"""
    return Div(
        Div(f"T{thruster_id}", cls="thruster-panel-id"),
        ThrusterRPMGauge(f"T{thruster_id} Speed", t.rpm),
        Div(
            Div(
                Span("Voltage", cls="tp-metric-label"),
                Div(fmt_val(t.voltage), cls="tp-metric-value"),
                Span("V", cls="tp-metric-unit"),
                cls="tp-metric-row",
            ),
            Div(
                Span("Current", cls="tp-metric-label"),
                Div(fmt_val(t.current), cls="tp-metric-value"),
                Span("A", cls="tp-metric-unit"),
                cls="tp-metric-row",
            ),
            Div(
                Span("Temp", cls="tp-metric-label"),
                Div(fmt_val(t.temp), cls="tp-metric-value"),
                Span("°C", cls="tp-metric-unit"),
                cls="tp-metric-row",
            ),
            cls="tp-metrics",
        ),
        Div(
            Span(f"T{thruster_id} ctrl", cls="tp-ctrl-label"),
            Div(fmt_val(t.ctrl), cls="tp-ctrl-value"),
            cls="tp-ctrl-row",
        ),
        cls="thruster-panel",
    )


def PropCenterToggleBlock(thruster_id, power, enable, toggle_url_p=None, toggle_url_e=None):
    """Power + Enable toggle pair with label for the center column"""
    def tiny_tog(label, is_on, suffix_id, url):
        t_cls = "toggle-on" if is_on else "toggle-off"
        d_cls = "toggle-dot-on" if is_on else "toggle-dot-off"
        
        attrs = {"cls": "prop-center-tog-row"}
        if suffix_id:
            attrs["id"] = f"pctb-{thruster_id}-{suffix_id}"
            attrs["hx_swap_oob"] = "true"
        if url:
            attrs["hx_post"] = url
            attrs["hx_swap"] = "none"

        return Div(
            Span(label, cls="prop-center-tog-label"),
            Div(
                Div(
                    Div(cls=f"toggle-dot {d_cls}"),
                    cls=f"toggle-track {t_cls}",
                ),
                Span("ON" if is_on else "OFF", cls="prop-center-tog-state"),
                cls="prop-center-tog-controls",
            ),
            **attrs
        )

    return Div(
        tiny_tog(f"T{thruster_id}_Power", power, "power", toggle_url_p),
        tiny_tog(f"T{thruster_id}_Enable", enable, "enable", toggle_url_e),
        cls="prop-center-block",
    )


def PropAxisControl(label, value):
    """Bottom axis control box: Heading ctrl, Fwd ctrl, etc."""
    return Div(
        Span(label, cls="prop-axis-label"),
        Div(fmt_val(value), cls="prop-axis-value"),
        cls="prop-axis-ctrl",
    )


# ----------------- POWER SCREEN SPECIFIC WIDGETS -----------------


def PowerMetricRow(label, value, unit=None):
    """Grey label, white box value row for power metrics."""
    return Div(
        Span(label, cls="power-metric-label"),
        Div(
            Span(fmt_val(value), cls="power-metric-value"),
            Span(unit, cls="power-metric-unit") if unit else None,
            cls="power-metric-box",
        ),
        cls="power-metric-row",
    )


def PowerLinearGauge(label, value, min_val, max_val, scale_labels):
    """Horizontal visual bar with ticks used for battery voltage."""
    percent = max(0, min(100, ((value - min_val) / (max_val - min_val)) * 100))
    scale_items = [Span(str(sl), cls="power-gauge-scale-label") for sl in scale_labels]
    
    return Div(
        Span(label, cls="power-gauge-title"),
        Div(
            Div(
                Div(cls="power-gauge-fill", style=f"width: {percent}%;"),
                cls="power-gauge-track",
            ),
            Div(*scale_items, cls="power-gauge-scale-row"),
            cls="power-gauge-wrap",
        ),
        Div(fmt_val(value), cls="power-gauge-value"),
        cls="power-linear-gauge",
    )


def PowerStatusPill(label, status_text, is_ok):
    """Rectangular red/green indicator for IR and leaks."""
    bg_cls = "power-status-ok" if is_ok else "power-status-err"
    if label:
        return Div(
            Span(label, cls="power-status-label"),
            Div(status_text, cls=f"power-status-box {bg_cls}"),
            cls="power-status-container"
        )
    else:
        return Div(
            status_text, 
            cls=f"power-status-box {bg_cls}"
        )


def BatteryPanel(title, prefix, battery, scale_labels, min_val, max_val):
    return Div(
        Div(title, cls="power-panel-title"),
        PowerLinearGauge(f"{prefix} Volt (V)", battery.voltage.value, min_val, max_val, scale_labels),
        PowerMetricRow(f"{prefix} Current (A)", battery.current.value),
        PowerMetricRow(f"{prefix} Power (kW)", battery.power.value),
        PowerMetricRow(f"{prefix} SOC (%)", battery.soc.value),
        PowerMetricRow(f"{prefix} Temp (deg C)", battery.temp.value),
        cls="power-panel battery-panel"
    )


def PDEPanel(title, prefix, enclosure):
    return Div(
        Div(title, cls="power-panel-title"),
        PowerMetricRow(f"{prefix} Voltage (V)", enclosure.voltage.value),
        PowerMetricRow(f"{prefix} Current (A)", enclosure.current.value),
        PowerMetricRow(f"{prefix} Temp (degC)", enclosure.temp.value),
        PowerMetricRow(f"{prefix} IR_24 (Kohm)", enclosure.ir_24.value),
        PowerMetricRow(f"{prefix}_IR_Ext (Kohm)", enclosure.ir_ext.value),
        PowerMetricRow(f"{prefix}_148 IR (Kohm)", enclosure.ir_148.value),
        PowerStatusPill(f"{prefix} IR Status", enclosure.ir_status, is_ok=(enclosure.ir_status != "LOW IR")),
        PowerStatusPill(f"{prefix} Water Leak", enclosure.water_leak, is_ok=(enclosure.water_leak == "No Leak")),
        cls="power-panel pde-panel"
    )


def IDEPanel(title, prefix, enclosure):
    return Div(
        Div(title, cls="power-panel-title"),
        PowerMetricRow(f"{prefix} Voltage (V)", enclosure.voltage.value),
        PowerMetricRow(f"{prefix} Current (A)", enclosure.current.value),
        PowerMetricRow(f"{prefix} Temp (degC)", enclosure.temp.value),
        PowerMetricRow(f"{prefix} IR (kohm)", enclosure.ir.value),
        PowerStatusPill(f"{prefix} IR Status", enclosure.ir_status, is_ok=(enclosure.ir_status != "LOW IR")),
        PowerStatusPill(f"{prefix} Water Leak", enclosure.water_leak, is_ok=(enclosure.water_leak == "No Leak")),
        cls="power-panel ide-panel"
    )


def UmbilicalPanel(title, prefix, umbilical):
    # Has a 3 column layout for metrics and pills
    return Div(
        Div(title, cls="power-panel-title"),
        Div(
            Div(
                PowerMetricRow(f"{prefix} Voltage (V)", umbilical.voltage.value),
                PowerMetricRow(f"{prefix} Current (A)", umbilical.current.value),
                cls="ub-col"
            ),
            Div(
                PowerMetricRow(f"{prefix} Temp (degC)", umbilical.temp.value),
                PowerMetricRow(f"{prefix} IR (Kohm)", umbilical.ir.value),
                cls="ub-col"
            ),
            Div(
                PowerStatusPill(None, umbilical.water_leak, is_ok=(umbilical.water_leak == "No Leak")),
                Div(f"{prefix} IR", cls="power-grey-label"),
                PowerStatusPill(None, umbilical.ir_status, is_ok=(umbilical.ir_status != "LOW IR")),
                cls="ub-col ub-col-status"
            ),
            cls="ub-row"
        ),
        cls="power-panel umb-panel"
    )


# ----------------- IMAGING SCREEN SPECIFIC WIDGETS -----------------

def ImagingToggle(label, is_on, inline=False, id_key=None, toggle_url=None):
    """Toggle switch specific to imaging screen with optional inline styling"""
    t_cls = "toggle-on" if is_on else "toggle-off"
    d_cls = "toggle-dot-on" if is_on else "toggle-dot-off"
    wrapper_cls = "img-toggle-inline" if inline else "img-toggle-block"

    attrs = {"cls": wrapper_cls}
    if id_key:
        attrs["id"] = id_key
        attrs["hx_swap_oob"] = "true"
    if toggle_url:
        attrs["hx_post"] = toggle_url
        attrs["hx_swap"] = "none"

    return Div(
        Span(label, cls="img-toggle-label"),
        Div(
            Div(
                Div(cls=f"toggle-dot {d_cls}"),
                cls=f"toggle-track {t_cls}",
            ),
            Span("ON" if is_on else "OFF", cls="img-toggle-state"),
            cls="img-toggle-controls",
        ),
        **attrs
    )


def LedDimmerSlider(label, value, min_val=0, max_val=10):
    """Horizontal slider for LED Dim% (0-10) with text above and scale below"""
    percent = (value - min_val) / (max_val - min_val) * 100
    percent = max(0, min(100, percent))
    scale_labels = ["0", "2", "4", "6", "8", "10"]
    
    ticks = []
    for i in range(21): # 0, 0.5, 1, 1.5 ... 10. (21 ticks)
        tick_cls = "dim-tick-major" if i % 4 == 0 else "dim-tick-minor"
        ticks.append(Div(cls=f"dim-tick {tick_cls}"))
    tick_row = Div(*ticks, cls="dim-tick-row")
    
    labels = []
    for sl in scale_labels:
        labels.append(Span(sl, cls="dim-scale-label"))
    label_row = Div(*labels, cls="dim-scale-row")

    return Div(
        Span(label, cls="dim-label"),
        Div(
            Div(
                Div(cls="dim-thumb", style=f"left: {percent}%;"),
                Div(cls="dim-fill", style=f"width: {percent}%;"),
                cls="dim-track",
            ),
            tick_row,
            label_row,
            cls="dim-slider-wrap"
        ),
        cls="led-dimmer-slider"
    )


def CameraActionGrid():
    """6 button grid for Iris open/close, zoom etc."""
    return Div(
        Div("Iris close", cls="cam-btn"),
        Div("Zoom in", cls="cam-btn"),
        Div("Iris open", cls="cam-btn"),
        Div("Zoom out", cls="cam-btn"),
        Div("Near", cls="cam-btn"),
        Div("Far", cls="cam-btn"),
        cls="cam-action-grid"
    )


def PanTiltBar(label, value, min_val, max_val, scale_labels):
    """Heavy blue/white horizontal sliders for PAN and TILT"""
    percent = (value - min_val) / (max_val - min_val) * 100
    percent = max(0, min(100, percent))
    
    scale_row = Div(*[Span(sl, cls="pt-scale-label") for sl in scale_labels], cls="pt-scale-row")
    
    return Div(
        Div(
            Span(label, cls="pt-label"),
            Div(fmt_val(value), cls="pt-value-box"),
            Span("deg", cls="pt-unit"),
            Div(cls="pt-indicator-led pt-led-on"),
            cls="pt-header"
        ),
        Div(
            Div(
                Div(cls="pt-thumb", style=f"left: {percent}%;"),
                Div(cls="pt-fill", style=f"width: {percent}%;"),
                cls="pt-track"
            ),
            scale_row,
            cls="pt-slider-wrap"
        ),
        cls="pan-tilt-bar"
    )


def PanTiltPad(pan_val, tilt_val):
    return Div(
        Div(
            Div("T-UP", cls="pt-pad-btn pt-pad-up"),
            Div("P-LFT", cls="pt-pad-btn pt-pad-left"),
            Div(IconHome(), cls="pt-pad-home"),
            Div("P-RGT", cls="pt-pad-btn pt-pad-right"),
            Div("T-DWN", cls="pt-pad-btn pt-pad-down"),
            cls="pt-pad-grid"
        ),
        Div(
            Div("manual", cls="pt-manual-btn"),
            Div(
                Div(
                    Span("PAN", cls="pt-manual-label"),
                    Div(fmt_val(pan_val), cls="pt-manual-input"),
                    Span("Deg", cls="pt-manual-unit"),
                    cls="pt-manual-row"
                ),
                Div(
                    Span("TILT", cls="pt-manual-label"),
                    Div(fmt_val(tilt_val), cls="pt-manual-input"),
                    Span("Deg", cls="pt-manual-unit"),
                    cls="pt-manual-row"
                ),
                cls="pt-manual-inputs"
            ),
            cls="pt-manual-section"
        ),
        cls="pan-tilt-pad"
    )

# ----------------- SENSORS SCREEN SPECIFIC WIDGETS -----------------

def SensorToggleBlock(label, is_on, id_key=None, toggle_url=None):
    """Toggle switch with label above"""
    t_cls = "toggle-on" if is_on else "toggle-off"
    d_cls = "toggle-dot-on" if is_on else "toggle-dot-off"
    
    attrs = {"cls": "sens-toggle-block"}
    if id_key:
        attrs["id"] = id_key
        attrs["hx_swap_oob"] = "true"
    if toggle_url:
        attrs["hx_post"] = toggle_url
        attrs["hx_swap"] = "none"

    return Div(
        Span(label, cls="sens-toggle-label"),
        Div(
            Div(
                Div(cls=f"toggle-dot {d_cls}"),
                cls=f"toggle-track {t_cls}",
            ),
            Span("ON" if is_on else "OFF", cls="sens-toggle-state"),
            cls="sens-toggle-controls"
        ),
        **attrs
    )


def SensorLedStatus(label, is_on):
    """Label above a green/red LED circle"""
    dot_cls = "sens-led-on" if is_on else "sens-led-off"
    return Div(
        Span(label, cls="sens-led-label"),
        Div(
            Div(cls=f"sens-led-dot {dot_cls}"),
            Div(cls="sens-led-rect") if is_on else Div(cls="sens-led-rect-off"),
            cls="sens-led-graphic"
        ),
        cls="sens-led-container"
    )


def AlarmLedStatus(label, is_on):
    """Label above a green/red LED circle with NO rect next to it, used for alarms"""
    dot_cls = "sens-led-on" if is_on else "sens-led-off"
    return Div(
        Span(label, cls="sens-led-label"),
        Div(cls=f"sens-led-dot {dot_cls}"),
        cls="sens-led-container"
    )


def ScientificSensorRowItem(label, port_val, stbd_val, unit=None):
    """Row in the central Scientific Sensors section"""
    return Div(
        Span(label, cls="sci-sens-label"),
        Div(str(port_val), cls="sci-sens-value"),
        Div(str(stbd_val), cls="sci-sens-value"),
        Span(unit, cls="sci-sens-unit") if unit else None,
        cls="sci-sens-row"
    )


def SensorBoxMetric(label, value, unit=None):
    """Right side metrics like Surface INS"""
    return Div(
        Span(label, cls="sens-box-label"),
        Div(fmt_val(value), cls="sens-box-value"),
        Span(unit, cls="sens-box-unit") if unit else None,
        cls="sens-box-row"
    )


def BuzzerPanel(active):
    dot_cls = "sens-led-on buzzer-active" if active else "sens-led-off"
    return Div(
        Div("Buzzer", cls="buzzer-label"),
        Div(cls=f"buzzer-light {dot_cls}"),
        Div("ACK", cls="buzzer-ack-btn"),
        cls="buzzer-panel"
    )


# ----------------- LOGGING SCREEN SPECIFIC WIDGETS -----------------
def LogTable(title, is_event, rows):
    """A scrolling table for Event or Error logging"""
    headers = ["Date", "Time", "Location", "Event" if is_event else "Error"]
    
    header_cells = [Div(h, cls="log-table-th") for h in headers]
    header_row = Div(*header_cells, cls="log-table-header-row")
    
    # We will render 15 empty rows to simulate the grid from the image, filling them as needed
    rendered_rows = []
    for i in range(15):
        if i < len(rows):
            r = rows[i]
            cells = [
                Div(r.date, cls="log-table-td"),
                Div(r.time, cls="log-table-td"),
                Div(r.location, cls="log-table-td"),
                Div(r.message, cls="log-table-td log-table-td-stretch")
            ]
            rendered_rows.append(Div(*cells, cls="log-table-row"))
        else:
            cells = [
                Div("", cls="log-table-td empty"),
                Div("", cls="log-table-td empty"),
                Div("", cls="log-table-td empty"),
                Div("", cls="log-table-td log-table-td-stretch empty")
            ]
            rendered_rows.append(Div(*cells, cls="log-table-row"))
            
    return Div(
        Div(title, cls="log-table-title"),
        Div(
            header_row,
            Div(*rendered_rows, cls="log-table-body"),
            cls="log-table-container"
        ),
        cls="log-panel"
    )


def HorizontalToggle(label, is_on, id_key=None, toggle_url=None):
    """Horizontal toggle: Label -> Switch -> ON/OFF"""
    t_cls = "toggle-on" if is_on else "toggle-off"
    d_cls = "toggle-dot-on" if is_on else "toggle-dot-off"
    
    attrs = {"cls": "h-toggle-wrap"}
    if id_key:
        attrs["id"] = id_key
        attrs["hx_swap_oob"] = "true"
    if toggle_url:
        attrs["hx_post"] = toggle_url
        attrs["hx_swap"] = "none"

    return Div(
        Span(label, cls="h-toggle-label"),
        Div(
            Div(cls=f"toggle-dot {d_cls}"),
            cls=f"toggle-track {t_cls}",
        ),
        Span("ON" if is_on else "OFF", cls="h-toggle-state"),
        **attrs
    )


def RedSignalIndicator(label, is_on):
    """Red circle indicator with label underneath or above"""
    cls_dot = "signal-dot-on" if is_on else "signal-dot-off"
    return Div(
        Span(label, cls="signal-label"),
        Div(cls=f"signal-dot {cls_dot}"),
        cls="signal-indicator"
    )

# ----------------- STATUS SCREEN SPECIFIC WIDGETS -----------------
def StatusChartRowComponent(selected_option, y_labels, x_labels):
    dropdown = Div(
        Span(selected_option, cls="status-dropdown-text"),
        Div(IconChevronDown(), cls="status-dropdown-icon"),
        cls="status-dropdown"
    )
    
    y_axis = Div(*[Span(str(y), cls="status-y-label") for y in reversed(y_labels)], cls="status-y-axis")
    x_axis = Div(*[Span(str(x), cls="status-x-label") for x in x_labels], cls="status-x-axis")
    grid_area = Div(cls="status-grid")
    
    chart_area = Div(
        Div("Amplitude", cls="status-y-title"),
        Div(
            Div(y_axis, grid_area, cls="status-chart-main"),
            Div(x_axis, Div("Time", cls="status-x-title"), cls="status-chart-bottom"),
            cls="status-chart-inner"
        ),
        cls="status-chart-container"
    )
    
    return Div(
        Div(dropdown, cls="status-dropdown-container"),
        chart_area,
        cls="status-row-widget"
    )


# ----------------- 50 KWH SCREEN SPECIFIC WIDGETS -----------------
def KwhDataGrid(title_sub, col_headers, batteries):
    rows_labels = ["CUR", "VOT", "ID Cell Max", "Max Temp", "ID Cell Min", "Min Temp", "Temp", "SOC", "SOH"]
    fields = ["cur", "vot", "id_cell_max", "max_temp", "id_cell_min", "min_temp", "temp", "soc", "soh"]
    
    header_col = Div(Span(""), *[Span(l, cls="kwh-row-label") for l in rows_labels], cls="kwh-label-col")
    
    bat_cols = []
    for i, bat in enumerate(batteries):
        cells = [Span(col_headers[i], cls="kwh-col-header")]
        for f in fields:
            val = getattr(bat, f)
            cells.append(Div(fmt_val(val), cls="kwh-cell-value"))
        bat_cols.append(Div(*cells, cls="kwh-data-col"))
        
    grid_content = Div(header_col, *bat_cols, cls="kwh-grid-content")
    
    return Div(
        Div(title_sub, cls="kwh-grid-subtitle"),
        grid_content,
        cls="kwh-grid-panel"
    )


def KwhVerticalGauge(label, value, min_val, max_val, scale_labels):
    percent = (value - min_val) / (max_val - min_val) * 100
    percent = max(0, min(100, percent))
    
    # scale labels are arranged vertically
    scale_items = [Span(str(sl), cls="kwh-vg-scale-label") for sl in reversed(scale_labels)]
    scale_col = Div(*scale_items, cls="kwh-vg-scale-col")
    
    return Div(
        Span(label, cls="kwh-vg-title"),
        Div(
            scale_col,
            Div(
                Div(cls="kwh-vg-fill", style=f"height: {percent}%;"),
                cls="kwh-vg-track"
            ),
            cls="kwh-vg-body"
        ),
        Div(fmt_val(value), cls="kwh-vg-input"),
        cls="kwh-vg-container"
    )

# ----------------- MCC SCREEN SPECIFIC WIDGETS -----------------
def MccIndicator(label, is_on):
    led_cls = "mcc-led-on" if is_on else "mcc-led-off"
    return Div(
        Span(label, cls="mcc-label"),
        Div(cls=f"mcc-led {led_cls}"),
        cls="mcc-indicator-row"
    )

def MccStatusBox(label, value, bg_color_cls):
    return Div(
        Span(label, cls="mcc-status-label"),
        Div(value, cls=f"mcc-status-box {bg_color_cls}"),
        cls="mcc-status-row"
    )

def MccMessageInput(label, value):
    return Div(
        Span(label, cls="mcc-message-label"),
        Div(value, cls="mcc-message-value"),
        cls="mcc-message-row"
    )

def MccShipData(label, value):
    return Div(
        Span(label, cls="mcc-ship-label"),
        Div(fmt_val(value), cls="mcc-ship-value"),
        cls="mcc-ship-col"
    )

def MccRadioGroup(selected_val):
    def radio_item(val):
        dot_cls = "mcc-radio-dot-on" if val == selected_val else "mcc-radio-dot-off"
        return Div(
            Div(cls=f"mcc-radio-circle {dot_cls}"),
            Span(val, cls="mcc-radio-label"),
            cls="mcc-radio-item"
        )
    return Div(
        Span("Power Status", cls="mcc-power-title"),
        radio_item("Low"),
        radio_item("Medium"),
        radio_item("High"),
        radio_item("Very High"),
        cls="mcc-radio-group"
    )

def MccCrewStatus(label, is_ok):
    bg_cls = "mcc-crew-ok" if is_ok else "mcc-crew-err"
    text = "OK" if is_ok else "ERR"
    return Div(
        Span(label, cls="mcc-crew-label"),
        Div(text, cls=f"mcc-crew-box {bg_cls}"),
        cls="mcc-crew-row"
    )

def MccPowerDropdown(val):
    return Div(
        Span("Power", cls="mcc-dropdown-label"),
        Div(
            Span(val, cls="mcc-dropdown-val"),
            IconChevronDown(),
            cls="mcc-dropdown-box"
        ),
        cls="mcc-dropdown-wrap"
    )
