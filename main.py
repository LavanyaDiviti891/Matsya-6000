from fasthtml.common import Div, Span, Link, H1, to_xml, FastHTML, H2, H3, Title, serve, Form, Input, Select, Option
from starlette.staticfiles import StaticFiles
from models import MatsyaUIState
from components import (
    TopbarInlineMetric,
    VerticalGauge,
    SimpleRpmBox,
    SimpleMetricBox,
    CompassBox,
    SidebarMetric,
    StatusPill,
    ToggleSwitch,
    BottomTabsNav,
    BigNumber,
    LedPanel,
    SemiCircleGauge,
    HorizontalProgressBar,
    SensorStatusPill,
    HSSSLabelInput,
    BallastActionButton,
    BallastPressureRead,
    BallastActSlider,
    VBSTankGauge,
    VBSMetricRow,
    VBSWaterButton,
    VBSSetControl,
    TrimPositionBar,
    SpeedControlSlider,
    OIMToggleRow,
    ThrusterPanel,
    PropCenterToggleBlock,
    PropAxisControl,
    BatteryPanel,
    PDEPanel,
    IDEPanel,
    UmbilicalPanel,
    ImagingToggle,
    LedDimmerSlider,
    CameraActionGrid,
    PanTiltBar,
    PanTiltPad,
    SensorToggleBlock,
    SensorLedStatus,
    AlarmLedStatus,
    ScientificSensorRowItem,
    SensorBoxMetric,
    BuzzerPanel,
    LogTable,
    HorizontalToggle,
    RedSignalIndicator,
    StatusChartRowComponent,
    KwhDataGrid,
    KwhVerticalGauge,
    MccIndicator,
    MccStatusBox,
    MccMessageInput,
    MccShipData,
    MccRadioGroup,
    MccCrewStatus,
    MccPowerDropdown,
)


from scenario import (
    scenario_state,
    reset_scenario,
    run_emg_dropweights_scenario,
    AscendScenario)

import asyncio
import random
import os
import re
import json
import glob
from datetime import datetime


# Favicon + Inter Font + Custom Stylesheet
inter_font = Link(
    href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap",
    rel="stylesheet",
)
custom_css = Link(href="/static/styles.css", rel="stylesheet")

app = FastHTML(exts="ws", hdrs=(inter_font, custom_css))
app.mount("/static", StaticFiles(directory="static"), name="static")
rt = app.route

# ─────────────────────────────────────────────────────────────────────────────
# Global state
# ─────────────────────────────────────────────────────────────────────────────
app_state = MatsyaUIState()
connected_clients = set()
ascend_scenario = AscendScenario()



# ─────────────────────────────────────────────────────────────────────────────
# WebSocket plumbing
# ─────────────────────────────────────────────────────────────────────────────
async def on_conn(ws, send):
    connected_clients.add(send)


async def on_disconn(ws, send):
    connected_clients.discard(send)


@app.ws("/ws", conn=on_conn, disconn=on_disconn)
async def ws_handler(msg: str, send):
    pass


async def broadcast(html_component):
    xml_str = to_xml(html_component)
    for client_send in list(connected_clients):
        try:
            await client_send(xml_str)
        except Exception as e:
            print(f"Broadcast error: {e}")
            connected_clients.discard(client_send)


# ─────────────────────────────────────────────────────────────────────────────
# Scenario Overlay  — rendered as an OOB element (id="scenario-overlay")
# ─────────────────────────────────────────────────────────────────────────────
def ScenarioOverlay():
    sc = scenario_state

    # ── idle: invisible placeholder ───────────────────────────────────────────
    popup_text = ascend_scenario.get_popup()
    
    if not sc.active and sc.success is None and popup_text == "":
        return Div(id="scenario-overlay", hx_swap_oob="true")

 
    # ── DESCEND SOP POPUP PRIORITY ───────────────────────
    if popup_text != "":

        border_color = "#facc15"
        glow_color   = "#facc1544"

        status_text = popup_text

    # ── SUCCESS ──────────────────────────────────────────
    elif sc.success is True:

        border_color = "#00ff88"
        glow_color   = "#00ff8844"

        status_text = "✓ MISSION COMPLETE"

    # ── FAILURE ──────────────────────────────────────────
    elif sc.success is False:

        border_color = "#ff4444"
        glow_color   = "#ff444444"

        status_text = "✗ MISSION FAILED"

    # ── EMERGENCY SCENARIO ───────────────────────────────
    else:

        urgent = sc.active and sc.timer_remaining <= 10

        border_color = (
            "#ff6600"
            if (urgent and sc.blink)
            else "#facc15"
        )

        glow_color = "#facc1544"

        status_text = "⚠ SCENARIO IN PROGRESS"

    # ── timer bar (only while active) ─────────────────────────────────────────
    pct = (
    max(0, sc.timer_remaining / sc.timer_total * 100)
    if sc.timer_total > 0 else 0
    )
    bar_color = "#ff4444" if pct < 20 else ("#facc15" if pct < 50 else "#00ff88")

    timer_bar = Div(
        Div(
            style=(
                f"height:6px; width:{pct:.1f}%; background:{bar_color};"
                "border-radius:3px; transition:width 0.9s linear;"
            )
        ),
        style=(
            "height:6px; width:100%; background:#333; border-radius:3px;"
            "margin-top:10px;"
        ),
    ) if sc.success is None else Div()

    # ── depth + timer readout ─────────────────────────────────────────────────
    metrics = Div(
        Span("DEPTH ", style="color:#aaa; font-size:13px;"),
        Span(
            f"{app_state.header.depth.value:.1f} m",
            style="color:#fff; font-weight:700; font-size:15px; margin-right:20px;",
        ),
        Span("TIME ", style="color:#aaa; font-size:13px;"),
        Span(
            f"{sc.timer_remaining if sc.active else 0}s",
            style=(
                f"color:{'#ff4444' if (sc.active and sc.timer_remaining <= 10) else '#00ff88'};"
                "font-weight:700; font-size:15px;"
            ),
        ),
        style="margin-top:8px;",
    ) if sc.success is None else Div(
        sc.result_message,
        style="color:#ccc; font-size:13px; margin-top:8px; max-width:460px;",
    )

    # ── mission hint (shown while in-progress) ────────────────────────────────
        # ── feedback / SOP status ─────────────────────────────
    if popup_text != "":

        hint = Div(
            "ASCEND SOP ACTIVE",
            style=(
                "font-size:13px;"
                "color:#facc15;"
                "margin-top:6px;"
                "font-weight:700;"
            )
        )

    elif getattr(sc, 'feedback_msg', ''):

        hint = Div(
            sc.feedback_msg,
            style=(
                "font-size:13px;"
                "color:#facc15;"
                "margin-top:6px;"
                "font-weight:700;"
            )
        )

    else:

        hint = Div()

    # ── overlay ────────────────────────────────────────────
    return Div(

        Div(
            *[
                Div(
                    line,
                    style="margin-bottom:4px;"
                )
                for line in status_text.split("\n")
            ],

            style=(
                f"color:{border_color};"
                "font-size:18px;"
                "font-weight:800;"
                "letter-spacing:2px;"
            ),
        ),

        Div(
            "NORMAL ASCEND SOP"
            if popup_text != ""
            else sc.mission_name,

            style=(
                "color:#888;"
                "font-size:12px;"
                "margin-top:3px;"
            )
        ),

        metrics,
        hint,
        timer_bar,

        id="scenario-overlay",
        hx_swap_oob="true",

        style=(
            "position:fixed;"
            "bottom:80px;"
            "left:50%;"
            "transform:translateX(-50%);"
            "background:#0d0d0dee;"
            f"border:1.5px solid {border_color};"
            "border-radius:12px;"
            "padding:16px 28px;"
            "z-index:9999;"
            "text-align:center;"
            "backdrop-filter:blur(8px);"
            "min-width:360px;"
            "max-width:520px;"
            f"box-shadow:0 0 28px {glow_color};"
            "pointer-events:none;"
        ),
    )



# ─────────────────────────────────────────────────────────────────────────────
# UI Views
# ─────────────────────────────────────────────────────────────────────────────
def HeaderArea():
    s = app_state.header
    return Div(
        # Top strip: Dive info + Title + Present Time
        Div(
            Div(
                Div(
                    Span("DIVE #", cls="header-label"),
                    Form(
                        Select(
                            Option("Dive 1", value="1", selected=(s.dive_num == 1)),
                            Option("Dive 2", value="2", selected=(s.dive_num == 2)),
                            Option("Dive 3", value="3", selected=(s.dive_num == 3)),
                            Option("Dive 4", value="4", selected=(s.dive_num == 4)),
                            Option("Dive 5", value="5", selected=(s.dive_num == 5)),
                            Option("Dive 6", value="6", selected=(s.dive_num == 6)),
                            Option("Dive 7", value="7", selected=(s.dive_num == 7)),
                            Option("Dive 8", value="8", selected=(s.dive_num == 8)),
                            Option("Dive 9", value="9", selected=(s.dive_num == 9)),
                            name="dive_num",
                            style="width: 80px; background: transparent; border: 1px solid #333; color: black; text-align: center; font-weight: bold; padding: 2px;",
                            hx_post="/api/sim/set_dive", hx_trigger="change", hx_swap="none"
                        ),
                        style="display: inline-block; margin: 0;"
                    ),
                    cls="header-metric",
                ),
                Div(
                    Span("Mission Run Time", cls="header-label"),
                    Span(s.mission_time, cls="header-value-box mono"),
                    cls="header-metric",
                ),
                cls="header-left",
            ),
            H1("Manned Submersible — MATSYA 6000", cls="header-title"),
            Div(
                Span("Present Time", cls="header-label"),
                Span(s.present_time, cls="header-value-box mono"),
                # Playback controls
                Div(
                    Span("⏮", hx_post="/api/sim/start", hx_swap="none", style="cursor: pointer; user-select: none; margin-right: 5px;"),
                    Span("⏸" if not sim_global.paused else "▶️", hx_post="/api/sim/toggle_pause", hx_swap="none", style="cursor: pointer; user-select: none; margin-right: 5px;", id="play-pause-btn"),
                    Form(
                        Select(
                            Option("1x Speed", value="1", selected=(sim_global.speed == "1")),
                            Option("Max Speed", value="max", selected=(sim_global.speed == "max")),
                            name="speed",
                            style="background: transparent; border: 1px solid #333; color: white; font-size: 12px; cursor: pointer; padding: 2px;",
                            hx_post="/api/sim/set_speed", hx_trigger="change", hx_swap="none"
                        ),
                        style="display: inline-block; margin: 0; margin-right: 5px;"
                    ),
                    Span("⏭", hx_post="/api/sim/end", hx_swap="none", style="cursor: pointer; user-select: none;"),
                    style="display: flex; gap: 5px; margin-top: 5px; font-size: 14px; justify-content: center; background: #111; padding: 2px 10px; border-radius: 4px; border: 1px solid #333; align-items: center;"
                ),
                cls="header-metric",
                style="display: flex; flex-direction: column; align-items: center;"
            ),
            cls="header-top",
        ),
        # Bottom metric strip
        Div(
            TopbarInlineMetric("Heading", s.heading.value, s.heading.unit),
            TopbarInlineMetric("Depth", s.depth.value, s.depth.unit),
            TopbarInlineMetric("Altitude", s.altitude.value, s.altitude.unit),
            TopbarInlineMetric("MB_P SOC", s.mb_p_soc.value, s.mb_p_soc.unit),
            TopbarInlineMetric("MB_S SOC", s.mb_s_soc.value, s.mb_s_soc.unit),
            cls="header-metrics-strip",
        ),
        cls="header-area",
    )


