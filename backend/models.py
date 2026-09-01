from pydantic import BaseModel
from typing import Optional, List


# ----------------- SAMPLE COLLECTION SCENARIO (ported from old UI) -----------------
class SampleScenarioTelemetry(BaseModel):
    active: bool = False
    mission_name: str = ""
    success: Optional[bool] = None
    result_message: str = ""
    current_stage: int = 0
    feedback_msg: str = ""


class Co2ScenarioTelemetry(BaseModel):
    active: bool = False
    mission_name: str = ""
    success: Optional[bool] = None
    result_message: str = ""
    current_stage: int = 0
    feedback_msg: str = ""
    timer_total: int = 60
    timer_remaining: int = 60
    blink: bool = False
    # Audio-only alarm cue -- "" | "warning" | "critical". No pop-up/banner
    # is driven by this; it exists purely so the frontend knows whether to
    # play a single beep (warning) or a continuous beep (critical), per
    # the same critical/warning split used in alarm_engine.py.
    beep_level: str = ""


# ----------------- EMERGENCY BUOY DEPLOYMENT SCENARIO -----------------
class BuoyScenarioTelemetry(BaseModel):
    active: bool = False
    mission_name: str = ""
    success: Optional[bool] = None
    result_message: str = ""
    current_stage: int = 0
    feedback_msg: str = ""
    blink: bool = False
    # Audio-only alarm cue fields used by emergency_buoy_scenario.py's
    # Stage 1 (navigation instability). No pop-up/banner is driven by
    # this -- same convention as ScenarioTelemetry/Co2ScenarioTelemetry.
    alarm_active: bool = False
    alarm_message: str = ""


# ----------------- RULE ENGINE / SOP STATE -----------------
class EventLogEntry(BaseModel):
    timestamp: str = ""
    side: str = ""                       # PORT / STARBOARD / GLOBAL
    switch: str = ""
    field_path: str = ""                 # e.g. "switches.p.emg_led_p" -- lets the
                                          # frontend correlate a toggle with its result
    previous_state: str = ""
    new_state: str = ""
    expected_action: str = ""
    action_type: str = ""                # CORRECT / FLEXIBLE_ORDER / OUT_OF_ORDER / EARLY_ACTION / WARNING / NO_GO
    warning: str = ""
    go_no_go: str = ""                   # GO / NO_GO / ""
    measured_voltage: float = 0.0
    measured_soc: float = 0.0
    measured_temperature: float = 0.0
    measured_ir: float = 0.0
    alarm_status: str = "NONE"
    seq: int = 0                          # monotonic counter, unique per log entry -- lets the
                                           # frontend dedupe voice-over reliably instead of relying
                                           # on the 1-second-resolution `timestamp` string


class ScenarioTelemetry(BaseModel):
    active: bool = False
    mission_name: str = "MATSYA Power-Up SOP"
    feedback_msg: str = "Awaiting power-up sequence start."
    active_side: str = ""    # "" / "P" / "S" -- which side is currently being powered up
    next_step_p: str = "[P] Check/confirm E_BATTS position, then activate EMG_LED and run SCRUBBER_CO2_CHECK (any order)"
    next_step_s: str = "[S] Check/confirm E_BATTS position, then activate EMG_LED and run SCRUBBER_CO2_CHECK (any order)"
    last_result: str = ""
    blink: bool = False
    global_power_available: bool = False
    communication_system_ready: bool = False
    power_control_system_ready: bool = False
    last_action_type: str = ""
    last_warning: str = ""
    last_go_no_go: str = ""
    event_log: List[EventLogEntry] = []

    # ── Fault-injection / alarm state (Medium & Hard training scenarios) ──
    alarm_active: bool = False            # True while a NO-GO fault is unresolved
    alarm_message: str = ""               # spoken + shown while alarm_active is True
    fault_type: str = ""                  # "" / "IR_FAULT_MB_S3" / "BLACKOUT_UB_P"
    clear_message: str = ""               # spoken once, on the alarm_active True -> False edge

    # ── Final phase (SOP Steps 57-60: comms/SOC checks, EB revert, UB AB->MB changeover) ──
    next_step_final: str = ""
    main_battery_complete: bool = False   # scenario intentionally ends here (SOP steps 1-60)

    # Post power-up phases (SOP order, steps 63-108):
    # IMAGING -> SENSORS -> COMMS -> BALLAST -> PROPULSION
    # (each phase only activates once the previous one is complete)
    imaging_active: bool = False
    imaging_complete: bool = False
    next_step_imaging: str = ""
    sensors_active: bool = False
    sensors_complete: bool = False
    next_step_sensors: str = ""
    comms_active: bool = False
    comms_complete: bool = False
    next_step_comms: str = ""
    ballast_active: bool = False
    ballast_complete: bool = False
    next_step_ballast: str = ""
    propulsion_active: bool = False
    propulsion_complete: bool = False
    next_step_propulsion: str = ""


# ----------------- ATOMIC TYPES -----------------
class NumericTelemetry(BaseModel):
    value: float = 0.0
    unit: str = ""


