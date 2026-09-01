import { useEffect, useRef } from "react";

/**
 * useScenarioBeep — audible-only reaction to appState.co2_scenario.beep_level.
 * Covers BOTH alarm points in the combined CO2 -> navigation-instability ->
 * emergency-buoy mission:
 *   "critical" -> a single short beep repeated at a fixed interval, until
 *                 it clears (NOT a continuous tone -- a continuous square
 *                 wave played at the same time as the old alarm siren made
 *                 the two sounds run together / "merge"; repeating a
 *                 single beep is distinct and easy to tell apart)
 *   ""          -> silent
 * There is intentionally NO visual pop-up/banner/flashing element here --
 * `co2_scenario.feedback_msg` still carries the plain-text instruction for
 * whatever already displays it; this hook only ever makes sound.
 *
 * Usage in App.jsx:
 *   import { useScenarioBeep } from './hooks/useScenarioBeep'
 *   ...
 *   useScenarioBeep(appState)   // call unconditionally, alongside the other hooks
 */
const BEEP_INTERVAL_MS = 1000; // gap between repeated beeps while critical

export function useScenarioBeep(appState) {
  const audioCtxRef = useRef(null);
  const intervalRef = useRef(null);
  const prevLevelRef = useRef("");

  const getCtx = () => {
    if (!audioCtxRef.current) {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      audioCtxRef.current = new AudioCtx();
    }
    return audioCtxRef.current;
  };

  const playSingleBeep = (freq = 880, durationMs = 220) => {
    const ctx = getCtx();
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.type = "sine";
    osc.frequency.value = freq;
    gain.gain.value = 0.1;
    osc.connect(gain);
    gain.connect(ctx.destination);
    osc.start();
    osc.stop(ctx.currentTime + durationMs / 1000);
  };

  const stopRepeating = () => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  };

  const startRepeating = (freq = 880) => {
    stopRepeating();
    playSingleBeep(freq); // beep immediately, then keep repeating
    intervalRef.current = setInterval(() => playSingleBeep(freq), BEEP_INTERVAL_MS);
  };

  useEffect(() => {
    const level = appState?.co2_scenario?.beep_level || "";
    const prevLevel = prevLevelRef.current;

    if (level === "critical") {
      if (prevLevel !== "critical") {
        startRepeating(880);
      }
    } else {
      stopRepeating();
      if (level === "warning" && prevLevel !== "warning") {
        playSingleBeep(660, 220);
      }
    }

    prevLevelRef.current = level;
  }, [appState?.co2_scenario?.beep_level]);

  useEffect(() => {
    return () => {
      stopRepeating();
      if (audioCtxRef.current) {
        audioCtxRef.current.close();
      }
    };
  }, []);
}
