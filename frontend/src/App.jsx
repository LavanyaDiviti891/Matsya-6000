import { useState, useEffect } from 'react'
import './index.css'
import { HeaderArea, AppLayout } from './components/MainLayout'
import { BottomTabsNav } from './components/Layout'
import { SwitchesPLayout, SwitchesSLayout, Switches3Layout } from './components/SwitchesLayout'
import {
  HsssLayout, BallastLayout, PropulsionLayout, PowerLayout,
  ImagingLayout, SensorsLayout, LoggingLayout, StatusLayout,
  Kwh50Layout, MccLayout
} from './components/PageLayouts'

// 👇 1. IMPORT THE SCENARIO BANNER COMPONENT
import { ScenarioBanner } from './components/ScenarioBanner'

const TABS = [
  "Main", "HSSS", "Ballast", "Propulsion", "POWER", "Imaging", 
  "Sensors", "Logging", "Status", "50 Kwh", "MCC", 
  "Switches_P", "Switches_S", "SW-3"
]

const SWITCHES_ONLY_TABS = ["Main", "Switches_P", "Switches_S", "SW-3"]

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
    }

    return () => {
      ws.close()
    }
  }, [])

  // When system powers off, redirect away from restricted pages
  useEffect(() => {
    if (!appState?.is_powered_on && !SWITCHES_ONLY_TABS.includes(activeTab)) {
      setActiveTab("Main")
    }
  }, [appState?.is_powered_on])

  if (!appState) {
    return <div className="loading">Connecting to Submersible Data Stream...</div>
  }

  const apiCall = (endpoint, formData = null) => {
    fetch(`http://localhost:8000${endpoint}`, {
      method: 'POST',
      body: formData
    }).catch(e => console.error("API call failed", e))
  }

  const handleTabSelect = (tab) => {
    if (!appState.is_powered_on && !SWITCHES_ONLY_TABS.includes(tab)) {
      return 
    }
    setActiveTab(tab)
  }

  const isOnSwitchesPage = SWITCHES_ONLY_TABS.includes(activeTab)

  return (
    <div className={`dashboard-root ${!appState.is_powered_on ? 'system-off' : ''} ${isOnSwitchesPage ? 'on-switches-page' : ''}`}>
      {!connected && <div style={{ background: 'red', color: 'white', padding: '5px', textAlign: 'center' }}>Disconnected from Backend</div>}
      
      {/* 1. Header Row */}
      <HeaderArea appState={appState} apiCall={apiCall} />
      
      {/* 👇 2. Combined Middle Layout Container (Prevents Grid breakdown) */}
      <div style={{ display: 'flex', flexDirection: 'column', width: '100%', height: '100%', minHeight: 0, overflow: 'hidden', flex: 1 }}>
        
        {/* Scenario Banner stays safely inside the layout stream */}
        <ScenarioBanner appState={appState} />

        {activeTab === "Main" ? <AppLayout appState={appState} apiCall={apiCall} />
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
      </div>

      {/* 3. Footer Navigation Row */}
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