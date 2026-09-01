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

// Chrome (and some other engines) silently drop an utterance if the
// synthesis queue is already speaking/paused, or if getVoices() hasn't
// resolved yet on first use -- both look exactly like "nothing happened",
// no error thrown. Falling back to an explicit voice once the voice list
// has loaded fixes the second case.
let voicesReady = false
let cachedVoices = []

function warmUpVoices() {
  if (!('speechSynthesis' in window)) return
  const load = () => {
    cachedVoices = window.speechSynthesis.getVoices()
    if (cachedVoices.length > 0) voicesReady = true
  }
  load()
  if (!voicesReady) {
    window.speechSynthesis.onvoiceschanged = load
  }
}
warmUpVoices()

// ─────────────────────────────────────────────────────────────────────────
// Speech QUEUE, not cancel-and-replace.
//
// The old version called synth.cancel() before every speak(), so if a
// second line arrived while the first was still talking (e.g. the alarm
// firing right as a switch-trigger line was mid-sentence), the first line
// got cut off mid-word -- heard as two announcements "colliding". Lines
// are now queued and played back-to-back instead; nothing is ever
// interrupted once it's started.
// ─────────────────────────────────────────────────────────────────────────
let speechQueue = []
let isSpeaking = false

function processSpeechQueue() {
  if (isSpeaking || speechQueue.length === 0) return
  if (!('speechSynthesis' in window)) {
    speechQueue = []
    return
  }
  const text = speechQueue.shift()
  const synth = window.speechSynthesis
  isSpeaking = true

  const utter = new SpeechSynthesisUtterance(text)
  utter.rate = 0.95
  utter.pitch = 1.0
  utter.volume = 1.0
  if (voicesReady && cachedVoices.length > 0) {
    const preferred = cachedVoices.find(v => v.lang && v.lang.startsWith('en')) || cachedVoices[0]
    utter.voice = preferred
  }
  const advance = () => {
    isSpeaking = false
    processSpeechQueue()
  }
  utter.onend = advance
  utter.onerror = (e) => {
    console.error('speechSynthesis error', e)
    advance()
  }

  if (!voicesReady) warmUpVoices()
  synth.speak(utter)
}

function speak(text) {
  const clean = sanitizeForSpeech(text)
  if (!clean) return
  speechQueue.push(clean)
  processSpeechQueue()
}

// Exported so useCo2ScenarioEffects.js (and any other scenario-effect hook)
// can reuse the same speech queue / siren / chime instead of duplicating
// the Web Audio setup. Purely additive -- nothing above changes behavior.
export { speak, playSiren, playCompletionChime, playFanSound, playThrusterSound }

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
// Siren: classic two-tone wail via an oscillator whose frequency is swept
// up and down repeatedly. Used for the buoy-scenario alarm INSTEAD OF a
// spoken line at the exact moment it fires, so it can never collide with
// (or get cut off by) other speech -- it's a distinct sound, not another
// queued utterance.
// ─────────────────────────────────────────────────────────────────────────
function playSiren(durationSec = 3) {
  const ctx = getAudioCtx()
  if (!ctx) return

  const osc = ctx.createOscillator()
  osc.type = 'sawtooth'

  const gain = ctx.createGain()
  gain.gain.value = 0.0

  osc.connect(gain)
  gain.connect(ctx.destination)

  const now = ctx.currentTime
  gain.gain.linearRampToValueAtTime(0.12, now + 0.05)
  gain.gain.setValueAtTime(0.12, now + durationSec - 0.15)
  gain.gain.linearRampToValueAtTime(0.0, now + durationSec)

  // Wail between ~500Hz and ~900Hz, ~0.6s per sweep.
  const sweep = 0.6
  let t = now
  osc.frequency.setValueAtTime(500, t)
  while (t < now + durationSec) {
    osc.frequency.linearRampToValueAtTime(900, t + sweep / 2)
    osc.frequency.linearRampToValueAtTime(500, t + sweep)
    t += sweep
  }

  osc.start(now)
  osc.stop(now + durationSec)
}

// ─────────────────────────────────────────────────────────────────────────
// Thruster hum: low-frequency filtered noise + a sawtooth drone, ramping
// in like a motor spinning up. Played when a thruster's POWER switch
// transitions off -> on.
// ─────────────────────────────────────────────────────────────────────────
function playThrusterSound(durationSec = 3) {
  const ctx = getAudioCtx()
  if (!ctx) return
  const now = ctx.currentTime

  // Motor drone.
  const osc = ctx.createOscillator()
  osc.type = 'sawtooth'
  osc.frequency.setValueAtTime(60, now)
  osc.frequency.linearRampToValueAtTime(110, now + 0.8)

  const oscGain = ctx.createGain()
  oscGain.gain.value = 0.0
  osc.connect(oscGain)
  oscGain.connect(ctx.destination)

  // Low rumble noise bed.
  const bufferSize = 2 * ctx.sampleRate
  const noiseBuffer = ctx.createBuffer(1, bufferSize, ctx.sampleRate)
  const output = noiseBuffer.getChannelData(0)
  for (let i = 0; i < bufferSize; i++) output[i] = Math.random() * 2 - 1
  const noise = ctx.createBufferSource()
  noise.buffer = noiseBuffer
  noise.loop = true
  const lowpass = ctx.createBiquadFilter()
  lowpass.type = 'lowpass'
  lowpass.frequency.value = 220
  const noiseGain = ctx.createGain()
  noiseGain.gain.value = 0.0
  noise.connect(lowpass)
  lowpass.connect(noiseGain)
  noiseGain.connect(ctx.destination)

  oscGain.gain.linearRampToValueAtTime(0.10, now + 0.6)
  oscGain.gain.setValueAtTime(0.10, now + durationSec - 0.4)
  oscGain.gain.linearRampToValueAtTime(0.0, now + durationSec)

  noiseGain.gain.linearRampToValueAtTime(0.07, now + 0.6)
  noiseGain.gain.setValueAtTime(0.07, now + durationSec - 0.4)
  noiseGain.gain.linearRampToValueAtTime(0.0, now + durationSec)

  osc.start(now)
  osc.stop(now + durationSec)
  noise.start(now)
  noise.stop(now + durationSec)
}

