import React from 'react';
import { fmtVal } from '../utils';

export function VerticalGauge({
  label,
  value,
  maxVal,
  unit = "",
  lowIsGood = false,
  scaleLabels = [],
  idKey = null
}) {
  let percent = 0;
  if (maxVal && maxVal > 0) {
    percent = Math.min(100, Math.max(0, (value / maxVal) * 100));
  }
  
  let fillCls = "gauge-fill-green";
  if (lowIsGood) {
    fillCls = percent > 80 ? "gauge-fill-red" : "gauge-fill-green";
  }

  return (
    <div className="gauge-container" id={idKey}>
      <div className="gauge-body">
        <div className="gauge-scale">
          {scaleLabels && scaleLabels.map((lbl, idx) => (
            <span key={idx} className="gauge-scale-label">{lbl}</span>
          ))}
        </div>
        <div className="gauge-track">
          <div className={`gauge-fill ${fillCls}`} style={{ height: `${percent}%` }}></div>
        </div>
      </div>
      <h3 className="gauge-title">{label}</h3>
      <div className="gauge-readout">
        <span className="gauge-value">{fmtVal(value)}</span>
        {unit && <span className="gauge-unit">{unit}</span>}
      </div>
    </div>
  );
}

export function SimpleRpmBox({ label, value, idKey = null }) {
  return (
    <div className="rpm-box" id={idKey}>
      <span className="rpm-label">{label}</span>
      <div className="rpm-value">{fmtVal(value)}</div>
    </div>
  );
}

export function CompassBox({ idKey = null }) {
  return (
    <div className="compass-box" id={idKey}>
      <span className="compass-label compass-n">N</span>
      <span className="compass-label compass-s">S</span>
      <span className="compass-label compass-w">W</span>
      <span className="compass-label compass-e">E</span>
      <div className="compass-inner"></div>
    </div>
  );
}
