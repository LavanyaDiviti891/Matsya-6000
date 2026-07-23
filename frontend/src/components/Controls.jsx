import React, { useRef, useCallback } from 'react';
import { fmtVal } from '../utils';

// Helper for generating random tape rotations
const getTapeStyle = (label) => {
  // deterministic pseudo-random rotation based on label length
  const rot = ((label?.length || 5) % 5) - 2; 
  return { transform: `rotate(${rot}deg)` };
};

export function ToggleSwitch({ label, isOn, onToggle, idKey = null }) {
  const toggleCls = isOn ? "toggle-on" : "toggle-off";
  const dotCls = isOn ? "toggle-dot-on" : "toggle-dot-off";
  return (
    <div className="toggle-switch" id={idKey} onClick={onToggle}>
      <span className="toggle-label">{label}</span>
      <div className="toggle-controls">
        <span className="toggle-state-text">{isOn ? "ON" : "OFF"}</span>
        <div className={`toggle-track ${toggleCls}`}>
          <div className={`toggle-dot ${dotCls}`}></div>
        </div>
      </div>
    </div>
  );
}

export function MetalSwitch({ label, isOn, onToggle, idKey = null, showLed = false }) {
  const id = idKey || (label ? label.replace(/\s/g,'_') : Math.random().toString(36).slice(2));

  return (
    <div
      className="metal-switch-container"
      id={idKey}
      onClick={onToggle}
      style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', cursor: 'pointer', margin: '6px 8px', userSelect: 'none' }}
    >
      <svg width="60" height="100" viewBox="0 0 60 100"
        style={{ overflow: 'visible', filter: 'drop-shadow(2px 6px 10px rgba(0,0,0,0.8))' }}
      >
        <defs>
          {/* Hex nut — strong multi-stop left-to-right chrome sweep */}
          <linearGradient id={`hex-${id}`} x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%"   stopColor="#282828"/>
            <stop offset="8%"   stopColor="#606060"/>
            <stop offset="20%"  stopColor="#b8b8b8"/>
            <stop offset="32%"  stopColor="#e8e8e8"/>
            <stop offset="42%"  stopColor="#fafafa"/>
            <stop offset="50%"  stopColor="#ffffff"/>
            <stop offset="60%"  stopColor="#f0f0f0"/>
            <stop offset="72%"  stopColor="#c8c8c8"/>
            <stop offset="85%"  stopColor="#808080"/>
            <stop offset="100%" stopColor="#282828"/>
          </linearGradient>

          {/* Hex face shading — subtle diagonal for depth */}
          <linearGradient id={`hexFace-${id}`} x1="0%" y1="0%" x2="60%" y2="100%">
            <stop offset="0%"   stopColor="rgba(255,255,255,0.18)"/>
            <stop offset="100%" stopColor="rgba(0,0,0,0.22)"/>
          </linearGradient>

          {/* Bushing ring — radial chrome with strong specular */}
          <radialGradient id={`bus-${id}`} cx="35%" cy="30%" r="72%">
            <stop offset="0%"   stopColor="#f8f8f8"/>
            <stop offset="18%"  stopColor="#d8d8d8"/>
            <stop offset="40%"  stopColor="#a8a8a8"/>
            <stop offset="65%"  stopColor="#686868"/>
            <stop offset="85%"  stopColor="#404040"/>
            <stop offset="100%" stopColor="#282828"/>
          </radialGradient>

          {/* Inner recess — dark concave bowl */}
          <radialGradient id={`rec-${id}`} cx="40%" cy="35%" r="68%">
            <stop offset="0%"   stopColor="#787878"/>
            <stop offset="30%"  stopColor="#404040"/>
            <stop offset="70%"  stopColor="#1a1a1a"/>
            <stop offset="100%" stopColor="#080808"/>
          </radialGradient>

          {/* Mounting tabs — light brushed chrome */}
          <linearGradient id={`tab-${id}`} x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%"   stopColor="#b0b0b0"/>
            <stop offset="30%"  stopColor="#f0f0f0"/>
            <stop offset="50%"  stopColor="#ffffff"/>
            <stop offset="70%"  stopColor="#f0f0f0"/>
            <stop offset="100%" stopColor="#b0b0b0"/>
          </linearGradient>

          {/* Bat unified shaft gradient */}
          <linearGradient id={`shaftMetal-${id}`} x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%"   stopColor="#505050"/>
            <stop offset="20%"  stopColor="#a8a8a8"/>
            <stop offset="40%"  stopColor="#eeeeee"/>
            <stop offset="70%"  stopColor="#909090"/>
            <stop offset="100%" stopColor="#404040"/>
          </linearGradient>

          {/* Bat spherical volume glow */}
          <radialGradient id={`bulbGlow-${id}`} cx="35%" cy="35%" r="65%">
            <stop offset="0%"   stopColor="rgba(255,255,255,0.7)"/>
            <stop offset="40%"  stopColor="rgba(255,255,255,0.3)"/>
            <stop offset="100%" stopColor="rgba(255,255,255,0)"/>
          </radialGradient>
        </defs>

        {/* ── TOP MOUNTING TAB (I = ON indicator) ── */}
        <rect x="20" y="1" width="20" height="24" rx="4"
          fill={`url(#tab-${id})`} stroke="#707070" strokeWidth="0.8"/>
        {/* Tab top bevel highlight */}
        <rect x="21" y="2" width="18" height="4" rx="2"
          fill="rgba(255,255,255,0.75)"/>
        {/* Tab bottom shadow */}
        <rect x="21" y="22" width="18" height="2" rx="1"
          fill="rgba(0,0,0,0.18)"/>
        {/* I mark */}
        <line x1="30" y1="7" x2="30" y2="19"
          stroke="#111" strokeWidth="3" strokeLinecap="round"/>

        {/* ── BOTTOM MOUNTING TAB (O = OFF indicator) ── */}
        <rect x="20" y="74" width="20" height="24" rx="4"
          fill={`url(#tab-${id})`} stroke="#707070" strokeWidth="0.8"/>
        {/* Tab top bevel highlight */}
        <rect x="21" y="75" width="18" height="4" rx="2"
          fill="rgba(255,255,255,0.65)"/>
        {/* Tab bottom shadow */}
        <rect x="21" y="95" width="18" height="2" rx="1"
          fill="rgba(0,0,0,0.15)"/>
        {/* O mark */}
        <circle cx="30" cy="86" r="5.5"
          fill="none" stroke="#111" strokeWidth="3"/>

        {/* ── HEX NUT BODY (center 30,50) ── */}
        {/* Outer hex — chrome gradient base */}
        <polygon
          points="30,26  55,40  55,60  30,74  5,60  5,40"
          fill={`url(#hex-${id})`}
        />
        {/* Hex face overlay for depth */}
        <polygon
          points="30,26  55,40  55,60  30,74  5,60  5,40"
          fill={`url(#hexFace-${id})`}
        />
        {/* Outer hex dark border */}
        <polygon
          points="30,26  55,40  55,60  30,74  5,60  5,40"
          fill="none" stroke="#1a1a1a" strokeWidth="0.9"
        />
        {/* Inner bevel highlight (bright edge) */}
        <polygon
          points="30,28.5  52.4,41.2  52.4,58.8  30,71.5  7.6,58.8  7.6,41.2"
          fill="none" stroke="rgba(255,255,255,0.65)" strokeWidth="1.5"
        />
        {/* Inner bevel shadow (dark edge inside) */}
        <polygon
          points="30,31  50,42.5  50,57.5  30,69  10,57.5  10,42.5"
          fill="none" stroke="rgba(0,0,0,0.35)" strokeWidth="1.2"
        />

        {/* ── KNURLED BUSHING RING ── */}
        <circle cx="30" cy="50" r="19" fill={`url(#bus-${id})`}/>
        {/* Knurl tick marks — alternating dark/light */}
        {Array.from({length: 32}).map((_, i) => {
          const a = (i / 32) * Math.PI * 2;
          const x1 = 30 + Math.cos(a) * 14.2, y1 = 50 + Math.sin(a) * 14.2;
          const x2 = 30 + Math.cos(a) * 18.5, y2 = 50 + Math.sin(a) * 18.5;
          return (
            <line key={i} x1={x1} y1={y1} x2={x2} y2={y2}
              stroke={i % 2 === 0 ? 'rgba(0,0,0,0.6)' : 'rgba(255,255,255,0.45)'}
              strokeWidth="1.0"
            />
          );
        })}
        {/* Bushing inner dark ring */}
        <circle cx="30" cy="50" r="14" fill="#4a4a4a"
          stroke="rgba(255,255,255,0.3)" strokeWidth="0.9"/>
        {/* Bushing highlight arc — top-left glint */}
        <path d="M 22,43 A 10,10 0 0 1 35,41" fill="none"
          stroke="rgba(255,255,255,0.5)" strokeWidth="1.5" strokeLinecap="round"/>

        {/* ── INNER RECESS (dark concave bowl) ── */}
        <circle cx="30" cy="50" r="13.5" fill={`url(#rec-${id})`}/>
        {/* Recess rim highlight */}
        <circle cx="30" cy="50" r="13.5" fill="none"
          stroke="rgba(255,255,255,0.2)" strokeWidth="0.8"/>

        {/* ── BAT LEVER (drawn last to be on top) ── */}
        {isOn ? (
          /* ON: bat pointing straight up — single connected shape */
          <g>
            {/* Unified shadow */}
            <path d="M 26.5 51.5 L 19.5 24.5 A 13 13 0 1 1 43.5 24.5 L 36.5 51.5 Z" fill="rgba(0,0,0,0.28)"/>
            {/* Unified bat body */}
            <path d="M 25 50 L 18 23 A 13 13 0 1 1 42 23 L 35 50 Z" fill={`url(#shaftMetal-${id})`}/>
            {/* Shaft left highlight */}
            <polygon points="26,50 27.5,50 21.5,23 20,23" fill="rgba(255,255,255,0.4)"/>
            
            {/* Bulb volume glow (soft blend) */}
            <circle cx="30" cy="18" r="11" fill={`url(#bulbGlow-${id})`}/>
            
            {/* Primary specular blob */}
            <ellipse cx="25" cy="13" rx="5" ry="3.5" fill="rgba(255,255,255,0.9)" transform="rotate(-20 25 13)"/>
            {/* Secondary sheen */}
            <ellipse cx="28.5" cy="18" rx="2" ry="1.5" fill="rgba(255,255,255,0.6)" transform="rotate(-20 28.5 18)"/>
            {/* Sphere bottom ambient rim (dark) */}
            <ellipse cx="30" cy="29" rx="7" ry="3" fill="rgba(0,0,0,0.3)"/>
          </g>
        ) : (
          /* OFF: bat pointing straight down — single connected shape */
          <g>
            {/* Unified shadow */}
            <path d="M 26.5 51.5 L 19.5 78.5 A 13 13 0 1 0 43.5 78.5 L 36.5 51.5 Z" fill="rgba(0,0,0,0.3)"/>
            {/* Unified bat body */}
            <path d="M 25 50 L 18 77 A 13 13 0 1 0 42 77 L 35 50 Z" fill={`url(#shaftMetal-${id})`}/>
            {/* Shaft left highlight */}
            <polygon points="26,50 27.5,50 21.5,77 20,77" fill="rgba(255,255,255,0.45)"/>
            
            {/* Bulb volume glow (soft blend) */}
            <circle cx="30" cy="82" r="11" fill={`url(#bulbGlow-${id})`}/>
            
            {/* Primary specular blob */}
            <ellipse cx="25" cy="77" rx="5" ry="3.5" fill="rgba(255,255,255,0.9)" transform="rotate(-20 25 77)"/>
            {/* Secondary specular */}
            <ellipse cx="28.5" cy="82" rx="2" ry="1.5" fill="rgba(255,255,255,0.6)" transform="rotate(-20 28.5 82)"/>
            {/* Sphere bottom ambient rim (dark) */}
            <ellipse cx="30" cy="93" rx="7" ry="3" fill="rgba(0,0,0,0.3)"/>
          </g>
        )}
      </svg>

      {label && (
        <div className="tape-label-real" style={{ marginTop: '4px', ...getTapeStyle(label) }}>
          {label}
        </div>
      )}
      {showLed && <LedIndicator isOn={isOn} />}
    </div>
  );
}

