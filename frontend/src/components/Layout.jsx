import React from 'react';
import { fmtVal } from '../utils';

export function TopbarInlineMetric({ label, value, unit = "", idKey = null }) {
  return (
    <div className="topbar-metric" id={idKey}>
      <span className="topbar-metric-label">{label}</span>
      <div className="topbar-metric-box">
        <span className="topbar-metric-value">{fmtVal(value)}</span>
        {unit && <span className="topbar-metric-unit">{unit}</span>}
      </div>
    </div>
  );
}

export function SimpleMetricBox({ label, value, unit = "", idKey = null }) {
  return (
    <div className="metric-box" id={idKey}>
      <span className="metric-label">{label}</span>
      <div className="metric-input">
        <span className="metric-value">{fmtVal(value)}</span>
      </div>
      {unit && <span className="metric-unit">{unit}</span>}
    </div>
  );
}

export function BigNumber({ label, value, unit = "", idKey = null }) {
  return (
    <div className="big-number" id={idKey}>
      <span className="big-number-label">{label}</span>
      <div className="big-number-readout">
        <span className="big-number-value">{fmtVal(value)}</span>
        {unit && <span className="big-number-unit">{unit}</span>}
      </div>
    </div>
  );
}

export function SidebarMetric({ label, value, unit = "", idKey = null }) {
  return (
    <div className="sidebar-metric" id={idKey}>
      <span className="sidebar-metric-label">{label}</span>
      <div className="sidebar-metric-readout">
        <span className="sidebar-metric-value">{fmtVal(value)}</span>
        {unit && <span className="sidebar-metric-unit">{unit}</span>}
      </div>
    </div>
  );
}

export function StatusPill({ label, isOk, okText = "OK", errText = "ERR", idKey = null }) {
  const statusCls = isOk ? "status-pill-ok" : "status-pill-err";
  const text = isOk ? okText : errText;
  return (
    <div className={`status-pill ${statusCls}`} id={idKey}>
      {label} {text}
    </div>
  );
}

export function LedPanel({ leds = {}, idKey = null }) {
  const renderLed = (label, isOn) => {
    const cls = isOn ? "led-dot led-on" : "led-dot led-off";
    return (
      <div className="led-item" key={label}>
        <div className={cls}></div>
        <span className="led-label">{label}</span>
      </div>
    );
  };

  return (
    <div className="led-panel" id={idKey}>
      <div className="led-row">
        {renderLed("PSS", leds.pss)}
        {renderLed("PDS", leds.pds)}
        {renderLed("IDS", leds.ids)}
      </div>
      <div className="led-row">
        {renderLed("PSP", leds.psp)}
        {renderLed("PDP", leds.pdp)}
        {renderLed("IDP", leds.idp)}
      </div>
    </div>
  );
}

export function BottomTabsNav({ tabs, activeTab = "Main", onTabSelect, isPoweredOn = true, switchesOnlyTabs = [] }) {
  return (
    <div className="bottom-tabs">
      {tabs.map(t => {
        const isDisabled = !isPoweredOn && !switchesOnlyTabs.includes(t)
        const activeCls = t === activeTab ? "tab-active" : "tab-inactive";
        return (
          <a
            key={t}
            href="#"
            onClick={(e) => {
              e.preventDefault();
              if (!isDisabled && onTabSelect) onTabSelect(t);
            }}
            className={`tab-link ${activeCls} ${isDisabled ? 'tab-disabled' : ''}`}
            title={isDisabled ? 'System is powered off' : undefined}
            style={isDisabled ? { opacity: 0.35, cursor: 'not-allowed', filter: 'grayscale(1)', pointerEvents: 'none' } : undefined}
          >
            {t}
          </a>
        );
      })}
    </div>
  );
}

