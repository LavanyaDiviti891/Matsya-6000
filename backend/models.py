from pydantic import BaseModel


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
    altitude: NumericTelemetry = NumericTelemetry(value=0.0, unit="m")
    mb_p_soc: NumericTelemetry = NumericTelemetry(value=0.0, unit="%")
    mb_s_soc: NumericTelemetry = NumericTelemetry(value=0.0, unit="%")


class IMUTelemetry(BaseModel):
    roll: NumericTelemetry = NumericTelemetry(value=0.0, unit="")
    pitch: NumericTelemetry = NumericTelemetry(value=0.0, unit="")
    heading_p: NumericTelemetry = NumericTelemetry(value=0.0, unit="deg")


class BottomStrip(BaseModel):
    east_speed: NumericTelemetry = NumericTelemetry(value=0.0, unit="m/s")
    vert_speed: NumericTelemetry = NumericTelemetry(value=0.0, unit="m/s")
    north_speed: NumericTelemetry = NumericTelemetry(value=0.0, unit="m/s")
    ship_heading: NumericTelemetry = NumericTelemetry(value=0.0, unit="deg")


class PropulsionTelemetry(BaseModel):
    t1_rpm: float = 0
    t2_rpm: float = 0
    t3_rpm: float = 0
    t4_rpm: float = 0
    t5_rpm: float = 0
    t6_rpm: float = 0
    t7_rpm: float = 0
    t8_rpm: float = 0
    latitude: NumericTelemetry = NumericTelemetry(value=0.0, unit="deg")
    longitude: NumericTelemetry = NumericTelemetry(value=0.0, unit="deg")


class ThrusterTelemetry(BaseModel):
    """Per-thruster detailed telemetry shown in the Propulsion screen"""
    rpm: float = 0.0           # 0-1600
    voltage: float = 0.0       # V
    current: float = 0.0       # A
    temp: float = 0.0          # deg C
    ctrl: float = 0.0          # control setpoint
    power: bool = False         # power toggle
    enable: bool = False        # enable toggle


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
    o2: NumericTelemetry = NumericTelemetry(value=0.0, unit="%")
    co2: NumericTelemetry = NumericTelemetry(value=0.0, unit="ppm")
    temp: NumericTelemetry = NumericTelemetry(value=0.0, unit="deg C")
    pressure: NumericTelemetry = NumericTelemetry(value=0.0, unit="mbar")


class SidebarControls(BaseModel):
    joystick: bool = False
    thrusters_enable: bool = False
    high_speed: bool = False
    ir_ok: bool = True
    water_ingress: bool = False
    comm_status: bool = False


class LedIndicators(BaseModel):
    pss: bool = False
    pds: bool = False
    ids: bool = False
    psp: bool = False
    pdp: bool = False
    idp: bool = False


class HSSSSideTelemetry(BaseModel):
    co2: NumericTelemetry = NumericTelemetry(value=0.0, unit="ppm")
    oxygen: NumericTelemetry = NumericTelemetry(value=21.0, unit="% v/v")
    pressure: NumericTelemetry = NumericTelemetry(value=0.0, unit="")
    temp: NumericTelemetry = NumericTelemetry(value=0.0, unit="")
    humidity: NumericTelemetry = NumericTelemetry(value=0.0, unit="")
    smoke_sensor: str = "NO SMOKE"
    flame_sensor: str = "NO FLAME"
    heat_sensor: str = "Normal"
    hydrogen: NumericTelemetry = NumericTelemetry(value=0.0, unit="%")
    lp_l_pressure: NumericTelemetry = NumericTelemetry(value=0.0, unit="bar")
    hp_b1_pressure: NumericTelemetry = NumericTelemetry(value=0.0, unit="bar")
    hp_b2_pressure: NumericTelemetry = NumericTelemetry(value=0.0, unit="bar")
    hp_b3_pressure: NumericTelemetry = NumericTelemetry(value=0.0, unit="bar")


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
    depth_sensor_pri: bool = False
    ins: bool = False
    ctdo: bool = False
    dvl: bool = False
    multibeam_sonar: bool = False
    
    altimeter: bool = False
    dissolved_o2: bool = False
    ctdo_s: bool = False
    mbs: bool = False
    img_sonar: bool = False

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
    conductivity: ScientificSensorRow = ScientificSensorRow()
    salinity: ScientificSensorRow = ScientificSensorRow()
    water_density: ScientificSensorRow = ScientificSensorRow()
    turbidity: ScientificSensorRow = ScientificSensorRow()
    ph: ScientificSensorRow = ScientificSensorRow()
    ctd_temp: ScientificSensorRow = ScientificSensorRow()
    pressure: ScientificSensorRow = ScientificSensorRow()
    dissolved_oxygen: ScientificSensorRow = ScientificSensorRow()
    orp: ScientificSensorRow = ScientificSensorRow()