// ─────────────────────────────────────────────────────────────────────────
// Mission-complete chime: short ascending 3-note tone for success, a
// single low tone for failure. Played once when a scenario resolves.
// ─────────────────────────────────────────────────────────────────────────
function playCompletionChime(success = true) {
  const ctx = getAudioCtx()
  if (!ctx) return
  const now = ctx.currentTime

  const notes = success ? [523.25, 659.25, 783.99] : [220.0]
  const noteDur = success ? 0.18 : 0.6

  notes.forEach((freq, i) => {
    const osc = ctx.createOscillator()
    osc.type = success ? 'triangle' : 'sine'
    osc.frequency.value = freq
    const gain = ctx.createGain()
    gain.gain.value = 0.0
    osc.connect(gain)
    gain.connect(ctx.destination)

    const start = now + i * noteDur
    gain.gain.linearRampToValueAtTime(0.15, start + 0.02)
    gain.gain.setValueAtTime(0.15, start + noteDur - 0.05)
    gain.gain.linearRampToValueAtTime(0.0, start + noteDur)

    osc.start(start)
    osc.stop(start + noteDur)
  })
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
  const prevAlarmRef = useRef(false)
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
        // Dedupe on the backend's monotonic `seq` counter, not on the
        // `timestamp` string (only 1-second resolution). Two distinct
        // classified actions on the same field within the same wall-clock
        // second used to collide on the same dedupe key, which silently
        // swallowed the second one -- and conversely, if this effect ran
        // twice for the very same broadcast (e.g. a duplicate/late
        // websocket message), the timestamp alone didn't reliably catch
        // it. `seq` uniquely identifies one specific event_log entry, so
        // "already spoken this seq" is an exact, unambiguous check with no
        // time window needed.
        const dedupeKey = `${path}:${entry ? entry.seq : 'unmapped'}`

        if (spokenRef.current.has(dedupeKey)) {
          // This exact classified action has already been spoken — skip
          // the repeat instead of saying it again.
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

  // ---- Thruster hum: propulsion_detail.tN.power turning on ----
  const prevPropDetailRef = useRef(null)
  useEffect(() => {
    if (!appState) return
    const prevPD = prevPropDetailRef.current
    if (prevPD === appState.propulsion_detail) return

    if (prevPD) {
      const turnedOn = diffTurnedOn(prevPD, appState.propulsion_detail, ['propulsion_detail'])
      // Only care about the *_power_ fields, not enable/other toggles --
      // the hum represents the motor spinning up, which starts at POWER.
      const powerOn = turnedOn.some(({ path }) => path.endsWith('.power'))
      if (powerOn) playThrusterSound(3)
    }
    prevPropDetailRef.current = appState.propulsion_detail
  }, [appState])

  // ---- Alarm voice-over (Medium/Hard fault-injection scenarios) ----
  // Edge-triggered on scenario.alarm_active, kept as its own effect/ref so
  // it can never collide with (or double up alongside) the switch
  // voice-over above: it fires exactly once on False->True (the alarm) and
  // exactly once on True->False (the "scenario cleared" resolution line).
  useEffect(() => {
    if (!appState || !voiceEnabled) return
    const sc = appState.scenario
    if (!sc) return

    const alarmNow = !!sc.alarm_active
    const wasAlarm = prevAlarmRef.current

    if (alarmNow && !wasAlarm) {
      playSiren(3)
      speak(sc.alarm_message || 'Fault detected. Check the event log.')
    } else if (!alarmNow && wasAlarm) {
      speak(`Scenario cleared. ${sc.clear_message || ''}`)
    }

    prevAlarmRef.current = alarmNow
  }, [appState?.scenario?.alarm_active, voiceEnabled])

  return { glowingLeds }
}

/**
 * useSampleScenarioEffects(appState)
 *   Voice-over for the SAMPLE COLLECTION mission (sample_scenario.py):
 *     - active False->True: announce mission start
 *     - current_stage change: announce that stage's feedback_msg
 *     - active True->False: chime + announce the final result_message
 *   Kept as its own hook/effect so it never collides with the switch or
 *   SOP-alarm voice-overs in useSopEffects() above.
 */
export function useSampleScenarioEffects(appState, { voiceEnabled = true } = {}) {
  const prevActiveRef = useRef(false)
  const prevStageRef = useRef(0)

  useEffect(() => {
    if (!appState || !voiceEnabled) return
    const sc = appState.sample_scenario
    if (!sc) return

    const activeNow = !!sc.active
    const wasActive = prevActiveRef.current
    const stageNow = sc.current_stage || 0
    const wasStage = prevStageRef.current

    if (activeNow && !wasActive) {
      if (stageNow <= 1) {
        speak(`${sc.mission_name || 'Sample Collection'}. Mission started.`)
      }
    } else if (!activeNow && wasActive) {
      if (sc.result_message) {
        playCompletionChime(sc.success !== false)
        speak(sc.result_message)
      }
    } else if (activeNow && wasActive) {
      if (stageNow !== wasStage && sc.feedback_msg) {
        speak(sc.feedback_msg)
      }
    }

    prevActiveRef.current = activeNow
    prevStageRef.current = stageNow
  }, [
    appState?.sample_scenario?.active,
    appState?.sample_scenario?.current_stage,
    voiceEnabled,
  ])
}
