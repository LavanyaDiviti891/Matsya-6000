import React from 'react';
import { fmtVal, onPost } from '../utils';

export function ImagingToggle({ label, isOn, inline, idKey, toggleUrl }) {
  const tCls = isOn ? "toggle-on" : "toggle-off";
  const dCls = isOn ? "toggle-dot-on" : "toggle-dot-off";
  const wrapperCls = inline ? "img-toggle-inline" : "img-toggle-block";

  return (
    <div className={wrapperCls} id={idKey} onClick={() => onPost(toggleUrl)}>
      <span className="img-toggle-label">{label}</span>
      <div className="img-toggle-controls">
        <div className={`toggle-track ${tCls}`}>
          <div className={`toggle-dot ${dCls}`}></div>
        </div>
        <span className="img-toggle-state">{isOn ? "ON" : "OFF"}</span>
      </div>
    </div>
  );
}

export function LedDimmerSlider({ label, value, minVal = 0, maxVal = 10 }) {
  const percent = Math.max(0, Math.min(100, ((value - minVal) / (maxVal - minVal)) * 100));
  const scaleLabels = ["0", "2", "4", "6", "8", "10"];
  
  const ticks = Array.from({ length: 21 }).map((_, i) => (
    <div key={i} className={`dim-tick ${i % 4 === 0 ? "dim-tick-major" : "dim-tick-minor"}`}></div>
  ));

  return (
    <div className="led-dimmer-slider">
      <span className="dim-label">{label}</span>
      <div className="dim-slider-wrap">
        <div className="dim-track">
          <div className="dim-fill" style={{ width: `${percent}%` }}></div>
          <div className="dim-thumb" style={{ left: `${percent}%` }}></div>
        </div>
        <div className="dim-tick-row">{ticks}</div>
        <div className="dim-scale-row">
          {scaleLabels.map((sl, i) => <span key={i} className="dim-scale-label">{sl}</span>)}
        </div>
      </div>
    </div>
  );
}

export function CameraActionGrid() {
  return (
    <div className="cam-action-grid">
      <div className="cam-btn">Iris close</div>
      <div className="cam-btn">Zoom in</div>
      <div className="cam-btn">Iris open</div>
      <div className="cam-btn">Zoom out</div>
      <div className="cam-btn">Near</div>
      <div className="cam-btn">Far</div>
    </div>
  );
}

export function PanTiltBar({ label, value, minVal, maxVal, scaleLabels }) {
  const percent = Math.max(0, Math.min(100, ((value - minVal) / (maxVal - minVal)) * 100));
  
  return (
    <div className="pan-tilt-bar">
      <div className="pt-header">
        <span className="pt-label">{label}</span>
        <div className="pt-value-box">{fmtVal(value)}</div>
        <span className="pt-unit">deg</span>
        <div className="pt-indicator-led pt-led-on"></div>
      </div>
      <div className="pt-slider-wrap">
        <div className="pt-track">
          <div className="pt-fill" style={{ width: `${percent}%` }}></div>
          <div className="pt-thumb" style={{ left: `${percent}%` }}></div>
        </div>
        <div className="pt-scale-row">
          {scaleLabels.map((sl, i) => <span key={i} className="pt-scale-label">{sl}</span>)}
        </div>
      </div>
    </div>
  );
}

export function PanTiltPad({ panVal, tiltVal }) {
  return (
    <div className="pan-tilt-pad">
      <div className="pt-pad-grid">
        <div className="pt-pad-btn pt-pad-up">T-UP</div>
        <div className="pt-pad-btn pt-pad-left">P-LFT</div>
        <div className="pt-pad-home">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path><polyline points="9 22 9 12 15 12 15 22"></polyline></svg>
        </div>
        <div className="pt-pad-btn pt-pad-right">P-RGT</div>
        <div className="pt-pad-btn pt-pad-down">T-DWN</div>
      </div>
      <div className="pt-manual-section">
        <div className="pt-manual-btn">manual</div>
        <div className="pt-manual-inputs">
          <div className="pt-manual-row">
            <span className="pt-manual-label">PAN</span>
            <div className="pt-manual-input">{fmtVal(panVal)}</div>
            <span className="pt-manual-unit">Deg</span>
          </div>
          <div className="pt-manual-row">
            <span className="pt-manual-label">TILT</span>
            <div className="pt-manual-input">{fmtVal(tiltVal)}</div>
            <span className="pt-manual-unit">Deg</span>
          </div>
        </div>
      </div>
    </div>
  );
}
