import React from 'react'

const ACTION_COLORS = {
  CORRECT: '#2e7d32',
  FLEXIBLE_ORDER: '#2e7d32',
  EARLY_ACTION: '#b8860b',
  OUT_OF_ORDER: '#b8860b',
  WARNING: '#b8860b',
  NO_GO: '#c62828',
}

export function ScenarioBanner({ appState, apiCall }) {
  const scenario = appState?.scenario
  const sample = appState?.sample_scenario
  const co2 = appState?.co2_scenario

  const startScenario = () => apiCall('/api/scenario/poweringup/start', new FormData())
  const stopScenario = () => apiCall('/api/scenario/poweringup/stop', new FormData())
  const startSample = () => apiCall('/api/scenario/sample/start', new FormData())
  const resetSample = () => apiCall('/api/scenario/sample/reset', new FormData())
  const startCo2 = () => apiCall('/api/scenario/co2/start', new FormData())
  const resetCo2 = () => apiCall('/api/scenario/co2/reset', new FormData())

  // Stage numbers must match co2_scenario.py exactly.
  const CO2_STAGE_LABELS = {
    1: 'Descending',
    2: 'Approaching seabed',
    3: 'Waiting on service weights',
    4: 'CO2 rising',
    5: 'CO2 alarm',
    6: 'CO2 recovery',
    7: 'Navigation instability',
    8: 'Navigation instability',
    9: 'Buoy release',
    10: 'Complete',
  }
  const co2StageLabel = co2 ? (CO2_STAGE_LABELS[co2.current_stage] || '') : ''
  const co2IsIdle = !co2?.active && co2?.success === null

  const isActive = scenario?.active
  const resultColor = ACTION_COLORS[scenario?.last_action_type] || '#555'

  const sampleIsIdle = !sample?.active && sample?.success === null
  let sampleBorder = '#facc15'
  let sampleStatusText = '⚠  SCENARIO IN PROGRESS'
  if (sample?.success === true) {
    sampleBorder = '#00ff88'
    sampleStatusText = '✓  MISSION COMPLETE'
  } else if (sample?.success === false) {
    sampleBorder = '#ff4444'
    sampleStatusText = '✗  MISSION FAILED'
  }

  const styles = {
    wrapper: {
      backgroundColor: '#1e2128',
      borderBottom: '2px solid #2a2d35',
      padding: '12px 20px',
      color: 'white',
      width: '100%',
    },
    section: { marginTop: '4px' },
    divider: { borderTop: '1px solid #2a2d35', margin: '12px 0' },
    topRow: {
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      gap: '15px',
    },
    title: { color: '#e8c14a', fontWeight: 'bold', fontSize: '15px' },
    btnStart: { background: '#1f6f43', color: 'white', padding: '8px 14px', cursor: 'pointer', border: 'none', borderRadius: '4px' },
    btnStop: { background: '#7a1f1f', color: 'white', padding: '8px 14px', cursor: 'pointer', border: 'none', borderRadius: '4px' },
    stepsRow: {
      display: 'flex',
      gap: '15px',
      marginTop: '10px',
    },
    stepBox: {
      flex: 1,
      background: '#2a2d35',
      borderLeft: '4px solid #4a90d9',
      padding: '8px 12px',
      borderRadius: '4px',
    },
    stepLabel: { fontSize: '11px', color: '#8fa8c9', textTransform: 'uppercase', marginBottom: '2px' },
    resultBox: {
      marginTop: '8px',
      background: '#2a2d35',
      borderLeft: `4px solid ${resultColor}`,
      padding: '8px 12px',
      borderRadius: '4px',
      fontSize: '14px',
    },
    alarmBox: {
      marginTop: '10px',
      background: '#3a1414',
      border: '2px solid #c62828',
      borderRadius: '4px',
      padding: '10px 14px',
      animation: 'sop-alarm-blink 1s infinite',
    },
    alarmLabel: {
      fontSize: '11px',
      color: '#ff8a80',
      textTransform: 'uppercase',
      fontWeight: 'bold',
      letterSpacing: '1px',
      marginBottom: '4px',
    },
    clearedBox: {
      marginTop: '10px',
      background: '#12251a',
      borderLeft: '4px solid #2e7d32',
      padding: '8px 12px',
      borderRadius: '4px',
      fontSize: '14px',
    },
    completeBox: {
      marginTop: '10px',
      background: '#12251a',
      border: '2px solid #2e7d32',
      borderRadius: '4px',
      padding: '10px 14px',
      fontWeight: 'bold',
    },
    sampleTitle: { color: '#e8c14a', fontWeight: 'bold', fontSize: '13px' },
    sampleOverlay: {
      marginTop: '8px',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      background: '#0d0d0dee',
      borderRadius: '8px',
      padding: '8px 20px',
      textAlign: 'center',
      backdropFilter: 'blur(6px)',
    },
    sampleStatus: { fontSize: '13px', fontWeight: 800, letterSpacing: '1.5px' },
    sampleMission: { color: '#888', fontSize: '11px', marginLeft: '8px' },
    metricLabel: { color: '#aaa', fontSize: '11px' },
    metricVal: { color: '#fff', fontWeight: 700, fontSize: '13px', marginRight: '16px' },
    resultMsg: { color: '#ccc', fontSize: '11px', marginTop: '4px' },
    hint: { fontSize: '11px', color: '#facc15', marginTop: '4px', fontWeight: 700 },
    timerBarOuter: { height: '4px', width: '100%', background: '#333', borderRadius: '2px', marginTop: '6px' },
  }

  return (
    <div style={styles.wrapper}>
      <style>{`
        @keyframes sop-alarm-blink {
          0%, 100% { box-shadow: 0 0 0 rgba(198,40,40,0); }
          50% { box-shadow: 0 0 12px rgba(198,40,40,0.9); }
        }
      `}</style>

      {/* ── SOP POWER-UP SCENARIO ─────────────────────────────────────── */}
      <div style={styles.topRow}>
        <div>
          <div style={styles.title}>{scenario?.mission_name}</div>
          <div style={{ fontSize: '12px', color: '#aaa' }}>
            Global Power: {scenario?.global_power_available ? 'AVAILABLE' : 'PENDING'}
            {'  '}|{'  '}Comm Ready: {scenario?.communication_system_ready ? 'YES' : 'NO'}
            {'  '}|{'  '}System: {scenario?.power_control_system_ready ? 'READY' : 'NOT READY'}
          </div>
        </div>
        {!isActive ? (
          <button style={styles.btnStart} onClick={startScenario}>Start SOP Monitor</button>
        ) : (
          <button style={styles.btnStop} onClick={stopScenario} title="Resets so you can start the other side">Stop / Reset</button>
        )}
      </div>

      {isActive && (
        <>
          <div style={styles.stepsRow}>
            {!scenario?.active_side ? (
              <div style={styles.stepBox}>
                <div style={styles.stepLabel}>Next Step</div>
                <div>Toggle any PORT or STARBOARD switch to begin. Whichever side you touch first becomes the active side.</div>
              </div>
            ) : (
              <div style={styles.stepBox}>
                <div style={styles.stepLabel}>
                  Active Side: {scenario.active_side === 'P' ? 'PORT' : 'STARBOARD'} — Next Step
                </div>
                <div>{scenario.active_side === 'P' ? scenario?.next_step_p : scenario?.next_step_s}</div>
              </div>
            )}
          </div>

          {scenario?.imaging_active && (
            <div style={styles.stepsRow}>
              <div style={{ ...styles.stepBox, borderLeftColor: scenario.imaging_complete ? '#2e7d32' : '#4a90d9' }}>
                <div style={styles.stepLabel}>Phase: Imaging (Steps 63-83)</div>
                <div>{scenario.next_step_imaging}</div>
              </div>
            </div>
          )}

          {scenario?.sensors_active && (
            <div style={styles.stepsRow}>
              <div style={{ ...styles.stepBox, borderLeftColor: scenario.sensors_complete ? '#2e7d32' : '#4a90d9' }}>
                <div style={styles.stepLabel}>Phase: Sensors (Steps 84-92)</div>
                <div>{scenario.next_step_sensors}</div>
              </div>
            </div>
          )}

          {scenario?.comms_active && (
            <div style={styles.stepsRow}>
              <div style={{ ...styles.stepBox, borderLeftColor: scenario.comms_complete ? '#2e7d32' : '#4a90d9' }}>
                <div style={styles.stepLabel}>Phase: Acoustic &amp; Voice Comms (Steps 93-95)</div>
                <div>{scenario.next_step_comms}</div>
              </div>
            </div>
          )}

          {scenario?.ballast_active && (
            <div style={styles.stepsRow}>
              <div style={{ ...styles.stepBox, borderLeftColor: scenario.ballast_complete ? '#2e7d32' : '#4a90d9' }}>
                <div style={styles.stepLabel}>Phase: Main Ballast (Steps 96-100)</div>
                <div>{scenario.next_step_ballast}</div>
              </div>
            </div>
          )}

          {scenario?.propulsion_active && (
            <div style={styles.stepsRow}>
              <div style={{ ...styles.stepBox, borderLeftColor: scenario.propulsion_complete ? '#2e7d32' : '#4a90d9' }}>
                <div style={styles.stepLabel}>Phase: Propulsion (Steps 101-108)</div>
                <div>{scenario.next_step_propulsion}</div>
              </div>
            </div>
          )}

          {(scenario?.next_step_final || scenario?.main_battery_complete) && (
            <div style={styles.stepsRow}>
              <div style={{ ...styles.stepBox, borderLeftColor: scenario.main_battery_complete ? '#2e7d32' : '#4a90d9' }}>
                <div style={styles.stepLabel}>Phase: Final (Steps 57-60)</div>
                <div>{scenario.next_step_final}</div>
              </div>
            </div>
          )}

          {scenario?.alarm_active && (
            <div style={styles.alarmBox}>
              <div style={styles.alarmLabel}>⚠ ALARM — {scenario.fault_type === 'IR_FAULT_MB_S3' ? 'Insulation Fault' : scenario.fault_type === 'BLACKOUT_UB_P' ? 'Bus Changeover Blackout' : 'Fault'}</div>
              <div>{scenario.alarm_message}</div>
            </div>
          )}

          {!scenario?.alarm_active && scenario?.clear_message && (
            <div style={styles.clearedBox}>
              <strong>Scenario Cleared: </strong>{scenario.clear_message}
            </div>
          )}

          {scenario?.main_battery_complete && !scenario?.alarm_active && (
            <div style={styles.completeBox}>
              ✅ MAIN BATTERY POWER-UP COMPLETE (SOP Steps 1-60) — training scenario ends here.
            </div>
          )}

          {scenario?.feedback_msg && (
            <div style={styles.resultBox}>
              {scenario.feedback_msg}
            </div>
          )}

          {scenario?.last_result && (
            <div style={styles.resultBox}>
              <strong>Last action: </strong>{scenario.last_result}
            </div>
          )}
        </>
      )}

      {/* ── SAMPLE COLLECTION MISSION ─────────────────────────────────── */}
      <div style={styles.divider} />
      <div style={styles.topRow}>
        <div style={styles.sampleTitle}>SAMPLE COLLECTION MISSION</div>
        {sampleIsIdle ? (
          <button style={styles.btnStart} onClick={startSample}>Start Sample Collection</button>
        ) : (
          <button style={styles.btnStop} onClick={resetSample}>Reset</button>
        )}
      </div>

      {!sampleIsIdle && sample && (
        <div style={{ ...styles.sampleOverlay, border: `1.5px solid ${sampleBorder}`, boxShadow: `0 0 18px ${sampleBorder}44` }}>
          <div>
            <span style={{ ...styles.sampleStatus, color: sampleBorder }}>{sampleStatusText}</span>
            <span style={styles.sampleMission}>{sample.mission_name}</span>
          </div>

          {sample.success === null ? (
            <div style={styles.section}>
              <span style={styles.metricLabel}>DEPTH </span>
              <span style={styles.metricVal}>{appState.header.depth.value.toFixed(1)} m</span>
            </div>
          ) : (
            <div style={styles.resultMsg}>{sample.result_message}</div>
          )}

          {sample.feedback_msg && <div style={styles.hint}>{sample.feedback_msg}</div>}
        </div>
      )}

      {/* ── CO2 SCRUBBER FAILURE -> NAV INSTABILITY -> BUOY MISSION ────── */}
      {/* One combined mission (co2_scenario.py): CO2 alarm runs first,
          then navigation instability, then buoy release. Both alarm
          points are audio-only (see useScenarioBeep) -- intentionally
          NO flashing alarmBox here, just the plain-text feedback_msg
          that already carries the instruction. */}
      <div style={styles.divider} />
      <div style={styles.topRow}>
        <div>
          <div style={styles.sampleTitle}>CO2 SCRUBBER FAILURE → EMERGENCY BUOY DEPLOYMENT</div>
          {co2?.active && (
            <div style={{ fontSize: '12px', color: '#aaa' }}>
              Stage {co2.current_stage} / 10{co2StageLabel ? ` — ${co2StageLabel}` : ''}
            </div>
          )}
        </div>
        {co2IsIdle ? (
          <button style={styles.btnStart} onClick={startCo2}>Start Mission</button>
        ) : (
          <button style={styles.btnStop} onClick={resetCo2}>Stop / Reset</button>
        )}
      </div>

      {co2?.active && (
        <div style={styles.resultBox}>{co2.feedback_msg}</div>
      )}

      {!co2?.active && co2?.result_message && (
        <div
          style={
            co2.success
              ? styles.completeBox
              : { ...styles.completeBox, border: '2px solid #c62828', background: '#3a1414' }
          }
        >
          {co2.success ? '✅ ' : '❌ '}{co2.result_message}
        </div>
      )}
    </div>
  )
}
