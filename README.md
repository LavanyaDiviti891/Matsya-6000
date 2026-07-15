# MATSYA 6000 — Manned Submersible Control Dashboard

A comprehensive real-time monitoring and control dashboard for **MATSYA 6000**, a manned submersible (deep-sea research vehicle). This project is built with **FastHTML** and provides an interactive web-based interface for submarine operations, sensor monitoring, and emergency scenarios.

---

## 📋 Project Overview

MATSYA 6000 is a sophisticated submersible control system designed for deep-sea exploration and research missions. This repository contains a full-stack dashboard that allows operators (pilot, co-pilot, observer) to monitor and control all aspects of the submersible including:

- **Real-time telemetry** from multiple sensor systems
- **Propulsion and thruster control** for 8 thrusters
- **Ballast and buoyancy management** (VBS, trim, main ballast systems)
- **Power management** (battery systems, umbilicals, power distribution)
- **Imaging systems** (cameras, LEDs, pan-tilt controls)
- **Emergency scenarios** and safety protocols
- **Mission logging and data recording**

---

## 🏗️ Technology Stack

- **Backend**: Python 3.11, FastHTML, Uvicorn
- **Frontend**: HTML5, CSS3, HTMX (for real-time updates)
- **Real-time Communication**: WebSockets
- **Containerization**: Docker
- **Data Format**: JSON-based simulation data
- **Framework**: FastHTML (a minimal Python web framework built on Starlette)

---

## 📁 Project Structure

```
.
├── main.py                 # Main application (FastHTML server + UI rendering)
├── components.py           # Reusable UI components (gauges, toggles, panels)
├── models.py              # Data models (MatsyaUIState, sensor structures)
├── scenario.py            # Emergency scenario logic (drop weight drills)
├── static/
│   └── styles.css         # Custom CSS styling
├── sim_data_processed/    # Pre-processed JSON files with dive telemetry
│   ├── dive_1.json
│   ├── dive_2.json
│   └── ...
├── Dockerfile             # Container configuration
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

---

## 🎯 Core Features

### 1. **Multi-Tab Dashboard Interface**
The application provides 12 specialized tabs, each focused on a specific system:

| Tab | Purpose |
|-----|---------|
| **Main** | Primary navigation & heading/depth/altitude displays |
| **HSSS** | Habitability & Safety Support System (life support monitoring) |
| **Ballast** | Ballast tank, VBS, trim system, OIM controls |
| **Propulsion** | Thruster power, speed, and axis control (8 thrusters) |
| **POWER** | Battery SOC, power distribution, umbilical status |
| **Imaging** | Underwater cameras, LEDs, pan-tilt systems |
| **Sensors** | Sensor toggles, scientific data (CTD, sonar, DVL, etc.) |
| **Logging** | Event & error logging, signal indicators |
| **Status** | Status charts & trend visualization |
| **50 Kwh** | Battery 50 kWh system status & gauges |
| **MCC** | Mission Control Center data & communications |
| **Switches** | Emergency switches, drop-weight scenarios, jettison controls |

### 2. **Real-Time Data Simulation**
- Loads pre-processed JSON files containing 9 dive profiles
- Simulates submersible telemetry in real-time
- Supports playback controls: **start/pause/resume/speed/end**
- Dynamically switches between dive profiles

### 3. **WebSocket Broadcasting**
- Bidirectional WebSocket communication (`/ws`)
- Broadcasts UI updates to all connected clients
- Real-time state synchronization across all tabs

### 4. **Emergency Scenario Engine**
Includes two interactive training scenarios:
- **DROP WEIGHT — EMERGENCY ASCENT**: Time-based drill to test emergency procedures
  - 30-second countdown timer
  - Visual feedback with color coding (yellow → orange → red)
  - Pilot must flip emergency switches (P1 or P2) within time limit
  - Success/failure overlay with feedback

- **SEQUENTIAL DROP DRILL**: Similar structure with sequential weight drops

### 5. **Component Library**
Extensive reusable components for UI consistency:
- **Gauges**: `VerticalGauge`, `SemiCircleGauge`, `HorizontalProgressBar`
- **Indicators**: `StatusPill`, `LedPanel`, `RedSignalIndicator`, `AlarmLedStatus`
- **Controls**: `ToggleSwitch`, `BallastActSlider`, `SpeedControlSlider`, `PanTiltPad`
- **Data Display**: `SimpleMetricBox`, `BigNumber`, `LogTable`, `KwhDataGrid`
- **Specialized**: `CompassBox`, `ThrusterPanel`, `BatteryPanel`, `MccIndicator`

---

## 🚀 Getting Started

### Prerequisites
- Docker (recommended) or Python 3.11+
- Browser with WebSocket support

### Installation (Docker)

1. **Build the image**:
   ```bash
   docker build -t matsya-6000 .
   ```

2. **Run the container**:
   ```bash
   docker run -p 7860:7860 matsya-6000
   ```

3. **Access the dashboard**:
   - Open `http://localhost:7860` in your browser

