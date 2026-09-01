import { useEffect, useRef } from "react";

/**
 * useAlarmBeep — audible-only reaction to the DNV alarm-document thresholds
 * computed backend-side in alarm_engine.py (`appState.beep_level`).
 *
 * Per the alarm document's classification table:
 *   Critical          -> continuous beep, until the level clears
 *   Warning/Advisory   -> a single beep each time a new warning appears
 * There is intentionally NO visual pop-up/banner/modal here — only sound.
 *
 * Usage in App.jsx:
 *   import { useAlarmBeep } from './hooks/useAlarmBeep'
 *   ...
 *   useAlarmBeep(appState)   // call unconditionally, alongside useSopEffects
 */
export function useAlarmBeep(appState) {
  const audioCtxRef = useRef(null);
  const oscillatorRef = useRef(null);
  const gainRef = useRef(null);
  const prevLevelRef = useRef("");

  const getCtx = () => {
    if (!audioCtxRef.current) {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      audioCtxRef.current = new AudioCtx();
    }
    return audioCtxRef.current;
  };

  const stopContinuous = () => {
    if (oscillatorRef.current) {
      try {
        oscillatorRef.current.stop();
      } catch (e) {
        /* already stopped */
      }
      oscillatorRef.current.disconnect();
      oscillatorRef.current = null;
    }
    if (gainRef.current) {
      gainRef.current.disconnect();
      gainRef.current = null;
    }
  };

  const startContinuous = (freq = 880) => {
    stopContinuous();
    const ctx = getCtx();
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.type = "square";
    osc.frequency.value = freq;
    gain.gain.value = 0.08; // gentle, not jarring, but audible
    osc.connect(gain);
    gain.connect(ctx.destination);
    osc.start();
    oscillatorRef.current = osc;
    gainRef.current = gain;
  };

  const playSingleBeep = (freq = 660, durationMs = 220) => {
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

  useEffect(() => {
    const level = appState?.beep_level || "";
    const prevLevel = prevLevelRef.current;

    if (level === "critical") {
      // Continuous beep until it clears (Table: "Continuous Beep till ack").
      if (prevLevel !== "critical") {
        startContinuous(880);
      }
    } else {
      stopContinuous();
      if (level === "warning" && prevLevel !== "warning") {
        // Single beep only on a NEW warning, not on every tick it's active.
        playSingleBeep(660, 220);
      }
    }

    prevLevelRef.current = level;
  }, [appState?.beep_level]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      stopContinuous();
      if (audioCtxRef.current) {
        audioCtxRef.current.close();
      }
    };
  }, []);
}
