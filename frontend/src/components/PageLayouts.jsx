import React from 'react';
import { Sidebar } from './MainLayout';
import { SemiCircleGauge, HorizontalProgressBar, SensorStatusPill, HSSSLabelInput } from './HsssWidgets';
import { BallastActionButton, BallastPressureRead, BallastActSlider, VBSTankGauge, VBSMetricRow, VBSWaterButton, VBSSetControl, TrimPositionBar, SpeedControlSlider, OIMToggleRow } from './BallastWidgets';
import { ThrusterPanel, PropCenterToggleBlock, PropAxisControl } from './PropulsionWidgets';
import { BatteryPanel, PDEPanel, IDEPanel, UmbilicalPanel } from './PowerWidgets';
import { ImagingToggle, LedDimmerSlider, CameraActionGrid, PanTiltBar, PanTiltPad } from './ImagingWidgets';
import { SensorToggleBlock, SensorLedStatus, AlarmLedStatus, ScientificSensorRowItem, SensorBoxMetric, BuzzerPanel, LogTable, HorizontalToggle, RedSignalIndicator, StatusChartRowComponent, KwhDataGrid, KwhVerticalGauge, MccIndicator, MccStatusBox, MccMessageInput, MccShipData, MccRadioGroup, MccCrewStatus, MccPowerDropdown } from './MiscWidgets';
import { ToggleSwitch, MetalSwitch } from './Controls';
import { SimpleMetricBox } from './Layout';

function renderHsssPanel(title, sideData, sfSuffix) {
  return (
    <div className="hsss-panel">
      <div className="hsss-panel-title">{title}</div>
      <div className="hsss-gauges-row">
        <SemiCircleGauge label={`CO2${sfSuffix}`} value={sideData.co2?.value} minVal={0} maxVal={5000} unit="ppm" scaleLabels={["0", "1000", "2000", "3000", "4000", "5000"]} />
        <SemiCircleGauge label={`Oxygen${sfSuffix}`} value={sideData.oxygen?.value} minVal={19} maxVal={25} unit="% v/v" scaleLabels={["19", "20", "21", "22", "23", "24", "25"]} isOxygen={true} />
      </div>
      <div className="hsss-two-col">
        <div className="hsss-col-left">
          <HorizontalProgressBar label={`Pressure in mbar${sfSuffix}`} value={sideData.pressure?.value} minVal={800} maxVal={1200} unit="" scaleLabels={["800", "850", "900", "950", "1000", "1050", "1100", "1150", "1200"]} />
          <HorizontalProgressBar label={`Temp in Deg C${sfSuffix}`} value={sideData.temp?.value} minVal={0} maxVal={100} unit="" scaleLabels={["0", "10", "20", "30", "40", "50", "60", "70", "80", "90", "100"]} />
          <HorizontalProgressBar label={`Humidity${sfSuffix} in %`} value={sideData.humidity?.value} minVal={0} maxVal={100} unit="" scaleLabels={["0", "10", "20", "30", "40", "50", "60", "70", "80", "90", "100"]} />
        </div>
        <div className="hsss-col-right">
          <SensorStatusPill label={`Smoke Sensor${sfSuffix.toLowerCase()}`} statusText={sideData.smoke_sensor} isOk={sideData.smoke_sensor === "NO SMOKE"} />
          <SensorStatusPill label={`Flame Sensor${sfSuffix.toLowerCase()}`} statusText={sideData.flame_sensor} isOk={sideData.flame_sensor === "NO FLAME"} />
          <SensorStatusPill label={`Heat Sensor${sfSuffix.toLowerCase()}`} statusText={sideData.heat_sensor} isOk={sideData.heat_sensor === "Normal"} />
          <HSSSLabelInput label={`Hydrogen${sfSuffix}`} value={sideData.hydrogen?.value} unit="%" />
          <HSSSLabelInput label={`LP_L Pressure${sfSuffix}`} value={sideData.lp_l_pressure?.value} unit="bar" />
        </div>
      </div>
      <div className="hsss-bottom-row">
        <HSSSLabelInput label={`HP_B1 Pressure${sfSuffix}`} value={sideData.hp_b1_pressure?.value} unit="bar" />
        <HSSSLabelInput label={`HP_B2 Pressure${sfSuffix}`} value={sideData.hp_b2_pressure?.value} unit="bar" />
        <HSSSLabelInput label={`HP_B3 Pressure${sfSuffix}`} value={sideData.hp_b3_pressure?.value} unit="bar" />
      </div>
    </div>
  );
}

export function HsssLayout({ appState, apiCall }) {
  const s = appState;
  return (
    <div className="main-content-wrapper">
      <div className="main-content">
        <div className="hsss-content-row">
          {renderHsssPanel("HSSS_P", s.hsss.p, "_P")}
          {renderHsssPanel("HSSS_S", s.hsss.s, "_S")}
        </div>
        <Sidebar appState={appState} apiCall={apiCall} />
      </div>
    </div>
  );
}

