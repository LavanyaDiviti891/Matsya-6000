import { useEffect, useRef } from 'react';

/**
 * Plays a fan-like whirring sound for `durationMs` using the Web Audio API.
 * No audio file needed — it's synthesized noise run through a bandpass
 * filter (gives it a "moving air" character instead of flat static) with a
 * short fade-in/out so it doesn't click at the start/end.
 */
function playFanSound(durationMs = 5000) {
  try {
    const AudioCtx = window.AudioContext || window.webkitAudioContext;
    if (!AudioCtx) return;
    const ctx = new AudioCtx();

    const bufferSize = ctx.sampleRate * (durationMs / 1000);
    const buffer = ctx.createBuffer(1, bufferSize, ctx.sampleRate);
    const data = buffer.getChannelData(0);
    for (let i = 0; i < bufferSize; i++) {
      data[i] = Math.random() * 2 - 1; // white noise
    }

    const noiseSource = ctx.createBufferSource();
    noiseSource.buffer = buffer;

    // Bandpass filter shapes flat white noise into a dull "fan/motor" hum
    const filter = ctx.createBiquadFilter();
    filter.type = 'bandpass';
    filter.frequency.value = 500;
    filter.Q.value = 0.7;

    // Fade in/out envelope
    const gain = ctx.createGain();
    const now = ctx.currentTime;
    const durSec = durationMs / 1000;
    gain.gain.setValueAtTime(0, now);
    gain.gain.linearRampToValueAtTime(0.35, now + 0.3);
    gain.gain.setValueAtTime(0.35, now + durSec - 0.4);
    gain.gain.linearRampToValueAtTime(0, now + durSec);

    noiseSource.connect(filter);
    filter.connect(gain);
    gain.connect(ctx.destination);

    noiseSource.start(now);
    noiseSource.stop(now + durSec);
    noiseSource.onended = () => ctx.close();
  } catch (e) {
    console.error('Fan sound playback failed', e);
  }
}

const SOUND_EFFECTS = {
  fan: () => playFanSound(5000),
};

/**
 * Speaks scenario confirmation messages aloud (and/or plays a sound effect)
 * the instant a stage completes on the backend, regardless of which tab the
 * pilot currently has open.
 *
 * How it works:
 * - The backend (scenario.py) bumps `scenario.announce_seq` and sets
 *   `scenario.announce_text` and/or `scenario.sound_effect` every time a
 *   stage is confirmed complete AND that stage was explicitly opted into
 *   audio feedback (most stages are silent by design).
 * - This hook watches those fields. When `announce_seq` changes:
 *     - if `announce_text` is set, it's spoken via the browser's built-in
 *       Speech Synthesis API (no external service/API key/network call).
 *     - if `sound_effect` is set (e.g. "fan"), the matching sound plays
 *       instead of / alongside the spoken line.
 * - On first mount it just records the current seq without triggering
 *   anything, so we never replay a message that already happened before
 *   this component existed (e.g. on page load / tab remount).
 *
 * Usage: call once, near the top of App.jsx, unconditionally:
 *   useVoiceAnnouncer(appState?.scenario)
 */
export function useVoiceAnnouncer(scenario) {
  const lastSeqRef = useRef(null);

  useEffect(() => {
    if (!scenario) return;

    const seq = scenario.announce_seq;
    const text = scenario.announce_text;
    const sound = scenario.sound_effect;

    // First time we see any scenario data — just baseline the counter.
    if (lastSeqRef.current === null) {
      lastSeqRef.current = seq;
      return;
    }

    if (seq !== lastSeqRef.current) {
      lastSeqRef.current = seq;

      if (text && typeof window !== 'undefined' && window.speechSynthesis) {
        // Cancel any in-flight utterance so announcements never overlap/stack
        // if two confirmations land close together.
        window.speechSynthesis.cancel();
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = 1.0;
        utterance.pitch = 1.0;
        utterance.volume = 1.0;
        window.speechSynthesis.speak(utterance);
      }

      if (sound && SOUND_EFFECTS[sound]) {
        SOUND_EFFECTS[sound]();
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [scenario?.announce_seq, scenario?.announce_text, scenario?.sound_effect]);
}