# ----------------- STATE SECTIONS -----------------
class HeaderTelemetry(BaseModel):
    dive_num: int = 0
    mission_time: str = "00:00:00"
    present_time: str = "00:00:00"
    heading: NumericTelemetry = NumericTelemetry(value=0.0, unit="deg")
    depth: NumericTelemetry = NumericTelemetry(value=0.0, unit="m")
    altitude: NumericTelemetry = NumericTelemetry(value=4.2, unit="m")
    mb_p_soc: NumericTelemetry = NumericTelemetry(value=85.0, unit="%")
    mb_s_soc: NumericTelemetry = NumericTelemetry(value=85.0, unit="%")


class IMUTelemetry(BaseModel):
    roll: NumericTelemetry = NumericTelemetry(value=0.6, unit="")
    pitch: NumericTelemetry = NumericTelemetry(value=-0.3, unit="")
    heading_p: NumericTelemetry = NumericTelemetry(value=142.0, unit="deg")


class BottomStrip(BaseModel):
    east_speed: NumericTelemetry = NumericTelemetry(value=0.15, unit="m/s")
    vert_speed: NumericTelemetry = NumericTelemetry(value=0.05, unit="m/s")
    north_speed: NumericTelemetry = NumericTelemetry(value=0.10, unit="m/s")
    ship_heading: NumericTelemetry = NumericTelemetry(value=142.0, unit="deg")


class PropulsionTelemetry(BaseModel):
    # In-dive default: vehicle already underway with thrusters running
    # (matches ThrusterTelemetry's running defaults below), not freshly
    # powered off -- that's what made the Main tab RPM boxes read 0.00.
    t1_rpm: float = 900.0
    t2_rpm: float = 900.0
    t3_rpm: float = 900.0
    t4_rpm: float = 900.0
    t5_rpm: float = 900.0
    t6_rpm: float = 900.0
    t7_rpm: float = 900.0
    t8_rpm: float = 900.0
    latitude: NumericTelemetry = NumericTelemetry(value=12.90, unit="deg")
    longitude: NumericTelemetry = NumericTelemetry(value=80.30, unit="deg")


class ThrusterTelemetry(BaseModel):
    """Per-thruster detailed telemetry shown in the Propulsion screen"""
    # In-dive default: already running (power+enable ON), not idle at 0 --
    # values match the "running" branch of main.py's
    # _sync_thruster_telemetry() so a toggle later doesn't cause a jump.
    rpm: float = 900.0         # 0-1600
    voltage: float = 48.0      # V
    current: float = 17.0      # A
    temp: float = 35.0         # deg C
    ctrl: float = 65.0         # control setpoint
    power: bool = True          # power toggle
    enable: bool = True         # enable toggle


class PropulsionDetailState(BaseModel):
    """Full detail state for the Propulsion dedicated screen"""
    t1: ThrusterTelemetry = ThrusterTelemetry()
    t2: ThrusterTelemetry = ThrusterTelemetry()
    t3: ThrusterTelemetry = ThrusterTelemetry()
    t4: ThrusterTelemetry = ThrusterTelemetry()
    t5: ThrusterTelemetry = ThrusterTelemetry()
    t6: ThrusterTelemetry = ThrusterTelemetry()
    t7: ThrusterTelemetry = ThrusterTelemetry()
    t8: ThrusterTelemetry = ThrusterTelemetry()
    heading_ctrl: float = 0.0
    fwd_ctrl: float = 0.0
    lat_ctrl: float = 0.0
    vertical_ctrl: float = 0.0
    speed_factor: int = 4


class EnvironmentTelemetry(BaseModel):
    o2: NumericTelemetry = NumericTelemetry(value=20.9, unit="%")
    co2: NumericTelemetry = NumericTelemetry(value=450.0, unit="ppm")
    temp: NumericTelemetry = NumericTelemetry(value=24.0, unit="deg C")
    pressure: NumericTelemetry = NumericTelemetry(value=1013.0, unit="mbar")


class SidebarControls(BaseModel):
    # In-dive default: vehicle already underway, not freshly powered off --
    # matches ThrusterTelemetry's running defaults above.
    joystick: bool = True
    thrusters_enable: bool = True
    high_speed: bool = True
    ir_ok: bool = True
    water_ingress: bool = False
    comm_status: bool = False
    # Per-side EMCS/WAGO power state. `comm_status` above stays as the
    # global OR (for anything that only cares "is EMCS up at all"), but the
    # PORT and STARBOARD switch pages must react to their OWN side only —
    # otherwise powering WAGO on one side lights up both pages.
    comm_status_p: bool = False
    comm_status_s: bool = False


class LedIndicators(BaseModel):
    pss: bool = False
    pds: bool = False
    ids: bool = False
    psp: bool = False
    pdp: bool = False
    idp: bool = False