### Installation (Local)

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the server**:
   ```bash
   python main.py
   ```

3. **Access at** `http://localhost:7860`

---

## 📊 Data Model

### Core State Structure (`MatsyaUIState`)

```python
class MatsyaUIState:
    header          # Navigation data (depth, heading, altitude, time, dive_num)
    environment     # Life support (O₂, CO₂, temperature, pressure)
    sidebar         # System toggles & status indicators
    imu             # Inertial Measurement Unit (roll, pitch, heading)
    propulsion      # Thruster RPMs, lat/lon, speed factor
    ballast         # Main ballast, VBS, trim, OIM systems
    power           # Battery SOC, power distribution, umbilicals
    imaging         # LED controls, cameras, pan-tilt
    sensors         # Sensor toggles, indicators, scientific data
    logging         # Event/error logs, signal monitoring
    status          # Chart selections for trend visualization
    kwh             # 50 kWh battery system
    mcc             # Mission Control Center data
    switches        # Emergency control switches
    leds            # LED panel status
    hsss            # HSSS-specific sensors (port/starboard)
```

---

## 🎮 Simulation Engine

### How It Works

1. **Data Loading**: Reads `sim_data_processed/*.json` files containing real dive telemetry
2. **Record Playback**: Iterates through records at 1 record/second (or max speed)
3. **State Update**: Updates `MatsyaUIState` fields based on current record
4. **Broadcasting**: Sends updated UI to all connected WebSocket clients
5. **Playback Control**: Supports rewind, forward, start, end, pause, and speed adjustments

### API Routes for Simulation

- `GET/POST /api/start_sim` — Start simulation
- `GET/POST /api/stop_sim` — Stop simulation
- `POST /api/sim/set_dive?dive_num=X` — Switch dive profile
- `POST /api/sim/toggle_pause` — Pause/resume
- `POST /api/sim/set_speed?speed=1|max` — Set playback speed
- `POST /api/sim/{cmd}` — Navigate (start/end)

---

## 🛡️ Emergency Scenarios

### Scenario Architecture

The `scenario.py` module provides:
- `ScenarioState` — Tracks mission status, timer, feedback
- `run_drop_weight_scenario()` — 30-second emergency ascent drill
- `run_sequential_drop_scenario()` — Sequential weight drop drill
- `reset_scenario()` — Resets scenario state

### How Scenarios Work

1. **Activation**: User clicks "START" on Switches tab
2. **Timer**: 30-second countdown begins with visual feedback
3. **Switch Monitoring**: Watches for `em_drop_weight_p1_sc` or `em_drop_weight_p2_pc` toggles
4. **Detection**: When either switch is toggled, scenario completes successfully
5. **Feedback**: Displays "MISSION COMPLETE" ✓ or "MISSION FAILED" ✗

---

## 🔧 API Endpoints

### Toggle API
- `POST /api/toggle/{state_path}` — Toggle any boolean in state (e.g., `/api/toggle/sidebar.joystick`)

### Scenario API
- `POST /api/scenario/drop_weight/start`
- `POST /api/scenario/drop_weight/reset`
- `POST /api/scenario/sequential_drop/start`
- `POST /api/scenario/sequential_drop/reset`

