import React from 'react';
import { fmtVal, onPost } from '../utils';

export function ThrusterRPMGauge({ label, rpm, maxRpm = 1600 }) {
  const percent = Math.max(0, Math.min(100, (rpm / maxRpm) * 100));
  const rotation = (percent / 100) * 180;
  const scaleValues = [0, 200, 400, 600, 800, 1000, 1200, 1400, 1600];
  
  const labelsDivs = scaleValues.map((sv, i) => {
    const f = i / (scaleValues.length - 1);
    const angle = Math.PI * (1 - f);
    const r = 62, cx = 70, cy = 65;
    const x = cx + r * Math.cos(angle);
    const y = cy - r * Math.sin(angle);
    return (
      <span key={i} className="tg-scale-label" style={{ left: `${Math.round(x)}px`, top: `${Math.round(y)}px`, transform: 'translate(-50%,-50%)' }}>
        {sv}
      </span>
    );
  });

  return (
    <div className="thruster-gauge">
      <div className="tg-labels-container">{labelsDivs}</div>
      <div className="tg-track">
        <div className="tg-fill" style={{ transform: `rotate(${rotation}deg)` }}></div>
        <div className="tg-cover"></div>
      </div>
      <div className="tg-readout">
        <span className="tg-rpm-value">{fmtVal(rpm)}</span>
      </div>
      <span className="tg-label">{label}</span>
      <span className="tg-rpm-unit">RPM</span>
    </div>
  );
}

function MiniToggle({ label, isOn, suffixId, url, thrusterId }) {
  const tCls = isOn ? "toggle-on" : "toggle-off";
  const dCls = isOn ? "toggle-dot-on" : "toggle-dot-off";
  return (
    <div className="prop-toggle-row" id={`tpet-${thrusterId}-${suffixId}`} onClick={() => onPost(url)}>
      <span className="prop-toggle-label">{label}</span>
      <div className="prop-toggle-controls">
        <div className={`toggle-track ${tCls}`}>
          <div className={`toggle-dot ${dCls}`}></div>
        </div>
        <span className="prop-toggle-state">{isOn ? "ON" : "OFF"}</span>
      </div>
    </div>
  );
}

export function ThrusterPowerEnableToggles({ thrusterId, power, enable, toggleUrlP, toggleUrlE }) {
  return (
    <div className="prop-toggle-pair">
      <MiniToggle label={`T${thrusterId}_Power`} isOn={power} suffixId="power" url={toggleUrlP} thrusterId={thrusterId} />
      <MiniToggle label={`T${thrusterId}_Enable`} isOn={enable} suffixId="enable" url={toggleUrlE} thrusterId={thrusterId} />
    </div>
  );
}

export function ThrusterPanel({ thrusterId, t }) {
  return (
    <div className="thruster-panel">
      <div className="thruster-panel-id">T{thrusterId}</div>
      <ThrusterRPMGauge label={`T${thrusterId} Speed`} rpm={t.rpm} />
      <div className="tp-metrics">
        <div className="tp-metric-row">
          <span className="tp-metric-label">Voltage</span>
          <div className="tp-metric-value">{fmtVal(t.voltage)}</div>
          <span className="tp-metric-unit">V</span>
        </div>
        <div className="tp-metric-row">
          <span className="tp-metric-label">Current</span>
          <div className="tp-metric-value">{fmtVal(t.current)}</div>
          <span className="tp-metric-unit">A</span>
        </div>
        <div className="tp-metric-row">
          <span className="tp-metric-label">Temp</span>
          <div className="tp-metric-value">{fmtVal(t.temp)}</div>
          <span className="tp-metric-unit">°C</span>
        </div>
      </div>
      <div className="tp-ctrl-row">
        <span className="tp-ctrl-label">{`T${thrusterId} ctrl`}</span>
        <div className="tp-ctrl-value">{fmtVal(t.ctrl)}</div>
      </div>
    </div>
  );
}

function TinyTog({ label, isOn, suffixId, url, thrusterId }) {
  const tCls = isOn ? "toggle-on" : "toggle-off";
  const dCls = isOn ? "toggle-dot-on" : "toggle-dot-off";
  return (
    <div className="prop-center-tog-row" id={`pctb-${thrusterId}-${suffixId}`} onClick={() => onPost(url)}>
      <span className="prop-center-tog-label">{label}</span>
      <div className="prop-center-tog-controls">
        <div className={`toggle-track ${tCls}`}>
          <div className={`toggle-dot ${dCls}`}></div>
        </div>
        <span className="prop-center-tog-state">{isOn ? "ON" : "OFF"}</span>
      </div>
    </div>
  );
}

export function PropCenterToggleBlock({ thrusterId, power, enable, toggleUrlP, toggleUrlE }) {
  return (
    <div className="prop-center-block">
      <TinyTog label={`T${thrusterId}_Power`} isOn={power} suffixId="power" url={toggleUrlP} thrusterId={thrusterId} />
      <TinyTog label={`T${thrusterId}_Enable`} isOn={enable} suffixId="enable" url={toggleUrlE} thrusterId={thrusterId} />
    </div>
  );
}

export function PropAxisControl({ label, value }) {
  return (
    <div className="prop-axis-ctrl">
      <span className="prop-axis-label">{label}</span>
      <div className="prop-axis-value">{fmtVal(value)}</div>
    </div>
  );
}
