import React from 'react'

export function ScenarioBanner({ appState }) {
  const scenario = appState?.scenario

  const startScenario = () => {
    fetch('http://localhost:8000/api/scenario/poweringup/start', { method: 'POST' })
      .catch(e => console.error("Start failed", e))
  }

  // NOTE: No longer auto-starts on mount. The banner now lives on the
  // Main-2 tab only, so it mounts/unmounts every time the user switches
  // tabs — an auto-start effect here would silently kick off (or restart)
  // the SOP scenario on every visit. Starting is manual via the button,
  // and the banner keeps showing live state regardless of which tab the
  // user is on since the scenario itself runs on the backend.

  const stopScenario = () => {
    fetch('http://localhost:8000/api/scenario/poweringup/stop', { method: 'POST' })
      .catch(e => console.error("Stop failed", e))
  }

  // ... rest of your formatting and return statement remains the same

  const formatTime = (secs) => {
    if (secs === undefined || secs === null) return '00:00'
    const m = Math.floor(secs / 60).toString().padStart(2, '0')
    const s = Math.floor(secs % 60).toString().padStart(2, '0')
    return `${m}:${s}`
  }

  const isActive = scenario?.active
  const isSuccess = scenario?.success === true
  const isFailure = scenario?.success === false

  // INLINE STYLES SO IT CANNOT POSSIBLY HIDE
  const styles = {
    wrapper: {
      backgroundColor: '#1e2128',
      borderBottom: '2px solid #2a2d35',
      padding: '15px 20px',
      color: 'white',
      minHeight: '60px', // Forces it to take up space
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      width: '100%'
    },
    btnStart: { background: '#1f6f43', color: 'white', padding: '10px', margin: '5px', cursor: 'pointer' },
    btnStop: { background: '#7a1f1f', color: 'white', padding: '10px', margin: '5px', cursor: 'pointer' }
  }

  return (
    <div style={styles.wrapper}>
      {!isActive ? (
        <div>
          <span>
            {isSuccess ? scenario?.result_message || 'Scenario complete.' 
             : isFailure ? scenario?.result_message || 'Scenario failed.' 
             : 'No scenario running.'}
          </span>
          <button style={styles.btnStart} onClick={startScenario}>Start SOP</button>
        </div>
      ) : (
        <div style={{ display: 'flex', gap: '20px', alignItems: 'center' }}>
          <div>
            <div style={{ color: '#e8c14a', fontWeight: 'bold' }}>{scenario?.mission_name}</div>
            <div style={{ color: scenario?.timer_remaining <= 60 ? '#f44336' : '#fff' }}>
              Time: {formatTime(scenario?.timer_remaining)}
            </div>
          </div>
          <div style={{ background: '#2a2d35', padding: '10px', borderRadius: '5px', flexGrow: 1 }}>
            {scenario?.feedback_msg}
          </div>
          <button style={styles.btnStop} onClick={stopScenario}>ABORT</button>
        </div>
      )}
    </div>
  )
}

