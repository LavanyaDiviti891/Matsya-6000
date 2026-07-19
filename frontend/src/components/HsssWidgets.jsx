import React from 'react';
import { fmtVal, onPost } from '../utils';

export function SemiCircleGauge({ label, value, minVal, maxVal, unit, scaleLabels, isOxygen }) {
  const percent = Math.max(0, Math.min(100, ((value - minVal) / (maxVal - minVal)) * 100));
  const rotation = (percent / 100) * 180;

  const labelsDivs = (scaleLabels || []).map((sl, i) => {
    const n = scaleLabels.length;
    const f = n > 1 ? i / (n - 1) : 0.5;
    const angle = Math.PI * (1 - f);
    const r = 120, cx = 130, cy = 120;
    const x = cx + r * Math.cos(angle);
    const y = cy - r * Math.sin(angle);
    return (
      <span key={i} className="sc-label" style={{ left: `${x}px`, top: `${y}px`, transform: 'translate(-50%, -50%)' }}>
        {sl}
      </span>
    );
  });

  const gaugeType = isOxygen ? "sc-gauge-oxygen" : "sc-gauge-co2";

  return (
    <div className="semi-circle-gauge">
      <div className="sc-labels-container">{labelsDivs}</div>
      <div className="sc-track">
        <div className={`sc-fill ${gaugeType}`} style={{ transform: `rotate(${rotation}deg)` }}></div>
        <div className="sc-cover"></div>
      </div>
      <div className="sc-readout">
        <span className="sc-value">{fmtVal(value)}</span>
        <span className="sc-title">{label}</span>
        <span className="sc-unit">({unit})</span>
      </div>
    </div>
  );
}

export function HorizontalProgressBar({ label, value, minVal, maxVal, unit, scaleLabels }) {
  const percent = Math.max(0, Math.min(100, ((value - minVal) / (maxVal - minVal)) * 100));
  return (
    <div className="horizontal-progress-bar">
      <div className="hp-header">
        <span className="hp-title">{label}</span>
        <div className="hp-value-box">{fmtVal(value)}</div>
      </div>
      <div className="hp-track">
        <div className="hp-fill" style={{ width: `${percent}%` }}></div>
      </div>
      {scaleLabels && (
        <div className="hp-scale-row">
          {scaleLabels.map((sl, i) => <span key={i} className="hp-scale-label">{sl}</span>)}
        </div>
      )}
    </div>
  );
}

export function SensorStatusPill({ label, statusText, isOk }) {
  const bgCls = isOk ? "sensor-ok" : "sensor-err";
  return (
    <div className="sensor-pill-container">
      <span className="sensor-label">{label}</span>
      <div className={`sensor-status ${bgCls}`}>{statusText}</div>
    </div>
  );
}

export function HSSSLabelInput({ label, value, unit }) {
  return (
    <div className="hsss-input-container">
      <span className="hsss-input-label">{label}</span>
      <div className="hsss-input-row">
        <div className="hsss-input-value">{fmtVal(value)}</div>
        <span className="hsss-input-unit">{unit}</span>
      </div>
    </div>
  );
}