class HSSSSideTelemetry(BaseModel):
    co2: NumericTelemetry = NumericTelemetry(value=420.0, unit="ppm")
    oxygen: NumericTelemetry = NumericTelemetry(value=21.0, unit="% v/v")
    pressure: NumericTelemetry = NumericTelemetry(value=1013.0, unit="mbar")
    temp: NumericTelemetry = NumericTelemetry(value=24.5, unit="deg C")
    humidity: NumericTelemetry = NumericTelemetry(value=45.0, unit="%")
    smoke_sensor: str = "NO SMOKE"
    flame_sensor: str = "NO FLAME"
    heat_sensor: str = "Normal"
    hydrogen: NumericTelemetry = NumericTelemetry(value=0.4, unit="%")
    lp_l_pressure: NumericTelemetry = NumericTelemetry(value=210.0, unit="bar")
    hp_b1_pressure: NumericTelemetry = NumericTelemetry(value=205.0, unit="bar")
    hp_b2_pressure: NumericTelemetry = NumericTelemetry(value=207.0, unit="bar")
    hp_b3_pressure: NumericTelemetry = NumericTelemetry(value=203.0, unit="bar")


class HSSSTelemetry(BaseModel):
    p: HSSSSideTelemetry = HSSSSideTelemetry()
    s: HSSSSideTelemetry = HSSSSideTelemetry()


# ----------------- BALLAST STATE SECTIONS -----------------
class MainBallastState(BaseModel):
    act3_pos: float = 0.0        # -150 to 150
    act3_pos2: float = 0.0
    act3_pos3: float = 0.0
    read_pressure_s: float = 0.0
    read_pressure_p: float = 0.0
    pressure_s_enable: bool = False
    pressure_p_enable: bool = False


class VBSTelemetry(BaseModel):
    hpu_enable: bool = False
    hpu_pressure: NumericTelemetry = NumericTelemetry(value=0.0, unit="bar")
    hpu_temp: NumericTelemetry = NumericTelemetry(value=0.0, unit="deg C")
    tank_level: float = 1.0      # 0-300 L
    vbs_set: float = 0.0


class TrimTelemetry(BaseModel):
    position_mm: float = 0.0    # 0-4500
    power: bool = False
    cw_ccw: bool = False
    voltage: NumericTelemetry = NumericTelemetry(value=0.0, unit="V")
    current: NumericTelemetry = NumericTelemetry(value=0.0, unit="A")
    temp: NumericTelemetry = NumericTelemetry(value=0.0, unit="deg C")
    speed: NumericTelemetry = NumericTelemetry(value=0.0, unit="mm/min")
    speed_control: float = 1.0  # 1-7


class OIMControls(BaseModel):
    s1_ext_reset: bool = False
    s2_int_reset: bool = False
    p1_ext_reset: bool = False
    p2_int_reset: bool = False


class BallastTelemetry(BaseModel):
    main_ballast: MainBallastState = MainBallastState()
    vbs: VBSTelemetry = VBSTelemetry()
    trim: TrimTelemetry = TrimTelemetry()
    oim: OIMControls = OIMControls()


# ----------------- POWER STATE SECTIONS -----------------
class BatteryState(BaseModel):
    voltage: NumericTelemetry = NumericTelemetry(value=0.0, unit="V")
    current: NumericTelemetry = NumericTelemetry(value=0.0, unit="A")
    power: NumericTelemetry = NumericTelemetry(value=0.0, unit="kW")
    soc: NumericTelemetry = NumericTelemetry(value=0.0, unit="%")
    temp: NumericTelemetry = NumericTelemetry(value=0.0, unit="deg C")


class EnclosureState(BaseModel):
    voltage: NumericTelemetry = NumericTelemetry(value=0.0, unit="V")
    current: NumericTelemetry = NumericTelemetry(value=0.0, unit="A")
    temp: NumericTelemetry = NumericTelemetry(value=0.0, unit="degC")
    ir_24: NumericTelemetry = NumericTelemetry(value=0.0, unit="Kohm")
    ir_ext: NumericTelemetry = NumericTelemetry(value=0.0, unit="Kohm")
    ir_148: NumericTelemetry = NumericTelemetry(value=0.0, unit="Kohm")
    ir: NumericTelemetry = NumericTelemetry(value=0.0, unit="kohm")
    ir_status: str = "LOW IR"
    water_leak: str = "No Leak"


class UmbilicalState(BaseModel):
    voltage: NumericTelemetry = NumericTelemetry(value=0.0, unit="V")
    current: NumericTelemetry = NumericTelemetry(value=0.0, unit="A")
    temp: NumericTelemetry = NumericTelemetry(value=0.0, unit="degC")
    ir: NumericTelemetry = NumericTelemetry(value=0.0, unit="Kohm")
    ir_status: str = "LOW IR"
    water_leak: str = "No Leak"


class PowerTelemetry(BaseModel):
    mb_p: BatteryState = BatteryState()
    aux_p: BatteryState = BatteryState()
    mb_s: BatteryState = BatteryState()
    aux_s: BatteryState = BatteryState()
    pde_p: EnclosureState = EnclosureState()
    ide_p: EnclosureState = EnclosureState()
    pde_s: EnclosureState = EnclosureState()
    ide_s: EnclosureState = EnclosureState()
    ub_port: UmbilicalState = UmbilicalState()
    ub_stbd: UmbilicalState = UmbilicalState()


