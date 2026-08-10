import React from 'react'
import { API_BASE_URL } from '../apiConfig'

const ACTION_COLORS = {
  CORRECT: '#2e7d32',
  FLEXIBLE_ORDER: '#2e7d32',
  EARLY_ACTION: '#b8860b',
  OUT_OF_ORDER: '#b8860b',
  WARNING: '#b8860b',
  NO_GO: '#c62828',
}

export function ScenarioBanner({ appState }) {
  const scenario = appState?.scenario

  const startScenario = () => {
    fetch(`${API_BASE_URL}/api/scenario/poweringup/start`, { method: 'POST' })
      .catch(e => console.error('Start failed', e))
  }

  const stopScenario = () => {
    fetch(`${API_BASE_URL}/api/scenario/poweringup/stop`, { method: 'POST' })
      .catch(e => console.error('Stop failed', e))
  }

  const isActive = scenario?.active
  const resultColor = ACTION_COLORS[scenario?.last_action_type] || '#555'

  const styles = {
    wrapper: {
      backgroundColor: '#1e2128',
      borderBottom: '2px solid #2a2d35',
      padding: '12px 20px',
      color: 'white',
      width: '100%',
    },
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
  }

  return (
    <div style={styles.wrapper}>
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
    </div>
  )
}