### Sidebar Controls
- `POST /api/toggle_power`
- `POST /api/toggle_joystick`
- `POST /api/toggle_thrusters_enable`
- `POST /api/toggle_high_speed`

### Test
- `POST /api/test` — Manual state update (for testing)

---

## 🎨 UI/UX Design

### Visual Hierarchy
- **Header**: Mission time, dive number, playback controls, real-time metrics (depth, heading, altitude)
- **Sidebar**: Environment status, toggles, system indicators, power button
- **Main Content**: Tab-specific layouts with specialized components
- **Bottom Tab Navigation**: 12-tab selector bar

### Color Scheme
- **Green (#00ff88)**: Normal/OK status, mission complete
- **Yellow (#facc15)**: Warning, active scenario
- **Red (#ff4444)**: Critical/failure, mission failed
- **Dark (#0d0d0d, #1a1a1a)**: Background with subtle borders

### Responsive Design
- Uses CSS Grid and Flexbox for responsive layouts
- Font: Inter (Google Fonts)
- Fixed sidebar, scrollable main content areas

---

## 📈 Metrics & Data Points

The dashboard monitors **200+ real-time metrics** including:

- **Navigation**: Heading, depth, altitude, latitude, longitude
- **Propulsion**: 8 thruster RPMs, speed factor, axis control
- **Power**: 10 battery states, voltage, current, SOC, temperature
- **Life Support**: O₂, CO₂, pressure, temperature, humidity
- **Sensors**: CTD, sonar, DVL, altimeter, insulation status
- **Imaging**: 6 LED systems, 2 HD cameras, 4 pan-tilt systems
- **Safety**: Water ingress, system alarms, buzzer status

---

## 🔐 Security Considerations

- **Docker Isolation**: Runs as non-root user (UID 1000)
- **Port Binding**: Only exposes port 7860
- **No Authentication** (currently) — Assumes trusted environment
- **WebSocket Validation**: Tracks connected clients

---

## 📝 Simulation Data Format

Each JSON file in `sim_data_processed/` contains an array of records:

```json
[
  {
    "header.depth": 5.2,
    "header.heading.value": 185.4,
    "imu.roll.value": 2.1,
    "propulsion.t1_rpm": 1200,
    "environment.o2.value": 20.8,
    ...
  },
  ...
]
```

Each record represents one simulation frame (≈1 second at normal speed).

---

## 🚧 Development Notes

### Adding New Components
1. Define in `components.py` as a function returning HTML elements
2. Import into `main.py`
3. Use in appropriate tab layout
4. Bind state via `id_key` and `toggle_url` for interactivity

### Adding New Tabs
1. Add tab name to bottom navigation list (line 1122)
2. Create `AppLayout()` elif branch with custom layout
3. Add route function `@rt("/{tab_name.lower()}")`
4. Render tab content using components

### Updating Simulation Data
1. Place new JSON files in `sim_data_processed/`
2. Name format: `dive_N.json` where N is dive number
3. Restart server; new files auto-discovered

---

## 📦 Dependencies

- **fasthtml** — Web framework
- **starlette** — ASGI app framework
- **uvicorn** — ASGI server
- **pydantic** — Data validation (optional, used implicitly)

See `requirements.txt` for complete list.

---

## 🐛 Troubleshooting

### No data displayed
- Check `sim_data_processed/` directory exists with JSON files
- Verify JSON format matches expected schema
- Check browser console for WebSocket errors

### Slow performance
- Reduce browser tabs open
- Disable unnecessary UI elements
- Switch to "Max Speed" playback for testing

### WebSocket disconnection
- Check browser network tab for 1006 codes
- Verify server is running and port accessible
- Try browser hard refresh (Ctrl+Shift+R)

---

## 📞 Support & Contact

**Repository**: [LavanyaDiviti891/Matsya-6000](https://github.com/LavanyaDiviti891/Matsya-6000)

---

## 📄 License

See repository for license information.

---

## 🎓 Credits

Built as a comprehensive control system for the **MATSYA 6000** manned submersible research platform.

**Tech Stack**: Python, FastHTML, HTMX, WebSockets, Docker

**Last Updated**: June 2026