def AppLayout(active_tab="Main"):
    s = app_state

    # ── RIGHT SIDEBAR (shared across tabs) ───────────────────────────────────
    sidebar_col = Div(
        Div(
            SidebarMetric("O₂", s.environment.o2.value, s.environment.o2.unit),
            SidebarMetric("CO₂", s.environment.co2.value, s.environment.co2.unit),
            SidebarMetric("Temp", s.environment.temp.value, s.environment.temp.unit),
            SidebarMetric("Pressure", s.environment.pressure.value, s.environment.pressure.unit),
            cls="sidebar-section",
        ),
        Div(cls="sidebar-divider"),
        Div(
            ToggleSwitch("Joystick", s.sidebar.joystick, id_key="toggle-joystick", toggle_url="/api/toggle_joystick"),
            ToggleSwitch("Thrusters Enable", s.sidebar.thrusters_enable, id_key="toggle-thrusters", toggle_url="/api/toggle_thrusters_enable"),
            ToggleSwitch("High Speed", s.sidebar.high_speed, id_key="toggle-high-speed", toggle_url="/api/toggle_high_speed"),
            cls="sidebar-section",
        ),
        Div(cls="sidebar-divider"),
        Div(
            StatusPill("IR", s.sidebar.ir_ok),
            StatusPill("Water Ingress", is_ok=not s.sidebar.water_ingress, ok_text="CLEAR", err_text="ALERT"),
            StatusPill("Comm", s.sidebar.comm_status, ok_text="Status OK", err_text="Status"),
            cls="sidebar-section",
        ),
        Div(cls="sidebar-divider"),
        LedPanel(s.leds),
        Div(
            Div(
                "OFF" if s.is_powered_on else "ON",
                cls="on-button" + (" power-on" if s.is_powered_on else ""),
                hx_post="/api/toggle_power",
                hx_swap="none",
            ),
            cls="sidebar-footer",
        ),
        cls="col-sidebar",
    )

    # ─────────────────────────────────────────────────────────────────────────
    # MAIN TAB
    # ─────────────────────────────────────────────────────────────────────────
    if active_tab == "Main":
        alt_col = Div(
            VerticalGauge("Altitude", s.header.altitude.value, max_val=10, unit="m",
                          low_is_good=False, scale_labels=list(range(10, -1, -1))),
            cls="col-altitude",
        )

        center_col = Div(
            Div(
                SimpleMetricBox("Roll", s.imu.roll.value),
                SimpleMetricBox("Pitch", s.imu.pitch.value),
                cls="roll-pitch-row",
            ),
            Div(CompassBox(), cls="compass-area"),
            Div(
                BigNumber("Altitude", s.header.altitude.value, "m"),
                BigNumber("Heading_P", s.imu.heading_p.value, "deg"),
                BigNumber("Depth", s.header.depth.value, "m"),
                cls="big-numbers-row",
            ),
            cls="col-center",
        )

        depth_prop_col = Div(
            Div(
                VerticalGauge("Depth", s.header.depth.value, max_val=12, unit="m",
                              low_is_good=True, scale_labels=list(range(-2, 13))),
                cls="depth-gauge-wrap",
            ),
            Div(
                H3("Propulsion", cls="section-title"),
                Div(SimpleRpmBox("T2 RPM", s.propulsion.t2_rpm), SimpleRpmBox("T1 RPM", s.propulsion.t1_rpm), cls="rpm-row"),
                Div(SimpleRpmBox("T3 RPM", s.propulsion.t3_rpm), cls="rpm-row-center"),
                Div(SimpleRpmBox("T4 RPM", s.propulsion.t4_rpm), cls="rpm-row-center"),
                Div(SimpleRpmBox("T5 RPM", s.propulsion.t5_rpm), cls="rpm-row-center"),
                Div(SimpleRpmBox("T8 RPM", s.propulsion.t8_rpm), SimpleRpmBox("T6 RPM", s.propulsion.t6_rpm), cls="rpm-row"),
                Div(SimpleRpmBox("T7 RPM", s.propulsion.t7_rpm), cls="rpm-row-center"),
                Div(cls="prop-separator"),
                Div(
                    SimpleMetricBox("Latitude", s.propulsion.latitude.value, "deg"),
                    SimpleMetricBox("Longitude", s.propulsion.longitude.value, "deg"),
                    cls="latlon-stack",
                ),
                cls="propulsion-panel",
            ),
            cls="col-depth-prop",
        )

        main_content_area = Div(
            Div(alt_col, center_col, depth_prop_col, sidebar_col, cls="main-content"),
            Div(
                SimpleMetricBox("East_speed", s.bottom.east_speed.value, "m/s"),
                SimpleMetricBox("Vert_speed", s.bottom.vert_speed.value, "m/s"),
                SimpleMetricBox("North_Speed", s.bottom.north_speed.value, "m/s"),
                SimpleMetricBox("Ship Heading", s.bottom.ship_heading.value, "deg"),
                cls="bottom-speed-strip",
            ),
            cls="main-content-wrapper",
        )

    # ─────────────────────────────────────────────────────────────────────────
    # HSSS TAB
    # ─────────────────────────────────────────────────────────────────────────
    elif active_tab == "HSSS":

        def render_hsss_panel(title, side_data, sf_suffix):
            return Div(
                Div(title, cls="hsss-panel-title"),
                Div(
                    SemiCircleGauge(f"CO2{sf_suffix}", side_data.co2.value, 0, 5000, "ppm",
                                    scale_labels=["0", "1000", "2000", "3000", "4000", "5000"]),
                    SemiCircleGauge(f"Oxygen{sf_suffix}", side_data.oxygen.value, 19, 25, "% v/v",
                                    scale_labels=["19", "20", "21", "22", "23", "24", "25"], is_oxygen=True),
                    cls="hsss-gauges-row",
                ),
                Div(
                    Div(
                        HorizontalProgressBar(f"Pressure in mbar{sf_suffix}", side_data.pressure.value, 800, 1200, "",
                                              scale_labels=["800","850","900","950","1000","1050","1100","1150","1200"]),
                        HorizontalProgressBar(f"Temp in Deg C{sf_suffix}", side_data.temp.value, 0, 100, "",
                                              scale_labels=["0","10","20","30","40","50","60","70","80","90","100"]),
                        HorizontalProgressBar(f"Humidity{sf_suffix} in %", side_data.humidity.value, 0, 100, "",
                                              scale_labels=["0","10","20","30","40","50","60","70","80","90","100"]),
                        cls="hsss-col-left",
                    ),
                    Div(
                        SensorStatusPill(f"Smoke Sensor{sf_suffix.lower()}", side_data.smoke_sensor, is_ok=(side_data.smoke_sensor == "NO SMOKE")),
                        SensorStatusPill(f"Flame Sensor{sf_suffix.lower()}", side_data.flame_sensor, is_ok=(side_data.flame_sensor == "NO FLAME")),
                        SensorStatusPill(f"Heat Sensor{sf_suffix.lower()}", side_data.heat_sensor, is_ok=(side_data.heat_sensor == "Normal")),
                        HSSSLabelInput(f"Hydrogen{sf_suffix}", side_data.hydrogen.value, "%"),
                        HSSSLabelInput(f"LP_L Pressure{sf_suffix}", side_data.lp_l_pressure.value, "bar"),
                        cls="hsss-col-right",
                    ),
                    cls="hsss-two-col",
                ),
                Div(
                    HSSSLabelInput(f"HP_B1 Pressure{sf_suffix}", side_data.hp_b1_pressure.value, "bar"),
                    HSSSLabelInput(f"HP_B2 Pressure{sf_suffix}", side_data.hp_b2_pressure.value, "bar"),
                    HSSSLabelInput(f"HP_B3 Pressure{sf_suffix}", side_data.hp_b3_pressure.value, "bar"),
                    cls="hsss-bottom-row",
                ),
                cls="hsss-panel",
            )

        main_content_area = Div(
            Div(
                Div(render_hsss_panel("HSSS_P", s.hsss.p, "_P"), render_hsss_panel("HSSS_S", s.hsss.s, "_S"), cls="hsss-content-row"),
                sidebar_col,
                cls="main-content",
            ),
            cls="main-content-wrapper",
        )

    # ─────────────────────────────────────────────────────────────────────────
    # BALLAST TAB
    # ─────────────────────────────────────────────────────────────────────────
    elif active_tab == "Ballast":
        b = s.ballast

        main_ballast_panel = Div(
            Div(
                BallastActionButton("Ready to Dive open"),
                BallastActionButton("Ready to Dive Close"),
                BallastActionButton("Dive open"),
                BallastActionButton("Dive Close"),
                BallastActionButton("Surface open"),
                BallastActionButton("Surface Close"),
                cls="ballast-btn-grid",
            ),
            Div(
                Div(
                    BallastPressureRead("Read Pressure_S", b.main_ballast.read_pressure_s, b.main_ballast.pressure_s_enable, id_key="tog-bpr-s", toggle_url="/api/toggle/ballast.main_ballast.pressure_s_enable"),
                    BallastPressureRead("Read Pressure_P", b.main_ballast.read_pressure_p, b.main_ballast.pressure_p_enable, id_key="tog-bpr-p", toggle_url="/api/toggle/ballast.main_ballast.pressure_p_enable"),
                    cls="ballast-pressure-col",
                ),
                Div("Main\nBallast\nSystem", cls="ballast-main-label"),
                cls="ballast-mid-row",
            ),
            BallastActSlider("ACT 3 pos",  b.main_ballast.act3_pos),
            BallastActSlider("ACT 3 pos 2", b.main_ballast.act3_pos2),
            BallastActSlider("ACT 3 pos 3", b.main_ballast.act3_pos3),
            cls="ballast-main-panel",
        )

        vbs_panel = Div(
            Div("VBS", cls="vbs-panel-title"),
            Div(
                Div(
                    Div(
                        Div("VBS_HPU_Enable", cls="vbs-hpu-label"),
                        Div("HPU ON" if b.vbs.hpu_enable else "HPU OFF", cls="vbs-hpu-btn" + (" vbs-hpu-on" if b.vbs.hpu_enable else "")),
                        cls="vbs-hpu-row",
                    ),
                    VBSMetricRow("HPU Pressure", b.vbs.hpu_pressure.value, "bar"),
                    VBSMetricRow("HPU temp", b.vbs.hpu_temp.value, "deg C"),
                    VBSWaterButton("Water IN"),
                    VBSWaterButton("Water OUT"),
                    VBSSetControl(b.vbs.vbs_set),
                    cls="vbs-left-col",
                ),
                VBSTankGauge(b.vbs.tank_level),
                cls="vbs-content-row",
            ),
            cls="ballast-vbs-panel",
        )

        trim_panel = Div(
            Div(
                Div("Trim Position (mm)", cls="trim-position-label"),
                Div("TRIM", cls="trim-title"),
                cls="trim-header",
            ),
            TrimPositionBar(b.trim.position_mm),
            Div(
                Div(ToggleSwitch("power", b.trim.power, id_key="tog-trim-pwr", toggle_url="/api/toggle/ballast.trim.power"), cls="trim-toggle-col"),
                Div(SimpleMetricBox("Voltage", b.trim.voltage.value, "V"), SimpleMetricBox("Current", b.trim.current.value, "A"), cls="trim-metrics-left"),
                Div(SimpleMetricBox("Temp", b.trim.temp.value, "deg C"), SimpleMetricBox("speed", b.trim.speed.value, "mm/min"), cls="trim-metrics-right"),
                Div(ToggleSwitch("CW/CCW", b.trim.cw_ccw, id_key="tog-trim-cw", toggle_url="/api/toggle/ballast.trim.cw_ccw"), cls="trim-toggle-col"),
                cls="trim-metrics-row",
            ),
            cls="ballast-trim-panel",
        )

        oim_panel = Div(
            SpeedControlSlider(b.trim.speed_control),
            Div(
                OIMToggleRow("OIM_S1_Ext_Reset", b.oim.s1_ext_reset, id_key="tog-oim-s1e", toggle_url="/api/toggle/ballast.oim.s1_ext_reset"),
                OIMToggleRow("OIM_S2_Int_Reset", b.oim.s2_int_reset, id_key="tog-oim-s2i", toggle_url="/api/toggle/ballast.oim.s2_int_reset"),
                OIMToggleRow("OIM_P1_Ext_Reset", b.oim.p1_ext_reset, id_key="tog-oim-p1e", toggle_url="/api/toggle/ballast.oim.p1_ext_reset"),
                OIMToggleRow("OIM_P2_Int_Reset", b.oim.p2_int_reset, id_key="tog-oim-p2i", toggle_url="/api/toggle/ballast.oim.p2_int_reset"),
                cls="oim-toggles-col",
            ),
            cls="ballast-oim-panel",
        )

        main_content_area = Div(
            Div(
                Div(
                    Div(main_ballast_panel, vbs_panel, cls="ballast-top-row"),
                    Div(trim_panel, oim_panel, cls="ballast-bottom-row"),
                    cls="ballast-content-col",
                ),
                sidebar_col,
                cls="main-content",
            ),
            cls="main-content-wrapper",
        )

    # ─────────────────────────────────────────────────────────────────────────
    # PROPULSION TAB
    # ─────────────────────────────────────────────────────────────────────────
    elif active_tab == "Propulsion":
        pd = s.propulsion_detail

        left_col     = Div(ThrusterPanel(2, pd.t2), ThrusterPanel(4, pd.t4), cls="prop-thruster-col")
        mid_left_col = Div(ThrusterPanel(6, pd.t6), ThrusterPanel(8, pd.t8), cls="prop-thruster-col")

        center_col = Div(
            Div("POWER / ENABLE", cls="prop-center-header"),
            PropCenterToggleBlock(2, pd.t2.power, pd.t2.enable, toggle_url_p="/api/toggle/propulsion_detail.t2.power", toggle_url_e="/api/toggle/propulsion_detail.t2.enable"),
            PropCenterToggleBlock(6, pd.t6.power, pd.t6.enable, toggle_url_p="/api/toggle/propulsion_detail.t6.power", toggle_url_e="/api/toggle/propulsion_detail.t6.enable"),
            PropCenterToggleBlock(5, pd.t5.power, pd.t5.enable, toggle_url_p="/api/toggle/propulsion_detail.t5.power", toggle_url_e="/api/toggle/propulsion_detail.t5.enable"),
            PropCenterToggleBlock(1, pd.t1.power, pd.t1.enable, toggle_url_p="/api/toggle/propulsion_detail.t1.power", toggle_url_e="/api/toggle/propulsion_detail.t1.enable"),
            PropCenterToggleBlock(4, pd.t4.power, pd.t4.enable, toggle_url_p="/api/toggle/propulsion_detail.t4.power", toggle_url_e="/api/toggle/propulsion_detail.t4.enable"),
            PropCenterToggleBlock(8, pd.t8.power, pd.t8.enable, toggle_url_p="/api/toggle/propulsion_detail.t8.power", toggle_url_e="/api/toggle/propulsion_detail.t8.enable"),
            PropCenterToggleBlock(7, pd.t7.power, pd.t7.enable, toggle_url_p="/api/toggle/propulsion_detail.t7.power", toggle_url_e="/api/toggle/propulsion_detail.t7.enable"),
            PropCenterToggleBlock(3, pd.t3.power, pd.t3.enable, toggle_url_p="/api/toggle/propulsion_detail.t3.power", toggle_url_e="/api/toggle/propulsion_detail.t3.enable"),
            cls="prop-center-col",
        )

        mid_right_col = Div(ThrusterPanel(5, pd.t5), ThrusterPanel(7, pd.t7), cls="prop-thruster-col")
        right_col     = Div(ThrusterPanel(1, pd.t1), ThrusterPanel(3, pd.t3), cls="prop-thruster-col")

        main_content_area = Div(
            Div(
                Div(
                    left_col, mid_left_col, center_col, mid_right_col, right_col, sidebar_col,
                    cls="main-content",
                ),
                Div(
                    PropAxisControl("Heading ctrl", pd.heading_ctrl),
                    PropAxisControl("Fwd ctrl", pd.fwd_ctrl),
                    PropAxisControl("Lat ctrl", pd.lat_ctrl),
                    PropAxisControl("Vertical ctrl", pd.vertical_ctrl),
                    Div(
                        Span("🐢", cls="prop-speed-icon"),
                        Span(str(pd.speed_factor), cls="prop-speed-value"),
                        Span("speed factor", cls="prop-speed-label"),
                        cls="prop-speed-factor",
                    ),
                    cls="prop-bottom-strip",
                ),
                cls="prop-content-wrapper",
            ),
            cls="main-content-wrapper",
        )

    # ─────────────────────────────────────────────────────────────────────────
    # POWER TAB
    # ─────────────────────────────────────────────────────────────────────────
    elif active_tab == "POWER":
        p = s.power

        row1 = Div(
            BatteryPanel("MB_P",  "MB_P",  p.mb_p,  ["100","120","140","160","180"], 100, 180),
            BatteryPanel("AUX_P", "AUX_P", p.aux_p, ["0","10","20","30","40"],       0,   40),
            BatteryPanel("MB_S",  "MB_S",  p.mb_s,  ["100","120","140","160","180"], 100, 180),
            BatteryPanel("AUX_S", "AUX_S", p.aux_s, ["0","10","20","30","40"],       0,   40),
            cls="power-row"
        )
        row2 = Div(
            PDEPanel("PDE_P", "PDE_P", p.pde_p),
            IDEPanel("IDE_P", "IDE_P", p.ide_p),
            PDEPanel("PDE_S", "PDE_S", p.pde_s),
            IDEPanel("IDE_S", "IDE_S", p.ide_s),
            cls="power-row"
        )
        row3 = Div(
            UmbilicalPanel("UB_Port", "PSP", p.ub_port),
            UmbilicalPanel("UB_Stbd", "PSS", p.ub_stbd),
            cls="power-row power-row-bottom"
        )

        main_content_area = Div(
            Div(
                Div(row1, row2, row3, cls="power-grid-container"),
                sidebar_col,
                cls="main-content",
            ),
            cls="main-content-wrapper",
        )

    # ─────────────────────────────────────────────────────────────────────────
    # IMAGING TAB
    # ─────────────────────────────────────────────────────────────────────────
    elif active_tab == "Imaging":
        img = s.imaging

        led_p_col = Div(
            Div(
                ImagingToggle("LED P1", img.led_p1.power, id_key="tog-led-p1", toggle_url="/api/toggle/imaging.led_p1.power"),
                ImagingToggle("LED P2", img.led_p2.power, id_key="tog-led-p2", toggle_url="/api/toggle/imaging.led_p2.power"),
                ImagingToggle("LED P3", img.led_p3.power, id_key="tog-led-p3", toggle_url="/api/toggle/imaging.led_p3.power"),
                cls="img-toggle-block"
            ),
            Div(
                LedDimmerSlider("led 3 Dim%(10x)", img.led_p1.dim),
                LedDimmerSlider("led 5 Dim%(10x)", img.led_p2.dim),
                LedDimmerSlider("led 7 Dim%(10x)", img.led_p3.dim),
                cls="img-toggle-block"
            ),
            cls="img-led-row"
        )
        led_s_col = Div(
            Div(
                ImagingToggle("LED S1", img.led_s1.power, id_key="tog-led-s1", toggle_url="/api/toggle/imaging.led_s1.power"),
                ImagingToggle("LED S2", img.led_s2.power, id_key="tog-led-s2", toggle_url="/api/toggle/imaging.led_s2.power"),
                ImagingToggle("LED S3", img.led_s3.power, id_key="tog-led-s3", toggle_url="/api/toggle/imaging.led_s3.power"),
                cls="img-toggle-block"
            ),
            Div(
                LedDimmerSlider("led 4 Dim%(10x)", img.led_s1.dim),
                LedDimmerSlider("led 6 Dim%(10x)", img.led_s2.dim),
                LedDimmerSlider("led 8 Dim%(10x)", img.led_s3.dim),
                cls="img-toggle-block"
            ),
            cls="img-led-row"
        )
        led_section = Div(
            Div("LED Controls", cls="img-panel-title"),
            Div(
                Div(Div("Underwater LED_P", style="font-size:12px; font-weight:700; color:var(--color-text); text-align:center;"), led_p_col, cls="img-col-main"),
                Div(Div("Underwater LED_S", style="font-size:12px; font-weight:700; color:var(--color-text); text-align:center;"), led_s_col, cls="img-col-main"),
                cls="img-top-row"
            ),
            cls="img-panel"
        )

        cam_section = Div(
            Div("Camera Controls", cls="img-panel-title"),
            Div(
                Div(
                    ImagingToggle("HD camera P", img.hd_camera_p, inline=True, id_key="tog-hd-cam-p", toggle_url="/api/toggle/imaging.hd_camera_p"),
                    Div(
                        Div(ImagingToggle("HD SDI_P1", img.hd_sdi_p1, id_key="tog-hd-sdi-p1", toggle_url="/api/toggle/imaging.hd_sdi_p1"), ImagingToggle("HD SDI_P2", img.hd_sdi_p2, id_key="tog-hd-sdi-p2", toggle_url="/api/toggle/imaging.hd_sdi_p2"), cls="sdi-col"),
                        Div(ImagingToggle("HD SDI_P3", img.hd_sdi_p3, id_key="tog-hd-sdi-p3", toggle_url="/api/toggle/imaging.hd_sdi_p3"), ImagingToggle("HD SDI_P4", img.hd_sdi_p4, id_key="tog-hd-sdi-p4", toggle_url="/api/toggle/imaging.hd_sdi_p4"), cls="sdi-col"),
                        cls="sdi-grid"
                    ),
                    Div("HD Camera_P", style="font-size:14px; font-weight:800; color:var(--color-text); text-align:center; margin-bottom:8px;"),
                    CameraActionGrid(),
                    cls="img-cam-col"
                ),
                Div(
                    ImagingToggle("HD camera S", img.hd_camera_s, inline=True, id_key="tog-hd-cam-s", toggle_url="/api/toggle/imaging.hd_camera_s"),
                    Div(
                        Div(ImagingToggle("HD Camera S2", img.hd_camera_s2, inline=True, id_key="tog-hd-cam-s2", toggle_url="/api/toggle/imaging.hd_camera_s2"), ImagingToggle("HD SDI_S1", img.hd_sdi_s1, inline=True, id_key="tog-hd-sdi-s1", toggle_url="/api/toggle/imaging.hd_sdi_s1"), cls="sdi-col"),
                        Div(ImagingToggle("HD SDI_S2", img.hd_sdi_s2, inline=True, id_key="tog-hd-sdi-s2", toggle_url="/api/toggle/imaging.hd_sdi_s2"), ImagingToggle("HD SDI_S3", img.hd_sdi_s3, inline=True, id_key="tog-hd-sdi-s3", toggle_url="/api/toggle/imaging.hd_sdi_s3"), cls="sdi-col"),
                        cls="sdi-grid"
                    ),
                    Div("HD Camera _S", style="font-size:14px; font-weight:800; color:var(--color-text); text-align:center; margin-bottom:8px;"),
                    CameraActionGrid(),
                    cls="img-cam-col"
                ),
                cls="img-cam-grid"
            ),
            cls="img-panel"
        )

        left_col = Div(led_section, cam_section, cls="img-col-main")

        pt = img.pt_p1
        right_col = Div(
            Div(
                PanTiltBar("PAN", pt.pan, -170, 170, ["-170", "-100", "0", "100", "170"]),
                PanTiltBar("TILT", pt.tilt, -50, 110, ["-50", "0", "50", "110"]),
                cls="img-panel img-pt-panel"
            ),
            Div(
                Div(Div("Pan&Tilt P1", cls="pt-tab active"), Div("Pan &Tilt S1", cls="pt-tab"), Div("Pan& Tilt S2", cls="pt-tab"), cls="pt-tabs-row"),
                Div("PnT CTRL P1", style="font-size:14px; font-weight:800; color:var(--color-text); padding:10px 0 0 0; text-align:center;"),
                PanTiltPad(pt.pan, pt.tilt),
                cls="img-panel", style="margin-top:0;"
            ),
            cls="img-col-right"
        )

        main_content_area = Div(
            Div(Div(left_col, right_col, cls="img-layout-row"), sidebar_col, cls="main-content"),
            cls="main-content-wrapper"
        )

    # ─────────────────────────────────────────────────────────────────────────
    # SENSORS TAB
    # ─────────────────────────────────────────────────────────────────────────
    elif active_tab == "Sensors":
        sens = s.sensors

        port_toggles = Div(
            Div("Port side", cls="sens-panel-title"),
            SensorToggleBlock("Depth Sensor Pri", sens.toggles.depth_sensor_pri, id_key="tog-sens-ds-pri", toggle_url="/api/toggle/sensors.toggles.depth_sensor_pri"),
            SensorToggleBlock("INS", sens.toggles.ins, id_key="tog-sens-ins", toggle_url="/api/toggle/sensors.toggles.ins"),
            SensorToggleBlock("CTDO", sens.toggles.ctdo, id_key="tog-sens-ctdo", toggle_url="/api/toggle/sensors.toggles.ctdo"),
            SensorToggleBlock("DVL", sens.toggles.dvl, id_key="tog-sens-dvl", toggle_url="/api/toggle/sensors.toggles.dvl"),
            SensorToggleBlock("Multibeam Sonar", sens.toggles.multibeam_sonar, id_key="tog-sens-mbs1", toggle_url="/api/toggle/sensors.toggles.multibeam_sonar"),
            cls="sens-panel"
        )
        stbd_toggles = Div(
            Div("Starboard", cls="sens-panel-title"),
            SensorToggleBlock("Altimeter", sens.toggles.altimeter, id_key="tog-sens-alt", toggle_url="/api/toggle/sensors.toggles.altimeter"),
            SensorToggleBlock("Dissolved O2", sens.toggles.dissolved_o2, id_key="tog-sens-do2", toggle_url="/api/toggle/sensors.toggles.dissolved_o2"),
            SensorToggleBlock("CTDO_S", sens.toggles.ctdo_s, id_key="tog-sens-ctdo-s", toggle_url="/api/toggle/sensors.toggles.ctdo_s"),
            SensorToggleBlock("MBS", sens.toggles.mbs, id_key="tog-sens-mbs2", toggle_url="/api/toggle/sensors.toggles.mbs"),
            SensorToggleBlock("IMG SONAR", sens.toggles.img_sonar, id_key="tog-sens-img-sonar", toggle_url="/api/toggle/sensors.toggles.img_sonar"),
            cls="sens-panel"
        )
        wi_p    = Div(Div("Water Ingress_p", cls="sens-panel-title"), SensorLedStatus("WI PS_P", sens.indicators.wi_ps_p), SensorLedStatus("WI IDE_P", sens.indicators.wi_ide_p), SensorLedStatus("WI PDE_P", sens.indicators.wi_pde_p), cls="sens-panel sens-panel-clear")
        ins_p   = Div(Div("Insulation_P", cls="sens-panel-title"), SensorLedStatus("IR UB_P", sens.indicators.ir_ub_p), SensorLedStatus("IR IDE_P", sens.indicators.ir_ide_p), SensorLedStatus("IR PDE_P INT", sens.indicators.ir_pde_p_int), SensorLedStatus("IR PDE_P EXT", sens.indicators.ir_pde_p_ext), SensorLedStatus("IR PDE 148_P", sens.indicators.ir_pde_148_p), cls="sens-panel sens-panel-clear")
        sensor_alarm_p = Div(Div("Sensor Alarm", cls="sens-panel-title"), AlarmLedStatus("O2 alarm", sens.indicators.o2_alarm), AlarmLedStatus("Co2 alarm", sens.indicators.co2_alarm), AlarmLedStatus("Pressure 2", sens.indicators.pressure_2), AlarmLedStatus("Altitude_P", sens.indicators.altitude_p), AlarmLedStatus("Depth alarm", sens.indicators.depth_alarm), cls="sens-panel sens-panel-clear")

        warning_panel = Div(
            Div("Warning and Alarm Panel", cls="warning-panel-title"),
            Div(
                BuzzerPanel(sens.buzzer_active),
                Div(
                    SensorToggleBlock("Laser Light 2", sens.toggles.laser_light_2, id_key="tog-sens-ll2", toggle_url="/api/toggle/sensors.toggles.laser_light_2"),
                    SensorToggleBlock("Pan and Tilt P1", sens.toggles.pan_and_tilt_p1, id_key="tog-sens-pt-p1", toggle_url="/api/toggle/sensors.toggles.pan_and_tilt_p1"),
                    SensorToggleBlock("Pan and Tilt S1", sens.toggles.pan_and_tilt_s1, id_key="tog-sens-pt-s1", toggle_url="/api/toggle/sensors.toggles.pan_and_tilt_s1"),
                    SensorToggleBlock("Pan and Tilt S2", sens.toggles.pan_and_tilt_s2, id_key="tog-sens-pt-s2", toggle_url="/api/toggle/sensors.toggles.pan_and_tilt_s2"),
                    cls="warning-toggles"
                ),
                cls="warning-panel-content"
            ),
            cls="warning-panel-section"
        )

        ins_s = Div(Div("Insulation_S", cls="sens-panel-title"), SensorLedStatus("IR UB_S", sens.indicators.ir_ub_s), SensorLedStatus("IR IDE_S", sens.indicators.ir_ide_s), SensorLedStatus("IR PDE_S INT", sens.indicators.ir_pde_s_int), SensorLedStatus("IR PDE_S EXT", sens.indicators.ir_pde_s_ext), SensorLedStatus("IR PDE 148_S", sens.indicators.ir_pde_148_s), cls="sens-panel sens-panel-clear")
        wi_s  = Div(Div("Water Ingress_S", cls="sens-panel-title"), SensorLedStatus("WI PS_S", sens.indicators.wi_ps_s), SensorLedStatus("WI IDE_S", sens.indicators.wi_ide_s), SensorLedStatus("WI PDE_S", sens.indicators.wi_pde_s), cls="sens-panel sens-panel-clear")

        sci = sens.scientific
        sci_table = Div(
            Div(Span("CTDO Sensor", cls="sci-sens-header-sub"), Span("Scientific Sensors", cls="sci-sens-main-title"), cls="sci-sens-top"),
            Div(Span("", cls="sci-sens-th"), Span("Port", cls="sci-sens-th text-center"), Span("Stbd", cls="sci-sens-th text-center"), Span("", cls="sci-sens-th"), cls="sci-sens-table-header"),
            ScientificSensorRowItem("Conductivity", sci.conductivity.port, sci.conductivity.stbd, "S/m"),
            ScientificSensorRowItem("Salinity", sci.salinity.port, sci.salinity.stbd, "PSU"),
            ScientificSensorRowItem("Water denisty", sci.water_density.port, sci.water_density.stbd, "kg/m3"),
            ScientificSensorRowItem("Turbidity", sci.turbidity.port, sci.turbidity.stbd, "NTU"),
            ScientificSensorRowItem("pH", sci.ph.port, sci.ph.stbd, ""),
            ScientificSensorRowItem("CTD Temp", sci.ctd_temp.port, sci.ctd_temp.stbd, "DegC"),
            ScientificSensorRowItem("Pressure", sci.pressure.port, sci.pressure.stbd, ""),
            ScientificSensorRowItem("Dissolved Oxygen", sci.dissolved_oxygen.port, sci.dissolved_oxygen.stbd, "uM"),
            ScientificSensorRowItem("ORP", sci.orp.port, sci.orp.stbd, ""),
            cls="sci-sens-table"
        )

        surf = sens.surface_ins
        surf_ins_panel = Div(
            Div("Surface INS", cls="sens-right-title"),
            SensorBoxMetric("S_Roll", surf.s_roll, "deg"), SensorBoxMetric("S_Pitch", surf.s_pitch, "deg"),
            SensorBoxMetric("S_Heading", surf.s_heading, "deg"), SensorBoxMetric("S_Speed1", surf.s_speed1, "m/s"),
            SensorBoxMetric("S_Speed2", surf.s_speed2, "m/s"), SensorBoxMetric("S_Speed3", surf.s_speed3, "m/s"),
            SensorBoxMetric("S_Latitude", surf.s_latitude, ""), SensorBoxMetric("S_Longitude", surf.s_longitude, ""),
            cls="sens-right-panel"
        )
        ssg = sens.subsea_gps
        subsea_panel = Div(Div("SubSea GPS", cls="sens-right-title"), SensorBoxMetric("GPS Latitude", ssg.gps_latitude, ""), SensorBoxMetric("GPS Longitude", ssg.gps_longitude, ""), cls="sens-right-panel sens-subsea")
        redt = sens.redt_depth
        redt_panel   = Div(Div("Redt Depth Sensor", cls="sens-right-title"), SensorBoxMetric("S_Depth", redt.s_depth, "m"), cls="sens-right-panel sens-redt")

        top_row    = Div(Div(port_toggles, stbd_toggles, cls="sens-toggles-pair"), sci_table, Div(surf_ins_panel, subsea_panel, redt_panel, cls="sens-right-stack"), cls="sens-top-area")
        bottom_row = Div(wi_p, ins_p, sensor_alarm_p, warning_panel, ins_s, wi_s, cls="sens-bottom-area")

        main_content_area = Div(
            Div(Div(top_row, bottom_row, cls="sens-dashboard"), sidebar_col, cls="main-content"),
            cls="main-content-wrapper"
        )

    # ─────────────────────────────────────────────────────────────────────────
    # LOGGING TAB
    # ─────────────────────────────────────────────────────────────────────────
    elif active_tab == "Logging":
        log_state = s.logging
        t = log_state.toggles

        tables_row = Div(LogTable("Event Logging", True, log_state.events), LogTable("Error Logging", False, log_state.errors), cls="logging-tables-row")

        toggles_left = Div(
            Div(HorizontalToggle("148 V LED S1", t.led_s1_148v, id_key="tog-log-led-s1", toggle_url="/api/toggle/logging.toggles.led_s1_148v"), HorizontalToggle("148 V LED S2", t.led_s2_148v, id_key="tog-log-led-s2", toggle_url="/api/toggle/logging.toggles.led_s2_148v"), cls="log-tog-col"),
            Div(HorizontalToggle("148 V LED S3", t.led_s3_148v, id_key="tog-log-led-s3", toggle_url="/api/toggle/logging.toggles.led_s3_148v"), HorizontalToggle("148 V LED S4", t.led_s4_148v, id_key="tog-log-led-s4", toggle_url="/api/toggle/logging.toggles.led_s4_148v"), cls="log-tog-col"),
            Div(HorizontalToggle("148 V LED P1", t.led_p1_148v, id_key="tog-log-led-p1", toggle_url="/api/toggle/logging.toggles.led_p1_148v"), HorizontalToggle("148 V LED P2", t.led_p2_148v, id_key="tog-log-led-p2", toggle_url="/api/toggle/logging.toggles.led_p2_148v"), cls="log-tog-col"),
            Div(HorizontalToggle("148 V LED P3", t.led_p3_148v, id_key="tog-log-led-p3", toggle_url="/api/toggle/logging.toggles.led_p3_148v"), HorizontalToggle("148 V LED P4", t.led_p4_148v, id_key="tog-log-led-p4", toggle_url="/api/toggle/logging.toggles.led_p4_148v"), cls="log-tog-col"),
            cls="log-toggles-left"
        )
        toggles_right = Div(
            Div(HorizontalToggle("Trim_S", t.trim_s, id_key="tog-log-trim-s", toggle_url="/api/toggle/logging.toggles.trim_s"), RedSignalIndicator("Trim_S signal", t.trim_s_signal), cls="log-tog-group"),
            Div(HorizontalToggle("PDE_P 1", t.pde_p_1, id_key="tog-log-pde-1", toggle_url="/api/toggle/logging.toggles.pde_p_1"), RedSignalIndicator("PDE_P signal", t.pde_p_signal), HorizontalToggle("PDE_P 2", t.pde_p_2, id_key="tog-log-pde-2", toggle_url="/api/toggle/logging.toggles.pde_p_2"), cls="log-tog-group-center"),
            Div(HorizontalToggle("Trim_P", t.trim_p, id_key="tog-log-trim-p", toggle_url="/api/toggle/logging.toggles.trim_p"), RedSignalIndicator("Trim_P signal", t.trim_p_signal), cls="log-tog-group"),
            cls="log-toggles-right"
        )

        main_content_area = Div(
            Div(Div(tables_row, Div(toggles_left, toggles_right, cls="log-toggles-panel"), cls="logging-dashboard"), sidebar_col, cls="main-content"),
            cls="main-content-wrapper"
        )

    # ─────────────────────────────────────────────────────────────────────────
    # STATUS TAB
    # ─────────────────────────────────────────────────────────────────────────
    elif active_tab == "Status":
        status_state = s.status
        row1 = StatusChartRowComponent(status_state.chart1_selection, [-45, -20, 0, 20, 45], [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 57])
        row2 = StatusChartRowComponent(status_state.chart2_selection, [-15, -10, 0, 10, 15], [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 57])

        main_content_area = Div(
            Div(Div(row1, row2, cls="status-dashboard"), sidebar_col, cls="main-content"),
            cls="main-content-wrapper"
        )

    # ─────────────────────────────────────────────────────────────────────────
    # 50 KWH TAB
    # ─────────────────────────────────────────────────────────────────────────
    elif active_tab == "50 Kwh":
        kwh = s.kwh
        port_bats = [kwh.port.bat1, kwh.port.bat2, kwh.port.bat3, kwh.port.bat4, kwh.port.bat5]
        stbd_bats = [kwh.stbd.bat6, kwh.stbd.bat7, kwh.stbd.bat8, kwh.stbd.bat9, kwh.stbd.bat10]

        port_grid = KwhDataGrid("port side", ["BAT 1","BAT 2","BAT 3","BAT 4","BAT 5"], port_bats)
        stbd_grid = KwhDataGrid("starboard side", ["BAT 6","BAT 7","BAT 8","BAT 9","BAT 10"], stbd_bats)

        center_toggles = Div(
            Div(Div("VBS_Enable_sig", cls="kwh-sig-label"), Div(cls=f"kwh-sig-dot {'signal-dot-on' if kwh.vbs_enable_sig else 'signal-dot-off'}"), cls="kwh-sig-row"),
            Div(Div("Trim_Enable_sig", cls="kwh-sig-label"), Div(cls=f"kwh-sig-dot {'signal-dot-on' if kwh.trim_enable_sig else 'signal-dot-off'}"), cls="kwh-sig-row"),
            ToggleSwitch("Trim_Enable", kwh.trim_enable, id_key="tog-kwh-trim", toggle_url="/api/toggle/kwh.trim_enable"),
            cls="kwh-center-toggles"
        )

        top_section = Div(port_grid, center_toggles, stbd_grid, cls="kwh-top-section")

        pg = kwh.port_gauges
        sg = kwh.stbd_gauges
        port_gauges_row = Div(KwhVerticalGauge("BAT VOL", pg.vol, 100, 170, [100,120,140,160,170]), KwhVerticalGauge("BAT TEMP", pg.temp, 0, 50, [0,25,50]), KwhVerticalGauge("BAT SOC", pg.soc, 0, 200, [0,50,100,150,200]), KwhVerticalGauge("BAT CUR", pg.cur, 0, 100, [0,25,50,75,100]), cls="kwh-gauges-row")
        stbd_gauges_row = Div(KwhVerticalGauge("BAT VOL 2", sg.vol, 100, 170, [100,120,140,160,170]), KwhVerticalGauge("BAT TEMP 2", sg.temp, 0, 50, [0,25,50]), KwhVerticalGauge("BAT SOC 2", sg.soc, 0, 200, [0,50,100,150,200]), KwhVerticalGauge("BAT CUR 2", sg.cur, 0, 100, [0,25,50,75,100]), cls="kwh-gauges-row")

        bottom_section = Div(port_gauges_row, Div(ToggleSwitch("VBS_Enable", kwh.vbs_enable, id_key="tog-kwh-vbs", toggle_url="/api/toggle/kwh.vbs_enable"), cls="kwh-bottom-center"), stbd_gauges_row, cls="kwh-bottom-section")

        main_content_area = Div(
            Div(Div(Div("BATTERY 50 kWh STATUS", cls="kwh-main-title"), top_section, bottom_section, cls="kwh-dashboard"), sidebar_col, cls="main-content"),
            cls="main-content-wrapper"
        )

    # ─────────────────────────────────────────────────────────────────────────
    # MCC TAB
    # ─────────────────────────────────────────────────────────────────────────
    elif active_tab == "MCC":
        mcc = s.mcc
        ind = mcc.indicators
        st  = mcc.status

        col1 = Div(MccIndicator("CO2 Sensor-D", ind.co2_sensor_d), MccIndicator("Trim System-D", ind.trim_system_d), MccIndicator("Magnetometer-D", ind.magnetometer_d), MccIndicator("Conduct & Temp-D", ind.conduct_temp_d), MccIndicator("Thruster_T1-D", ind.thruster_t1_d), MccIndicator("Thruster_T2-D", ind.thruster_t2_d), MccIndicator("Thruster_En_P-D", ind.thruster_en_p_d), MccIndicator("Thruster_En_S-D", ind.thruster_en_s_d), MccIndicator("4K camera P-D", ind.camera_4k_p_d), MccIndicator("HD Camera P3-D", ind.hd_camera_p3_d), MccIndicator("SD_Camera_P4-D", ind.sd_camera_p4_d), MccIndicator("CTDO-D", ind.ctdo_d), cls="mcc-col")
        col2 = Div(MccIndicator("Forwd_Low-D", ind.forwd_low_d), MccIndicator("Forwd_Medi-D", ind.forwd_medi_d), MccIndicator("Lateral_Low-D", ind.lateral_low_d), MccIndicator("Lateral_Medi-D", ind.lateral_medi_d), MccIndicator("Verti_Low-D", ind.verti_low_d), MccIndicator("Verti_Medi-D", ind.verti_medi_d), MccIndicator("Heading_Low-D", ind.heading_low_d), MccIndicator("Heading_Medi-D", ind.heading_medi_d), MccIndicator("4K camera S-D", ind.camera_4k_s_d), MccIndicator("HD Camera S1-D", ind.hd_camera_s1_d), MccIndicator("SD Camera S4-D", ind.sd_camera_s4_d), MccIndicator("Dissolved O2-D", ind.dissolved_o2_d), Div(Div("Data Receiving Mode", cls="mcc-disabled-label"), Div(st.data_receiving_mode, cls="mcc-disabled-box"), cls="mcc-disabled-wrap"), cls="mcc-col")
        col3 = Div(MccIndicator("LED Light S2-D", ind.led_light_s2_d), MccIndicator("LED Light S3-D", ind.led_light_s3_d), MccIndicator("LED Light S4-D", ind.led_light_s4_d), MccIndicator("INS-D", ind.ins_d), MccIndicator("DVL-D", ind.dvl_d), MccIndicator("Depth Sensor Pri-D", ind.depth_sensor_pri_d), MccIndicator("Altimeter-D", ind.altimeter_d), MccIndicator("LED Light P2-D", ind.led_light_p2_d), MccIndicator("LED Light P3-D", ind.led_light_p3_d), MccIndicator("LED Light P4-D", ind.led_light_p4_d), cls="mcc-col")

        col4_center = Div(
            Div(MccStatusBox("Modem Ready Status", st.modem_ready_status, "mcc-bg-green"), MccStatusBox("Read/ Write", st.read_write, "mcc-bg-gray"), MccStatusBox("Data Sending Mode", st.data_sending_mode, "mcc-bg-gray"), cls="mcc-center-top"),
            Div(ToggleSwitch("Acoustic comm Auto", st.acoustic_comm_auto), cls="mcc-center-toggle"),
            Div(Div("MCC message", cls="mcc-msg-title"), Div(st.mcc_message, cls="mcc-msg-box"), Div("Pilot message", cls="mcc-msg-title"), Div(st.pilot_message, cls="mcc-msg-box"), cls="mcc-center-msg"),
            Div(MccShipData("Ship Latitude", st.ship_latitude), MccShipData("Ship Longitude", st.ship_longitude), MccShipData("Ship Heading", st.ship_heading), MccShipData("Ship Time", st.ship_time), cls="mcc-center-ship"),
            cls="mcc-col mcc-col-center"
        )
        col5_right = Div(
            MccRadioGroup(st.power_status),
            Div(MccCrewStatus("PILOT", st.pilot_ok), MccCrewStatus("CO-PILOT", st.copilot_ok), MccCrewStatus("OBSERVER", st.observer_ok), cls="mcc-crew-group"),
            MccPowerDropdown(st.power_dropdown),
            Div(ToggleSwitch("data mode", st.data_mode), cls="mcc-right-toggle"),
            cls="mcc-col mcc-col-right"
        )

        mcc_panel = Div(Div("Data from MCC", cls="mcc-panel-title"), Div(col1, col2, col3, col4_center, col5_right, cls="mcc-grid"), cls="mcc-panel")
        main_content_area = Div(Div(mcc_panel, sidebar_col, cls="main-content"), cls="main-content-wrapper")

    # ─────────────────────────────────────────────────────────────────────────
    # SWITCHES TAB  (includes scenario launcher)
    # ─────────────────────────────────────────────────────────────────────────
    elif active_tab == "Switches":
        sw = s.switches.state
        sc = scenario_state

        def ToggleBlock(label, is_on, state_key):

            t_cls = "toggle-on" if is_on else "toggle-off"
            d_cls = "toggle-dot-on" if is_on else "toggle-dot-off"

            popup_text = ascend_scenario.get_popup()

            # ====================================================
            # SOP HIGHLIGHTING
            # ====================================================

            highlight = False

                        # ---- RELEASE 300kg ----
            if (
                "300kg" in popup_text and
                state_key in (
                    "port_side_sdw_3",
                    "starboard_side_sdw_3"
                )
            ):
                highlight = True

            # ---- MAIN BALLAST ----
            elif (
                "BALLAST" in popup_text and
                state_key == "freeboard_p"
            ):
                highlight = True

            # ---- SONAR & LIGHTS ----
            elif (
                "SONAR" in popup_text and
                state_key in (
                    "sonar",
                    "uw_led_p",
                    "uw_led_s"
                )
            ):
                highlight = True

            # ====================================================
            # BORDER STYLE
            # ====================================================

            border = (
                "border:2px solid #facc15;"
                "border-radius:6px;"
                "box-shadow:0 0 12px #facc1555;"
                if highlight else
                "border:1px solid #333;"
                "border-radius:6px;"
            )

            # ====================================================
            # COMPONENT
            # ====================================================

            return Div(

                Span(
                    label,
                    style=(
                        "font-size:12px;"
                        "font-weight:600;"
                        "color:white;"
                    )
                ),

                Div(

                    Span(
                        "ON" if is_on else "OFF",
                        style=(
                            "font-size:10px;"
                            "margin-right:6px;"
                            "color:#bbb;"
                        )
                    ),

                    Div(
                        Div(cls=f"toggle-dot {d_cls}"),
                        cls=f"toggle-track {t_cls}",
                        style=(
                            "transform:scale(0.8);"
                            "transform-origin:right center;"
                        )
                    ),

                    style="display:flex; align-items:center;"
                ),

                style=(
                    "display:flex;"
                    "transition:all 0.25s ease;"
                    "justify-content:space-between;"
                    "align-items:center;"
                    "padding:8px 10px;"
                    "background:rgba(0,0,0,0.25);"
                    f"{border}"
                    "margin-bottom:6px;"
                ),

                id=f"tog-sw-{state_key.replace('_','-')}",

                hx_post=f"/api/toggle/switches.state.{state_key}",
                hx_trigger="click",
                hx_swap="none"
            )

        # ── Scenario launcher banner (sits above the switch grid) ─────────────

        man_is_active = sc.active and sc.mission_name == "MANEUVERING PHASE"
        man_is_success = sc.success if sc.mission_name == "MANEUVERING PHASE" else None
        man_border = "#facc15" if man_is_active else ("#00ff88" if man_is_success is True else ("#ff4444" if man_is_success is False else "#333"))
        man_label  = "🟡 ASCEND PHASE ACTIVE" if man_is_active else ("✅ MISSION COMPLETE" if man_is_success is True else ("❌ MISSION FAILED" if man_is_success is False else "▶  START SCENARIO"))
        man_scenario_banner = Div(
            Div(
                Span("NORMAL ASCEND SOP", style="font-weight:800; color:#facc15; font-size:13px; letter-spacing:1px;"),
                Span(man_label, style=f"font-size:12px; color:{man_border}; margin-left:12px;"),
                style="display:flex; align-items:center; flex:1;"
            ),
            # Div(
            #     Span(
            #         "START" if not man_is_active else "RUNNING…",
            #         hx_post="/api/scenario/Emergency/start",
            #         hx_swap="none",
            #         style=(
            #             "cursor:pointer; background:#1a1a1a; border:1px solid #facc15;"
            #             "color:#facc15; padding:5px 14px; border-radius:5px; font-size:12px;"
            #             "font-weight:700; margin-right:8px; pointer-events:" +
            #             ("none; opacity:0.4;" if sc.active else "auto;")
            #         ),
            #     ),
            #     Span(
            #         "RESET",
            #         hx_post="/api/scenario/Emergency/reset",
            #         hx_swap="none",
            #         style="cursor:pointer; background:#1a1a1a; border:1px solid #555; color:#aaa; padding:5px 10px; border-radius:5px; font-size:12px;",
            #     ),
            #     style="display:flex; align-items:center;"
            # ),
            style=(
                f"display:flex; justify-content:space-between; align-items:center;"
                f"padding:10px 16px; background:#111; border:1px solid {man_border};"
                f"border-radius:8px; margin-bottom:12px;"
            )
        )

        col1 = Div(
            Div("Thruster Controls", cls="mcc-panel-title", style="background:#ffea00; color:black;"),
            ToggleBlock("Speed Control", sw.speed_control, "speed_control"),
            ToggleBlock("Heading trim", sw.heading_trim, "heading_trim"),
            ToggleBlock("Depth trim", sw.depth_trim, "depth_trim"),
            ToggleBlock("lateral trim", sw.lateral_trim, "lateral_trim"),
            Div("BATS Control", cls="mcc-panel-title", style="background:#ffea00; color:black; margin-top: 10px;"),
            ToggleBlock("HP_AP_ON/OFF", sw.hp_ap_on_off, "hp_ap_on_off"),
            ToggleBlock("HP_BP_ON/OFF", sw.hp_bp_on_off, "hp_bp_on_off"),
            ToggleBlock("HP_Reg_set", sw.hp_reg_set, "hp_reg_set"),
            ToggleBlock("Pitch ON/OFF", sw.pitch_on_off, "pitch_on_off"),
            ToggleBlock("VBT_Set value", sw.vbt_set_value, "vbt_set_value"),
            ToggleBlock("Pitch up & Down _Analog", sw.pitch_up_down_analog, "pitch_up_down_analog"),
            ToggleBlock("FreeBoard_P", sw.freeboard_p, "freeboard_p"),
            ToggleBlock("Dive in", sw.dive_in, "dive_in"),
            ToggleBlock("Water OUT_ON/OFF", sw.water_out_on_off, "water_out_on_off"),
            cls="mcc-col", style="display:flex; flex-direction:column; gap:4px;"
        )
        col2 = Div(
            Div("General control Switches", cls="mcc-panel-title", style="background:#ffea00; color:black;"),
            ToggleBlock("Co2 scrubber_P", sw.co2_scrubber_p, "co2_scrubber_p"),
            ToggleBlock("Joystick Enable", sw.joystick_enable, "joystick_enable"),
            ToggleBlock("Pilot selection", sw.pilot_selection, "pilot_selection"),
            ToggleBlock("Copilot selection", sw.copilot_selection, "copilot_selection"),
            ToggleBlock("VHS_Power_P", sw.vhs_power_p, "vhs_power_p"),
            ToggleBlock("LED_Emegency_Port", sw.led_emergency_port, "led_emergency_port"),
            ToggleBlock("UW Camera _P", sw.uw_camera_p, "uw_camera_p"),
            ToggleBlock("SONAR", sw.sonar, "sonar"),
            ToggleBlock("Surface_INS", sw.surface_ins, "surface_ins"),
            Div("POWER DIRECT CONTROL_PORT", cls="mcc-panel-title", style="background:#ffea00; color:black; margin-top: 10px;"),
            ToggleBlock("MB_P_1*", sw.mb_p_1, "mb_p_1"),
            ToggleBlock("MB_P_2*", sw.mb_p_2, "mb_p_2"),
            ToggleBlock("MB_P_3*", sw.mb_p_3, "mb_p_3"),
            ToggleBlock("MB_P_4*", sw.mb_p_4, "mb_p_4"),
            ToggleBlock("MB_P_5*", sw.mb_p_5, "mb_p_5"),
            ToggleBlock("AB_P_BMS*", sw.ab_p_bms, "ab_p_bms"),
            ToggleBlock("MB_P_BMS*", sw.mb_p_bms, "mb_p_bms"),
            ToggleBlock("AB_P Power selection*", sw.ab_p_power_selection, "ab_p_power_selection"),
            ToggleBlock("MB_P-PDE_P*", sw.mb_p_pde_p, "mb_p_pde_p"),
            cls="mcc-col", style="display:flex; flex-direction:column; gap:4px;"
        )
        col3 = Div(
            Div("Service Drop Weight Switches", cls="mcc-panel-title", style="background:#ffea00; color:black;"),
            ToggleBlock("Port side SDW 1", sw.port_side_sdw_1, "port_side_sdw_1"),
            ToggleBlock("Port side SDW 2", sw.port_side_sdw_2, "port_side_sdw_2"),
            ToggleBlock("Port side SDW 3", sw.port_side_sdw_3, "port_side_sdw_3"),
            ToggleBlock("Port side SDW 4", sw.port_side_sdw_4, "port_side_sdw_4"),
            ToggleBlock("Port side SDW 5", sw.port_side_sdw_5, "port_side_sdw_5"),
            ToggleBlock("Starboard side SDW 1", sw.starboard_side_sdw_1, "starboard_side_sdw_1"),
            ToggleBlock("Starboard side SDW 2", sw.starboard_side_sdw_2, "starboard_side_sdw_2"),
            ToggleBlock("Starboard side SDW 3", sw.starboard_side_sdw_3, "starboard_side_sdw_3"),
            ToggleBlock("Starboard side SDW 4", sw.starboard_side_sdw_4, "starboard_side_sdw_4"),
            ToggleBlock("Starboard side SDW 5", sw.starboard_side_sdw_5, "starboard_side_sdw_5"),
            cls="mcc-col", style="display:flex; flex-direction:column; gap:4px;"
        )
        col4 = Div(
            Div("Emergency Jettisoning_P (1/2)", cls="mcc-panel-title", style="background:#ffea00; color:black;"),
            ToggleBlock("Emergency Jettisoning of Manipulator_1", sw.ej_manipulator_1, "ej_manipulator_1"),
            ToggleBlock("Emergency Jettisoning of Manipulator_2", sw.ej_manipulator_2, "ej_manipulator_2"),
            ToggleBlock("Emergency Jettisoning of Manipulator_3", sw.ej_manipulator_3, "ej_manipulator_3"),
            ToggleBlock("Emergency Jettisoning of Manipulator_4", sw.ej_manipulator_4, "ej_manipulator_4"),
            ToggleBlock("Emergency Jettisoning of Trim System_1", sw.ej_trim_system_1, "ej_trim_system_1"),
            ToggleBlock("Emergency Jettisoning of Trim System_2", sw.ej_trim_system_2, "ej_trim_system_2"),
            ToggleBlock("Emergency Jettisoning of Trim System_3", sw.ej_trim_system_3, "ej_trim_system_3"),
            ToggleBlock("Emergency Jettisoning of Trim System_4", sw.ej_trim_system_4, "ej_trim_system_4"),
            ToggleBlock("Emergency Marker Buoy Release_1", sw.em_buoy_release_1, "em_buoy_release_1"),
            cls="mcc-col", style="display:flex; flex-direction:column; gap:4px;"
        )
        col5 = Div(
            Div("Emergency Jettisoning_P (2/2)", cls="mcc-panel-title", style="background:#ffea00; color:black;"),
            ToggleBlock("Emergency Marker Buoy Release_2", sw.em_buoy_release_2, "em_buoy_release_2"),
            ToggleBlock("Emergency Marker Buoy Release_3", sw.em_buoy_release_3, "em_buoy_release_3"),
            ToggleBlock("Emergency Marker Buoy Release_4", sw.em_buoy_release_4, "em_buoy_release_4"),
            ToggleBlock("Emergency Jettisoning of Sampling Basket_1", sw.ej_sampling_basket_1, "ej_sampling_basket_1"),
            ToggleBlock("Emergency Jettisoning of Sampling Basket_2", sw.ej_sampling_basket_2, "ej_sampling_basket_2"),
            ToggleBlock("Emergency Jettisoning of Sampling Basket_3", sw.ej_sampling_basket_3, "ej_sampling_basket_3"),
            ToggleBlock("Emergency Jettisoning of Sampling Basket_4", sw.ej_sampling_basket_4, "ej_sampling_basket_4"),
            # ── THE TWO KEY SWITCHES — highlighted during scenario ────────────
            ToggleBlock("Emergency Drop Weight_P1(SC)", sw.em_drop_weight_p1_sc, "em_drop_weight_p1_sc"),
            ToggleBlock("Emergency Drop Weight_P2(PC)", sw.em_drop_weight_p2_pc, "em_drop_weight_p2_pc"),
            cls="mcc-col", style="display:flex; flex-direction:column; gap:4px;"
        )

        switches_panel = Div(
            man_scenario_banner,
            Div(col1, col2, col3, col4, col5, style="display:grid; grid-template-columns: repeat(5, 1fr); gap: 15px; overflow-y: auto; flex: 1;"),
            cls="mcc-panel",
            style="display: flex; flex-direction: column; padding:15px;"
        )

        main_content_area = Div(
            Div(switches_panel, sidebar_col, cls="main-content"),
            cls="main-content-wrapper"
        )

    else:
        main_content_area = Div(
            Div(H2(f"{active_tab} Tab Content", style="margin:auto;"), sidebar_col, cls="main-content"),
            cls="main-content-wrapper",
        )

    return Div(
        HeaderArea(),
        main_content_area,
        BottomTabsNav(
            ["Main","HSSS","Ballast","Propulsion","POWER","Imaging","Sensors","Logging","Status","50 Kwh","MCC","Switches"],
            active_tab=active_tab,
        ),
        # Scenario overlay placeholder — swapped via OOB on every broadcast
        Div(id="scenario-overlay"),
        id=f"dashboard-content-{active_tab.lower()}",
        cls="dashboard-root",
        hx_swap_oob="true",
    )