export function CompactToggle({ label, isOn, onToggle, idKey = null }) {
  const bg = isOn ? "#4caf50" : "#f44336";
  const align = isOn ? "flex-end" : "flex-start";
  return (
    <div 
      id={idKey} 
      onClick={onToggle}
      style={{
        display: 'flex', justifyContent: 'space-between', alignItems: 'center', 
        background: '#222', padding: '4px 8px', borderRadius: '4px',
        border: '1px solid #444', cursor: 'pointer', fontSize: '11px', width: '100%', boxSizing: 'border-box'
      }}
    >
      <span style={{ color: '#ddd', flex: 1, textAlign: 'left', paddingRight: '10px' }}>{label}</span>
      <div style={{ width: '32px', height: '16px', borderRadius: '8px', background: '#111', display: 'flex', alignItems: 'center', padding: '2px', boxSizing: 'border-box', justifyContent: align }}>
        <div style={{ width: '12px', height: '12px', borderRadius: '50%', background: bg, boxShadow: '0 0 4px rgba(0,0,0,0.5)' }}></div>
      </div>
    </div>
  );
}

export function Toggle3Pos({ labelTop, labelCenter, labelBottom, value, onToggle, idKey = null, showLed = false }) {
  const id = idKey || (labelTop ? labelTop.replace(/\s/g,'_') : Math.random().toString(36).slice(2));
  return (
    <div className="toggle-3pos-container" id={idKey} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', cursor: 'pointer', margin: '6px 8px', userSelect: 'none' }} onClick={onToggle}>
      <div className="tape-label-real" style={{ marginBottom: '12px', ...getTapeStyle(labelTop) }}>{labelTop}</div>
      <div style={{ display: 'flex', alignItems: 'center' }}>
        <svg width="60" height="100" viewBox="0 0 60 100" style={{ overflow: 'visible', filter: 'drop-shadow(2px 6px 10px rgba(0,0,0,0.8))' }}>
        <defs>
          {/* Hex nut — strong multi-stop left-to-right chrome sweep */}
          <linearGradient id={`hex-${id}`} x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%"   stopColor="#282828"/>
            <stop offset="8%"   stopColor="#606060"/>
            <stop offset="20%"  stopColor="#b8b8b8"/>
            <stop offset="32%"  stopColor="#e8e8e8"/>
            <stop offset="42%"  stopColor="#fafafa"/>
            <stop offset="50%"  stopColor="#ffffff"/>
            <stop offset="60%"  stopColor="#f0f0f0"/>
            <stop offset="72%"  stopColor="#c8c8c8"/>
            <stop offset="85%"  stopColor="#808080"/>
            <stop offset="100%" stopColor="#282828"/>
          </linearGradient>

          {/* Hex face shading — subtle diagonal for depth */}
          <linearGradient id={`hexFace-${id}`} x1="0%" y1="0%" x2="60%" y2="100%">
            <stop offset="0%"   stopColor="rgba(255,255,255,0.18)"/>
            <stop offset="100%" stopColor="rgba(0,0,0,0.22)"/>
          </linearGradient>

          {/* Bushing ring — radial chrome with strong specular */}
          <radialGradient id={`bus-${id}`} cx="35%" cy="30%" r="72%">
            <stop offset="0%"   stopColor="#f8f8f8"/>
            <stop offset="18%"  stopColor="#d8d8d8"/>
            <stop offset="40%"  stopColor="#a8a8a8"/>
            <stop offset="65%"  stopColor="#686868"/>
            <stop offset="85%"  stopColor="#404040"/>
            <stop offset="100%" stopColor="#282828"/>
          </radialGradient>

          {/* Inner recess — dark concave bowl */}
          <radialGradient id={`rec-${id}`} cx="40%" cy="35%" r="68%">
            <stop offset="0%"   stopColor="#787878"/>
            <stop offset="30%"  stopColor="#404040"/>
            <stop offset="70%"  stopColor="#1a1a1a"/>
            <stop offset="100%" stopColor="#080808"/>
          </radialGradient>

          {/* Mounting tabs — light brushed chrome */}
          <linearGradient id={`tab-${id}`} x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%"   stopColor="#b0b0b0"/>
            <stop offset="30%"  stopColor="#f0f0f0"/>
            <stop offset="50%"  stopColor="#ffffff"/>
            <stop offset="70%"  stopColor="#f0f0f0"/>
            <stop offset="100%" stopColor="#b0b0b0"/>
          </linearGradient>

          {/* Bat unified shaft gradient */}
          <linearGradient id={`shaftMetal-${id}`} x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%"   stopColor="#505050"/>
            <stop offset="20%"  stopColor="#a8a8a8"/>
            <stop offset="40%"  stopColor="#eeeeee"/>
            <stop offset="70%"  stopColor="#909090"/>
            <stop offset="100%" stopColor="#404040"/>
          </linearGradient>

          {/* Bat spherical volume glow */}
          <radialGradient id={`bulbGlow-${id}`} cx="35%" cy="35%" r="65%">
            <stop offset="0%"   stopColor="rgba(255,255,255,0.7)"/>
            <stop offset="40%"  stopColor="rgba(255,255,255,0.3)"/>
            <stop offset="100%" stopColor="rgba(255,255,255,0)"/>
          </radialGradient>
        </defs>

        {/* ── TOP MOUNTING TAB (I = ON indicator) ── */}
        <rect x="20" y="1" width="20" height="24" rx="4"
          fill={`url(#tab-${id})`} stroke="#707070" strokeWidth="0.8"/>
        {/* Tab top bevel highlight */}
        <rect x="21" y="2" width="18" height="4" rx="2"
          fill="rgba(255,255,255,0.75)"/>
        {/* Tab bottom shadow */}
        <rect x="21" y="22" width="18" height="2" rx="1"
          fill="rgba(0,0,0,0.18)"/>
        {/* I mark */}
        <line x1="30" y1="7" x2="30" y2="19"
          stroke="#111" strokeWidth="3" strokeLinecap="round"/>

        {/* ── BOTTOM MOUNTING TAB (I = ON indicator for 3-pos) ── */}
        <rect x="20" y="74" width="20" height="24" rx="4"
          fill={`url(#tab-${id})`} stroke="#707070" strokeWidth="0.8"/>
        {/* Tab top bevel highlight */}
        <rect x="21" y="75" width="18" height="4" rx="2"
          fill="rgba(255,255,255,0.65)"/>
        {/* Tab bottom shadow */}
        <rect x="21" y="95" width="18" height="2" rx="1"
          fill="rgba(0,0,0,0.15)"/>
        {/* I mark for bottom as well since both are ON */}
        <line x1="30" y1="80" x2="30" y2="92"
          stroke="#111" strokeWidth="3" strokeLinecap="round"/>

        {/* ── HEX NUT BODY (center 30,50) ── */}
        <polygon
          points="30,26  55,40  55,60  30,74  5,60  5,40"
          fill={`url(#hex-${id})`}
        />
        <polygon
          points="30,26  55,40  55,60  30,74  5,60  5,40"
          fill={`url(#hexFace-${id})`}
        />
        <polygon
          points="30,26  55,40  55,60  30,74  5,60  5,40"
          fill="none" stroke="#1a1a1a" strokeWidth="0.9"
        />
        <polygon
          points="30,28.5  52.4,41.2  52.4,58.8  30,71.5  7.6,58.8  7.6,41.2"
          fill="none" stroke="rgba(255,255,255,0.65)" strokeWidth="1.5"
        />
        <polygon
          points="30,31  50,42.5  50,57.5  30,69  10,57.5  10,42.5"
          fill="none" stroke="rgba(0,0,0,0.35)" strokeWidth="1.2"
        />

        {/* ── KNURLED BUSHING RING ── */}
        <circle cx="30" cy="50" r="19" fill={`url(#bus-${id})`}/>
        {Array.from({length: 32}).map((_, i) => {
          const a = (i / 32) * Math.PI * 2;
          const x1 = 30 + Math.cos(a) * 14.2, y1 = 50 + Math.sin(a) * 14.2;
          const x2 = 30 + Math.cos(a) * 18.5, y2 = 50 + Math.sin(a) * 18.5;
          return (
            <line key={i} x1={x1} y1={y1} x2={x2} y2={y2}
              stroke={i % 2 === 0 ? 'rgba(0,0,0,0.6)' : 'rgba(255,255,255,0.45)'}
              strokeWidth="1.0"
            />
          );
        })}
        <circle cx="30" cy="50" r="14" fill="#4a4a4a"
          stroke="rgba(255,255,255,0.3)" strokeWidth="0.9"/>
        <path d="M 22,43 A 10,10 0 0 1 35,41" fill="none"
          stroke="rgba(255,255,255,0.5)" strokeWidth="1.5" strokeLinecap="round"/>

        {/* ── INNER RECESS (dark concave bowl) ── */}
        <circle cx="30" cy="50" r="13.5" fill={`url(#rec-${id})`}/>
        <circle cx="30" cy="50" r="13.5" fill="none"
          stroke="rgba(255,255,255,0.2)" strokeWidth="0.8"/>

        {/* ── BAT LEVER ── */}
        {value === 1 ? (
          <g>
            <path d="M 26.5 51.5 L 19.5 24.5 A 13 13 0 1 1 43.5 24.5 L 36.5 51.5 Z" fill="rgba(0,0,0,0.28)"/>
            <path d="M 25 50 L 18 23 A 13 13 0 1 1 42 23 L 35 50 Z" fill={`url(#shaftMetal-${id})`}/>
            <polygon points="26,50 27.5,50 21.5,23 20,23" fill="rgba(255,255,255,0.4)"/>
            <circle cx="30" cy="18" r="11" fill={`url(#bulbGlow-${id})`}/>
            <ellipse cx="25" cy="13" rx="5" ry="3.5" fill="rgba(255,255,255,0.9)" transform="rotate(-20 25 13)"/>
            <ellipse cx="28.5" cy="18" rx="2" ry="1.5" fill="rgba(255,255,255,0.6)" transform="rotate(-20 28.5 18)"/>
            <ellipse cx="30" cy="29" rx="7" ry="3" fill="rgba(0,0,0,0.3)"/>
          </g>
        ) : value === -1 ? (
          <g>
            <path d="M 26.5 51.5 L 19.5 78.5 A 13 13 0 1 0 43.5 78.5 L 36.5 51.5 Z" fill="rgba(0,0,0,0.3)"/>
            <path d="M 25 50 L 18 77 A 13 13 0 1 0 42 77 L 35 50 Z" fill={`url(#shaftMetal-${id})`}/>
            <polygon points="26,50 27.5,50 21.5,77 20,77" fill="rgba(255,255,255,0.45)"/>
            <circle cx="30" cy="82" r="11" fill={`url(#bulbGlow-${id})`}/>
            <ellipse cx="25" cy="77" rx="5" ry="3.5" fill="rgba(255,255,255,0.9)" transform="rotate(-20 25 77)"/>
            <ellipse cx="28.5" cy="82" rx="2" ry="1.5" fill="rgba(255,255,255,0.6)" transform="rotate(-20 28.5 82)"/>
            <ellipse cx="30" cy="93" rx="7" ry="3" fill="rgba(0,0,0,0.3)"/>
          </g>
        ) : (
          <g>
             <circle cx="30" cy="53" r="14" fill="rgba(0,0,0,0.3)"/>
             <circle cx="30" cy="50" r="13" fill={`url(#shaftMetal-${id})`}/>
             <circle cx="30" cy="50" r="13" fill={`url(#bulbGlow-${id})`}/>
             <ellipse cx="26" cy="45" rx="5" ry="3.5" fill="rgba(255,255,255,0.9)" transform="rotate(-20 26 45)"/>
             <ellipse cx="29" cy="50" rx="2" ry="1.5" fill="rgba(255,255,255,0.6)" transform="rotate(-20 29 50)"/>
             <ellipse cx="30" cy="61" rx="7" ry="3" fill="rgba(0,0,0,0.3)"/>
          </g>
        )}

        </svg>
        {labelCenter && (
          <div className="tape-label-real" style={{ marginLeft: '12px', ...getTapeStyle(labelCenter) }}>{labelCenter}</div>
        )}
      </div>
      <div className="tape-label-real" style={{ marginTop: '12px', ...getTapeStyle(labelBottom) }}>{labelBottom}</div>
      {showLed && <LedIndicator isOn={value !== 0} />}
    </div>
  );
}

