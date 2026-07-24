import React from "react";
import {
  TopbarInlineMetric,
  SimpleMetricBox,
  BigNumber,
  SidebarMetric,
  StatusPill,
  LedPanel,
} from "./Layout";
import { ToggleSwitch, MetalSwitch } from "./Controls";
import { VerticalGauge, SimpleRpmBox, CompassBox } from "./Gauges";

export function HeaderArea({ appState, apiCall }) {
  const s = appState.header;

  return (
    <div className="header-area">
      <div className="header-top">
        <div className="header-left">
          <div className="header-metric">
            <span className="header-label">DIVE #</span>
            <select
              value={s.dive_num}
              onChange={(e) =>
                apiCall(
                  "/api/sim/set_dive",
                  new URLSearchParams({ dive_num: e.target.value }),
                )
              }
              style={{
                width: "80px",
                background: "transparent",
                border: "1px solid #333",
                color: "black",
                textAlign: "center",
                fontWeight: "bold",
                padding: "2px",
              }}
            >
              {[1, 2, 3, 4, 5, 6, 7, 8, 9].map((num) => (
                <option key={num} value={num}>
                  Dive {num}
                </option>
              ))}
            </select>
          </div>
          <div className="header-metric">
            <span className="header-label">Mission Run Time</span>
            <span className="header-value-box mono">{s.mission_time}</span>
          </div>
        </div>
        <h1 className="header-title">Manned Submersible — MATSYA 6000</h1>
        <div
          className="header-metric"
          style={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
          }}
        >
          <span className="header-label">Present Time</span>
          <span className="header-value-box mono">{s.present_time}</span>
          <div
            style={{
              display: "flex",
              gap: "5px",
              marginTop: "5px",
              fontSize: "14px",
              justifyContent: "center",
              background: "#111",
              padding: "2px 10px",
              borderRadius: "4px",
              border: "1px solid #333",
              alignItems: "center",
            }}
          >
            <span
              onClick={() => apiCall("/api/sim/start")}
              style={{
                cursor: "pointer",
                userSelect: "none",
                marginRight: "5px",
              }}
            >
              ⏮
            </span>
            <span
              onClick={() => apiCall("/api/sim/toggle_pause")}
              style={{
                cursor: "pointer",
                userSelect: "none",
                marginRight: "5px",
              }}
            >
              ⏸️
            </span>
            <select
              onChange={(e) =>
                apiCall(
                  "/api/sim/set_speed",
                  new URLSearchParams({ speed: e.target.value }),
                )
              }
              style={{
                background: "transparent",
                border: "1px solid #333",
                color: "white",
                fontSize: "12px",
                cursor: "pointer",
                padding: "2px",
                display: "inline-block",
                margin: "0 5px 0 0",
              }}
            >
              <option value="1">1x Speed</option>
              <option value="max">Max Speed</option>
            </select>
            <span
              onClick={() => apiCall("/api/sim/end")}
              style={{ cursor: "pointer", userSelect: "none" }}
            >
              ⏭
            </span>
          </div>
        </div>
      </div>
      <div className="header-metrics-strip">
        <TopbarInlineMetric
          label="Heading"
          value={s.heading?.value}
          unit={s.heading?.unit}
        />
        <TopbarInlineMetric
          label="Depth"
          value={s.depth?.value}
          unit={s.depth?.unit}
        />
        <TopbarInlineMetric
          label="Altitude"
          value={s.altitude?.value}
          unit={s.altitude?.unit}
        />
        <TopbarInlineMetric
          label="MB_P SOC"
          value={s.mb_p_soc?.value}
          unit={s.mb_p_soc?.unit}
        />
        <TopbarInlineMetric
          label="MB_S SOC"
          value={s.mb_s_soc?.value}
          unit={s.mb_s_soc?.unit}
        />
      </div>
    </div>
  );
}

