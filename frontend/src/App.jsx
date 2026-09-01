import { useState, useEffect, useRef } from 'react'
import './index.css'
import { HeaderArea, AppLayout } from './components/MainLayout'
import { BottomTabsNav } from './components/Layout'
import { SwitchesPLayout, SwitchesSLayout, Switches3Layout } from './components/SwitchesLayout'
import { ScenarioBanner } from './components/ScenarioBanner'
import { useSopEffects, useSampleScenarioEffects } from './hooks/useSopEffects'
import { useCo2ScenarioEffects } from './hooks/useCo2ScenarioEffects'
import { useScenarioBeep } from './hooks/useScenarioBeep'
import {
  HsssLayout, BallastLayout, PropulsionLayout, PowerLayout,
  ImagingLayout, SensorsLayout, LoggingLayout, StatusLayout,
  Kwh50Layout, MccLayout
} from './components/PageLayouts'

const TABS = [
  "Main", "Main-2", "HSSS", "Ballast", "Propulsion", "POWER", "Imaging", 
  "Sensors", "Logging", "Status", "50 Kwh", "MCC", 
  "Switches_P", "Switches_S", "SW-3"
]

const SWITCHES_ONLY_TABS = ["Main", "Main-2", "Switches_P", "Switches_S", "SW-3"]

function App() {
  const [appState, setAppState] = useState(null)
  const [connected, setConnected] = useState(false)
  const [activeTab, setActiveTab] = useState("Main")

  useEffect(() => {
    let isMounted = true
    let ws = null
    let reconnectTimer = null

    const connect = () => {
      ws = new WebSocket('ws://localhost:8000/ws')

      ws.onopen = () => {
        if (!isMounted) return
        setConnected(true)
        if (reconnectTimer) {
          clearTimeout(reconnectTimer)
          reconnectTimer = null
        }
      }

      ws.onmessage = (event) => {
        if (!isMounted) return
        try {
          const data = JSON.parse(event.data)
          setAppState(data)
        } catch (e) {
          console.error("Failed to parse websocket message", e)
        }
      }

      ws.onclose = () => {
        if (!isMounted) return
        setConnected(false)
        // The backend's --reload watcher (or a dropped connection) closes
        // the socket without warning. Without this, `connected` just stays
        // false forever, the red banner never clears, and appState freezes
        // -- which looks exactly like "I click the button and nothing
        // happens", even though the POST itself succeeded server-side.
        reconnectTimer = setTimeout(() => {
          if (isMounted) connect()
        }, 2000)
      }

      ws.onerror = (err) => {
        console.error("WebSocket error:", err)
        ws.close()
      }
    }

    connect()

    return () => {
      isMounted = false
      if (reconnectTimer) clearTimeout(reconnectTimer)
      if (ws) ws.close()
    }
  }, [])

  // When system powers off, redirect away from restricted pages
  // Must be before the early return so hooks are always called in the same order
  useEffect(() => {
    if (!appState?.is_powered_on && !SWITCHES_ONLY_TABS.includes(activeTab)) {
      setActiveTab("Main")
    }
  }, [appState?.is_powered_on])

  // Voice-over effects -- also called unconditionally, before the early
  // return, so hook order stays stable across renders. Each hook no-ops
  // internally until appState is populated.
  useSopEffects(appState)
  useSampleScenarioEffects(appState)
  useCo2ScenarioEffects(appState)
  // Beep-only cue for both the CO2 alarm and the navigation-instability
  // alarm in the combined co2_scenario.py mission -- no pop-up is added
  // by this hook (see hooks/useScenarioBeep.js). If useCo2ScenarioEffects
  // already renders its own visual alarm for the CO2 stage, that's a
  // separate file we don't have this turn -- see the note below.
  useScenarioBeep(appState)

  if (!appState) {
    return <div className="loading">Connecting to Submersible Data Stream...</div>
  }

  // Helper to send post requests
  const apiCall = (endpoint, formData = null) => {
    fetch(`http://localhost:8000${endpoint}`, {
      method: 'POST',
      body: formData
    }).catch(e => console.error("API call failed", e))
  }

  const handleTabSelect = (tab) => {
    if (!appState.is_powered_on && !SWITCHES_ONLY_TABS.includes(tab)) {
      return // Block navigation when system is off, except for switches pages
    }
    setActiveTab(tab)
  }

  const isOnSwitchesPage = SWITCHES_ONLY_TABS.includes(activeTab)
  const isDedicatedSwitchesPage = ["Switches_P", "Switches_S", "SW-3"].includes(activeTab)

  return (
    <div className={`dashboard-root ${!appState.is_powered_on ? 'system-off' : ''} ${isOnSwitchesPage ? 'on-switches-page' : ''}`}>
      {!connected && <div style={{ background: 'red', color: 'white', padding: '5px', textAlign: 'center' }}>Disconnected from Backend</div>}
      {activeTab === "Main-2" && <ScenarioBanner appState={appState} apiCall={apiCall} />}
      {!isDedicatedSwitchesPage && <HeaderArea appState={appState} apiCall={apiCall} />}
      {activeTab === "Main" ? <AppLayout appState={appState} apiCall={apiCall} />
      : activeTab === "Main-2" ? <AppLayout appState={appState} apiCall={apiCall} />
      : activeTab === "Switches_P" ? <SwitchesPLayout appState={appState} apiCall={apiCall} />
      : activeTab === "Switches_S" ? <SwitchesSLayout appState={appState} apiCall={apiCall} />
      : activeTab === "SW-3" ? <Switches3Layout appState={appState} apiCall={apiCall} />
      : activeTab === "HSSS" ? <HsssLayout appState={appState} apiCall={apiCall} />
      : activeTab === "Ballast" ? <BallastLayout appState={appState} apiCall={apiCall} />
      : activeTab === "Propulsion" ? <PropulsionLayout appState={appState} apiCall={apiCall} />
      : activeTab === "POWER" ? <PowerLayout appState={appState} apiCall={apiCall} />
      : activeTab === "Imaging" ? <ImagingLayout appState={appState} apiCall={apiCall} />
      : activeTab === "Sensors" ? <SensorsLayout appState={appState} apiCall={apiCall} />
      : activeTab === "Logging" ? <LoggingLayout appState={appState} apiCall={apiCall} />
      : activeTab === "Status" ? <StatusLayout appState={appState} apiCall={apiCall} />
      : activeTab === "50 Kwh" ? <Kwh50Layout appState={appState} apiCall={apiCall} />
      : activeTab === "MCC" ? <MccLayout appState={appState} apiCall={apiCall} />
      : (
        <div className="main-content-wrapper">
          <div style={{ padding: '20px', color: 'white', fontSize: '24px' }}>
            {activeTab} layout is currently under construction.
          </div>
        </div>
      )}
      <BottomTabsNav
        tabs={TABS}
        activeTab={activeTab}
        onTabSelect={handleTabSelect}
        isPoweredOn={appState.is_powered_on}
        switchesOnlyTabs={SWITCHES_ONLY_TABS}
      />
    </div>
  )
}

export default App