export function AlarmIndicator({ label, isOn, idKey = null }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', margin: '4px' }}>
      <div className={`real-black-square-btn ${isOn ? 'is-on' : ''}`}></div>
      {label && <div className="tape-label-real" style={{ marginTop: '4px', fontSize: '9px', ...getTapeStyle(label) }}>{label}</div>}
    </div>
  );
}

export function LedIndicator({ isOn, idKey = null }) {
  const bezelStyle = {
    width: '16px',
    height: '16px',
    borderRadius: '50%',
    background: 'linear-gradient(145deg, #e6e6e6 0%, #888888 40%, #333333 100%)',
    boxShadow: '0 2px 4px rgba(0,0,0,0.5), inset 0 1px 2px rgba(255,255,255,0.8), inset 0 -1px 2px rgba(0,0,0,0.5)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: '6px'
  };

  const lensStyle = {
    width: '10px',
    height: '10px',
    borderRadius: '50%',
    position: 'relative',
    background: isOn 
      ? 'radial-gradient(circle at 35% 35%, #ffb3b3 0%, #ff0000 40%, #990000 100%)' 
      : 'radial-gradient(circle at 35% 35%, #5a1111 0%, #2a0000 50%, #0a0000 100%)',
    boxShadow: isOn 
      ? '0 0 8px 3px rgba(255,0,0,0.8), inset 0 -1px 2px rgba(0,0,0,0.3)' 
      : 'inset 0 2px 4px rgba(0,0,0,0.9), 0 1px 1px rgba(255,255,255,0.3)',
    overflow: 'hidden'
  };

  const reflectionStyle = {
    position: 'absolute',
    top: '1px',
    left: '10%',
    width: '80%',
    height: '4px',
    borderRadius: '50%',
    background: 'linear-gradient(180deg, rgba(255,255,255,0.7) 0%, rgba(255,255,255,0) 100%)',
  };

  const bottomReflectionStyle = {
    position: 'absolute',
    bottom: '1px',
    left: '2px',
    width: '3px',
    height: '2px',
    borderRadius: '50%',
    background: 'rgba(255,255,255,0.4)',
    transform: 'rotate(-45deg)',
    filter: 'blur(0.5px)'
  };

  return (
    <div id={idKey} style={bezelStyle}>
      <div style={lensStyle}>
        <div style={reflectionStyle}></div>
        {!isOn && <div style={bottomReflectionStyle}></div>}
      </div>
    </div>
  );
}