# ----------------- IMAGING SECTIONS -----------------
class LedControl(BaseModel):
    power: bool = False
    dim: float = 0.0


class PanTiltState(BaseModel):
    pan: float = 0.0
    tilt: float = 0.0


class ImagingState(BaseModel):
    # Leds
    led_p1: LedControl = LedControl()
    led_p2: LedControl = LedControl()
    led_p3: LedControl = LedControl()
    led_s1: LedControl = LedControl()
    led_s2: LedControl = LedControl()
    led_s3: LedControl = LedControl()
    
    # Cameras
    hd_camera_p: bool = False
    hd_camera_s: bool = False
    hd_sdi_p1: bool = False
    hd_sdi_p2: bool = False
    hd_sdi_p3: bool = False
    hd_sdi_p4: bool = False
    
    hd_camera_s2: bool = False
    hd_sdi_s1: bool = False
    hd_sdi_s2: bool = False
    hd_sdi_s3: bool = False
    
    # Pan Tilt
    pt_p1: PanTiltState = PanTiltState()
    pt_s1: PanTiltState = PanTiltState()
    pt_s2: PanTiltState = PanTiltState()


# ----------------- SENSORS SECTIONS -----------------
class SensorsToggles(BaseModel):
    # In-dive default: sensor suite is already powered up and running, not
    # freshly off (which is what made the Sensors tab read blank).
    depth_sensor_pri: bool = True
    ins: bool = True
    ctdo: bool = True
    dvl: bool = True
    multibeam_sonar: bool = True

    altimeter: bool = True
    dissolved_o2: bool = True
    ctdo_s: bool = True
    mbs: bool = True
    img_sonar: bool = True

    laser_light_2: bool = False
    pan_and_tilt_p1: bool = False
    pan_and_tilt_s1: bool = False
    pan_and_tilt_s2: bool = False


class SensorsIndicators(BaseModel):
    wi_ps_p: bool = True
    wi_ide_p: bool = True
    wi_pde_p: bool = True
    
    ir_ub_p: bool = True
    ir_ide_p: bool = True
    ir_pde_p_int: bool = True
    ir_pde_p_ext: bool = True
    ir_pde_148_p: bool = True
    
    wi_ps_s: bool = True
    wi_ide_s: bool = True
    wi_pde_s: bool = True
    
    ir_ub_s: bool = True
    ir_ide_s: bool = True
    ir_pde_s_int: bool = True
    ir_pde_s_ext: bool = True
    ir_pde_148_s: bool = True
    
    o2_alarm: bool = True
    co2_alarm: bool = True
    pressure_2: bool = True
    altitude_p: bool = True
    depth_alarm: bool = True


class ScientificSensorRow(BaseModel):
    port: float = 0.0
    stbd: float = 0.0


class ScientificSensors(BaseModel):
    conductivity: ScientificSensorRow = ScientificSensorRow(port=5.2, stbd=5.2)
    salinity: ScientificSensorRow = ScientificSensorRow(port=34.7, stbd=34.7)
    water_density: ScientificSensorRow = ScientificSensorRow(port=1027.5, stbd=1027.5)
    turbidity: ScientificSensorRow = ScientificSensorRow(port=1.8, stbd=1.8)
    ph: ScientificSensorRow = ScientificSensorRow(port=7.9, stbd=7.9)
    ctd_temp: ScientificSensorRow = ScientificSensorRow(port=3.2, stbd=3.2)
    pressure: ScientificSensorRow = ScientificSensorRow(port=588.0, stbd=588.0)
    dissolved_oxygen: ScientificSensorRow = ScientificSensorRow(port=145.0, stbd=145.0)
    orp: ScientificSensorRow = ScientificSensorRow(port=210.0, stbd=210.0)


class SurfaceINS(BaseModel):
    s_roll: float = 0.4
    s_pitch: float = -0.2
    s_heading: float = 142.0
    s_speed1: float = 0.3
    s_speed2: float = 0.1
    s_speed3: float = 0.05
    s_latitude: float = 12.90
    s_longitude: float = 80.30


class SubSeaGPS(BaseModel):
    gps_latitude: float = 12.90
    gps_longitude: float = 80.30


class RedtDepthSensor(BaseModel):
    s_depth: float = 5850.0


class SensorsState(BaseModel):
    toggles: SensorsToggles = SensorsToggles()
    indicators: SensorsIndicators = SensorsIndicators()
    scientific: ScientificSensors = ScientificSensors()
    surface_ins: SurfaceINS = SurfaceINS()
    subsea_gps: SubSeaGPS = SubSeaGPS()
    redt_depth: RedtDepthSensor = RedtDepthSensor()
    buzzer_active: bool = False


