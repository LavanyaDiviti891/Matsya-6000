import { useState, useEffect } from 'react'
import './index.css'
import { HeaderArea, AppLayout } from './components/MainLayout'
import { BottomTabsNav } from './components/Layout'
import { ScenarioBanner } from './components/ScenarioBanner'
import { SwitchesPLayout, SwitchesSLayout, Switches3Layout } from './components/SwitchesLayout'
import {
  HsssLayout, BallastLayout, PropulsionLayout, PowerLayout,
  ImagingLayout, SensorsLayout, LoggingLayout, StatusLayout,
  Kwh50Layout, MccLayout
} from './components/PageLayouts'
import { useVoiceAnnouncer } from './hooks/useVoiceAnnouncer'

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
    const ws = new WebSocket('ws://localhost:8000/ws')

    ws.onopen = () => {
      setConnected(true)
    }

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        setAppState(data)
      } catch (e) {
        console.error("Failed to parse websocket message", e)
      }
    }

    ws.onclose = () => {
      setConnected(false)
      // Attempt to reconnect after a delay could go here
    }

    return () => {
      ws.close()
    }
  }, [])

  // When system powers off, redirect away from restricted pages
  // Must be before the early return so hooks are always called in the same order
  useEffect(() => {
    if (!appState?.is_powered_on && !SWITCHES_ONLY_TABS.includes(activeTab)) {
      setActiveTab("Main")
    }
  }, [appState?.is_powered_on])

  // Voice confirmation for pilot actions (e.g. "100kg weights dropped.")
  // Runs globally regardless of which tab is active, including Main-2.
  useVoiceAnnouncer(appState?.scenario)

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
      {!isDedicatedSwitchesPage && <HeaderArea appState={appState} apiCall={apiCall} />}
      {activeTab === "Main-2" && <ScenarioBanner appState={appState} />}
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