export function Sidebar({ appState: s, apiCall }) {
  return (
    <div className="col-sidebar">
      <div className="sidebar-section">
        <SidebarMetric
          label="O₂"
          value={s.environment?.o2?.value}
          unit={s.environment?.o2?.unit}
        />
        <SidebarMetric
          label="CO₂"
          value={s.environment?.co2?.value}
          unit={s.environment?.co2?.unit}
        />
        <SidebarMetric
          label="Temp"
          value={s.environment?.temp?.value}
          unit={s.environment?.temp?.unit}
        />
        <SidebarMetric
          label="Pressure"
          value={s.environment?.pressure?.value}
          unit={s.environment?.pressure?.unit}
        />
      </div>
      <div className="sidebar-divider"></div>
      <div className="sidebar-section">
        <ToggleSwitch
          label="Joystick"
          isOn={s.sidebar?.joystick}
          onToggle={() => apiCall("/api/toggle_joystick")}
        />
        <ToggleSwitch
          label="Thrusters Enable"
          isOn={s.sidebar?.thrusters_enable}
          onToggle={() => apiCall("/api/toggle_thrusters_enable")}
        />
        <ToggleSwitch
          label="High Speed"
          isOn={s.sidebar?.high_speed}
          onToggle={() => apiCall("/api/toggle_high_speed")}
        />
      </div>
      <div className="sidebar-divider"></div>
      <div className="sidebar-section">
        <StatusPill label="IR" isOk={s.sidebar?.ir_ok} />
        <StatusPill
          label="Water Ingress"
          isOk={!s.sidebar?.water_ingress}
          okText="CLEAR"
          errText="ALERT"
        />
        <StatusPill
          label="Comm"
          isOk={s.sidebar?.comm_status}
          okText="Status OK"
          errText="Status"
        />
      </div>
      <div className="sidebar-divider"></div>
      <LedPanel leds={s.leds} />
      <div className="sidebar-footer">
        <div
          className={`on-button ${s.is_powered_on ? "power-on" : ""}`}
          onClick={() => apiCall("/api/toggle_power")}
        >
          {s.is_powered_on ? "OFF" : "ON"}
        </div>
      </div>
    </div>
  );
}

export function AppLayout({ appState, apiCall }) {
  const s = appState;

  const altCol = (
    <div className="col-altitude">
      <VerticalGauge
        label="Altitude"
        value={s.header?.altitude?.value}
        maxVal={10}
        unit="m"
        lowIsGood={false}
        scaleLabels={[10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0]}
      />
    </div>
  );

  const centerCol = (
    <div className="col-center">
      <div className="roll-pitch-row">
        <SimpleMetricBox label="Roll" value={s.imu?.roll?.value} />
        <SimpleMetricBox label="Pitch" value={s.imu?.pitch?.value} />
      </div>
      <div className="compass-area">
        <CompassBox />
      </div>
      <div className="big-numbers-row">
        <BigNumber
          label="Altitude"
          value={s.header?.altitude?.value}
          unit="m"
        />
        <BigNumber
          label="Heading_P"
          value={s.imu?.heading_p?.value}
          unit="deg"
        />
        <BigNumber label="Depth" value={s.header?.depth?.value} unit="m" />
      </div>
    </div>
  );

  const depthPropCol = (
    <div className="col-depth-prop">
      <div className="depth-gauge-wrap">
        <VerticalGauge
          label="Depth"
          value={s.header?.depth?.value}
          maxVal={12}
          unit="m"
          lowIsGood={true}
          scaleLabels={[-2, -1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]}
        />
      </div>
      <div className="propulsion-panel">
        <h3 className="section-title">Propulsion</h3>
        <div className="rpm-row">
          <SimpleRpmBox label="T2 RPM" value={s.propulsion?.t2_rpm} />
          <SimpleRpmBox label="T1 RPM" value={s.propulsion?.t1_rpm} />
        </div>
        <div className="rpm-row-center">
          <SimpleRpmBox label="T3 RPM" value={s.propulsion?.t3_rpm} />
        </div>
        <div className="rpm-row-center">
          <SimpleRpmBox label="T4 RPM" value={s.propulsion?.t4_rpm} />
        </div>
        <div className="rpm-row-center">
          <SimpleRpmBox label="T5 RPM" value={s.propulsion?.t5_rpm} />
        </div>
        <div className="rpm-row">
          <SimpleRpmBox label="T8 RPM" value={s.propulsion?.t8_rpm} />
          <SimpleRpmBox label="T6 RPM" value={s.propulsion?.t6_rpm} />
        </div>
        <div className="rpm-row-center">
          <SimpleRpmBox label="T7 RPM" value={s.propulsion?.t7_rpm} />
        </div>
        <div className="prop-separator"></div>
        <div className="latlon-stack">
          <SimpleMetricBox
            label="Latitude"
            value={s.propulsion?.latitude?.value}
            unit="deg"
          />
          <SimpleMetricBox
            label="Longitude"
            value={s.propulsion?.longitude?.value}
            unit="deg"
          />
        </div>
      </div>
    </div>
  );

  return (
    <div className="main-content-wrapper">
      <div className="main-content">
        {altCol}
        {centerCol}
        {depthPropCol}
        <Sidebar appState={appState} apiCall={apiCall} />
      </div>
      <div className="bottom-speed-strip">
        <SimpleMetricBox
          label="East_speed"
          value={s.bottom?.east_speed?.value}
          unit="m/s"
        />
        <SimpleMetricBox
          label="Vert_speed"
          value={s.bottom?.vert_speed?.value}
          unit="m/s"
        />
        <SimpleMetricBox
          label="North_Speed"
          value={s.bottom?.north_speed?.value}
          unit="m/s"
        />
        <SimpleMetricBox
          label="Ship Heading"
          value={s.bottom?.ship_heading?.value}
          unit="deg"
        />
      </div>
    </div>
  );
}