class SurfaceINS(BaseModel):
    s_roll: float = 0.0
    s_pitch: float = 0.0
    s_heading: float = 0.0
    s_speed1: float = 0.0
    s_speed2: float = 0.0
    s_speed3: float = 0.0
    s_latitude: float = 0.0
    s_longitude: float = 0.0


class SubSeaGPS(BaseModel):
    gps_latitude: float = 0.0
    gps_longitude: float = 0.0


class RedtDepthSensor(BaseModel):
    s_depth: float = 0.0


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
    events: list[LogEntry] = []
    errors: list[LogEntry] = []
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


from pydantic import BaseModel

class SwitchesCategory_P(BaseModel):
    # Rotary & Displays
    ab_p: bool = False
    e_batts: bool = False
    ub_mcb: bool = False
    ub_voltage: float = 22.4
    eb_b_status: float = 0.0
    ib_insulation: float = 0.0
    
    # Resets
    pde_p_olr_rst: bool = False
    oim_p_reset: bool = False
    
    # Breakers & Power (Middle Section)
    ab_p_bms: bool = False
    ab_p_power: bool = False
    pde_p_oim: bool = False
    ide_p_1: bool = False
    ide_2: bool = False
    spare_2: bool = False
    oim_p: bool = False
    spare_p: bool = False
    wago_p: bool = False
    
    # Lower Status Toggles
    pde_p_24v: bool = False
    mb_p_bms: bool = False
    mb_1: bool = False
    mb_2: bool = False
    mb_3: bool = False
    mb_4: bool = False
    mb_5: bool = False
    pde_p_olr: bool = False
    pde_p_148: bool = False
    pde_p_24v_main: bool = False
    
    # Service Drop Weights (Port and Stbd routed through P)
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
    
    # SDW Masters
    sdw_master_p: bool = False
    sdw_master_s: bool = False
    sdw_master_stbd_p: bool = False
    sdw_master_stbd_s: bool = False

    # General Control Switch (Port specific variables)
    int_led_p: bool = False
    uw_led_p: bool = False
    joystick_p: bool = False
    co2_p: bool = False
    vhs_pow_p: bool = False
    emg_led_p: bool = False


class SwitchesCategory_S(BaseModel):
    # Rotary & Displays
    e_batt_s: bool = False
    ab_s: bool = False
    eb_s_insulation: float = 0.0
    eb_s_status: float = 0.0
    ub_voltage: float = 22.345
    ub_mcb: bool = False
    
    # Resets
    pde_s_olr_rst: bool = False
    oim_s_reset: bool = False
    
    # Breakers & Power (Middle Section)
    ab_s_bms: bool = False
    ab_s_power: bool = False
    pde_s_oim: bool = False
    spare_2: bool = False
    ide_2: bool = False
    ide_s_1: bool = False
    wago: bool = False
    xx: bool = False
    oim: bool = False
    
    # Lower Status Toggles
    secondary: bool = False
    mb_s_bms: bool = False
    mb_s_1: bool = False
    mb_s_2: bool = False
    mb_s_3: bool = False
    mb_s_4: bool = False
    mb_s_5: bool = False
    pde_s_olr: bool = False
    mb_s_pde_s: bool = False
    main_24_s: bool = False
    
    # General Control Switch (Starboard specific variables)
    uw_led_s: bool = False
    aps_2: bool = False
    emg_led_s: bool = False
    co2_s: bool = False
    vhs_pow_s: bool = False
    uwt: bool = False
    vhf: bool = False
    mbs_ctrl: bool = False
    dc_fan: bool = False
    int_led_s: bool = False


