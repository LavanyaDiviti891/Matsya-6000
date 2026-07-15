with open('/home/blank/Documents/github/personal/niot/frontend/src/components/Controls.jsx', 'r') as f:
    content = f.read()

svg_defs = """        <defs>
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
"""

replacement = f"""export function Toggle3Pos({{ labelTop, labelCenter, labelBottom, value, onToggle, idKey = null }}) {{
  const id = idKey || (labelTop ? labelTop.replace(/\\s/g,'_') : Math.random().toString(36).slice(2));
  return (
    <div className="toggle-3pos-container" id={{idKey}} style={{{{ display: 'flex', flexDirection: 'column', alignItems: 'center', cursor: 'pointer', margin: '6px 8px', userSelect: 'none' }}}} onClick={{onToggle}}>
      <div className="tape-label-real" style={{{{ marginBottom: '12px', ...getTapeStyle(labelTop) }}}}>{{labelTop}}</div>
      <div style={{{{ display: 'flex', alignItems: 'center' }}}}>
        <svg width="60" height="100" viewBox="0 0 60 100" style={{{{ overflow: 'visible', filter: 'drop-shadow(2px 6px 10px rgba(0,0,0,0.8))' }}}}>
{svg_defs}
        </svg>
        {{labelCenter && (
          <div className="tape-label-real" style={{{{ marginLeft: '12px', ...getTapeStyle(labelCenter) }}}}>{{labelCenter}}</div>
        )}}
      </div>
      <div className="tape-label-real" style={{{{ marginTop: '12px', ...getTapeStyle(labelBottom) }}}}>{{labelBottom}}</div>
    </div>
  );
}}"""

start_idx = content.find("export function Toggle3Pos")
end_idx = content.find("export function AlarmIndicator", start_idx)

if start_idx != -1 and end_idx != -1:
    new_content = content[:start_idx] + replacement + "\n\n" + content[end_idx:]
    with open('/home/blank/Documents/github/personal/niot/frontend/src/components/Controls.jsx', 'w') as f:
        f.write(new_content)
    print("Updated Toggle3Pos successfully.")
else:
    print("Could not find boundaries for Toggle3Pos.")
