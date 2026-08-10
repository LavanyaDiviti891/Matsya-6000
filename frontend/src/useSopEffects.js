import { useEffect, useRef, useState } from 'react'

// ─────────────────────────────────────────────────────────────────────────
// Voice-over policy: speaks ONLY when a switch is actually triggered
// (false -> true transition). No narration of banner text, no periodic
// status announcements -- just "that switch happened, here's whether it
// was right." Uses appState.scenario.event_log (matched by field_path) to
// get the backend's classification for that exact action.
// ─────────────────────────────────────────────────────────────────────────

// A small dictionary of domain acronyms that a generic TTS engine mangles
// if left as bare letters (e.g. "IDE" read as a word, "MCB" spelled out
// oddly). Expanding these to their spoken form fixes the "not reading the
// commands properly" complaint. Longer keys are matched first so e.g.
// "MCB" doesn't get clobbered inside a longer token first.
const SPOKEN_EXPANSIONS = [
  ['EMG', 'Emergency'],
  ['LED', 'L E D'],
  ['MCB', 'M C B'],
  ['BMS', 'B M S'],
  ['IDE', 'I D E'],
  ['PDE', 'P D E'],
  ['OIM', 'O I M'],
  ['OLR', 'O L R'],
  ['INT', 'Internal'],
  ['UB', 'U B'],
  ['AB', 'A B'],
  ['EB', 'E B'],
  ['CO2', 'C O two'],
  ['24V', 'twenty four volt'],
  ['148V', 'one forty eight volt'],
]

// Sanitizes any text before it's handed to speechSynthesis:
//   - underscores/hyphens -> spaces (otherwise engines either skip them
//     silently, mid-word, or read "underscore"/"dash" out loud)
//   - collapses repeated whitespace
//   - expands known acronyms to a form that reads cleanly
// Applied to BOTH the humanized switch name and any backend warning/result
// text before they're spoken, so nothing raw (with underscores or bare
// acronym letters) reaches the speech engine.
function sanitizeForSpeech(text) {
  if (!text) return ''
  let out = text.replace(/[_-]+/g, ' ').replace(/\s+/g, ' ').trim()

  // Expand acronyms as whole words only (word-boundary match), case
  // insensitive, so we don't mangle unrelated substrings.
  for (const [code, spoken] of SPOKEN_EXPANSIONS) {
    const re = new RegExp(`\\b${code}\\b`, 'gi')
    out = out.replace(re, spoken)
  }

  return out.replace(/\s+/g, ' ').trim()
}

function speak(text) {
  if (!('speechSynthesis' in window)) return
  const clean = sanitizeForSpeech(text)
  if (!clean) return
  const utter = new SpeechSynthesisUtterance(clean)
  utter.rate = 0.95
  utter.pitch = 1.0
  utter.volume = 1.0
  window.speechSynthesis.speak(utter)
}

function humanizeSwitchName(key) {
  return key.replace(/_/g, ' ')
}

function resultPhrase(entry) {
  if (!entry) return 'ON'
  switch (entry.action_type) {
    case 'CORRECT':
    case 'FLEXIBLE_ORDER':
      return entry.warning ? `ON. ${entry.warning}` : 'ON.'
    case 'EARLY_ACTION':
    case 'OUT_OF_ORDER':
    case 'WARNING':
    case 'NO_GO':
      return entry.warning ? `ON. ${entry.warning}` : 'ON.'
    default:
      return 'ON.'
  }
}

const SCRUBBER_FIELDS = new Set(['switches.p.co2_scrubber_p', 'switches.s.co2_scrubber_s'])

// ─────────────────────────────────────────────────────────────────────────
// Fan sound: 5 seconds of filtered noise via Web Audio API.
// ─────────────────────────────────────────────────────────────────────────
let audioCtx = null
function getAudioCtx() {
  if (!audioCtx) {
    const AC = window.AudioContext || window.webkitAudioContext
    if (!AC) return null
    audioCtx = new AC()
  }
  return audioCtx
}

function playFanSound(durationSec = 5) {
  const ctx = getAudioCtx()
  if (!ctx) return

  const bufferSize = 2 * ctx.sampleRate
  const noiseBuffer = ctx.createBuffer(1, bufferSize, ctx.sampleRate)
  const output = noiseBuffer.getChannelData(0)
  for (let i = 0; i < bufferSize; i++) output[i] = Math.random() * 2 - 1

  const noise = ctx.createBufferSource()
  noise.buffer = noiseBuffer
  noise.loop = true

  const bandpass = ctx.createBiquadFilter()
  bandpass.type = 'bandpass'
  bandpass.frequency.value = 600
  bandpass.Q.value = 0.7

  const gain = ctx.createGain()
  gain.gain.value = 0.0

  noise.connect(bandpass)
  bandpass.connect(gain)
  gain.connect(ctx.destination)

  const now = ctx.currentTime
  gain.gain.linearRampToValueAtTime(0.18, now + 0.3)
  gain.gain.setValueAtTime(0.18, now + durationSec - 0.4)
  gain.gain.linearRampToValueAtTime(0.0, now + durationSec)

  noise.start(now)
  noise.stop(now + durationSec)
}

