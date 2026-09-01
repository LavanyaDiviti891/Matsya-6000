import { useEffect, useRef } from 'react'
import { speak, playCompletionChime } from './useSopEffects'

// Stage numbers must match co2_scenario.py exactly.
const STAGE_DESCENDING = 1
const STAGE_APPROACHING = 2
const STAGE_WAIT_WEIGHTS = 3
const STAGE_CO2_RISING = 4
const STAGE_CO2_ALARM = 5
const STAGE_CO2_RECOVERY = 6
const STAGE_NAV_INSTABILITY = 7
const STAGE_NAV_CONFIRM = 8
const STAGE_BUOY_RELEASE = 9
const STAGE_COMPLETE = 10

// Stages that must stay BEEP-ONLY -- no siren, no spoken line. The
// continuous beep for these is driven separately by
// appState.co2_scenario.beep_level via hooks/useScenarioBeep.js. Speaking
// or sirening here would defeat the "beep only, no alarm" requirement for
// navigation instability.
const SILENT_STAGES = new Set([STAGE_NAV_INSTABILITY, STAGE_NAV_CONFIRM])

/**
 * useCo2ScenarioEffects(appState)
 *   Voice-over for the combined co2_scenario.py mission:
 *     - active False->True: announce mission start
 *     - current_stage change: announce that stage's feedback_msg, EXCEPT
 *       for the navigation-instability stages (7/8), which stay silent
 *       here -- those are beep-only per useScenarioBeep.js.
 *     - entering STAGE_CO2_ALARM specifically: siren + speak (this is the
 *       existing CO2 alarm behavior, unchanged -- only the navigation-
 *       instability alarm was asked to become beep-only, not this one)
 *     - active True->False: chime + announce the final result_message
 */
export function useCo2ScenarioEffects(appState, { voiceEnabled = true } = {}) {
  const prevActiveRef = useRef(false)
  const prevStageRef = useRef(0)

  useEffect(() => {
    if (!appState || !voiceEnabled) return
    const sc = appState.co2_scenario
    if (!sc) return

    const activeNow = !!sc.active
    const wasActive = prevActiveRef.current
    const stageNow = sc.current_stage || 0
    const wasStage = prevStageRef.current

    if (activeNow && !wasActive) {
      // Fresh mission start. If the hook mounts (or a websocket
      // reconnect happens) mid-mission, don't retroactively announce
      // "mission started" -- just sync refs and let the next real change
      // speak normally.
      if (stageNow <= 1) {
        speak(`${sc.mission_name || 'CO2 Scrubber Failure'}. Mission started.`)
      }
    } else if (!activeNow && wasActive) {
      if (sc.result_message) {
        playCompletionChime(sc.success !== false)
        speak(sc.result_message)
      }
    } else if (activeNow && wasActive && stageNow !== wasStage) {
      if (SILENT_STAGES.has(stageNow)) {
        // Beep-only stage -- intentionally no siren/speech here.
      } else if (stageNow === STAGE_CO2_ALARM) {
        // CO2 alarm: spoken instruction only. The siren used to play here
        // AT THE SAME TIME as useScenarioBeep's continuous tone for
        // beep_level="critical" -- the two sounds overlapping is what
        // sounded like they were "merging". Beep-only per requirement, so
        // the siren is gone; the audible alarm cue is the beep alone.
        if (sc.feedback_msg) speak(sc.feedback_msg)
      } else if (sc.feedback_msg) {
        speak(sc.feedback_msg)
      }
    }

    prevActiveRef.current = activeNow
    prevStageRef.current = stageNow
  }, [
    appState?.co2_scenario?.active,
    appState?.co2_scenario?.current_stage,
    voiceEnabled,
  ])
}
