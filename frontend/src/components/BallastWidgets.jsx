import React from 'react';
import { fmtVal, onPost } from '../utils';

export function BallastActionButton({ label }) {
  return <div className="ballast-btn">{label}</div>;
}

export function BallastPressureRead({ label, value, isEnabled, idKey, toggleUrl }) {
  const toggleCls = isEnabled ? "toggle-on" : "toggle-off";
  const dotCls = isEnabled ? "toggle-dot-on" : "toggle-dot-off";
  
  return (
    <div className="ballast-pressure-read" id={idKey}>
      <span className="ballast-pressure-label">{label}</span>
      <div className="ballast-pressure-right">
        <div className="ballast-pressure-value">{fmtVal(value)}</div>
        <div className="toggle-controls" onClick={() => onPost(toggleUrl)}>
          <span className="toggle-state-text">{isEnabled ? "ON" : "OFF"}</span>
          <div className={`toggle-track ${toggleCls}`}>
            <div className={`toggle-dot ${dotCls}`}></div>
          </div>
        </div>
      </div>
    </div>
  );
}

export function BallastActSlider({ label, value, minVal = -150, maxVal = 150 }) {
  const percent = Math.max(0, Math.min(100, ((value - minVal) / (maxVal - minVal)) * 100));
  const scaleLabels = ["-150", "-100", "-50", "0", "50", "100", "150"];
  return (
    <div className="act-slider-container">
      <span className="act-slider-title">{label}</span>
      <div className="act-slider-row">
        <span className="act-slider-side">Open</span>
        <div className="act-track-wrap">
          <div className="act-track">
            <div className="act-thumb" style={{ left: `${percent}%` }}></div>
          </div>
          <div className="act-scale-row">
            {scaleLabels.map((sl, i) => <span key={i} className="act-scale-label">{sl}</span>)}
          </div>
        </div>
        <span className="act-slider-side">Closed</span>
      </div>
    </div>
  );
}

export function VBSTankGauge({ level, maxVal = 300 }) {
  const percent = Math.max(0, Math.min(100, (level / maxVal) * 100));
  const scaleLabels = ["300", "250", "200", "150", "100", "50", "0"];
  return (
    <div className="vbs-tank-gauge">
      <div className="vbs-tank-title">VBS Tank</div>
      <div className="vbs-tank-body">
        <div className="vbs-tank-scale">
          {scaleLabels.map((lbl, i) => <span key={i} className="vbs-tank-scale-label">{lbl}</span>)}
        </div>
        <div className="vbs-tank-track">
          <div className="vbs-tank-fill" style={{ height: `${percent}%` }}></div>
        </div>
      </div>
      <div className="vbs-tank-readout">
        <span className="vbs-tank-value">{fmtVal(level)}</span>
        <span className="vbs-tank-unit">L</span>
      </div>
    </div>
  );
}

export function VBSMetricRow({ label, value, unit }) {
  return (
    <div className="vbs-metric-row">
      <span className="vbs-metric-label">{label}</span>
      <div className="vbs-metric-right">
        <div className="vbs-metric-value">{fmtVal(value)}</div>
        {unit && <span className="vbs-metric-unit">{unit}</span>}
      </div>
    </div>
  );
}

export function VBSWaterButton({ label }) {
  return <div className="vbs-water-btn">{label}</div>;
}

export function VBSSetControl({ value }) {
  return (
    <div className="vbs-set-container">
      <span className="vbs-set-label">VBS SET</span>
      <div className="vbs-set-spinbox">
        <div className="vbs-set-arrow">▲</div>
        <div className="vbs-set-value">{fmtVal(value)}</div>
        <div className="vbs-set-arrow">▼</div>
      </div>
    </div>
  );
}

export function TrimPositionBar({ value, maxVal = 4500 }) {
  const percent = Math.max(0, Math.min(100, (value / maxVal) * 100));
  const scaleLabels = ["0", "500", "1000", "1500", "2000", "2500", "3000", "3500", "4000", "4500"];
  return (
    <div className="trim-position-bar">
      <div>
        <div className="trim-track">
          <div className="trim-thumb" style={{ left: `${percent}%` }}></div>
        </div>
      </div>
      <div className="trim-scale-row">
        {scaleLabels.map((sl, i) => <span key={i} className="trim-scale-label">{sl}</span>)}
      </div>
    </div>
  );
}

export function SpeedControlSlider({ value, minVal = 1, maxVal = 7 }) {
  const percent = Math.max(0, Math.min(100, ((value - minVal) / (maxVal - minVal)) * 100));
  const scaleLabels = ["1", "2", "3", "4", "5", "6", "7"];
  return (
    <div className="speed-control-slider">
      <span className="speed-ctrl-label">Speed Control</span>
      <div className="speed-track-wrap">
        <div className="speed-track">
          <div className="speed-thumb" style={{ left: `${percent}%` }}></div>
        </div>
        <div className="speed-scale-row">
          {scaleLabels.map((sl, i) => <span key={i} className="speed-scale-label">{sl}</span>)}
        </div>
      </div>
    </div>
  );
}

export function OIMToggleRow({ label, isOn, idKey, toggleUrl }) {
  const toggleCls = isOn ? "toggle-on" : "toggle-off";
  const dotCls = isOn ? "toggle-dot-on" : "toggle-dot-off";
  return (
    <div className="oim-toggle-row" id={idKey} onClick={() => onPost(toggleUrl)}>
      <span className="oim-toggle-label">{label}</span>
      <div className="toggle-controls">
        <span className="toggle-state-text">{isOn ? "ON" : "OFF"}</span>
        <div className={`toggle-track ${toggleCls}`}>
          <div className={`toggle-dot ${dotCls}`}></div>
        </div>
      </div>
    </div>
  );
}