export function BallastLayout({ appState, apiCall }) {
  const s = appState;
  const b = s.ballast;

  const mainBallastPanel = (
    <div className="ballast-main-panel">
      <div className="ballast-btn-grid">
        <BallastActionButton label="Ready to Dive open" />
        <BallastActionButton label="Ready to Dive Close" />
        <BallastActionButton label="Dive open" />
        <BallastActionButton label="Dive Close" />
        <BallastActionButton label="Surface open" />
        <BallastActionButton label="Surface Close" />
      </div>
      <div className="ballast-mid-row">
        <div className="ballast-pressure-col">
          <BallastPressureRead label="Read Pressure_S" value={b.main_ballast.read_pressure_s} isEnabled={b.main_ballast.pressure_s_enable} toggleUrl="/api/toggle/ballast.main_ballast.pressure_s_enable" />
          <BallastPressureRead label="Read Pressure_P" value={b.main_ballast.read_pressure_p} isEnabled={b.main_ballast.pressure_p_enable} toggleUrl="/api/toggle/ballast.main_ballast.pressure_p_enable" />
        </div>
        <div className="ballast-main-label">{"Main\nBallast\nSystem"}</div>
      </div>
      <BallastActSlider label="ACT 3 pos" value={b.main_ballast.act3_pos} />
      <BallastActSlider label="ACT 3 pos 2" value={b.main_ballast.act3_pos2} />
      <BallastActSlider label="ACT 3 pos 3" value={b.main_ballast.act3_pos3} />
    </div>
  );

  const vbsPanel = (
    <div className="ballast-vbs-panel">
      <div className="vbs-panel-title">VBS</div>
      <div className="vbs-content-row">
        <div className="vbs-left-col">
          <div className="vbs-hpu-row">
            <div className="vbs-hpu-label">VBS_HPU_Enable</div>
            <div className={`vbs-hpu-btn ${b.vbs.hpu_enable ? 'vbs-hpu-on' : ''}`}>
              {b.vbs.hpu_enable ? "HPU ON" : "HPU OFF"}
            </div>
          </div>
          <VBSMetricRow label="HPU Pressure" value={b.vbs.hpu_pressure?.value} unit="bar" />
          <VBSMetricRow label="HPU temp" value={b.vbs.hpu_temp?.value} unit="deg C" />
          <VBSWaterButton label="Water IN" />
          <VBSWaterButton label="Water OUT" />
          <VBSSetControl value={b.vbs.vbs_set} />
        </div>
        <VBSTankGauge level={b.vbs.tank_level} />
      </div>
    </div>
  );

  const trimPanel = (
    <div className="ballast-trim-panel">
      <div className="trim-header">
        <div className="trim-position-label">Trim Position (mm)</div>
        <div className="trim-title">TRIM</div>
      </div>
      <TrimPositionBar value={b.trim.position_mm} />
      <div className="trim-metrics-row">
        <div className="trim-toggle-col">
          <ToggleSwitch label="power" isOn={b.trim.power} onToggle={() => apiCall('/api/toggle/ballast.trim.power')} />
        </div>
        <div className="trim-metrics-left">
          <SimpleMetricBox label="Voltage" value={b.trim.voltage?.value} unit="V" />
          <SimpleMetricBox label="Current" value={b.trim.current?.value} unit="A" />
        </div>
        <div className="trim-metrics-right">
          <SimpleMetricBox label="Temp" value={b.trim.temp?.value} unit="deg C" />
          <SimpleMetricBox label="speed" value={b.trim.speed?.value} unit="mm/min" />
        </div>
        <div className="trim-toggle-col">
          <ToggleSwitch label="CW/CCW" isOn={b.trim.cw_ccw} onToggle={() => apiCall('/api/toggle/ballast.trim.cw_ccw')} />
        </div>
      </div>
    </div>
  );

  const oimPanel = (
    <div className="ballast-oim-panel">
      <SpeedControlSlider value={b.trim.speed_control} />
      <div className="oim-toggles-col">
        <OIMToggleRow label="OIM_S1_Ext_Reset" isOn={b.oim.s1_ext_reset} toggleUrl="/api/toggle/ballast.oim.s1_ext_reset" />
        <OIMToggleRow label="OIM_S2_Int_Reset" isOn={b.oim.s2_int_reset} toggleUrl="/api/toggle/ballast.oim.s2_int_reset" />
        <OIMToggleRow label="OIM_P1_Ext_Reset" isOn={b.oim.p1_ext_reset} toggleUrl="/api/toggle/ballast.oim.p1_ext_reset" />
        <OIMToggleRow label="OIM_P2_Int_Reset" isOn={b.oim.p2_int_reset} toggleUrl="/api/toggle/ballast.oim.p2_int_reset" />
      </div>
    </div>
  );

  return (
    <div className="main-content-wrapper">
      <div className="main-content">
        <div className="ballast-content-col">
          <div className="ballast-top-row">
            {mainBallastPanel}
            {vbsPanel}
          </div>
          <div className="ballast-bottom-row">
            {trimPanel}
            {oimPanel}
          </div>
        </div>
        <Sidebar appState={appState} apiCall={apiCall} />
      </div>
    </div>
  );
}