export function Buzzer({ label, isOn, idKey = null }) {
  const holeFill = isOn ? "#880000" : "#050505";
  const defId = idKey || (label ? label.replace(/\s/g,'_') : Math.random().toString(36).slice(2));
  
  return (
    <div id={idKey} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', margin: '8px' }}>
      {label && <div className="tape-label-real" style={{ marginBottom: '6px', ...getTapeStyle(label) }}>{label}</div>}
      <svg width="48" height="48" viewBox="0 0 48 48" style={{ filter: isOn ? 'drop-shadow(0 0 6px red)' : 'none' }}>
        <defs>
          <filter id={`buzzerShadow-${defId}`}>
            <feDropShadow dx="0" dy="4" stdDeviation="4" floodOpacity="0.7" />
          </filter>
          
          <linearGradient id={`buzzerRim-${defId}`} x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#4a4a4a"/>
            <stop offset="50%" stopColor="#222"/>
            <stop offset="100%" stopColor="#0a0a0a"/>
          </linearGradient>

          <radialGradient id={`buzzerDome-${defId}`} cx="35%" cy="30%" r="65%">
            <stop offset="0%" stopColor="#555"/>
            <stop offset="20%" stopColor="#333"/>
            <stop offset="60%" stopColor="#151515"/>
            <stop offset="100%" stopColor="#050505"/>
          </radialGradient>
        </defs>

        {/* Outer housing (thick rim) */}
        <circle cx="24" cy="24" r="22" fill={`url(#buzzerRim-${defId})`} filter={`url(#buzzerShadow-${defId})`}/>
        
        {/* Inner dome */}
        <circle cx="24" cy="24" r="17" fill={`url(#buzzerDome-${defId})`} stroke="#000" strokeWidth="1"/>

        {/* Specular glint on outer rim */}
        <path d="M 8,24 A 16 16 0 0 1 24,8" fill="none" stroke="rgba(255,255,255,0.15)" strokeWidth="1.5" strokeLinecap="round" />
        
        {/* Specular glint on inner dome */}
        <ellipse cx="16" cy="16" rx="5" ry="3" fill="rgba(255,255,255,0.25)" transform="rotate(-45 16 16)" filter="blur(0.5px)"/>

        {/* Central hole */}
        <circle cx="24" cy="24" r="3" fill={holeFill} stroke="#0a0a0a" strokeWidth="1"/>
        <circle cx="24" cy="24" r="3" fill="none" stroke="rgba(0,0,0,0.8)" strokeWidth="1.5" />

        {/* 3 Sound arcs */}
        <g transform="translate(24,24)">
          {[0, 120, 240].map(angle => (
            <g key={angle} transform={`rotate(${angle})`}>
              <path d="M -6,-10.4 A 12 12 0 0 1 6,-10.4 L 3.5,-6 A 7 7 0 0 0 -3.5,-6 Z" fill={holeFill} stroke="#111" strokeWidth="0.5"/>
              <path d="M -6,-10.4 A 12 12 0 0 1 6,-10.4 L 3.5,-6 A 7 7 0 0 0 -3.5,-6 Z" fill="none" stroke="rgba(0,0,0,0.8)" strokeWidth="1.5"/>
            </g>
          ))}
        </g>
      </svg>
    </div>
  );
}