# ----------------- LOGGING SECTIONS -----------------
class LogEntry(BaseModel):
    date: str = ""
    time: str = ""
    location: str = ""
    message: str = ""


class LoggingToggles(BaseModel):
    led_s1_148v: bool = False
    led_s2_148v: bool = False
    led_s3_148v: bool = False
    led_s4_148v: bool = False
    led_p1_148v: bool = False
    led_p2_148v: bool = False
    led_p3_148v: bool = False
    led_p4_148v: bool = False
    
    trim_s: bool = False
    pde_p_1: bool = False
    trim_p: bool = False
    pde_p_2: bool = False
    
    trim_s_signal: bool = False
    pde_p_signal: bool = False
    trim_p_signal: bool = False


class LoggingState(BaseModel):
    events: list[LogEntry] = [
        LogEntry(date="2026-08-25", time="09:02:11", location="Surface", message="Pre-dive checks complete. System powered ON."),
        LogEntry(date="2026-08-25", time="09:14:47", location="Depth 120m", message="Descent initiated. All systems nominal."),
        LogEntry(date="2026-08-25", time="10:03:22", location="Depth 3400m", message="Passed mid-water checkpoint. HSSS readings stable."),
        LogEntry(date="2026-08-25", time="11:47:05", location="Depth 5850m", message="Seabed proximity detected. Altimeter engaged."),
    ]
    errors: list[LogEntry] = [
        LogEntry(date="2026-08-25", time="10:41:18", location="PDE_S", message="Transient IR dip on PDE_S bus — self-cleared within 4s."),
    ]
    toggles: LoggingToggles = LoggingToggles()


class StatusState(BaseModel):
    chart1_selection: str = "IDE_P Voltage"
    chart2_selection: str = "IDE_P Voltage"


# ----------------- 50 KWH SECTIONS -----------------
class KwhBatteryDetail(BaseModel):
    cur: float = 0.0
    vot: float = 0.0
    id_cell_max: float = 0.0
    max_temp: float = 0.0
    id_cell_min: float = 0.0
    min_temp: float = 0.0
    temp: float = 0.0
    soc: float = 0.0
    soh: float = 0.0


class KwhSideState(BaseModel):
    bat1: KwhBatteryDetail = KwhBatteryDetail()
    bat2: KwhBatteryDetail = KwhBatteryDetail()
    bat3: KwhBatteryDetail = KwhBatteryDetail()
    bat4: KwhBatteryDetail = KwhBatteryDetail()
    bat5: KwhBatteryDetail = KwhBatteryDetail()


class KwhSideStateStbd(BaseModel):
    bat6: KwhBatteryDetail = KwhBatteryDetail()
    bat7: KwhBatteryDetail = KwhBatteryDetail()
    bat8: KwhBatteryDetail = KwhBatteryDetail()
    bat9: KwhBatteryDetail = KwhBatteryDetail()
    bat10: KwhBatteryDetail = KwhBatteryDetail()


class KwhGauges(BaseModel):
    vol: float = 100.0
    temp: float = 0.0
    soc: float = 0.0
    cur: float = 0.0


class KwhState(BaseModel):
    port: KwhSideState = KwhSideState()
    stbd: KwhSideStateStbd = KwhSideStateStbd()
    
    vbs_enable_sig: bool = False
    trim_enable_sig: bool = False
    trim_enable: bool = False
    
    port_gauges: KwhGauges = KwhGauges()
    stbd_gauges: KwhGauges = KwhGauges()
    
    vbs_enable: bool = False


class MCCIndicators(BaseModel):
    co2_sensor_d: bool = False
    trim_system_d: bool = False
    magnetometer_d: bool = False
    conduct_temp_d: bool = False
    thruster_t1_d: bool = False
    thruster_t2_d: bool = False
    thruster_en_p_d: bool = False
    thruster_en_s_d: bool = False
    camera_4k_p_d: bool = False
    hd_camera_p3_d: bool = False
    sd_camera_p4_d: bool = False
    ctdo_d: bool = False

    forwd_low_d: bool = False
    forwd_medi_d: bool = False
    lateral_low_d: bool = False
    lateral_medi_d: bool = False
    verti_low_d: bool = False
    verti_medi_d: bool = False
    heading_low_d: bool = False
    heading_medi_d: bool = False
    camera_4k_s_d: bool = False
    hd_camera_s1_d: bool = False
    sd_camera_s4_d: bool = False
    dissolved_o2_d: bool = False

    led_light_s2_d: bool = False
    led_light_s3_d: bool = False
    led_light_s4_d: bool = False
    ins_d: bool = False
    dvl_d: bool = False
    depth_sensor_pri_d: bool = False
    altimeter_d: bool = False
    led_light_p2_d: bool = False
    led_light_p3_d: bool = False
    led_light_p4_d: bool = False