# ─────────────────────────────────────────────────────────────────────────────
# Page routes
# ─────────────────────────────────────────────────────────────────────────────
scenario_task = None

@rt("/")
async def get(dive_num: int = 1):
    global simulator_task
    global scenario_task
    if simulator_task is None or simulator_task.done():
        app_state.is_powered_on = True
        sim_global.target_dive = dive_num
        simulator_task = asyncio.create_task(simulate_data())
    elif dive_num != 1:
        sim_global.target_dive = dive_num

    if scenario_task is None or scenario_task.done():
        scenario_task = asyncio.create_task(
            run_emg_dropweights_scenario(app_state, broadcast, ScenarioOverlay)
        )

    return Title("MATSYA 6000 View"), Div(
        AppLayout(active_tab="Main"), id="ws-container", hx_ext="ws", ws_connect="/ws"
    )


@rt("/hsss")
def get_hsss():
    return Title("MATSYA 6000 View - HSSS"), Div(AppLayout(active_tab="HSSS"), id="ws-container", hx_ext="ws", ws_connect="/ws")

@rt("/ballast")
def get_ballast():
    return Title("MATSYA 6000 View - Ballast"), Div(AppLayout(active_tab="Ballast"), id="ws-container", hx_ext="ws", ws_connect="/ws")

