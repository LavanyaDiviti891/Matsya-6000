import React, { useState } from 'react';
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

const SUB_VIEWS = [
  { key: 'front', label: 'Front', src: '/sub_front.jpeg' },
  { key: 'back',  label: 'Back',  src: '/sub_back.jpeg'  },
  { key: 'side',  label: 'Side',  src: '/sub_side.jpeg'  },
  { key: 'top',   label: 'Top',   src: '/sub_top.jpeg'   },
  { key: 'bottom',label: 'Bottom',src: '/sub_bottom.jpeg'},
];

export function CompassBox({ idKey = null }) {
  const [active, setActive] = useState('side');
  const current = SUB_VIEWS.find(v => v.key === active);

  return (
    <div className="sub-viewer" id={idKey}>
      <div className="sub-viewer-img-wrap">
        <img
          key={current.src}
          src={current.src}
          alt={current.label + ' view of submersible'}
          className="sub-viewer-img"
        />
        <div className="sub-viewer-badge">{current.label} View</div>
      </div>
      <div className="sub-viewer-nav">
        {SUB_VIEWS.map(v => (
          <button
            key={v.key}
            className={`sub-view-btn${active === v.key ? ' active' : ''}`}
            onClick={() => setActive(v.key)}
          >
            {v.label}
          </button>
        ))}
      </div>
    </div>
  );
}