class MCCStatus(BaseModel):
    data_receiving_mode: str = "DISABLE"
    modem_ready_status: str = "OFF"
    read_write: str = "READ"
    data_sending_mode: str = "NORMAL"
    acoustic_comm_auto: bool = False
    mcc_message: str = "Hi MCC This is MATSYA 6000"
    pilot_message: str = "Hi MCC This is MATSYA 6000"
    ship_latitude: float = 0.0
    ship_longitude: float = 0.0
    ship_heading: float = 0.0
    ship_time: str = "00:00:00"
    power_status: str = "Low"
    pilot_ok: bool = True
    copilot_ok: bool = True
    observer_ok: bool = True
    power_dropdown: str = "Low"
    data_mode: bool = False


class MCCState(BaseModel):
    indicators: MCCIndicators = MCCIndicators()
    status: MCCStatus = MCCStatus()


class SwitchesCategory_P(BaseModel):
    # Thruster Controls
    speed_control: bool = False
    heading_trim: bool = False
    depth_trim: bool = False
    lateral_trim: bool = False

    # BATS Control
    hp_ap_on_off: bool = False
    hp_bp_on_off: bool = False
    hp_reg_set: bool = False
    pitch_on_off: bool = False
    vbt_set_value: bool = False
    pitch_up_down_analog: bool = False
    freeboard_p: bool = False
    dive_in: bool = False
    water_out_on_off: bool = False

    # General control Switches
    co2_scrubber_p: bool = False
    joystick_enable: bool = False
    pilot_selection: bool = False
    copilot_selection: bool = False
    vhs_power_p: bool = False
    led_emergency_port: bool = False
    uw_camera_p: bool = False
    sonar: bool = False
    surface_ins: bool = False

    # Service Drop Weight Switches
    port_side_sdw_1: bool = False
    port_side_sdw_2: bool = False
    port_side_sdw_3: bool = False
    port_side_sdw_4: bool = False
    port_side_sdw_5: bool = False
    starboard_side_sdw_1: bool = False
    starboard_side_sdw_2: bool = False
    starboard_side_sdw_3: bool = False
    starboard_side_sdw_4: bool = False
    starboard_side_sdw_5: bool = False

    # Emergency Jettisoning_P
    ej_manipulator_1: bool = False
    ej_manipulator_2: bool = False
    ej_manipulator_3: bool = False
    ej_manipulator_4: bool = False
    ej_trim_system_1: bool = False
    ej_trim_system_2: bool = False
    ej_trim_system_3: bool = False
    ej_trim_system_4: bool = False
    em_buoy_release_1: bool = False
    em_buoy_release_2: bool = False
    em_buoy_release_3: bool = False
    em_buoy_release_4: bool = False
    ej_sampling_basket_1: bool = False
    ej_sampling_basket_2: bool = False
    ej_sampling_basket_3: bool = False
    ej_sampling_basket_4: bool = False
    em_drop_weight_p1_sc: bool = False
    em_drop_weight_p2_pc: bool = False

    # POWER DIRECT CONTROL_PORT
    mb_p_1: bool = False
    mb_p_2: bool = False
    mb_p_3: bool = False
    mb_p_4: bool = False
    mb_p_5: bool = False
    ab_p_bms: bool = False
    mb_p_bms: bool = False
    ab_p_power_selection: bool = False
    mb_p_pde_p: bool = False

    # New additions
    ib_insulation: float = 4.0
    eb_b_status: float = 0.0
    ub_voltage: float = 0.0
    power_selection_eb: str = "1"
    power_selection_ub: str = "1"
    ub_mcb: bool = False
    
    # Frontend aliases
    # AB_P rotary starts in position 2 (24v PDE_P) per initial-condition spec
    ab_p: bool = True
    e_batts: bool = False
    ub_p_mcb: bool = False
    ub_p_mcb2: bool = False

    # Custom layout fields (frontend-specific names)
    pde_p_clr_rst: bool = False
    oim_p_reset: bool = False
    ab_p_power: bool = False
    pde_p_dim: bool = False
    ide_p_1: bool = False
    ide_2: bool = False
    spare_2: bool = False
    oim_p: bool = False
    spare_p: bool = False
    wago_p: bool = False
    pde_p_24v: bool = False
    mb_1: bool = False
    mb_2: bool = False
    mb_3: bool = False
    mb_4: bool = False
    mb_5: bool = False
    pde_p_olr: bool = False
    pde_p_148: bool = False
    pde_p_24v_main: bool = False
    emg_led_p: bool = False
    int_led_p: bool = False
    # SDW aliases (frontend uses sdwp_1..10 / sdws_1..10)
    sdwp_1: bool = False
    sdwp_2: bool = False
    sdwp_3: bool = False
    sdwp_4: bool = False
    sdwp_5: bool = False
    sdwp_6: bool = False
    sdwp_7: bool = False
    sdwp_8: bool = False
    sdwp_9: bool = False
    sdwp_10: bool = False
    sdws_1: bool = False
    sdws_2: bool = False
    sdws_3: bool = False
    sdws_4: bool = False
    sdws_5: bool = False
    sdws_6: bool = False
    sdws_7: bool = False
    sdws_8: bool = False
    sdws_9: bool = False
    sdws_10: bool = False
    sdw_master_p: bool = False
    sdw_master_s: bool = False
    sdw_master_stbd: bool = False
    sdw_master_stbd_p: bool = False
    sdw_master_stbd_s: bool = False

