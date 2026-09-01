import './AlarmBanner.css'

/**
 * Shows the active SOP scenario's current instruction plus any live alarms.
 * Renders nothing when no scenario is running and no alarms are present.
 *
 * Usage in App.jsx:
 *   import { AlarmBanner } from './components/AlarmBanner'
 *   ...
 *   <AlarmBanner appState={appState} apiCall={apiCall} />
 */
export function AlarmBanner({ appState, apiCall }) {
  if (!appState) return null

  const active_scenario = appState.active_scenario || ""
  const scenario_message = appState.scenario_message || ""
  const alarms = appState.alarms || []

  if (!active_scenario && alarms.length === 0) return null

  const hasCritical = alarms.some((a) => a.startsWith('🚨'))

  return (
    <div className={`alarm-banner ${hasCritical ? 'alarm-critical' : alarms.length ? 'alarm-warning' : ''}`}>
      {active_scenario && (
        <div className="alarm-scenario-row">
          <span className="alarm-scenario-tag">
            SCENARIO: {active_scenario.toUpperCase()} · STEP {appState.scenario_step}
          </span>
          <button
            className="alarm-stop-btn"
            onClick={() => apiCall('/api/scenario/stop')}
          >
            End Scenario
          </button>
        </div>
      )}
      {scenario_message && <div className="alarm-message">{scenario_message}</div>}
      {alarms.length > 0 && (
        <ul className="alarm-list">
          {alarms.map((a, i) => (
            <li key={i}>{a}</li>
          ))}
        </ul>
      )}
    </div>
  )
}

/**
 * Simple picker to kick off a scenario — drop anywhere (e.g. Status tab).
 */
export function ScenarioLauncher({ apiCall }) {
  return (
    <div className="scenario-launcher">
      <button onClick={() => apiCall('/api/scenario/start/medium')}>
        Start: Medium — IR Fault (MB_S)
      </button>
      <button onClick={() => apiCall('/api/scenario/start/high')}>
        Start: High — Bus Changeover Blackout (Port)
      </button>
    </div>
  )
}