@rt("/propulsion")
def get_propulsion():
    return Title("MATSYA 6000 View - Propulsion"), Div(AppLayout(active_tab="Propulsion"), id="ws-container", hx_ext="ws", ws_connect="/ws")

@rt("/power")
def get_power():
    return Title("MATSYA 6000 View - POWER"), Div(AppLayout(active_tab="POWER"), id="ws-container", hx_ext="ws", ws_connect="/ws")

@rt("/imaging")
def get_imaging():
    return Title("MATSYA 6000 View - Imaging"), Div(AppLayout(active_tab="Imaging"), id="ws-container", hx_ext="ws", ws_connect="/ws")

@rt("/sensors")
def get_sensors():
    return Title("MATSYA 6000 View - Sensors"), Div(AppLayout(active_tab="Sensors"), id="ws-container", hx_ext="ws", ws_connect="/ws")

@rt("/logging")
def get_logging():
    return Title("MATSYA 6000 View - Logging"), Div(AppLayout(active_tab="Logging"), id="ws-container", hx_ext="ws", ws_connect="/ws")

@rt("/status")
def get_status():
    return Title("MATSYA 6000 View - Status"), Div(AppLayout(active_tab="Status"), id="ws-container", hx_ext="ws", ws_connect="/ws")

@rt("/50-kwh")
def get_50kwh():
    return Title("MATSYA 6000 View - 50 Kwh"), Div(AppLayout(active_tab="50 Kwh"), id="ws-container", hx_ext="ws", ws_connect="/ws")