class SwitchesCategory_S(BaseModel):
    # Thruster Controls
    speed_control: bool = False
    heading_trim: bool = False
    depth_trim: bool = False
    lateral_trim: bool = False

    # BATS Control
    hp_as_on_off: bool = False
    hp_bs_on_off: bool = False
    hp_reg_set: bool = False
    pitch_on_off: bool = False
    vbt_set_value: bool = False
    pitch_up_down_analog: bool = False
    freeboard_s: bool = False
    dive_in: bool = False
    water_out_on_off: bool = False

    # General control Switches
    co2_scrubber_s: bool = False
    joystick_enable: bool = False
    pilot_selection: bool = False
    copilot_selection: bool = False
    vhs_power_s: bool = False
    led_emergency_port: bool = False
    uw_camera_s: bool = False
    sonar: bool = False
    surface_ins: bool = False

    # Service Drop Weight Switches
    port_side_sdw_1: bool = False
    port_side_sdw_2: bool = False
    port_side_sdw_3: bool = False
    port_side_sdw_4: bool = False
    port_side_sdw_5: bool = False
    starboard_side_sdw_1: bool = False
    starboard_side_sdw_2: bool = False
    starboard_side_sdw_3: bool = False
    starboard_side_sdw_4: bool = False
    starboard_side_sdw_5: bool = False

    # Emergency Jettisoning_S
    ej_manipulator_1: bool = False
    ej_manipulator_2: bool = False
    ej_manipulator_3: bool = False
    ej_manipulator_4: bool = False
    ej_trim_system_1: bool = False
    ej_trim_system_2: bool = False
    ej_trim_system_3: bool = False
    ej_trim_system_4: bool = False
    em_buoy_release_1: bool = False
    em_buoy_release_2: bool = False
    em_buoy_release_3: bool = False
    em_buoy_release_4: bool = False
    ej_sampling_basket_1: bool = False
    ej_sampling_basket_2: bool = False
    ej_sampling_basket_3: bool = False
    ej_sampling_basket_4: bool = False
    em_drop_weight_s1_sc: bool = False
    em_drop_weight_s2_pc: bool = False

    # POWER DIRECT CONTROL_STARBOARD
    mb_s_1: bool = False
    mb_s_2: bool = False
    mb_s_3: bool = False
    mb_s_4: bool = False
    mb_s_5: bool = False
    ab_s_bms: bool = False
    mb_s_bms: bool = False
    ab_s_power_selection: bool = False
    mb_s_pde_s: bool = False

    # New additions
    ib_insulation: float = 0.0
    eb_b_status: float = 0.0
    ub_voltage: float = 0.0
    power_selection_eb: str = "1"
    power_selection_ub: str = "1"
    ub_mcb: bool = False
    
    # Frontend aliases
    ab_s: bool = False
    e_batts: bool = False
    ub_s_mcb: bool = False
    ub_s_mcb2: bool = False
    ub_s: bool = False
    
    # Custom layout fields
    pde_s_olr_rst: bool = False
    oim_s_reset: bool = False
    pde_s_oim: bool = False
    ab_s_power: bool = False
    spare_2: bool = False
    ide_2: bool = False
    ide_s_1: bool = False
    wago: bool = False
    xx: bool = False
    oim: bool = False
    secondary: bool = False
    pde_s_olr: bool = False
    mb_s_pde_s: bool = False
    main_24_s: bool = False
    pde_s_148: bool = False

    # General control switch aliases (frontend-specific)
    e_batt_s: bool = False
    aps_2: bool = False
    joystick_p: bool = False
    emg_led_s: bool = False
    co2_s: bool = False
    co2_p: bool = False
    vhs_pow_s: bool = False
    vhs_pow_p: bool = False
    uwt: bool = False
    vhf: bool = False
    mbs_ctrl: bool = False
    dc_fan: bool = False
    emg_led_p: bool = False
    int_led_s: bool = False
    int_led_p: bool = False
    uw_led_s: bool = False
    uw_led_p: bool = False

