import React from 'react';
import { fmtVal } from '../utils';

export function PowerMetricRow({ label, value, unit }) {
  return (
    <div className="power-metric-row">
      <span className="power-metric-label">{label}</span>
      <div className="power-metric-box">
        <span className="power-metric-value">{fmtVal(value)}</span>
        {unit && <span className="power-metric-unit">{unit}</span>}
      </div>
    </div>
  );
}

export function PowerLinearGauge({ label, value, minVal, maxVal, scaleLabels }) {
  const percent = Math.max(0, Math.min(100, ((value - minVal) / (maxVal - minVal)) * 100));
  return (
    <div className="power-linear-gauge">
      <span className="power-gauge-title">{label}</span>
      <div className="power-gauge-wrap">
        <div className="power-gauge-track">
          <div className="power-gauge-fill" style={{ width: `${percent}%` }}></div>
        </div>
        <div className="power-gauge-scale-row">
          {scaleLabels.map((sl, i) => <span key={i} className="power-gauge-scale-label">{sl}</span>)}
        </div>
      </div>
      <div className="power-gauge-value">{fmtVal(value)}</div>
    </div>
  );
}

export function PowerStatusPill({ label, statusText, isOk }) {
  const bgCls = isOk ? "power-status-ok" : "power-status-err";
  if (label) {
    return (
      <div className="power-status-container">
        <span className="power-status-label">{label}</span>
        <div className={`power-status-box ${bgCls}`}>{statusText}</div>
      </div>
    );
  }
  return <div className={`power-status-box ${bgCls}`}>{statusText}</div>;
}

export function BatteryPanel({ title, prefix, battery, scaleLabels, minVal, maxVal }) {
  return (
    <div className="power-panel battery-panel">
      <div className="power-panel-title">{title}</div>
      <PowerLinearGauge label={`${prefix} Volt (V)`} value={battery.voltage.value} minVal={minVal} maxVal={maxVal} scaleLabels={scaleLabels} />
      <PowerMetricRow label={`${prefix} Current (A)`} value={battery.current.value} />
      <PowerMetricRow label={`${prefix} Power (kW)`} value={battery.power.value} />
      <PowerMetricRow label={`${prefix} SOC (%)`} value={battery.soc.value} />
      <PowerMetricRow label={`${prefix} Temp (deg C)`} value={battery.temp.value} />
    </div>
  );
}

export function PDEPanel({ title, prefix, enclosure }) {
  return (
    <div className="power-panel pde-panel">
      <div className="power-panel-title">{title}</div>
      <PowerMetricRow label={`${prefix} Voltage (V)`} value={enclosure.voltage.value} />
      <PowerMetricRow label={`${prefix} Current (A)`} value={enclosure.current.value} />
      <PowerMetricRow label={`${prefix} Temp (degC)`} value={enclosure.temp.value} />
      <PowerMetricRow label={`${prefix} IR_24 (Kohm)`} value={enclosure.ir_24.value} />
      <PowerMetricRow label={`${prefix}_IR_Ext (Kohm)`} value={enclosure.ir_ext.value} />
      <PowerMetricRow label={`${prefix}_148 IR (Kohm)`} value={enclosure.ir_148.value} />
      <PowerStatusPill label={`${prefix} IR Status`} statusText={enclosure.ir_status} isOk={enclosure.ir_status !== "LOW IR"} />
      <PowerStatusPill label={`${prefix} Water Leak`} statusText={enclosure.water_leak} isOk={enclosure.water_leak === "No Leak"} />
    </div>
  );
}

export function IDEPanel({ title, prefix, enclosure }) {
  return (
    <div className="power-panel ide-panel">
      <div className="power-panel-title">{title}</div>
      <PowerMetricRow label={`${prefix} Voltage (V)`} value={enclosure.voltage.value} />
      <PowerMetricRow label={`${prefix} Current (A)`} value={enclosure.current.value} />
      <PowerMetricRow label={`${prefix} Temp (degC)`} value={enclosure.temp.value} />
      <PowerMetricRow label={`${prefix} IR (kohm)`} value={enclosure.ir.value} />
      <PowerStatusPill label={`${prefix} IR Status`} statusText={enclosure.ir_status} isOk={enclosure.ir_status !== "LOW IR"} />
      <PowerStatusPill label={`${prefix} Water Leak`} statusText={enclosure.water_leak} isOk={enclosure.water_leak === "No Leak"} />
    </div>
  );
}

export function UmbilicalPanel({ title, prefix, umbilical }) {
  return (
    <div className="power-panel umb-panel">
      <div className="power-panel-title">{title}</div>
      <div className="ub-row">
        <div className="ub-col">
          <PowerMetricRow label={`${prefix} Voltage (V)`} value={umbilical.voltage.value} />
          <PowerMetricRow label={`${prefix} Current (A)`} value={umbilical.current.value} />
        </div>
        <div className="ub-col">
          <PowerMetricRow label={`${prefix} Temp (degC)`} value={umbilical.temp.value} />
          <PowerMetricRow label={`${prefix} IR (Kohm)`} value={umbilical.ir.value} />
        </div>
        <div className="ub-col ub-col-status">
          <PowerStatusPill label={null} statusText={umbilical.water_leak} isOk={umbilical.water_leak === "No Leak"} />
          <div className="power-grey-label">{`${prefix} IR`}</div>
          <PowerStatusPill label={null} statusText={umbilical.ir_status} isOk={umbilical.ir_status !== "LOW IR"} />
        </div>
      </div>
    </div>
  );
}