@rt("/mcc")
def get_mcc():
    return Title("MATSYA 6000 View - MCC"), Div(AppLayout(active_tab="MCC"), id="ws-container", hx_ext="ws", ws_connect="/ws")

@rt("/switches")
def get_switches():
    return Title("MATSYA 6000 View - Switches"), Div(AppLayout(active_tab="Switches"), id="ws-container", hx_ext="ws", ws_connect="/ws")


# ─────────────────────────────────────────────────────────────────────────────
# Simulation engine
# ─────────────────────────────────────────────────────────────────────────────
simulator_task = None

class SimState:
    command: str = None
    target_dive: int = None
    speed: str = "1"
    paused: bool = False

sim_global = SimState()


async def broadcast_all_layouts():
    """Push all tab layouts + scenario overlay to every connected client."""
    tabs = ["Main","HSSS","Ballast","Propulsion","POWER","Imaging","Sensors","Logging","Status","50 Kwh","MCC","Switches"]
    for tab in tabs:
        await broadcast(AppLayout(active_tab=tab))
    await broadcast(ScenarioOverlay())


async def simulate_data():
    s = app_state

    data_dir = "sim_data_processed"
    if not os.path.exists(data_dir):
        print(f"Data directory {data_dir} not found. Simulation stopped.")
        return

    json_files = glob.glob(os.path.join(data_dir, "*.json"))
    if not json_files:
        print(f"No JSON files found in {data_dir}. Simulation stopped.")
        return

    json_files.sort()

    current_file = json_files[0]
    for jf in json_files:
        m = re.search(r'(?i)dive[_\s]*(\d+)', jf)
        if m and int(m.group(1)) == s.header.dive_num:
            current_file = jf
            break

    m = re.search(r'(?i)dive[_\s]*(\d+)', current_file)
    if m:
        s.header.dive_num = int(m.group(1))

    print(f"Loading simulation data from {current_file} (Dive {s.header.dive_num})")

    try:
        with open(current_file, 'r') as f:
            records = json.load(f)
    except Exception as e:
        print(f"Failed to load JSON: {e}")
        return

    if not records:
        return

    idx = 0
    while True:
        state_changed = False
        cmd = sim_global.command
        sim_global.command = None

        if sim_global.target_dive is not None:
            t_dive = sim_global.target_dive
            sim_global.target_dive = None
            for jf in json_files:
                m = re.search(r'(?i)dive[_\s]*(\d+)', jf)
                if m and int(m.group(1)) == t_dive:
                    current_file = jf
                    s.header.dive_num = t_dive
                    try:
                        with open(current_file, 'r') as f:
                            records = json.load(f)
                        idx = 0
                        state_changed = True
                        print(f"Switched to {current_file}")
                    except Exception:
                        pass
                    break

        if cmd == "rewind":
            idx = max(0, idx - 10)
            state_changed = True
        elif cmd == "forward":
            idx = min(len(records) - 1, idx + 10)
            state_changed = True
        elif cmd == "start":
            idx = 0
            state_changed = True
        elif cmd == "end":
            idx = max(0, len(records) - 1)
            state_changed = True

        if sim_global.paused and not state_changed:
            await asyncio.sleep(0.1)
            continue

        if idx >= len(records):
            idx = 0

        record = records[idx]

        # --- only apply sim data when scenario is NOT controlling depth -------
        scenario_is_driving = scenario_state.active

        for var_path, value in record.items():
            if value is None:
                continue
            # Skip depth update so scenario controls it exclusively
            if scenario_is_driving and var_path == "header.depth":
                continue

            parts = var_path.split('.')
            obj = s
            try:
                for p in parts[:-1]:
                    obj = getattr(obj, p)
                leaf   = parts[-1]
                target = getattr(obj, leaf)
                if hasattr(target, 'value'):
                    try:
                        target.value = float(value)
                    except ValueError:
                        pass
                else:
                    setattr(obj, leaf, value)
            except AttributeError:
                pass

        if "header.present_time" in record and record["header.present_time"]:
            time_str = str(record["header.present_time"])
            time_str = time_str.replace("_", ":").split(".")[0]
            s.header.present_time = time_str
        else:
            s.header.present_time = datetime.now().strftime("%H:%M:%S")

        if "header.mission_time" not in record or not record["header.mission_time"]:
            s.header.mission_time = datetime.now().strftime("%H:%M:%S")

        
        ascend_scenario.update(
            s.header.depth.value,
            s.switches.state)
        
        if ascend_scenario.completed:

            scenario_state.success = True
            scenario_state.result_message = (
                "Normal Ascend SOP executed successfully"
            )

        elif ascend_scenario.failed:

            scenario_state.success = False
            scenario_state.result_message = (
                "Ascend SOP failed"
            )
        
        await broadcast_all_layouts()

        if not sim_global.paused:
            idx += 1
            sleep_dur = 1.0 if sim_global.speed != "max" else 0.008
            await asyncio.sleep(sleep_dur)
        else:
            await asyncio.sleep(0.1)