export function RotarySwitch({ label, value, onChange, idKey = null, topLabel="1", rightLabel="2", pos1Label="", pos2Label="" }) {
  const rotation = value === 1 ? -45 : 45;
  return (
    <div id={idKey} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '8px', position: 'relative' }}>
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'center' }}>
        {/* Left Label */}
        <div style={{ width: '80px', fontSize: '16px', fontWeight: 'bold', color: '#111', textAlign: 'right', whiteSpace: 'pre-wrap', marginRight: '10px', marginTop: '10px' }}>{pos1Label}</div>
        
        {/* Square gray faceplate */}
        <div
          onClick={onChange}
          style={{
            position: 'relative', width: '100px', height: '100px', borderRadius: '8px',
            background: '#4a4b4b', boxShadow: 'inset 0 0 2px rgba(255,255,255,0.2), 0 4px 6px rgba(0,0,0,0.5)',
            border: '1px solid #222', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer',
          }}
        >
          <div style={{ position: 'absolute', top: '8px', left: '12px', fontSize: '20px', fontWeight: 'bold', color: '#111', fontFamily: 'sans-serif' }}>{topLabel}</div>
          <div style={{ position: 'absolute', top: '8px', right: '12px', fontSize: '20px', fontWeight: 'bold', color: '#111', fontFamily: 'sans-serif' }}>{rightLabel}</div>

          {/* Knob */}
          <div style={{
            position: 'relative', width: '60px', height: '60px',
            transform: `rotate(${rotation}deg)`, transition: 'transform 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
          }}>
            <div style={{ position: 'absolute', top: '0', left: '0', width: '100%', height: '100%', borderRadius: '50%', background: '#1a1a1a', boxShadow: '2px 4px 6px rgba(0,0,0,0.8)' }}></div>
            {/* Pointer handle */}
            <div style={{
              position: 'absolute', top: '-10px', left: '50%', transform: 'translateX(-50%)',
              width: '18px', height: '40px', borderRadius: '8px', background: '#1a1a1a',
              boxShadow: '0 2px 4px rgba(0,0,0,0.6)'
            }}>
              <div style={{ position: 'absolute', top: '4px', left: '50%', transform: 'translateX(-50%)', width: '4px', height: '15px', borderRadius: '2px', background: '#e8e8e0' }}></div>
            </div>
          </div>
        </div>

        {/* Right Label */}
        <div style={{ width: '80px', fontSize: '16px', fontWeight: 'bold', color: '#111', textAlign: 'left', whiteSpace: 'pre-wrap', marginLeft: '10px', marginTop: '10px' }}>{pos2Label}</div>
      </div>

      <div style={{ position: 'absolute', bottom: '-45px', width: '100%', display: 'flex', justifyContent: 'center', zIndex: 10 }}>
        <div className="tape-label-real" style={{ fontSize: '15px', ...getTapeStyle(label) }}>{label}</div>
      </div>
    </div>
  );
}