// ─────────────────────────────────────────────────────────────────────────
// Diff two boolean trees, returning dotted field paths (matching the
// backend's field_path format, e.g. "switches.p.emg_led_p") for every leaf
// that changed false -> true.
// ─────────────────────────────────────────────────────────────────────────
function diffTurnedOn(prevObj, nextObj, prefix = []) {
  const results = []
  if (!prevObj || !nextObj) return results
  for (const key of Object.keys(nextObj)) {
    const nextVal = nextObj[key]
    const prevVal = prevObj[key]
    if (typeof nextVal === 'boolean') {
      if (nextVal === true && prevVal === false) {
        results.push({ path: [...prefix, key].join('.'), key })
      }
    } else if (nextVal && typeof nextVal === 'object' && !Array.isArray(nextVal)) {
      results.push(...diffTurnedOn(prevVal, nextVal, [...prefix, key]))
    }
  }
  return results
}

/**
 * useSopEffects(appState)
 *   - voice-over ONLY on switch trigger, stating whether it was correct
 *     (pulled from the matching event_log entry's field_path)
 *   - 5s fan sound for co2_scrubber_p / co2_scrubber_s
 *   - 2s "glow" window for any leds.* indicator turning on
 */
export function useSopEffects(appState, { voiceEnabled = true } = {}) {
  const prevSwitchesRef = useRef(null)
  const prevLedsRef = useRef(null)
  const [glowingLeds, setGlowingLeds] = useState(new Set())
  // Guards against the same physical action being announced twice — e.g.
  // React 18 StrictMode double-invoking effects in dev, or a stray extra
  // broadcast landing before prevSwitchesRef has updated. Keyed on
  // "path:timestamp of the matched log entry" (or just "path" if there's
  // no log entry yet), and pruned so it never grows unbounded.
  const spokenRef = useRef(new Map())

  useEffect(() => {
    if (!appState) return

    // ---- Switch voice-over (only on trigger) + fan sound ----
    const prevSwitches = prevSwitchesRef.current
    // Same object reference as last run -> nothing actually changed,
    // this effect fired again for an unrelated reason. Skip entirely.
    if (prevSwitches === appState.switches) {
      return
    }

    if (prevSwitches && voiceEnabled) {
      const turnedOn = diffTurnedOn(prevSwitches, appState.switches, ['switches'])
      const log = appState.scenario?.event_log || []
      const now = Date.now()

      for (const { path, key } of turnedOn) {
        // Most recent log entry for this exact field, if the backend
        // classified it (unmapped switches -- e.g. the hard MCB relay --
        // simply get the plain "ON" announcement, no classification).
        const entry = [...log].reverse().find(e => e.field_path === path)
        const dedupeKey = `${path}:${entry ? entry.timestamp : 'unmapped'}`

        const lastSpokenAt = spokenRef.current.get(dedupeKey)
        if (lastSpokenAt && now - lastSpokenAt < 3000) {
          // Same exact classified action already spoken within the last
          // 3s — skip the repeat instead of saying it again.
          continue
        }
        spokenRef.current.set(dedupeKey, now)

        if (SCRUBBER_FIELDS.has(path)) {
          speak(`${humanizeSwitchName(key)}. ${resultPhrase(entry)} Scrubber running.`)
          playFanSound(5)
        } else {
          speak(`${humanizeSwitchName(key)}. ${resultPhrase(entry)}`)
        }
      }

      // Prune old dedupe entries so the map doesn't grow forever.
      for (const [k, t] of spokenRef.current) {
        if (now - t > 10000) spokenRef.current.delete(k)
      }
    }
    prevSwitchesRef.current = appState.switches

    // ---- LED glow (2 seconds) ----
    const prevLeds = prevLedsRef.current
    if (prevLeds) {
      const turnedOn = diffTurnedOn(prevLeds, appState.leds, ['leds'])
      if (turnedOn.length > 0) {
        setGlowingLeds(prev => {
          const next = new Set(prev)
          turnedOn.forEach(({ key }) => next.add(key))
          return next
        })
        turnedOn.forEach(({ key }) => {
          setTimeout(() => {
            setGlowingLeds(prev => {
              const next = new Set(prev)
              next.delete(key)
              return next
            })
          }, 2000)
        })
      }
    }
    prevLedsRef.current = appState.leds
  }, [appState, voiceEnabled])

  return { glowingLeds }
}