# ─────────────────────────────────────────────────────────────────────────────
# Scenario API routes
# ─────────────────────────────────────────────────────────────────────────────
# ─────────────────────────────────────────────────────────────────────────────
@rt("/api/scenario/emergency/start", methods=["POST"])
async def man_scenario_start():
    global scenario_task
    if scenario_task is None or scenario_task.done():
        scenario_task = asyncio.create_task(
            run_emg_dropweights_scenario(app_state, broadcast, ScenarioOverlay)
        )
    return ""


@rt("/api/scenario/emergency/reset", methods=["POST"])
async def man_scenario_reset():

    global scenario_task
    global ascend_scenario

    if scenario_task and not scenario_task.done():
        scenario_task.cancel()

    reset_scenario(scenario_state)

    # ── reset descend SOP ─────────────────────────────
    ascend_scenario = AscendScenario()

    await broadcast(ScenarioOverlay())
    await broadcast_all_layouts()

    return ""


# ─────────────────────────────────────────────────────────────────────────────
# Existing API routes (unchanged)
# ─────────────────────────────────────────────────────────────────────────────
@rt("/api/toggle_power", methods=["POST"])
async def toggle_power():
    global simulator_task
    app_state.is_powered_on = not app_state.is_powered_on
    if app_state.is_powered_on:
        if simulator_task is None or simulator_task.done():
            simulator_task = asyncio.create_task(simulate_data())
    else:
        if simulator_task and not simulator_task.done():
            simulator_task.cancel()
            simulator_task = None
    await broadcast_all_layouts()
    return ""