export function KnobSwitch({ label, value = 50, onChange, idKey = null }) {
  const angle = typeof value === 'number' && value > 1 ? -135 + (value / 100) * 270 : 0;
  return (
    <div id={idKey} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '8px' }}>
      <div onClick={onChange} style={{
        position: 'relative', width: '50px', height: '50px', borderRadius: '50%', background: '#1a1a1a',
        boxShadow: '0 4px 6px rgba(0,0,0,0.6), inset 0 1px 2px rgba(255,255,255,0.1)', cursor: 'pointer',
        transform: `rotate(${angle}deg)`, transition: 'transform 0.1s linear',
      }}>
        <div style={{ position: 'absolute', top: '4px', left: '50%', transform: 'translateX(-50%)', width: '4px', height: '12px', borderRadius: '2px', background: '#fff' }}></div>
      </div>
      <div className="tape-label-real" style={getTapeStyle(label)}>{label}</div>
    </div>
  );
}

// ── KnobToggleSwitch ─────────────────────────────────────────────────────────
// Volume-knob style: drag up/right to increase, down/left to decrease.
export function KnobToggleSwitch({ label, value, onChange, idKey = null }) {
  // Settled rotation: -135° for pos 1, +135° for pos 2
  const settledAngle = value === 1 ? -135 : 135;
  const dragState = useRef(null); // { startY, startAngle, currentAngle }
  const knobRef = useRef(null);

  const onMouseDown = useCallback((e) => {
    e.preventDefault();
    dragState.current = {
      startY: e.clientY,
      startX: e.clientX,
      startAngle: settledAngle,
      currentAngle: settledAngle,
      hasFired: false,
    };

    const onMouseMove = (e) => {
      if (!dragState.current) return;
      // Vertical drag: up = positive rotation, down = negative
      const deltaY = dragState.current.startY - e.clientY;
      const deltaX = e.clientX - dragState.current.startX;
      const delta = (deltaY + deltaX) * 1.5; // sensitivity
      const raw = dragState.current.startAngle + delta;
      const clamped = Math.max(-135, Math.min(135, raw));
      dragState.current.currentAngle = clamped;

      // Live-rotate the knob via DOM ref
      if (knobRef.current) {
        knobRef.current.style.transform = `rotate(${clamped}deg)`;
        knobRef.current.style.transition = 'none';
      }

      // Fire onChange when crossing midpoint (0°)
      if (!dragState.current.hasFired) {
        if (value === 1 && clamped > 0) {
          dragState.current.hasFired = true;
          onChange();
        } else if (value === 2 && clamped < 0) {
          dragState.current.hasFired = true;
          onChange();
        }
      }
    };

    const onMouseUp = () => {
      // Snap back to settled position with animation
      if (knobRef.current) {
        knobRef.current.style.transition = 'transform 0.2s ease';
        knobRef.current.style.transform = `rotate(${settledAngle}deg)`;
      }
      dragState.current = null;
      window.removeEventListener('mousemove', onMouseMove);
      window.removeEventListener('mouseup', onMouseUp);
    };

    window.addEventListener('mousemove', onMouseMove);
    window.addEventListener('mouseup', onMouseUp);
  }, [settledAngle, value, onChange]);

  return (
    <div
      id={idKey}
      style={{
        display: 'flex', flexDirection: 'column', alignItems: 'center',
        gap: '8px', userSelect: 'none',
      }}
    >
      <div className="tape-label-real" style={getTapeStyle(label)}>{label}</div>

      {/* Knob circle */}
      <div
        ref={knobRef}
        onMouseDown={onMouseDown}
        style={{
          width: '70px', height: '70px', borderRadius: '50%',
          background: '#1e1e1e',
          boxShadow: '0 4px 10px rgba(0,0,0,0.8), inset 0 1px 2px rgba(255,255,255,0.08)',
          position: 'relative',
          transform: `rotate(${settledAngle}deg)`,
          transition: 'transform 0.25s ease',
          cursor: 'grab',
        }}
      >
        {/* Small indicator dot */}
        <div style={{
          position: 'absolute',
          top: '8px', left: '50%',
          transform: 'translateX(-50%)',
          width: '8px', height: '8px', borderRadius: '50%',
          background: '#ccc',
        }} />
      </div>
    </div>
  );
}