export function PropulsionLayout({ appState, apiCall }) {
  const s = appState;
  const pd = s.propulsion_detail;

  return (
    <div className="main-content-wrapper">
      <div className="prop-content-wrapper">
        <div className="main-content">
          <div className="prop-thruster-col">
            <ThrusterPanel thrusterId={2} t={pd.t2} />
            <ThrusterPanel thrusterId={4} t={pd.t4} />
          </div>
          <div className="prop-thruster-col">
            <ThrusterPanel thrusterId={6} t={pd.t6} />
            <ThrusterPanel thrusterId={8} t={pd.t8} />
          </div>
          <div className="prop-center-col">
            <div className="prop-center-header">POWER / ENABLE</div>
            <PropCenterToggleBlock thrusterId={2} power={pd.t2.power} enable={pd.t2.enable} toggleUrlP="/api/toggle/propulsion_detail.t2.power" toggleUrlE="/api/toggle/propulsion_detail.t2.enable" />
            <PropCenterToggleBlock thrusterId={6} power={pd.t6.power} enable={pd.t6.enable} toggleUrlP="/api/toggle/propulsion_detail.t6.power" toggleUrlE="/api/toggle/propulsion_detail.t6.enable" />
            <PropCenterToggleBlock thrusterId={5} power={pd.t5.power} enable={pd.t5.enable} toggleUrlP="/api/toggle/propulsion_detail.t5.power" toggleUrlE="/api/toggle/propulsion_detail.t5.enable" />
            <PropCenterToggleBlock thrusterId={1} power={pd.t1.power} enable={pd.t1.enable} toggleUrlP="/api/toggle/propulsion_detail.t1.power" toggleUrlE="/api/toggle/propulsion_detail.t1.enable" />
            <PropCenterToggleBlock thrusterId={4} power={pd.t4.power} enable={pd.t4.enable} toggleUrlP="/api/toggle/propulsion_detail.t4.power" toggleUrlE="/api/toggle/propulsion_detail.t4.enable" />
            <PropCenterToggleBlock thrusterId={8} power={pd.t8.power} enable={pd.t8.enable} toggleUrlP="/api/toggle/propulsion_detail.t8.power" toggleUrlE="/api/toggle/propulsion_detail.t8.enable" />
            <PropCenterToggleBlock thrusterId={7} power={pd.t7.power} enable={pd.t7.enable} toggleUrlP="/api/toggle/propulsion_detail.t7.power" toggleUrlE="/api/toggle/propulsion_detail.t7.enable" />
            <PropCenterToggleBlock thrusterId={3} power={pd.t3.power} enable={pd.t3.enable} toggleUrlP="/api/toggle/propulsion_detail.t3.power" toggleUrlE="/api/toggle/propulsion_detail.t3.enable" />
          </div>
          <div className="prop-thruster-col">
            <ThrusterPanel thrusterId={5} t={pd.t5} />
            <ThrusterPanel thrusterId={7} t={pd.t7} />
          </div>
          <div className="prop-thruster-col">
            <ThrusterPanel thrusterId={1} t={pd.t1} />
            <ThrusterPanel thrusterId={3} t={pd.t3} />
          </div>
          <Sidebar appState={appState} apiCall={apiCall} />
        </div>
        <div className="prop-bottom-strip">
          <PropAxisControl label="Heading ctrl" value={pd.heading_ctrl} />
          <PropAxisControl label="Fwd ctrl" value={pd.fwd_ctrl} />
          <PropAxisControl label="Lat ctrl" value={pd.lat_ctrl} />
          <PropAxisControl label="Vertical ctrl" value={pd.vertical_ctrl} />
          <div className="prop-speed-factor">
            <span className="prop-speed-icon">🐢</span>
            <span className="prop-speed-value">{pd.speed_factor}</span>
            <span className="prop-speed-label">speed factor</span>
          </div>
        </div>
      </div>
    </div>
  );
}

export function PowerLayout({ appState, apiCall }) {
  const s = appState;
  const p = s.power;

  return (
    <div className="main-content-wrapper">
      <div className="main-content">
        <div className="power-grid-container">
          <div className="power-row">
            <BatteryPanel title="MB_P" prefix="MB_P" battery={p.mb_p} scaleLabels={["100", "120", "140", "160", "180"]} minVal={100} maxVal={180} />
            <BatteryPanel title="AUX_P" prefix="AUX_P" battery={p.aux_p} scaleLabels={["0", "10", "20", "30", "40"]} minVal={0} maxVal={40} />
            <BatteryPanel title="MB_S" prefix="MB_S" battery={p.mb_s} scaleLabels={["100", "120", "140", "160", "180"]} minVal={100} maxVal={180} />
            <BatteryPanel title="AUX_S" prefix="AUX_S" battery={p.aux_s} scaleLabels={["0", "10", "20", "30", "40"]} minVal={0} maxVal={40} />
          </div>
          <div className="power-row">
            <PDEPanel title="PDE_P" prefix="PDE_P" enclosure={p.pde_p} />
            <IDEPanel title="IDE_P" prefix="IDE_P" enclosure={p.ide_p} />
            <PDEPanel title="PDE_S" prefix="PDE_S" enclosure={p.pde_s} />
            <IDEPanel title="IDE_S" prefix="IDE_S" enclosure={p.ide_s} />
          </div>
          <div className="power-row power-row-bottom">
            <UmbilicalPanel title="UB_Port" prefix="PSP" umbilical={p.ub_port} />
            <UmbilicalPanel title="UB_Stbd" prefix="PSS" umbilical={p.ub_stbd} />
          </div>
        </div>
        <Sidebar appState={appState} apiCall={apiCall} />
      </div>
    </div>
  );
}