@rt("/api/toggle_joystick", methods=["POST"])
async def toggle_joystick():
    s = app_state.sidebar
    s.joystick = not s.joystick
    comp = ToggleSwitch("Joystick", s.joystick, id_key="toggle-joystick", toggle_url="/api/toggle_joystick")
    await broadcast(comp)
    return ""


@rt("/api/toggle_thrusters_enable", methods=["POST"])
async def toggle_thrusters_enable():
    s = app_state.sidebar
    s.thrusters_enable = not s.thrusters_enable
    comp = ToggleSwitch("Thrusters Enable", s.thrusters_enable, id_key="toggle-thrusters", toggle_url="/api/toggle_thrusters_enable")
    await broadcast(comp)
    return ""


@rt("/api/toggle_high_speed", methods=["POST"])
async def toggle_high_speed():
    s = app_state.sidebar
    s.high_speed = not s.high_speed
    comp = ToggleSwitch("High Speed", s.high_speed, id_key="toggle-high-speed", toggle_url="/api/toggle_high_speed")
    await broadcast(comp)
    return ""


@rt("/api/toggle/{state_path:path}", methods=["POST"])
async def generic_toggle(state_path: str):
    parts = state_path.split(".")
    obj = app_state
    for p in parts[:-1]:
        obj = getattr(obj, p)
    val = getattr(obj, parts[-1])
    setattr(obj, parts[-1], not val)

    await broadcast_all_layouts()
    return ""