export function CircuitBreaker({ isOn, onToggle, idKey = null }) {
  // Realistic double-pole MCB (CHINT NB1-63 style)
  const poleStyle = {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    width: '34px',
  };

  const screwStyle = {
    width: '18px',
    height: '18px',
    borderRadius: '50%',
    background: 'radial-gradient(circle at 35% 35%, #555, #1a1a1a)',
    border: '2px solid #111',
    boxShadow: '0 2px 4px rgba(0,0,0,0.6), inset 0 1px 2px rgba(255,255,255,0.15)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    flexShrink: 0,
  };

  const screwSlotStyle = {
    width: '10px',
    height: '2px',
    background: '#111',
    transform: 'rotate(45deg)',
    borderRadius: '1px',
  };

  const indicatorStyle = {
    width: '8px',
    height: '8px',
    borderRadius: '1px',
    background: isOn ? '#00cc44' : '#004411',
    border: '1px solid #003309',
    boxShadow: isOn ? '0 0 4px #00ff55' : 'none',
    flexShrink: 0,
  };

  const handleStyle = {
    width: '18px',
    height: '38px',
    borderRadius: '3px 3px 5px 5px',
    background: isOn
      ? 'linear-gradient(180deg, #1a6fcc 0%, #0d4fa3 40%, #0a3d80 100%)'
      : 'linear-gradient(180deg, #1a6fcc 0%, #0d4fa3 40%, #0a3d80 100%)',
    border: '1px solid #083060',
    boxShadow: '0 2px 4px rgba(0,0,0,0.5), inset 0 1px 2px rgba(255,255,255,0.2)',
    cursor: 'pointer',
    transition: 'transform 0.12s ease',
    transform: isOn ? 'translateY(-5px)' : 'translateY(5px)',
    position: 'relative',
    flexShrink: 0,
  };

  // The "nub" on top of each handle
  const nubStyle = {
    position: 'absolute',
    top: '-6px',
    left: '50%',
    transform: 'translateX(-50%)',
    width: '10px',
    height: '8px',
    borderRadius: '2px 2px 0 0',
    background: 'linear-gradient(180deg, #2080e0 0%, #1060b0 100%)',
    border: '1px solid #083060',
    borderBottom: 'none',
  };

  return (
    <div
      id={idKey}
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        background: 'linear-gradient(180deg, #d8dce0 0%, #c8ccd0 50%, #d0d4d8 100%)',
        borderRadius: '6px',
        border: '1.5px solid #999',
        boxShadow: '2px 4px 10px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.6)',
        padding: '8px 6px',
        width: '82px',
        userSelect: 'none',
      }}
    >
      {/* Top screw terminals */}
      <div style={{ display: 'flex', gap: '10px', marginBottom: '6px' }}>
        <div style={screwStyle}><div style={screwSlotStyle} /></div>
        <div style={screwStyle}><div style={screwSlotStyle} /></div>
      </div>

      {/* Indicator row */}
      <div style={{ display: 'flex', gap: '18px', marginBottom: '4px' }}>
        <div style={indicatorStyle} />
        <div style={indicatorStyle} />
      </div>

      {/* Handle area */}
      <div
        style={{ display: 'flex', gap: '10px', alignItems: 'center', marginBottom: '4px', position: 'relative', height: '52px', cursor: 'pointer' }}
        onClick={onToggle}
      >
        <div style={{ ...poleStyle, justifyContent: 'center', height: '100%' }}>
          <div style={handleStyle}>
            <div style={nubStyle} />
          </div>
        </div>
        <div style={{ ...poleStyle, justifyContent: 'center', height: '100%' }}>
          <div style={handleStyle}>
            <div style={nubStyle} />
          </div>
        </div>
      </div>

      {/* Indicator row (bottom, mirrored) */}
      <div style={{ display: 'flex', gap: '18px', marginTop: '4px', marginBottom: '6px' }}>
        <div style={indicatorStyle} />
        <div style={indicatorStyle} />
      </div>

      {/* Bottom screw terminals */}
      <div style={{ display: 'flex', gap: '10px' }}>
        <div style={screwStyle}><div style={screwSlotStyle} /></div>
        <div style={screwStyle}><div style={screwSlotStyle} /></div>
      </div>
    </div>
  );
}

export function LcdScreen({ idKey = null }) {
  return (
    <div id={idKey} style={{ width: '648px', height: '456px', background: '#b8b9ba', border: '1px solid #888', borderRadius: '8px', padding: '12px', display: 'flex', flexDirection: 'column', boxShadow: '0 6px 12px rgba(0,0,0,0.4)', position: 'relative' }}>
      {/* black bevel */}
      <div style={{ flex: 1, background: '#111', borderRadius: '4px', border: '4px solid #222', boxShadow: 'inset 0 0 10px rgba(0,0,0,0.8)' }}></div>
      <div style={{ display: 'flex', justifyContent: 'center', gap: '20px', marginTop: '12px' }}>
        <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#666', boxShadow: 'inset 1px 1px 2px rgba(0,0,0,0.5)' }}></div>
        <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#666', boxShadow: 'inset 1px 1px 2px rgba(0,0,0,0.5)' }}></div>
        <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#666', boxShadow: 'inset 1px 1px 2px rgba(0,0,0,0.5)' }}></div>
        <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#666', boxShadow: 'inset 1px 1px 2px rgba(0,0,0,0.5)' }}></div>
      </div>
    </div>
  );
}

export function BlackPushButton({ labelTop, labelBottom, onClick, idKey = null }) {
  return (
    <div id={idKey} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', margin: '4px' }}>
      {labelTop && <div className="tape-label-real" style={{ marginBottom: '4px', ...getTapeStyle(labelTop) }}>{labelTop}</div>}
      <div className="real-black-square-btn" onClick={onClick}></div>
      {labelBottom && <div className="tape-label-real" style={{ marginTop: '4px', ...getTapeStyle(labelBottom) }}>{labelBottom}</div>}
    </div>
  );
}

export function RoundPushButton({ labelTop, labelBottom, onClick, idKey = null }) {
  return (
    <div id={idKey} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', margin: '4px' }}>
      {labelTop && <div className="tape-label-real" style={{ marginBottom: '4px', ...getTapeStyle(labelTop) }}>{labelTop}</div>}
      <div className="real-round-btn" onClick={onClick}></div>
      {labelBottom && <div className="tape-label-real" style={{ marginTop: '4px', ...getTapeStyle(labelBottom) }}>{labelBottom}</div>}
    </div>
  );
}

export function MastervoltDisplay({ label, value, idKey = null }) {
  return (
    <div id={idKey} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', margin: '10px' }}>
      <div style={{
        width: '90px', height: '90px', borderRadius: '50%', background: '#2c2e33',
        border: '3px solid #1a1a1a', boxShadow: '0 4px 8px rgba(0,0,0,0.5), inset 0 2px 4px rgba(255,255,255,0.1)',
        display: 'flex', flexDirection: 'column', alignItems: 'center', paddingTop: '10px'
      }}>
        <div style={{ color: '#aaa', fontSize: '8px', fontWeight: 'bold', letterSpacing: '1px' }}>MASTERVOLT</div>
        <div style={{
          width: '60px', height: '24px', background: '#9eb49e', border: '2px solid #111', borderRadius: '2px',
          marginTop: '6px', display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontFamily: 'monospace', fontSize: '14px', color: '#111', boxShadow: 'inset 1px 1px 3px rgba(0,0,0,0.5)'
        }}>
          {fmtVal(value)}
        </div>
        <div style={{ display: 'flex', gap: '8px', marginTop: '8px' }}>
          <div style={{ width: '12px', height: '12px', borderRadius: '50%', background: '#444', border: '1px solid #111' }}></div>
          <div style={{ width: '12px', height: '12px', borderRadius: '50%', background: '#444', border: '1px solid #111' }}></div>
          <div style={{ width: '12px', height: '12px', borderRadius: '50%', background: '#444', border: '1px solid #111' }}></div>
        </div>
      </div>
      <div className="tape-label-real" style={{ marginTop: '8px', ...getTapeStyle(label) }}>{label}</div>
    </div>
  );
}

