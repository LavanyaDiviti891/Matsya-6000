import { useState, useEffect, useRef } from 'react'
import './index.css'
import { API_BASE_URL, WS_BASE_URL } from './apiConfig'
import { useSopEffects } from './useSopEffects'
import { HeaderArea, AppLayout } from './components/MainLayout'
import { BottomTabsNav } from './components/Layout'
import { ScenarioBanner } from './components/ScenarioBanner'
import { SwitchesPLayout, SwitchesSLayout, Switches3Layout } from './components/SwitchesLayout'
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
  const wsRef = useRef(null)
  const reconnectTimerRef = useRef(null)

  // WebSocket connection with automatic reconnect
  useEffect(() => {
    let isComponentMounted = true

    const connectWebSocket = () => {
      try {
        const ws = new WebSocket(WS_BASE_URL)
        wsRef.current = ws

        ws.onopen = () => {
          if (isComponentMounted) {
            setConnected(true)
            if (reconnectTimerRef.current) {
              clearTimeout(reconnectTimerRef.current)
              reconnectTimerRef.current = null
            }
          }
        }

        ws.onmessage = (event) => {
          if (!isComponentMounted) return
          try {
            const data = JSON.parse(event.data)
            setAppState(data)
          } catch (e) {
            console.error("Failed to parse websocket message:", e)
          }
        }

        ws.onclose = () => {
          if (isComponentMounted) {
            setConnected(false)
            // Attempt auto-reconnect every 2 seconds if backend restarts
            reconnectTimerRef.current = setTimeout(connectWebSocket, 2000)
          }
        }

        ws.onerror = (err) => {
          console.error("WebSocket encountered an error:", err)
          ws.close()
        }
      } catch (err) {
        console.error("Failed to establish WebSocket connection:", err)
        if (isComponentMounted) {
          reconnectTimerRef.current = setTimeout(connectWebSocket, 2000)
        }
      }
    }

    connectWebSocket()

    return () => {
      isComponentMounted = false
      if (reconnectTimerRef.current) clearTimeout(reconnectTimerRef.current)
      if (wsRef.current) wsRef.current.close()
    }
  }, [])

  // Redirect away from restricted pages when system powers off
  useEffect(() => {
    if (appState && !appState.is_powered_on && !SWITCHES_ONLY_TABS.includes(activeTab)) {
      setActiveTab("Main")
    }
  }, [appState?.is_powered_on, activeTab])

  const { glowingLeds } = useSopEffects(appState)

  if (!appState) {
    return (
      <div className="loading" style={{ color: '#00f2fe', textAlign: 'center', marginTop: '20%' }}>
        <h2>Connecting to Submersible Data Stream...</h2>
        <p>{!connected ? "Attempting connection to backend server..." : "Receiving initial state..."}</p>
      </div>
    )
  }

  // Generic helper to send POST requests to FastAPI backend
  const apiCall = (endpoint, formData = null) => {
    fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'POST',
      body: formData
    }).catch(e => console.error(`API call to ${endpoint} failed:`, e))
  }

  const handleTabSelect = (tab) => {
    if (!appState.is_powered_on && !SWITCHES_ONLY_TABS.includes(tab)) {
      return // Block navigation when system is off, except for allowed switch pages
    }
    setActiveTab(tab)
  }

  const isOnSwitchesPage = SWITCHES_ONLY_TABS.includes(activeTab)
  const isDedicatedSwitchesPage = ["Switches_P", "Switches_S", "SW-3"].includes(activeTab)

  // EMCS display screen is active only when communication_system_ready or comm_status is True (SOP P-13 / S-13)
  const isEmcsPowered = Boolean(appState?.sidebar?.comm_status || appState?.scenario?.communication_system_ready)
  // Per-side EMCS power: the PORT and STARBOARD switch pages must each
  // react only to their own WAGO/UB selector state, not the combined flag
  // above — otherwise powering WAGO on one side lit up both pages' LCDs.
  const isEmcsPoweredP = Boolean(appState?.sidebar?.comm_status_p)
  const isEmcsPoweredS = Boolean(appState?.sidebar?.comm_status_s)

  return (
    <div className={`dashboard-root ${!appState.is_powered_on ? 'system-off' : ''} ${isOnSwitchesPage ? 'on-switches-page' : ''} ${isEmcsPowered ? 'emcs-active' : 'emcs-off'}`}>
      {!connected && (
        <div style={{ background: '#ff3333', color: 'white', padding: '6px', textAlign: 'center', fontWeight: 'bold' }}>
          Disconnected from Backend Server — Attempting Reconnection...
        </div>
      )}

      {!isDedicatedSwitchesPage && (
        <HeaderArea appState={appState} apiCall={apiCall} glowingLeds={glowingLeds} />
      )}

     {activeTab === "Main-2" && <ScenarioBanner appState={appState} />}

      {activeTab === "Main" ? (
        <AppLayout appState={appState} apiCall={apiCall} glowingLeds={glowingLeds} isEmcsPowered={isEmcsPowered} />
      ) : activeTab === "Main-2" ? (
        <AppLayout appState={appState} apiCall={apiCall} glowingLeds={glowingLeds} isEmcsPowered={isEmcsPowered} />
      ) : activeTab === "Switches_P" ? (
        <SwitchesPLayout appState={appState} apiCall={apiCall} isEmcsPowered={isEmcsPoweredP} />
      ) : activeTab === "Switches_S" ? (
        <SwitchesSLayout appState={appState} apiCall={apiCall} isEmcsPowered={isEmcsPoweredS} />
      ) : activeTab === "SW-3" ? (
        <Switches3Layout appState={appState} apiCall={apiCall} />
      ) : activeTab === "HSSS" ? (
        <HsssLayout appState={appState} apiCall={apiCall} />
      ) : activeTab === "Ballast" ? (
        <BallastLayout appState={appState} apiCall={apiCall} />
      ) : activeTab === "Propulsion" ? (
        <PropulsionLayout appState={appState} apiCall={apiCall} />
      ) : activeTab === "POWER" ? (
        <PowerLayout appState={appState} apiCall={apiCall} />
      ) : activeTab === "Imaging" ? (
        <ImagingLayout appState={appState} apiCall={apiCall} />
      ) : activeTab === "Sensors" ? (
        <SensorsLayout appState={appState} apiCall={apiCall} />
      ) : activeTab === "Logging" ? (
        <LoggingLayout appState={appState} apiCall={apiCall} />
      ) : activeTab === "Status" ? (
        <StatusLayout appState={appState} apiCall={apiCall} />
      ) : activeTab === "50 Kwh" ? (
        <Kwh50Layout appState={appState} apiCall={apiCall} />
      ) : activeTab === "MCC" ? (
        <MccLayout appState={appState} apiCall={apiCall} />
      ) : (
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