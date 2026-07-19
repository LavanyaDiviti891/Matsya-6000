import React from 'react';
import { fmtVal, onPost } from '../utils';

// ---- SENSORS WIDGETS ----
export function SensorToggleBlock({ label, isOn, idKey, toggleUrl }) {
  const tCls = isOn ? "toggle-on" : "toggle-off";
  const dCls = isOn ? "toggle-dot-on" : "toggle-dot-off";
  return (
    <div className="sens-toggle-block" id={idKey} onClick={() => onPost(toggleUrl)}>
      <span className="sens-toggle-label">{label}</span>
      <div className="sens-toggle-controls">
        <div className={`toggle-track ${tCls}`}>
          <div className={`toggle-dot ${dCls}`}></div>
        </div>
        <span className="sens-toggle-state">{isOn ? "ON" : "OFF"}</span>
      </div>
    </div>
  );
}

export function SensorLedStatus({ label, isOn }) {
  const dotCls = isOn ? "sens-led-on" : "sens-led-off";
  return (
    <div className="sens-led-container">
      <span className="sens-led-label">{label}</span>
      <div className="sens-led-graphic">
        <div className={`sens-led-dot ${dotCls}`}></div>
        <div className={isOn ? "sens-led-rect" : "sens-led-rect-off"}></div>
      </div>
    </div>
  );
}

export function AlarmLedStatus({ label, isOn }) {
  const dotCls = isOn ? "sens-led-on" : "sens-led-off";
  return (
    <div className="sens-led-container">
      <span className="sens-led-label">{label}</span>
      <div className={`sens-led-dot ${dotCls}`}></div>
    </div>
  );
}

export function ScientificSensorRowItem({ label, portVal, stbdVal, unit }) {
  return (
    <div className="sci-sens-row">
      <span className="sci-sens-label">{label}</span>
      <div className="sci-sens-value">{String(portVal)}</div>
      <div className="sci-sens-value">{String(stbdVal)}</div>
      {unit && <span className="sci-sens-unit">{unit}</span>}
    </div>
  );
}

export function SensorBoxMetric({ label, value, unit }) {
  return (
    <div className="sens-box-row">
      <span className="sens-box-label">{label}</span>
      <div className="sens-box-value">{fmtVal(value)}</div>
      {unit && <span className="sens-box-unit">{unit}</span>}
    </div>
  );
}

export function BuzzerPanel({ active }) {
  const dotCls = active ? "sens-led-on buzzer-active" : "sens-led-off";
  return (
    <div className="buzzer-panel">
      <div className="buzzer-label">Buzzer</div>
      <div className={`buzzer-light ${dotCls}`}></div>
      <div className="buzzer-ack-btn">ACK</div>
    </div>
  );
}

// ---- LOGGING WIDGETS ----
export function LogTable({ title, isEvent, rows }) {
  const headers = ["Date", "Time", "Location", isEvent ? "Event" : "Error"];
  const renderedRows = Array.from({ length: 15 }).map((_, i) => {
    if (i < (rows || []).length) {
      const r = rows[i];
      return (
        <div key={i} className="log-table-row">
          <div className="log-table-td">{r.date}</div>
          <div className="log-table-td">{r.time}</div>
          <div className="log-table-td">{r.location}</div>
          <div className="log-table-td log-table-td-stretch">{r.message}</div>
        </div>
      );
    }
    return (
      <div key={i} className="log-table-row">
        <div className="log-table-td empty"></div>
        <div className="log-table-td empty"></div>
        <div className="log-table-td empty"></div>
        <div className="log-table-td log-table-td-stretch empty"></div>
      </div>
    );
  });

  return (
    <div className="log-panel">
      <div className="log-table-title">{title}</div>
      <div className="log-table-container">
        <div className="log-table-header-row">
          {headers.map((h, i) => <div key={i} className="log-table-th">{h}</div>)}
        </div>
        <div className="log-table-body">{renderedRows}</div>
      </div>
    </div>
  );
}

export function HorizontalToggle({ label, isOn, idKey, toggleUrl }) {
  const tCls = isOn ? "toggle-on" : "toggle-off";
  const dCls = isOn ? "toggle-dot-on" : "toggle-dot-off";
  return (
    <div className="h-toggle-wrap" id={idKey} onClick={() => onPost(toggleUrl)}>
      <span className="h-toggle-label">{label}</span>
      <div className={`toggle-track ${tCls}`}>
        <div className={`toggle-dot ${dCls}`}></div>
      </div>
      <span className="h-toggle-state">{isOn ? "ON" : "OFF"}</span>
    </div>
  );
}

export function RedSignalIndicator({ label, isOn }) {
  const clsDot = isOn ? "signal-dot-on" : "signal-dot-off";
  return (
    <div className="signal-indicator">
      <span className="signal-label">{label}</span>
      <div className={`signal-dot ${clsDot}`}></div>
    </div>
  );
}