export function YellowLedDisplay({ label, value, unit="ohm", idKey = null }) {
  return (
    <div id={idKey} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', margin: '10px' }}>
      <div style={{
        width: '60px', height: '80px', background: '#ffcc00', borderRadius: '4px',
        border: '1px solid #aa8800', boxShadow: '0 4px 6px rgba(0,0,0,0.4), inset 1px 1px 2px rgba(255,255,255,0.5)',
        display: 'flex', flexDirection: 'column', alignItems: 'center', padding: '6px'
      }}>
        <div style={{ display: 'flex', gap: '6px', marginBottom: '8px' }}>
          <div style={{ width: '6px', height: '6px', borderRadius: '50%', background: '#222' }}></div>
          <div style={{ width: '6px', height: '6px', borderRadius: '50%', background: '#222' }}></div>
          <div style={{ width: '6px', height: '6px', borderRadius: '50%', background: '#222' }}></div>
        </div>
        <div style={{
          width: '46px', height: '24px', background: '#2a2c26', border: '2px solid #111',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontFamily: 'monospace', fontSize: '12px', color: '#8b9977', boxShadow: 'inset 1px 1px 3px #000'
        }}>
          {fmtVal(value)}
        </div>
        <div style={{ display: 'flex', gap: '6px', marginTop: '10px' }}>
          <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#1e3a8a', boxShadow: 'inset -1px -1px 2px #000' }}></div>
          <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#1e3a8a', boxShadow: 'inset -1px -1px 2px #000' }}></div>
          <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#1e3a8a', boxShadow: 'inset -1px -1px 2px #000' }}></div>
        </div>
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: '4px', marginTop: '8px' }}>
        <div className="tape-label-real" style={getTapeStyle(label)}>{label}</div>
        {unit && <div className="tape-label-real" style={getTapeStyle(unit)}>{unit}</div>}
      </div>
    </div>
  );
}

export function DigitalVoltageDisplay({ label, value, unit="V", idKey = null }) {
  return (
    <div id={idKey} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', margin: '10px' }}>
      <div style={{
        background: '#111', border: '2px solid #333', padding: '4px 8px',
        borderRadius: '4px', boxShadow: 'inset 0 0 6px rgba(0,0,0,0.8)'
      }}>
        <span style={{ fontFamily: 'monospace', fontSize: '20px', color: '#ff2222', textShadow: '0 0 5px #ff0000' }}>{fmtVal(value)}</span>
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: '4px', marginTop: '8px' }}>
        <div className="tape-label-real" style={getTapeStyle(label)}>{label}</div>
        <div className="tape-label-real" style={getTapeStyle(unit)}>{unit}</div>
      </div>
    </div>
  );
}

export function AxisCamera({ idKey = null }) {
  return (
    <div id={idKey} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', margin: '10px' }}>
      <div style={{
        width: '100px', height: '220px', background: '#e6e6e6', borderRadius: '12px',
        boxShadow: '0 6px 12px rgba(0,0,0,0.4), inset -2px -2px 6px rgba(0,0,0,0.15), inset 2px 2px 6px #fff',
        display: 'flex', flexDirection: 'column', alignItems: 'center', padding: '10px', position: 'relative'
      }}>
        {/* Top small mic holes or LEDs */}
        <div style={{ display: 'flex', gap: '15px', marginTop: '4px' }}>
          <div style={{ width: '2px', height: '2px', background: '#999', borderRadius: '50%' }}></div>
          <div style={{ width: '2px', height: '2px', background: '#999', borderRadius: '50%' }}></div>
        </div>
        
        {/* Top pill sensor */}
        <div style={{ width: '6px', height: '12px', background: '#ddd', borderRadius: '3px', marginTop: '6px', boxShadow: 'inset 0 1px 3px rgba(0,0,0,0.3)' }}></div>

        {/* Lens */}
        <div style={{
          width: '64px', height: '64px', borderRadius: '50%', background: '#222',
          border: '2px solid #ccc', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
          boxShadow: 'inset 0 4px 10px rgba(0,0,0,0.9), 0 2px 4px rgba(0,0,0,0.2)', marginTop: '8px', position: 'relative'
        }}>
          <div style={{ width: '26px', height: '26px', borderRadius: '50%', background: '#0a0a0a', border: '1px solid #111', position: 'relative', boxShadow: '0 0 4px #000' }}>
             {/* Lens reflection */}
             <div style={{ position: 'absolute', top: '4px', right: '4px', width: '6px', height: '6px', borderRadius: '50%', background: 'rgba(255,255,255,0.2)', filter: 'blur(1px)' }}></div>
          </div>
          {/* IR or light sensor below lens */}
          <div style={{ width: '12px', height: '12px', borderRadius: '50%', background: '#444', position: 'absolute', bottom: '6px', boxShadow: 'inset 0 1px 3px #000' }}></div>
        </div>

        {/* Speaker Grill */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(12, 1fr)', gap: '2px', marginTop: 'auto', marginBottom: '16px', width: '70px', padding: '4px 0' }}>
           {Array.from({length: 84}).map((_, i) => (
             <div key={i} style={{ width: '3px', height: '3px', background: '#aaa', borderRadius: '50%', boxShadow: 'inset 0 1px 2px rgba(0,0,0,0.4)' }}></div>
           ))}
        </div>
        
        {/* Bottom subtle inset line */}
        <div style={{ width: '50px', height: '1px', background: '#ccc', marginBottom: '4px', boxShadow: '0 1px 0 #fff' }}></div>

        {/* AXIS logo */}
        <div style={{ fontSize: '10px', color: '#666', fontWeight: '900', letterSpacing: '1px', marginBottom: '4px' }}>AXIS</div>
      </div>
    </div>
  );
}