class SwitchesSW3(BaseModel):
    # Emergency Jettisoning - Trim
    trim_p1: bool = False
    trim_p2: bool = False
    trim_p3: bool = False
    trim_p4: bool = False
    
    t_ej_p1: bool = False
    t_ej_p2: bool = False
    t_ej_p3: bool = False
    t_ej_p4: bool = False
    t_ej_s1: bool = False
    t_ej_s2: bool = False
    t_ej_s3: bool = False
    t_ej_s4: bool = False

    # Emergency Jettisoning - Marker Buoy
    mb_p1: bool = False
    mb_p2: bool = False
    mb_p3: bool = False
    mb_p4: bool = False

    mb_ej_p1: bool = False
    mb_ej_p2: bool = False
    mb_ej_p3: bool = False
    mb_ej_p4: bool = False
    mb_ej_s1: bool = False
    mb_ej_s2: bool = False
    mb_ej_s3: bool = False
    mb_ej_s4: bool = False

    # Emergency Jettisoning - Manipulator
    mani_p1: bool = False
    mani_p2: bool = False
    mani_p3: bool = False
    mani_p4: bool = False
    
    ejm_p1: bool = False
    ejm_p2: bool = False
    ejm_p3: bool = False
    ejm_p4: bool = False
    ejm_s1: bool = False
    ejm_s2: bool = False
    ejm_s3: bool = False
    ejm_s4: bool = False

    # Emergency Jettisoning - Sample Basket
    samp_p1: bool = False
    samp_p2: bool = False
    ejx_p1: bool = False
    ejx_p2: bool = False
    ejx_s1: bool = False
    ejx_s2: bool = False
    
    ejs_p1: bool = False
    ejs_p2: bool = False
    ejs_s1: bool = False
    ejs_s2: bool = False

    # Emergency Drop Weights
    edw_p1: bool = False
    edw_p2: bool = False
    edw_p3: bool = False
    edw_p4: bool = False
    edw_s1: bool = False
    edw_s2: bool = False
    edw_s3: bool = False
    edw_s4: bool = False

    # Bottom controls (field names match SwitchesLayout.jsx apiCall paths exactly)
    freeboard_p: bool = False
    freeboard_s: bool = False
    dive_in_on: bool = False
    dive_in_off: bool = False
    hp_ap_on: bool = False
    hp_ap_off: bool = False
    hp_bp_on: bool = False
    hp_bp_off: bool = False

    # Rotary controls
    fwd_ctrl: bool = False
    heading_ctrl: bool = False
    depth_ctrl: bool = False
    lat_trim: bool = False
    hp_reg: bool = False
    vbt_ctrl: bool = False
    pitch_ctrl: bool = False

    # Water Leak - Port
    wl_ps_p: bool = False
    wl_ide_p: bool = False
    wl_pde_p: bool = False
    wl_pjb_p: bool = False
    wl_tjb_p: bool = False
    wl_bat_p: bool = False

    # Water Leak - Starboard
    wl_ps_s: bool = False
    wl_ide_s: bool = False
    wl_pde_s: bool = False
    wl_pjb_s: bool = False
    wl_tjb_s: bool = False
    wl_bat_s: bool = False

    # Insulation - Port
    ins_ps_p: bool = False
    ins_ide_p: bool = False
    ins_pde_p: bool = False
    ins_148_p: bool = False
    ins_pseb_p: bool = False
    ins_sp1_p: bool = False

    # Insulation - Starboard
    ins_ps_s: bool = False
    ins_ide_s: bool = False
    ins_pde_s: bool = False
    ins_148_s: bool = False
    ins_pseb_s: bool = False
    ins_sp1_s: bool = False

class SwitchesState(BaseModel):
    p: SwitchesCategory_P = SwitchesCategory_P()
    s: SwitchesCategory_S = SwitchesCategory_S()
    sw3: SwitchesSW3 = SwitchesSW3()


# ----------------- ROOT STATE -----------------
# ----------------- ROOT STATE -----------------
class MatsyaUIState(BaseModel):
    is_powered_on: bool = False
    active_tab: str = "Main"

    # ADD THESE 4 LINES to support scenario.py
    active_scenario: str = ""
    scenario_step: int = 0
    scenario_message: str = ""
    alarms: list[str] = []

    # Populated every tick by alarm_engine.update_app_state() (called from
    # main.py's broadcast()) -- the DNV alarm-document threshold engine
    # needs these two fields to exist before it can write to them.
    active_alarms: list[dict] = []
    beep_level: str = ""

    header: HeaderTelemetry = HeaderTelemetry()
    imu: IMUTelemetry = IMUTelemetry()
    bottom: BottomStrip = BottomStrip()
    propulsion: PropulsionTelemetry = PropulsionTelemetry()
    propulsion_detail: PropulsionDetailState = PropulsionDetailState()
    environment: EnvironmentTelemetry = EnvironmentTelemetry()
    sidebar: SidebarControls = SidebarControls()
    leds: LedIndicators = LedIndicators()
    hsss: HSSSTelemetry = HSSSTelemetry()
    ballast: BallastTelemetry = BallastTelemetry()
    power: PowerTelemetry = PowerTelemetry()
    imaging: ImagingState = ImagingState()
    sensors: SensorsState = SensorsState()
    logging: LoggingState = LoggingState()
    status: StatusState = StatusState()
    kwh: KwhState = KwhState()
    mcc: MCCState = MCCState()
    switches: SwitchesState = SwitchesState()
    scenario: ScenarioTelemetry = ScenarioTelemetry()
    sample_scenario: SampleScenarioTelemetry = SampleScenarioTelemetry()
    co2_scenario: Co2ScenarioTelemetry = Co2ScenarioTelemetry()
    buoy_scenario: BuoyScenarioTelemetry = BuoyScenarioTelemetry()