class SwitchesSW3(BaseModel):
    # Emergency Jettisoning - Trim
    t_ej_p1: bool = False
    t_ej_s1: bool = False
    t_ej_p2: bool = False
    t_ej_s2: bool = False
    t_ej_p3: bool = False
    t_ej_s3: bool = False
    t_ej_p4: bool = False
    t_ej_s4: bool = False
    
    # Emergency Jettisoning - Marker Buoy
    mb_ej_p1: bool = False
    mb_ej_s1: bool = False
    mb_ej_p2: bool = False
    mb_ej_s2: bool = False
    mb_ej_p3: bool = False
    mb_ej_s3: bool = False
    mb_ej_p4: bool = False
    mb_ej_s4: bool = False

    # Manipulator
    ejm_p1: bool = False
    ejm_s1: bool = False
    ejm_p2: bool = False
    ejm_s2: bool = False
    ejm_p3: bool = False
    ejm_s3: bool = False
    ejm_p4: bool = False
    ejm_s4: bool = False

    # Sample Basket
    ejs_p1: bool = False
    ejs_s1: bool = False
    ejs_p2: bool = False
    ejs_s2: bool = False
    ejx_p1: bool = False
    ejx_s1: bool = False
    ejx_p2: bool = False
    ejx_s2: bool = False

    # EDW 
    edw_p1: bool = False
    edw_s1: bool = False
    edw_p2: bool = False
    edw_s2: bool = False
    edw_p3: bool = False
    edw_s3: bool = False
    edw_p4: bool = False
    edw_s4: bool = False

    # Water Leak Indicators (Booleans for UI logic)
    wl_ps: bool = False
    wl_ide: bool = False
    wl_pde: bool = False
    wl_pjb: bool = False
    wl_tjb: bool = False
    wl_bat: bool = False

    # Insulation Indicators (Booleans for UI logic)
    ins_p1: bool = False
    ins_p2: bool = False
    ins_p3: bool = False
    ins_p4: bool = False
    ins_p5: bool = False
    ins_p6: bool = False
    
    ins_ps_ub: bool = False
    ins_ide: bool = False
    ins_pde: bool = False
    ins_148v: bool = False
    ins_ps_eb: bool = False
    ins_spare_1: bool = False

    # Bottom Control Switches
    freeboard_p: bool = False
    freeboard_s: bool = False
    dive_in_on: bool = False
    dive_in_off: bool = False
    hp_ap_on: bool = False
    hp_ap_off: bool = False
    hp_bp_on: bool = False
    hp_bp_off: bool = False

    # Knobs (Treated as bools based on value ternary logic (sw.fwd_ctrl ? 2 : 1) )
    fwd_ctrl: bool = False
    heading_ctrl: bool = False
    depth_ctrl: bool = False
    lat_trim: bool = False
    hp_reg: bool = False
    vbt_ctrl: bool = False
    pitch_ctrl: bool = False


class SwitchesState(BaseModel):
    p: SwitchesCategory_P = SwitchesCategory_P()
    s: SwitchesCategory_S = SwitchesCategory_S()
    sw3: SwitchesSW3 = SwitchesSW3()

# ----------------- ROOT STATE -----------------
class MatsyaUIState(BaseModel):
    is_powered_on: bool = False
    active_tab: str = "Main"

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