export function ImagingLayout({ appState, apiCall }) {
  const s = appState;
  const img = s.imaging;

  const ledSection = (
    <div className="img-panel">
      <div className="img-panel-title">LED Controls</div>
      <div className="img-top-row">
        <div className="img-col-main">
          <div style={{fontSize:'12px', fontWeight:700, color:'var(--color-text)', textAlign:'center'}}>Underwater LED_P</div>
          <div className="img-led-row">
            <div className="img-toggle-block">
              <ImagingToggle label="LED P1" isOn={img.led_p1.power} toggleUrl="/api/toggle/imaging.led_p1.power" />
              <ImagingToggle label="LED P2" isOn={img.led_p2.power} toggleUrl="/api/toggle/imaging.led_p2.power" />
              <ImagingToggle label="LED P3" isOn={img.led_p3.power} toggleUrl="/api/toggle/imaging.led_p3.power" />
            </div>
            <div className="img-toggle-block">
              <LedDimmerSlider label="led 3 Dim%(10x)" value={img.led_p1.dim} />
              <LedDimmerSlider label="led 5 Dim%(10x)" value={img.led_p2.dim} />
              <LedDimmerSlider label="led 7 Dim%(10x)" value={img.led_p3.dim} />
            </div>
          </div>
        </div>
        <div className="img-col-main">
          <div style={{fontSize:'12px', fontWeight:700, color:'var(--color-text)', textAlign:'center'}}>Underwater LED_S</div>
          <div className="img-led-row">
            <div className="img-toggle-block">
              <ImagingToggle label="LED S1" isOn={img.led_s1.power} toggleUrl="/api/toggle/imaging.led_s1.power" />
              <ImagingToggle label="LED S2" isOn={img.led_s2.power} toggleUrl="/api/toggle/imaging.led_s2.power" />
              <ImagingToggle label="LED S3" isOn={img.led_s3.power} toggleUrl="/api/toggle/imaging.led_s3.power" />
            </div>
            <div className="img-toggle-block">
              <LedDimmerSlider label="led 4 Dim%(10x)" value={img.led_s1.dim} />
              <LedDimmerSlider label="led 6 Dim%(10x)" value={img.led_s2.dim} />
              <LedDimmerSlider label="led 8 Dim%(10x)" value={img.led_s3.dim} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const camSection = (
    <div className="img-panel">
      <div className="img-panel-title">Camera Controls</div>
      <div className="img-cam-grid">
        <div className="img-cam-col">
          <ImagingToggle label="HD camera P" isOn={img.hd_camera_p} inline={true} toggleUrl="/api/toggle/imaging.hd_camera_p" />
          <div className="sdi-grid">
            <div className="sdi-col">
              <ImagingToggle label="HD SDI_P1" isOn={img.hd_sdi_p1} toggleUrl="/api/toggle/imaging.hd_sdi_p1" />
              <ImagingToggle label="HD SDI_P2" isOn={img.hd_sdi_p2} toggleUrl="/api/toggle/imaging.hd_sdi_p2" />
            </div>
            <div className="sdi-col">
              <ImagingToggle label="HD SDI_P3" isOn={img.hd_sdi_p3} toggleUrl="/api/toggle/imaging.hd_sdi_p3" />
              <ImagingToggle label="HD SDI_P4" isOn={img.hd_sdi_p4} toggleUrl="/api/toggle/imaging.hd_sdi_p4" />
            </div>
          </div>
          <div style={{fontSize:'14px', fontWeight:800, color:'var(--color-text)', textAlign:'center', marginBottom:'8px'}}>HD Camera_P</div>
          <CameraActionGrid />
        </div>
        <div className="img-cam-col">
          <ImagingToggle label="HD camera S" isOn={img.hd_camera_s} inline={true} toggleUrl="/api/toggle/imaging.hd_camera_s" />
          <div className="sdi-grid">
            <div className="sdi-col">
              <ImagingToggle label="HD Camera S2" isOn={img.hd_camera_s2} inline={true} toggleUrl="/api/toggle/imaging.hd_camera_s2" />
              <ImagingToggle label="HD SDI_S1" isOn={img.hd_sdi_s1} inline={true} toggleUrl="/api/toggle/imaging.hd_sdi_s1" />
            </div>
            <div className="sdi-col">
              <ImagingToggle label="HD SDI_S2" isOn={img.hd_sdi_s2} inline={true} toggleUrl="/api/toggle/imaging.hd_sdi_s2" />
              <ImagingToggle label="HD SDI_S3" isOn={img.hd_sdi_s3} inline={true} toggleUrl="/api/toggle/imaging.hd_sdi_s3" />
            </div>
          </div>
          <div style={{fontSize:'14px', fontWeight:800, color:'var(--color-text)', textAlign:'center', marginBottom:'8px'}}>HD Camera _S</div>
          <CameraActionGrid />
        </div>
      </div>
    </div>
  );

  const pt = img.pt_p1;
  const rightCol = (
    <div className="img-col-right">
      <div className="img-panel img-pt-panel">
        <div className="img-panel-title">Pan and Tilt position</div>
        <PanTiltBar label="PAN" value={pt.pan} minVal={-170} maxVal={170} scaleLabels={["-170", "-100", "0", "100", "170"]} />
        <PanTiltBar label="TILT" value={pt.tilt} minVal={-50} maxVal={110} scaleLabels={["-50", "0", "50", "110"]} />
      </div>
      <div className="img-panel" style={{marginTop:0}}>
        <div className="pt-tabs-row">
          <div className="pt-tab active">Pan&Tilt P1</div>
          <div className="pt-tab">Pan &Tilt S1</div>
          <div className="pt-tab">Pan& Tilt S2</div>
        </div>
        <div style={{fontSize:'14px', fontWeight:800, color:'var(--color-text)', padding:'10px 0 0 0', textAlign:'center'}}>PnT CTRL P1</div>
        <PanTiltPad panVal={pt.pan} tiltVal={pt.tilt} />
      </div>
    </div>
  );

  return (
    <div className="main-content-wrapper">
      <div className="main-content">
        <div className="img-layout-row">
          <div className="img-col-main">
            {ledSection}
            {camSection}
          </div>
          {rightCol}
        </div>
        <Sidebar appState={appState} apiCall={apiCall} />
      </div>
    </div>
  );
}

export function SensorsLayout({ appState, apiCall }) {
  const s = appState;
  const sens = s.sensors;
  const sci = sens.scientific;
  const surf = sens.surface_ins;
  const ssg = sens.subsea_gps;
  const redt = sens.redt_depth;

  return (
    <div className="main-content-wrapper">
      <div className="main-content">
        <div className="sens-dashboard">

          {/* TOP ROW: toggles | sci table | right stack */}
          <div className="sens-top-area">

            {/* Port + Starboard toggle columns */}
            <div className="sens-toggles-pair">
              <div className="sens-panel">
                <div className="sens-panel-title">Port side</div>
                <SensorToggleBlock label="Depth Sensor Pri" isOn={sens.toggles.depth_sensor_pri} toggleUrl="/api/toggle/sensors.toggles.depth_sensor_pri" />
                <SensorToggleBlock label="INS" isOn={sens.toggles.ins} toggleUrl="/api/toggle/sensors.toggles.ins" />
                <SensorToggleBlock label="CTDO" isOn={sens.toggles.ctdo} toggleUrl="/api/toggle/sensors.toggles.ctdo" />
                <SensorToggleBlock label="DVL" isOn={sens.toggles.dvl} toggleUrl="/api/toggle/sensors.toggles.dvl" />
                <SensorToggleBlock label="Multibeam Sonar" isOn={sens.toggles.multibeam_sonar} toggleUrl="/api/toggle/sensors.toggles.multibeam_sonar" />
              </div>
              <div className="sens-panel">
                <div className="sens-panel-title">Starboard</div>
                <SensorToggleBlock label="Altimeter" isOn={sens.toggles.altimeter} toggleUrl="/api/toggle/sensors.toggles.altimeter" />
                <SensorToggleBlock label="Dissolved O2" isOn={sens.toggles.dissolved_o2} toggleUrl="/api/toggle/sensors.toggles.dissolved_o2" />
                <SensorToggleBlock label="CTDO_S" isOn={sens.toggles.ctdo_s} toggleUrl="/api/toggle/sensors.toggles.ctdo_s" />
                <SensorToggleBlock label="MBS" isOn={sens.toggles.mbs} toggleUrl="/api/toggle/sensors.toggles.mbs" />
                <SensorToggleBlock label="IMG SONAR" isOn={sens.toggles.img_sonar} toggleUrl="/api/toggle/sensors.toggles.img_sonar" />
              </div>
            </div>

            {/* Scientific Sensors Table */}
            <div className="sci-sens-table">
              <div className="sci-sens-top">
                <span className="sci-sens-header-sub">CTDO Sensor</span>
                <span className="sci-sens-main-title">Scientific Sensors</span>
              </div>
              <div className="sci-sens-table-header">
                <span className="sci-sens-th"></span>
                <span className="sci-sens-th text-center">Port</span>
                <span className="sci-sens-th text-center">Stbd</span>
                <span className="sci-sens-th"></span>
              </div>
              <ScientificSensorRowItem label="Conductivity" portVal={sci.conductivity.port} stbdVal={sci.conductivity.stbd} unit="S/m" />
              <ScientificSensorRowItem label="Salinity" portVal={sci.salinity.port} stbdVal={sci.salinity.stbd} unit="PSU" />
              <ScientificSensorRowItem label="Water denisty" portVal={sci.water_density.port} stbdVal={sci.water_density.stbd} unit="kg/m3" />
              <ScientificSensorRowItem label="Turbidity" portVal={sci.turbidity.port} stbdVal={sci.turbidity.stbd} unit="NTU" />
              <ScientificSensorRowItem label="pH" portVal={sci.ph.port} stbdVal={sci.ph.stbd} unit="" />
              <ScientificSensorRowItem label="CTD Temp" portVal={sci.ctd_temp.port} stbdVal={sci.ctd_temp.stbd} unit="DegC" />
              <ScientificSensorRowItem label="Pressure" portVal={sci.pressure.port} stbdVal={sci.pressure.stbd} unit="" />
              <ScientificSensorRowItem label="Dissolved Oxygen" portVal={sci.dissolved_oxygen.port} stbdVal={sci.dissolved_oxygen.stbd} unit="uM" />
              <ScientificSensorRowItem label="ORP" portVal={sci.orp.port} stbdVal={sci.orp.stbd} unit="" />
            </div>

            {/* Right stack: Surface INS, SubSea GPS, Redt Depth */}
            <div className="sens-right-stack">
              <div className="sens-right-panel">
                <div className="sens-right-title">Surface INS</div>
                <SensorBoxMetric label="S_Roll" value={surf.s_roll} unit="deg" />
                <SensorBoxMetric label="S_Pitch" value={surf.s_pitch} unit="deg" />
                <SensorBoxMetric label="S_Heading" value={surf.s_heading} unit="deg" />
                <SensorBoxMetric label="S_Speed1" value={surf.s_speed1} unit="m/s" />
                <SensorBoxMetric label="S_Speed2" value={surf.s_speed2} unit="m/s" />
                <SensorBoxMetric label="S_Speed3" value={surf.s_speed3} unit="m/s" />
                <SensorBoxMetric label="S_Latitude" value={surf.s_latitude} unit="" />
                <SensorBoxMetric label="S_Longitude" value={surf.s_longitude} unit="" />
              </div>
              <div className="sens-right-panel sens-subsea">
                <div className="sens-right-title">SubSea GPS</div>
                <SensorBoxMetric label="GPS Latitude" value={ssg.gps_latitude} unit="" />
                <SensorBoxMetric label="GPS Longitude" value={ssg.gps_longitude} unit="" />
              </div>
              <div className="sens-right-panel sens-redt">
                <div className="sens-right-title">Redt Depth Sensor</div>
                <SensorBoxMetric label="S_Depth" value={redt.s_depth} unit="m" />
              </div>
            </div>

          </div>{/* end sens-top-area */}

          {/* BOTTOM ROW: WI_P | Ins_P | Sensor Alarm | Warning Panel | Ins_S | WI_S */}
          <div className="sens-bottom-area">

            <div className="sens-panel sens-panel-clear">
              <div className="sens-panel-title">Water Ingress_p</div>
              <SensorLedStatus label="WI PS_P" isOn={sens.indicators.wi_ps_p} />
              <SensorLedStatus label="WI IDE_P" isOn={sens.indicators.wi_ide_p} />
              <SensorLedStatus label="WI PDE_P" isOn={sens.indicators.wi_pde_p} />
            </div>

            <div className="sens-panel sens-panel-clear">
              <div className="sens-panel-title">Insulation_P</div>
              <SensorLedStatus label="IR UB_P" isOn={sens.indicators.ir_ub_p} />
              <SensorLedStatus label="IR IDE_P" isOn={sens.indicators.ir_ide_p} />
              <SensorLedStatus label="IR PDE_P INT" isOn={sens.indicators.ir_pde_p_int} />
              <SensorLedStatus label="IR PDE_P EXT" isOn={sens.indicators.ir_pde_p_ext} />
              <SensorLedStatus label="IR PDE 148_P" isOn={sens.indicators.ir_pde_148_p} />
            </div>

            <div className="sens-panel sens-panel-clear">
              <div className="sens-panel-title">Sensor Alarm</div>
              <AlarmLedStatus label="O2 alarm" isOn={sens.indicators.o2_alarm} />
              <AlarmLedStatus label="Co2 alarm" isOn={sens.indicators.co2_alarm} />
              <AlarmLedStatus label="Pressure 2" isOn={sens.indicators.pressure_2} />
              <AlarmLedStatus label="Altitude_P" isOn={sens.indicators.altitude_p} />
              <AlarmLedStatus label="Depth alarm" isOn={sens.indicators.depth_alarm} />
            </div>

            <div className="warning-panel-section">
              <div className="warning-panel-title">Warning and Alarm Panel</div>
              <div className="warning-panel-content">
                <BuzzerPanel active={sens.buzzer_active} />
                <div className="warning-toggles">
                  <SensorToggleBlock label="Laser Light 2" isOn={sens.toggles.laser_light_2} toggleUrl="/api/toggle/sensors.toggles.laser_light_2" />
                  <SensorToggleBlock label="Pan and Tilt P1" isOn={sens.toggles.pan_and_tilt_p1} toggleUrl="/api/toggle/sensors.toggles.pan_and_tilt_p1" />
                  <SensorToggleBlock label="Pan and Tilt S1" isOn={sens.toggles.pan_and_tilt_s1} toggleUrl="/api/toggle/sensors.toggles.pan_and_tilt_s1" />
                  <SensorToggleBlock label="Pan and Tilt S2" isOn={sens.toggles.pan_and_tilt_s2} toggleUrl="/api/toggle/sensors.toggles.pan_and_tilt_s2" />
                </div>
              </div>
            </div>

            <div className="sens-panel sens-panel-clear">
              <div className="sens-panel-title">Insulation_S</div>
              <SensorLedStatus label="IR UB_S" isOn={sens.indicators.ir_ub_s} />
              <SensorLedStatus label="IR IDE_S" isOn={sens.indicators.ir_ide_s} />
              <SensorLedStatus label="IR PDE_S INT" isOn={sens.indicators.ir_pde_s_int} />
              <SensorLedStatus label="IR PDE_S EXT" isOn={sens.indicators.ir_pde_s_ext} />
              <SensorLedStatus label="IR PDE 148_S" isOn={sens.indicators.ir_pde_148_s} />
            </div>

            <div className="sens-panel sens-panel-clear">
              <div className="sens-panel-title">Water Ingress_S</div>
              <SensorLedStatus label="WI PS_S" isOn={sens.indicators.wi_ps_s} />
              <SensorLedStatus label="WI IDE_S" isOn={sens.indicators.wi_ide_s} />
              <SensorLedStatus label="WI PDE_S" isOn={sens.indicators.wi_pde_s} />
            </div>

          </div>{/* end sens-bottom-area */}

        </div>
        <Sidebar appState={appState} apiCall={apiCall} />
      </div>
    </div>
  );
}

export function LoggingLayout({ appState, apiCall }) {
  const s = appState;
  const logState = s.logging;
  const t = logState.toggles;

  return (
    <div className="main-content-wrapper">
      <div className="main-content">
        <div className="logging-dashboard">
          <div className="logging-tables-row">
            <LogTable title="Event Logging" isEvent={true} rows={logState.events} />
            <LogTable title="Error Logging" isEvent={false} rows={logState.errors} />
          </div>
          <div className="log-toggles-panel">
            <div className="log-toggles-left">
              <div className="log-tog-col">
                <HorizontalToggle label="148 V LED S1" isOn={t.led_s1_148v} toggleUrl="/api/toggle/logging.toggles.led_s1_148v" />
                <HorizontalToggle label="148 V LED S2" isOn={t.led_s2_148v} toggleUrl="/api/toggle/logging.toggles.led_s2_148v" />
              </div>
              <div className="log-tog-col">
                <HorizontalToggle label="148 V LED S3" isOn={t.led_s3_148v} toggleUrl="/api/toggle/logging.toggles.led_s3_148v" />
                <HorizontalToggle label="148 V LED S4" isOn={t.led_s4_148v} toggleUrl="/api/toggle/logging.toggles.led_s4_148v" />
              </div>
              <div className="log-tog-col">
                <HorizontalToggle label="148 V LED P1" isOn={t.led_p1_148v} toggleUrl="/api/toggle/logging.toggles.led_p1_148v" />
                <HorizontalToggle label="148 V LED P2" isOn={t.led_p2_148v} toggleUrl="/api/toggle/logging.toggles.led_p2_148v" />
              </div>
              <div className="log-tog-col">
                <HorizontalToggle label="148 V LED P3" isOn={t.led_p3_148v} toggleUrl="/api/toggle/logging.toggles.led_p3_148v" />
                <HorizontalToggle label="148 V LED P4" isOn={t.led_p4_148v} toggleUrl="/api/toggle/logging.toggles.led_p4_148v" />
              </div>
            </div>
            <div className="log-toggles-right">
              <div className="log-tog-group">
                <HorizontalToggle label="Trim_S" isOn={t.trim_s} toggleUrl="/api/toggle/logging.toggles.trim_s" />
                <RedSignalIndicator label="Trim_S signal" isOn={t.trim_s_signal} />
              </div>
              <div className="log-tog-group-center">
                <HorizontalToggle label="PDE_P 1" isOn={t.pde_p_1} toggleUrl="/api/toggle/logging.toggles.pde_p_1" />
                <RedSignalIndicator label="PDE_P signal" isOn={t.pde_p_signal} />
                <HorizontalToggle label="PDE_P 2" isOn={t.pde_p_2} toggleUrl="/api/toggle/logging.toggles.pde_p_2" />
              </div>
              <div className="log-tog-group">
                <HorizontalToggle label="Trim_P" isOn={t.trim_p} toggleUrl="/api/toggle/logging.toggles.trim_p" />
                <RedSignalIndicator label="Trim_P signal" isOn={t.trim_p_signal} />
              </div>
            </div>
          </div>
        </div>
        <Sidebar appState={appState} apiCall={apiCall} />
      </div>
    </div>
  );
}

export function StatusLayout({ appState, apiCall }) {
  const s = appState;
  const st = s.status;

  return (
    <div className="main-content-wrapper">
      <div className="main-content">
        <div className="status-dashboard">
          <StatusChartRowComponent selectedOption={st.chart1_selection} yLabels={[-45, -20, 0, 20, 45]} xLabels={[0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 57]} />
          <StatusChartRowComponent selectedOption={st.chart2_selection} yLabels={[-15, -10, 0, 10, 15]} xLabels={[0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 57]} />
        </div>
        <Sidebar appState={appState} apiCall={apiCall} />
      </div>
    </div>
  );
}

export function Kwh50Layout({ appState, apiCall }) {
  const s = appState;
  const kwh = s.kwh;
  
  const portBats = [kwh.port.bat1, kwh.port.bat2, kwh.port.bat3, kwh.port.bat4, kwh.port.bat5];
  const stbdBats = [kwh.stbd.bat6, kwh.stbd.bat7, kwh.stbd.bat8, kwh.stbd.bat9, kwh.stbd.bat10];
  const pg = kwh.port_gauges;
  const sg = kwh.stbd_gauges;

  return (
    <div className="main-content-wrapper">
      <div className="main-content">
        <div className="kwh-dashboard">
          <div className="kwh-main-title">BATTERY 50 kWh STATUS</div>
          <div className="kwh-top-section">
            <KwhDataGrid titleSub="port side" colHeaders={["BAT 1", "BAT 2", "BAT 3", "BAT 4", "BAT 5"]} batteries={portBats} />
            <div className="kwh-center-toggles">
              <div className="kwh-sig-row">
                <div className="kwh-sig-label">VBS_Enable_sig</div>
                <div className={`kwh-sig-dot ${kwh.vbs_enable_sig ? 'signal-dot-on' : 'signal-dot-off'}`}></div>
              </div>
              <div className="kwh-sig-row">
                <div className="kwh-sig-label">Trim_Enable_sig</div>
                <div className={`kwh-sig-dot ${kwh.trim_enable_sig ? 'signal-dot-on' : 'signal-dot-off'}`}></div>
              </div>
              <ToggleSwitch label="Trim_Enable" isOn={kwh.trim_enable} onToggle={() => apiCall('/api/toggle/kwh.trim_enable')} />
            </div>
            <KwhDataGrid titleSub="starboard side" colHeaders={["BAT 6", "BAT 7", "BAT 8", "BAT 9", "BAT 10"]} batteries={stbdBats} />
          </div>
          <div className="kwh-bottom-section">
            <div className="kwh-gauges-row">
              <KwhVerticalGauge label="BAT VOL" value={pg.vol} minVal={100} maxVal={170} scaleLabels={[100, 120, 140, 160, 170]} />
              <KwhVerticalGauge label="BAT TEMP" value={pg.temp} minVal={0} maxVal={50} scaleLabels={[0, 25, 50]} />
              <KwhVerticalGauge label="BAT SOC" value={pg.soc} minVal={0} maxVal={200} scaleLabels={[0, 50, 100, 150, 200]} />
              <KwhVerticalGauge label="BAT CUR" value={pg.cur} minVal={0} maxVal={100} scaleLabels={[0, 25, 50, 75, 100]} />
            </div>
            <div className="kwh-bottom-center">
              <ToggleSwitch label="VBS_Enable" isOn={kwh.vbs_enable} onToggle={() => apiCall('/api/toggle/kwh.vbs_enable')} />
            </div>
            <div className="kwh-gauges-row">
              <KwhVerticalGauge label="BAT VOL 2" value={sg.vol} minVal={100} maxVal={170} scaleLabels={[100, 120, 140, 160, 170]} />
              <KwhVerticalGauge label="BAT TEMP 2" value={sg.temp} minVal={0} maxVal={50} scaleLabels={[0, 25, 50]} />
              <KwhVerticalGauge label="BAT SOC 2" value={sg.soc} minVal={0} maxVal={200} scaleLabels={[0, 50, 100, 150, 200]} />
              <KwhVerticalGauge label="BAT CUR 2" value={sg.cur} minVal={0} maxVal={100} scaleLabels={[0, 25, 50, 75, 100]} />
            </div>
          </div>
        </div>
        <Sidebar appState={appState} apiCall={apiCall} />
      </div>
    </div>
  );
}

export function MccLayout({ appState, apiCall }) {
  const s = appState;
  const mcc = s.mcc;
  const ind = mcc.indicators;
  const st = mcc.status;

  return (
    <div className="main-content-wrapper">
      <div className="main-content">
        <div className="mcc-panel">
          <div className="mcc-panel-title">Data from MCC</div>
          <div className="mcc-grid">
            <div className="mcc-col">
              <MccIndicator label="CO2 Sensor-D" isOn={ind.co2_sensor_d} />
              <MccIndicator label="Trim System-D" isOn={ind.trim_system_d} />
              <MccIndicator label="Magnetometer-D" isOn={ind.magnetometer_d} />
              <MccIndicator label="Conduct & Temp-D" isOn={ind.conduct_temp_d} />
              <MccIndicator label="Thruster_T1-D" isOn={ind.thruster_t1_d} />
              <MccIndicator label="Thruster_T2-D" isOn={ind.thruster_t2_d} />
              <MccIndicator label="Thruster_En_P-D" isOn={ind.thruster_en_p_d} />
              <MccIndicator label="Thruster_En_S-D" isOn={ind.thruster_en_s_d} />
              <MccIndicator label="4K camera P-D" isOn={ind.camera_4k_p_d} />
              <MccIndicator label="HD Camera P3-D" isOn={ind.hd_camera_p3_d} />
              <MccIndicator label="SD_Camera_P4-D" isOn={ind.sd_camera_p4_d} />
              <MccIndicator label="CTDO-D" isOn={ind.ctdo_d} />
            </div>
            <div className="mcc-col">
              <MccIndicator label="Forwd_Low-D" isOn={ind.forwd_low_d} />
              <MccIndicator label="Forwd_Medi-D" isOn={ind.forwd_medi_d} />
              <MccIndicator label="Lateral_Low-D" isOn={ind.lateral_low_d} />
              <MccIndicator label="Lateral_Medi-D" isOn={ind.lateral_medi_d} />
              <MccIndicator label="Verti_Low-D" isOn={ind.verti_low_d} />
              <MccIndicator label="Verti_Medi-D" isOn={ind.verti_medi_d} />
              <MccIndicator label="Heading_Low-D" isOn={ind.heading_low_d} />
              <MccIndicator label="Heading_Medi-D" isOn={ind.heading_medi_d} />
              <MccIndicator label="4K camera S-D" isOn={ind.camera_4k_s_d} />
              <MccIndicator label="HD Camera S1-D" isOn={ind.hd_camera_s1_d} />
              <MccIndicator label="SD Camera S4-D" isOn={ind.sd_camera_s4_d} />
              <MccIndicator label="Dissolved O2-D" isOn={ind.dissolved_o2_d} />
              <div className="mcc-disabled-wrap">
                <div className="mcc-disabled-label">Data Receiving Mode</div>
                <div className="mcc-disabled-box">{st.data_receiving_mode}</div>
              </div>
            </div>
            <div className="mcc-col">
              <MccIndicator label="LED Light S2-D" isOn={ind.led_light_s2_d} />
              <MccIndicator label="LED Light S3-D" isOn={ind.led_light_s3_d} />
              <MccIndicator label="LED Light S4-D" isOn={ind.led_light_s4_d} />
              <MccIndicator label="INS-D" isOn={ind.ins_d} />
              <MccIndicator label="DVL-D" isOn={ind.dvl_d} />
              <MccIndicator label="Depth Sensor Pri-D" isOn={ind.depth_sensor_pri_d} />
              <MccIndicator label="Altimeter-D" isOn={ind.altimeter_d} />
              <MccIndicator label="LED Light P2-D" isOn={ind.led_light_p2_d} />
              <MccIndicator label="LED Light P3-D" isOn={ind.led_light_p3_d} />
              <MccIndicator label="LED Light P4-D" isOn={ind.led_light_p4_d} />
            </div>
            <div className="mcc-col mcc-col-center">
              <div className="mcc-center-top">
                <MccStatusBox label="Modem Ready Status" value={st.modem_ready_status} bgColorCls="mcc-bg-green" />
                <MccStatusBox label="Read/ Write" value={st.read_write} bgColorCls="mcc-bg-gray" />
                <MccStatusBox label="Data Sending Mode" value={st.data_sending_mode} bgColorCls="mcc-bg-gray" />
              </div>
              <div className="mcc-center-toggle">
                <ToggleSwitch label="Acoustic comm Auto" isOn={st.acoustic_comm_auto} onToggle={() => apiCall('/api/toggle/mcc.status.acoustic_comm_auto')} />
              </div>
              <div className="mcc-center-msg">
                <div className="mcc-msg-title">MCC message</div>
                <div className="mcc-msg-box">{st.mcc_message}</div>
                <div className="mcc-msg-title">Pilot message</div>
                <div className="mcc-msg-box">{st.pilot_message}</div>
              </div>
              <div className="mcc-center-ship">
                <MccShipData label="Ship Latitude" value={st.ship_latitude} />
                <MccShipData label="Ship Longitude" value={st.ship_longitude} />
                <MccShipData label="Ship Heading" value={st.ship_heading} />
                <MccShipData label="Ship Time" value={st.ship_time} />
              </div>
            </div>
            <div className="mcc-col mcc-col-right">
              <MccRadioGroup selectedVal={st.power_status} />
              <div className="mcc-crew-group">
                <MccCrewStatus label="PILOT" isOk={st.pilot_ok} />
                <MccCrewStatus label="CO-PILOT" isOk={st.copilot_ok} />
                <MccCrewStatus label="OBSERVER" isOk={st.observer_ok} />
              </div>
              <MccPowerDropdown val={st.power_dropdown} />
              <div className="mcc-right-toggle">
                <ToggleSwitch label="data mode" isOn={st.data_mode} onToggle={() => apiCall('/api/toggle/mcc.status.data_mode')} />
              </div>
            </div>
          </div>
        </div>
        <Sidebar appState={appState} apiCall={apiCall} />
      </div>
    </div>
  );
}