// ---- STATUS WIDGETS ----
export function StatusChartRowComponent({ selectedOption, yLabels, xLabels }) {
  return (
    <div className="status-row-widget">
      <div className="status-dropdown-container">
        <div className="status-dropdown">
          <span className="status-dropdown-text">{selectedOption}</span>
          <div className="status-dropdown-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="6 9 12 15 18 9"></polyline></svg>
          </div>
        </div>
      </div>
      <div className="status-chart-container">
        <div className="status-y-title">Amplitude</div>
        <div className="status-chart-inner">
          <div className="status-chart-main">
            <div className="status-y-axis">
              {[...yLabels].reverse().map((y, i) => <span key={i} className="status-y-label">{y}</span>)}
            </div>
            <div className="status-grid"></div>
          </div>
          <div className="status-chart-bottom">
            <div className="status-x-axis">
              {xLabels.map((x, i) => <span key={i} className="status-x-label">{x}</span>)}
            </div>
            <div className="status-x-title">Time</div>
          </div>
        </div>
      </div>
    </div>
  );
}

// ---- 50 KWH WIDGETS ----
export function KwhDataGrid({ titleSub, colHeaders, batteries }) {
  const rowsLabels = ["CUR", "VOT", "ID Cell Max", "Max Temp", "ID Cell Min", "Min Temp", "Temp", "SOC", "SOH"];
  const fields = ["cur", "vot", "id_cell_max", "max_temp", "id_cell_min", "min_temp", "temp", "soc", "soh"];
  
  return (
    <div className="kwh-grid-panel">
      <div className="kwh-grid-subtitle">{titleSub}</div>
      <div className="kwh-grid-content">
        <div className="kwh-label-col">
          <span></span>
          {rowsLabels.map((l, i) => <span key={i} className="kwh-row-label">{l}</span>)}
        </div>
        {batteries.map((bat, i) => (
          <div key={i} className="kwh-data-col">
            <span className="kwh-col-header">{colHeaders[i]}</span>
            {fields.map((f, j) => <div key={j} className="kwh-cell-value">{fmtVal(bat[f])}</div>)}
          </div>
        ))}
      </div>
    </div>
  );
}

export function KwhVerticalGauge({ label, value, minVal, maxVal, scaleLabels }) {
  const percent = Math.max(0, Math.min(100, ((value - minVal) / (maxVal - minVal)) * 100));
  return (
    <div className="kwh-vg-container">
      <span className="kwh-vg-title">{label}</span>
      <div className="kwh-vg-body">
        <div className="kwh-vg-scale-col">
          {[...scaleLabels].reverse().map((sl, i) => <span key={i} className="kwh-vg-scale-label">{sl}</span>)}
        </div>
        <div className="kwh-vg-track">
          <div className="kwh-vg-fill" style={{ height: `${percent}%` }}></div>
        </div>
      </div>
      <div className="kwh-vg-input">{fmtVal(value)}</div>
    </div>
  );
}

// ---- MCC WIDGETS ----
export function MccIndicator({ label, isOn }) {
  const ledCls = isOn ? "mcc-led-on" : "mcc-led-off";
  return (
    <div className="mcc-indicator-row">
      <span className="mcc-label">{label}</span>
      <div className={`mcc-led ${ledCls}`}></div>
    </div>
  );
}

export function MccStatusBox({ label, value, bgColorCls }) {
  return (
    <div className="mcc-status-row">
      <span className="mcc-status-label">{label}</span>
      <div className={`mcc-status-box ${bgColorCls}`}>{value}</div>
    </div>
  );
}

export function MccMessageInput({ label, value }) {
  return (
    <div className="mcc-message-row">
      <span className="mcc-message-label">{label}</span>
      <div className="mcc-message-value">{value}</div>
    </div>
  );
}

export function MccShipData({ label, value }) {
  return (
    <div className="mcc-ship-col">
      <span className="mcc-ship-label">{label}</span>
      <div className="mcc-ship-value">{fmtVal(value)}</div>
    </div>
  );
}

export function MccRadioGroup({ selectedVal }) {
  const options = ["Low", "Medium", "High", "Very High"];
  return (
    <div className="mcc-radio-group">
      <span className="mcc-power-title">Power Status</span>
      {options.map((val, i) => (
        <div key={i} className="mcc-radio-item">
          <div className={`mcc-radio-circle ${val === selectedVal ? 'mcc-radio-dot-on' : 'mcc-radio-dot-off'}`}></div>
          <span className="mcc-radio-label">{val}</span>
        </div>
      ))}
    </div>
  );
}

export function MccCrewStatus({ label, isOk }) {
  const bgCls = isOk ? "mcc-crew-ok" : "mcc-crew-err";
  const text = isOk ? "OK" : "ERR";
  return (
    <div className="mcc-crew-row">
      <span className="mcc-crew-label">{label}</span>
      <div className={`mcc-crew-box ${bgCls}`}>{text}</div>
    </div>
  );
}

export function MccPowerDropdown({ val }) {
  return (
    <div className="mcc-dropdown-wrap">
      <span className="mcc-dropdown-label">Power</span>
      <div className="mcc-dropdown-box">
        <span className="mcc-dropdown-val">{val}</span>
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="6 9 12 15 18 9"></polyline></svg>
      </div>
    </div>
  );
}
