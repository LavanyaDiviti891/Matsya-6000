const fs = require('fs');

const file = 'frontend/src/components/SwitchesLayout.jsx';
let content = fs.readFileSync(file, 'utf8');

const regex = /\/\/ --- Pilot PC \(SW-3\) Layout ---[\s\S]*?(?=\/\/ ---|$)/;
const replacement = `// --- Pilot PC (SW-3) Layout ---
export function Switches3Layout({ appState, apiCall }) {
  const sw = appState.switches?.sw3 || {};

  const LabelledToggle = ({ labelTopPink, labelTop, labelBottom, valueKeyP, valueKeyS }) => {
    const valP = sw[valueKeyP];
    const valS = sw[valueKeyS];
    const value = valP ? 1 : valS ? -1 : 0;
    const onToggle = () => {
       if (!valP && !valS) apiCall('/api/toggle/switches.sw3.' + valueKeyP);
       else if (valP && !valS) { apiCall('/api/toggle/switches.sw3.' + valueKeyP); apiCall('/api/toggle/switches.sw3.' + valueKeyS); }
       else apiCall('/api/toggle/switches.sw3.' + valueKeyS);
    };
    return (
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        <div style={{ color: '#ff00ff', fontSize: '10px', fontWeight: 'bold', marginBottom: '4px' }}>{labelTopPink}</div>
        <Toggle3Pos showLed={true} labelTop={labelTop} labelBottom={labelBottom} value={value} onToggle={onToggle} />
      </div>
    );
  };

  return (
    <div style={{ padding: '20px', flex: 1, minHeight: 0, overflowY: 'auto', display: 'flex', flexDirection: 'column', alignItems: 'center', background: '#c0c0c0' }}>
      
      <div style={{ fontSize: '28px', fontWeight: 'bold', color: '#ff1493', marginBottom: '20px', letterSpacing: '1px' }}>EMERGENCY JETTISONING SWITCHES</div>

      <div style={{ display: 'flex', width: '100%', justifyContent: 'space-around', alignItems: 'flex-start' }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '30px' }}>
          
          <div>
             <div style={{ color: '#008000', fontSize: '12px', fontWeight: 'bold', textAlign: 'center', marginBottom: '10px' }}>TRIM-EMG JET-PORT & STBD</div>
             <div style={{ display: 'flex', gap: '20px', justifyContent: 'center' }}>
               <LabelledToggle labelTopPink="T-EJ_PC" labelTop="PWR_P" labelBottom="PWR_S" valueKeyP="t_ej_pc_p" valueKeyS="t_ej_pc_s" />
               <LabelledToggle labelTopPink="T-EJ_PC_2" labelTop="PWR_P" labelBottom="PWR_S" valueKeyP="t_ej_pc2_p" valueKeyS="t_ej_pc2_s" />
               <LabelledToggle labelTopPink="T-EJ_SC" labelTop="PWR_S" labelBottom="PWR_P" valueKeyP="t_ej_sc_s" valueKeyS="t_ej_sc_p" />
               <LabelledToggle labelTopPink="T-EJ_SC_2" labelTop="PWR_S" labelBottom="PWR_P" valueKeyP="t_ej_sc2_s" valueKeyS="t_ej_sc2_p" />
             </div>
          </div>

          <div style={{ display: 'flex', gap: '40px' }}>
            <div>
               <div style={{ color: '#008000', fontSize: '12px', fontWeight: 'bold', textAlign: 'center', marginBottom: '10px' }}>MANIPULATOR_PORT</div>
               <div style={{ display: 'flex', gap: '20px', justifyContent: 'center' }}>
                 <LabelledToggle labelTopPink="EJM_P_PC" labelTop="PWR_P" labelBottom="PWR_S" valueKeyP="ejm_p_pc_p" valueKeyS="ejm_p_pc_s" />
                 <LabelledToggle labelTopPink="EJM_P_SC" labelTop="PWR_S" labelBottom="PWR_P" valueKeyP="ejm_p_sc_s" valueKeyS="ejm_p_sc_p" />
               </div>
            </div>
            <div>
               <div style={{ color: '#008000', fontSize: '12px', fontWeight: 'bold', textAlign: 'center', marginBottom: '10px' }}>MANIPULATOR_STBD</div>
               <div style={{ display: 'flex', gap: '20px', justifyContent: 'center' }}>
                 <LabelledToggle labelTopPink="EJM_S_PC" labelTop="PWR_P" labelBottom="PWR_S" valueKeyP="ejm_s_pc_p" valueKeyS="ejm_s_pc_s" />
                 <LabelledToggle labelTopPink="EJM_S_SC" labelTop="PWR_S" labelBottom="PWR_P" valueKeyP="ejm_s_sc_s" valueKeyS="ejm_s_sc_p" />
               </div>
            </div>
          </div>

          <div>
             <div style={{ color: '#008000', fontSize: '12px', fontWeight: 'bold', textAlign: 'center', marginBottom: '10px' }}>EMERGENCY DROP WEIGHT_P</div>
             <div style={{ display: 'flex', gap: '20px', justifyContent: 'center' }}>
               <LabelledToggle labelTopPink="EDW_P_PC" labelTop="PWR_P" labelBottom="PWR_S" valueKeyP="edw_p_pc_p" valueKeyS="edw_p_pc_s" />
               <LabelledToggle labelTopPink="EDW_P_SC" labelTop="PWR_S" labelBottom="PWR_P" valueKeyP="edw_p_sc_s" valueKeyS="edw_p_sc_p" />
             </div>
          </div>

        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '30px' }}>
          
          <div>
             <div style={{ color: '#008000', fontSize: '12px', fontWeight: 'bold', textAlign: 'center', marginBottom: '10px' }}>MARKER BUOY</div>
             <div style={{ display: 'flex', gap: '20px', justifyContent: 'center' }}>
               <LabelledToggle labelTopPink="MB-EJ_PC" labelTop="PWR_P" labelBottom="PWR_S" valueKeyP="mb_ej_pc_p" valueKeyS="mb_ej_pc_s" />
               <LabelledToggle labelTopPink="MB-EJ_SC" labelTop="PWR_S" labelBottom="PWR_P" valueKeyP="mb_ej_sc_s" valueKeyS="mb_ej_sc_p" />
             </div>
          </div>

          <div>
             <div style={{ color: '#008000', fontSize: '12px', fontWeight: 'bold', textAlign: 'center', marginBottom: '10px' }}>SAMPLE BASKET</div>
             <div style={{ display: 'flex', gap: '20px', justifyContent: 'center' }}>
               <LabelledToggle labelTopPink="EJS_PC" labelTop="PWR_P" labelBottom="PWR_S" valueKeyP="ejs_pc_p" valueKeyS="ejs_pc_s" />
               <LabelledToggle labelTopPink="EJS_SC" labelTop="PWR_S" labelBottom="PWR_P" valueKeyP="ejs_sc_s" valueKeyS="ejs_sc_p" />
             </div>
          </div>

          <div>
             <div style={{ color: '#008000', fontSize: '12px', fontWeight: 'bold', textAlign: 'center', marginBottom: '10px' }}>EMERGENCY DROP WEIGHT_S</div>
             <div style={{ display: 'flex', gap: '20px', justifyContent: 'center' }}>
               <LabelledToggle labelTopPink="EDW_S_PC" labelTop="PWR_S" labelBottom="PWR_P" valueKeyP="edw_s_pc_s" valueKeyS="edw_s_pc_p" />
               <LabelledToggle labelTopPink="EDW_S_SC" labelTop="PWR_P" labelBottom="PWR_S" valueKeyP="edw_s_sc_p" valueKeyS="edw_s_sc_s" />
             </div>
          </div>

        </div>
      </div>

      <div style={{ display: 'flex', width: '100%', justifyContent: 'center', marginTop: '30px', gap: '20px' }}>
        
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
           <div style={{ color: '#0000ff', fontSize: '12px', fontWeight: 'bold', marginBottom: '10px' }}>WATER INGRESS</div>
           <div style={{ display: 'flex', gap: '20px' }}>
             <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', alignItems: 'flex-end', paddingTop: '16px' }}>
                {['PS', 'IDE', 'PDE', 'PJB', 'TJB', 'BAT'].map(lbl => (
                  <div key={lbl} style={{ color: '#ff0000', fontSize: '12px', fontWeight: 'bold', height: '24px', lineHeight: '24px' }}>{lbl}</div>
                ))}
             </div>
             <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', alignItems: 'center' }}>
                <div style={{ color: '#ff00ff', fontSize: '12px', fontWeight: 'bold' }}>PORT</div>
                {['wl_p_ps', 'wl_p_ide', 'wl_p_pde', 'wl_p_pjb', 'wl_p_tjb', 'wl_p_bat'].map(k => (
                  <div key={k} className={`real-black-square-btn ${sw[k] ? 'is-on' : ''}`} style={{ width: '24px', height: '24px', background: sw[k] ? '#ff0000' : '#111' }} onClick={() => apiCall('/api/toggle/switches.sw3.' + k)}></div>
                ))}
             </div>
             <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', alignItems: 'center' }}>
                <div style={{ color: '#ff00ff', fontSize: '12px', fontWeight: 'bold' }}>STBD</div>
                {['wl_s_ps', 'wl_s_ide', 'wl_s_pde', 'wl_s_pjb', 'wl_s_tjb', 'wl_s_bat'].map(k => (
                  <div key={k} className={`real-black-square-btn ${sw[k] ? 'is-on' : ''}`} style={{ width: '24px', height: '24px', background: sw[k] ? '#ff0000' : '#111' }} onClick={() => apiCall('/api/toggle/switches.sw3.' + k)}></div>
                ))}
             </div>
           </div>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
           <div style={{ color: '#ff00ff', fontSize: '14px', fontWeight: 'bold', textAlign: 'center' }}>BUZZER_1</div>
           <Buzzer isOn={sw.buzzer_1} />
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
           <div style={{ width: '200px', height: '240px', background: '#fff', borderRadius: '40px', border: '1px solid #ccc', display: 'flex', flexDirection: 'column', alignItems: 'center', position: 'relative', overflow: 'hidden' }}>
             <div style={{ width: '120px', height: '120px', borderRadius: '50%', background: '#000', marginTop: '20px' }}>
                <div style={{ width: '2px', height: '2px', background: '#fff', position: 'absolute', top: '70px', left: '130px' }}></div>
             </div>
             <div style={{ fontSize: '10px', color: '#000', marginTop: '20px' }}>Internal IP Camera_Port_6</div>
             <div style={{ width: '100%', height: '60px', marginTop: 'auto', background: '#e0f0ff', display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center' }}>
                <div style={{ fontSize: '6px', textAlign: 'center', fontWeight: 'bold' }}>Gigabit Ethernet<br/>Switch_Stbd (ES 3)</div>
             </div>
             <div style={{ fontSize: '10px', color: '#ff8800', fontWeight: 'bold', position: 'absolute', bottom: '5px' }}>INTERNAL CAMERA</div>
           </div>

           <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '15px', marginTop: '20px' }}>
              {[
                { l: 'MB', k: 'al_mb' }, { l: 'AB', k: 'al_ab' }, { l: 'HYD OIL', k: 'al_hyd' }, { l: 'DEPTH', k: 'al_depth' },
                { l: 'ALTITUDE', k: 'al_alt' }, { l: 'SPARE-2', k: 'al_sp2' }, { l: 'SPARE-3', k: 'al_sp3' }, { l: 'SPARE-4', k: 'al_sp4' },
                { l: 'SPARE-5', k: 'al_sp5' }, { l: 'SPARE-6', k: 'al_sp6' }, { l: 'SPARE-7', k: 'al_sp7' }, { l: 'SPARE-8', k: 'al_sp8' }
              ].map(item => (
                 <div key={item.l} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                   <div className="real-black-square-btn" style={{ width: '30px', height: '30px', background: sw[item.k] ? '#ff0000' : '#111' }} onClick={() => apiCall('/api/toggle/switches.sw3.' + item.k)}></div>
                   <div style={{ color: '#ff0000', fontSize: '10px', fontWeight: 'bold', marginTop: '4px' }}>{item.l}</div>
                 </div>
              ))}
           </div>
           <div style={{ color: '#ff00ff', fontSize: '14px', fontWeight: 'bold', marginTop: '10px' }}>ALARM PANEL</div>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
           <div style={{ color: '#ff00ff', fontSize: '14px', fontWeight: 'bold', textAlign: 'center' }}>BUZZER_2</div>
           <Buzzer isOn={sw.buzzer_2} />
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
           <div style={{ color: '#0000ff', fontSize: '12px', fontWeight: 'bold', marginBottom: '10px' }}>LOW INSULATION</div>
           <div style={{ display: 'flex', gap: '20px' }}>
             <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', alignItems: 'center' }}>
                <div style={{ color: '#ff00ff', fontSize: '12px', fontWeight: 'bold' }}>PORT</div>
                {['ins_p_ps_ub', 'ins_p_ide', 'ins_p_pde', 'ins_p_148v', 'ins_p_ps_eb', 'ins_p_spare_1'].map(k => (
                  <div key={k} className={`real-black-square-btn ${sw[k] ? 'is-on' : ''}`} style={{ width: '24px', height: '24px', background: sw[k] ? '#ffcc00' : '#111' }} onClick={() => apiCall('/api/toggle/switches.sw3.' + k)}></div>
                ))}
             </div>
             <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', alignItems: 'center' }}>
                <div style={{ color: '#ff00ff', fontSize: '12px', fontWeight: 'bold' }}>STBD</div>
                {['ins_s_ps_ub', 'ins_s_ide', 'ins_s_pde', 'ins_s_148v', 'ins_s_ps_eb', 'ins_s_spare_1'].map(k => (
                  <div key={k} className={`real-black-square-btn ${sw[k] ? 'is-on' : ''}`} style={{ width: '24px', height: '24px', background: sw[k] ? '#ffcc00' : '#111' }} onClick={() => apiCall('/api/toggle/switches.sw3.' + k)}></div>
                ))}
             </div>
             <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', alignItems: 'flex-start', paddingTop: '16px' }}>
                {['PS_UB', 'IDE', 'PDE', '148V', 'PS_EB', 'SPARE-1'].map(lbl => (
                  <div key={lbl} style={{ color: '#ff0000', fontSize: '12px', fontWeight: 'bold', height: '24px', lineHeight: '24px' }}>{lbl}</div>
                ))}
             </div>
           </div>
        </div>

      </div>

      <div style={{ width: '100%', height: '2px', background: '#666', margin: '20px 0' }}></div>

      <div style={{ display: 'flex', flexDirection: 'column', width: '100%', alignItems: 'center', background: '#d0d0d0', padding: '20px' }}>
         <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#ff1493', marginBottom: '20px' }}>Control Panel</div>
         
         <div style={{ display: 'flex', gap: '40px', alignItems: 'flex-end', marginBottom: '30px' }}>
            <div style={{ display: 'flex', gap: '20px' }}>
               {[ {l:'SUBMERSIBLE CTRL', k:'sub_ctrl'}, {l:'WATER OUT', k:'water_out'}, {l:'TRIM', k:'trim'} ].map(item => (
                 <div key={item.l} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                   <div className="real-black-square-btn" style={{ width: '40px', height: '40px', marginBottom: '10px', background: sw[item.k] ? '#444' : '#111' }} onClick={() => apiCall('/api/toggle/switches.sw3.' + item.k)}></div>
                   <div style={{ color: '#ff0000', fontSize: '12px', fontWeight: 'bold' }}>{item.l}</div>
                 </div>
               ))}
            </div>
            
            <div style={{ display: 'flex', gap: '30px' }}>
               {[
                 { t: 'FREEBOARD_P', b: 'FREEBOARD_S', kp: 'freeboard_p', ks: 'freeboard_s' },
                 { t: 'DIVE-IN-ON', b: 'DIVE-IN-OFF', kp: 'dive_in_on', ks: 'dive_in_off' },
                 { t: 'HP-AP-ON', b: 'HP AP-OFF', kp: 'hp_ap_on', ks: 'hp_ap_off' },
                 { t: 'HP- BP-ON', b: 'HP-BP OFF', kp: 'hp_bp_on', ks: 'hp_bp_off' },
               ].map(item => {
                 const valP = sw[item.kp];
                 const valS = sw[item.ks];
                 const value = valP ? 1 : valS ? -1 : 0;
                 return (
                   <div key={item.t} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                     <div style={{ color: '#ff0000', fontSize: '12px', fontWeight: 'bold', marginBottom: '5px' }}>{item.t}</div>
                     <Toggle3Pos value={value} onToggle={() => {
                        if (!valP && !valS) apiCall('/api/toggle/switches.sw3.' + item.kp);
                        else if (valP && !valS) { apiCall('/api/toggle/switches.sw3.' + item.kp); apiCall('/api/toggle/switches.sw3.' + item.ks); }
                        else apiCall('/api/toggle/switches.sw3.' + item.ks);
                     }} />
                     <div style={{ color: '#ff0000', fontSize: '12px', fontWeight: 'bold', marginTop: '5px' }}>{item.b}</div>
                   </div>
                 );
               })}
            </div>
         </div>

         <div style={{ display: 'flex', gap: '40px' }}>
            {[
              {l:'FWD CTRL', k:'fwd_ctrl'}, {l:'HEADING_CTRL', k:'heading_ctrl'}, {l:'DEPTH_CTRL', k:'depth_ctrl'},
              {l:'LATERAL TRIM', k:'lat_trim'}, {l:'HP REG', k:'hp_reg'}, {l:'VBT CTRL', k:'vbt_ctrl'}, {l:'PITCH CTRL', k:'pitch_ctrl'}
            ].map(item => (
               <div key={item.l} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                 <div style={{ width: '30px', height: '30px', borderRadius: '50%', background: 'linear-gradient(135deg, #333, #000)', position: 'relative', marginBottom: '10px', boxShadow: '0 4px 6px rgba(0,0,0,0.5)', cursor: 'pointer', transform: sw[item.k] ? 'rotate(45deg)' : 'rotate(-45deg)', transition: 'transform 0.2s' }} onClick={() => apiCall('/api/toggle/switches.sw3.' + item.k)}>
                    <div style={{ width: '6px', height: '6px', borderRadius: '50%', background: '#ffcc00', position: 'absolute', top: '4px', left: '12px' }}></div>
                 </div>
                 <div style={{ color: '#ff0000', fontSize: '12px', fontWeight: 'bold' }}>{item.l}</div>
               </div>
            ))}
         </div>
      </div>
    </div>
  );
}
`;

content = content.replace(regex, replacement);
fs.writeFileSync(file, content);
console.log('updated');