@rt("/api/start_sim", methods=["GET", "POST"])
async def start_sim():
    global simulator_task
    if simulator_task is None or simulator_task.done():
        simulator_task = asyncio.create_task(simulate_data())
        return {"status": "Simulation started"}
    return {"status": "Simulation already running"}


@rt("/api/stop_sim", methods=["GET", "POST"])
async def stop_sim():
    global simulator_task
    if simulator_task and not simulator_task.done():
        simulator_task.cancel()
        simulator_task = None
        return {"status": "Simulation stopped"}
    return {"status": "Simulation not running"}


@rt("/api/sim/set_dive", methods=["POST"])
async def set_dive(dive_num: int):
    sim_global.target_dive = dive_num
    return ""


@rt("/api/sim/toggle_pause", methods=["POST"])
async def toggle_pause():
    sim_global.paused = not sim_global.paused
    comp = Span(
        "⏸" if not sim_global.paused else "▶️",
        hx_post="/api/sim/toggle_pause", hx_swap="none",
        style="cursor: pointer; user-select: none; margin-right: 5px;",
        id="play-pause-btn", hx_swap_oob="true"
    )
    await broadcast(comp)
    return ""


@rt("/api/sim/set_speed", methods=["POST"])
async def set_speed(speed: str):
    sim_global.speed = speed
    return ""


@rt("/api/sim/{cmd}", methods=["POST"])
async def sim_command(cmd: str):
    if cmd in ["start", "end"]:
        sim_global.command = cmd
    return ""


@rt("/api/test", methods=["POST", "GET"])
async def test_update():
    s = app_state
    s.header.mission_time = datetime.now().strftime("%H:%M:%S")
    s.header.depth.value = round(max(0, s.header.depth.value + random.uniform(-0.5, 0.5)), 1)
    await broadcast(AppLayout(active_tab="Main"))
    await broadcast(AppLayout(active_tab="HSSS"))
    return {"status": "Updated"}


if __name__ == "__main__":
    serve()
