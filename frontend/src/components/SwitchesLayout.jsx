import React from "react";
import {
  MetalSwitch,
  RotarySwitch,
  KnobToggleSwitch,
  CircuitBreaker,
  LcdScreen,
  BlackPushButton,
  MastervoltDisplay,
  YellowLedDisplay,
  DigitalVoltageDisplay,
  AxisCamera,
  AlarmIndicator,
  Toggle3Pos,
  Buzzer,
} from "./Controls";

const tc = (
  labelTop,
  labelBottom,
  isOn,
  onToggle,
  idKey,
  color = "black",
  isRedBox = false,
  showLed = false,
) => (
  <div
    style={{
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      margin: "4px",
      border: isRedBox ? "2px solid red" : "none",
      padding: isRedBox ? "4px" : "0",
    }}
  >
    <MetalSwitch
      isOn={isOn}
      onToggle={onToggle}
      idKey={idKey}
      label={labelTop || labelBottom}
      showLed={showLed}
    />
  </div>
);

// --- Port Side Layout ---
export function SwitchesPLayout({ appState, apiCall }) {
  const sw = appState.switches?.p || {};
  return (
    <div
      style={{
        padding: "20px",
        flex: 1,
        minHeight: 0,
        overflowY: "auto",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
      }}
    >
      <div className="screws" style={{ top: "10px", left: "10px" }}></div>
      <div className="screws" style={{ top: "10px", right: "10px" }}></div>

      <div style={{ display: "flex", gap: "80px", marginTop: "40px" }}>
        <RotarySwitch
          label={"Power Selection\nUB_P"}
          pos1Label="AB_P"
          pos2Label="24v PDE_P"
          value={sw.ab_p ? 2 : 1}
          onChange={() => apiCall("/api/toggle/switches.p.ab_p")}
        />
        <RotarySwitch
          label={"Power Selection\nEB_P"}
          pos1Label="E_BATT_P"
          pos2Label="UB_P"
          value={sw.e_batts ? 2 : 1}
          onChange={() => apiCall("/api/toggle/switches.p.e_batts")}
        />
      </div>

      <div
        style={{
          display: "flex",
          gap: "20px",
          marginTop: "40px",
          alignItems: "flex-start",
        }}
      >
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
          }}
        >
          <CircuitBreaker
            isOn={sw.ub_mcb}
            onToggle={() => apiCall("/api/toggle/switches.p.ub_mcb")}
          />
          <div className="tape-label-real" style={{ marginTop: "5px" }}>
            UB_P MCB
          </div>
        </div>
        <DigitalVoltageDisplay
          label="UB_P VOLTAGE"
          value={sw.ub_voltage || 22.4}
        />
        <MastervoltDisplay label="EB_P STATUS" value={sw.eb_b_status} />
        <YellowLedDisplay label="EB_P INSULATION" value={sw.ib_insulation} />
      </div>

      <div style={{ display: "flex", gap: "40px", marginTop: "20px" }}>
        <div style={{ display: "flex", flexDirection: "column", gap: "15px" }}>
          <div style={{ display: "flex", gap: "15px" }}>
            <BlackPushButton
              labelTop="NC"
              labelBottom="PDE_S_OLR_RESET"
              onClick={() => apiCall("/api/toggle/switches.p.pde_p_clr_rst")}
            />
            <BlackPushButton
              labelTop="NO"
              labelBottom="OIM_P_RESET"
              onClick={() => apiCall("/api/toggle/switches.p.oim_p_reset")}
            />
          </div>
          <div style={{ display: "flex", gap: "15px" }}>
            {tc("AB_P_BMS", "", sw.ab_p_bms, () =>
              apiCall("/api/toggle/switches.p.ab_p_bms"),
            )}
            {tc("AB_P", "", sw.ab_p_power, () =>
              apiCall("/api/toggle/switches.p.ab_p_power"),
            )}
            {tc("PDE_P_OIM", "", sw.pde_p_dim, () =>
              apiCall("/api/toggle/switches.p.pde_p_dim"),
            )}
          </div>
          <div style={{ display: "flex", gap: "15px" }}>
            {tc("IDE1_P", "", sw.ide_p_1, () =>
              apiCall("/api/toggle/switches.p.ide_p_1"),
            )}
            {tc("IDE2_P", "", sw.ide_2, () =>
              apiCall("/api/toggle/switches.p.ide_2"),
            )}
            {tc(
              "SPARE-2\nKEEP IN ON",
              "",
              sw.spare_2,
              () => apiCall("/api/toggle/switches.p.spare_2"),
              null,
              "black",
              true,
            )}
          </div>
          <div style={{ display: "flex", gap: "15px" }}>
            <div
              style={{
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
              }}
            >
              <div
                style={{
                  color: "#ff1493",
                  fontWeight: "bold",
                  fontSize: "24px",
                  marginBottom: "5px",
                }}
              >
                OIM
              </div>
              {tc("", "", sw.oim_p, () =>
                apiCall("/api/toggle/switches.p.oim_p"),
              )}
            </div>
            <div
              style={{
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
              }}
            >
              <div
                style={{
                  color: "red",
                  fontWeight: "bold",
                  fontSize: "12px",
                  marginBottom: "5px",
                }}
              >
                Spare
              </div>
              {tc("", "", sw.spare_p, () =>
                apiCall("/api/toggle/switches.p.spare_p"),
              )}
            </div>
            <div
              style={{
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
              }}
            >
              <div
                style={{
                  color: "#ff1493",
                  fontWeight: "bold",
                  fontSize: "24px",
                  marginBottom: "5px",
                }}
              >
                Wago
              </div>
              {tc("", "", sw.wago_p, () =>
                apiCall("/api/toggle/switches.p.wago_p"),
              )}
            </div>
          </div>
        </div>

        <div style={{ marginTop: "20px" }}>
          <LcdScreen />
        </div>
      </div>

      <div style={{ display: "flex", gap: "10px", marginTop: "10px" }}>
        {tc(
          "SECONDARY\nPRIMARY\nPDE-P\n24V CONTROL",
          "",
          sw.pde_p_24v,
          () => apiCall("/api/toggle/switches.p.pde_p_24v"),
        )}
        {tc("MB_P_BMS", "", sw.mb_p_bms, () =>
          apiCall("/api/toggle/switches.p.mb_p_bms"),
        )}
        {tc("MB_P1_EN", "", sw.mb_1, () =>
          apiCall("/api/toggle/switches.p.mb_1"),
        )}
        {tc("MB_P2_EN", "", sw.mb_2, () =>
          apiCall("/api/toggle/switches.p.mb_2"),
        )}
        {tc("MB_P3_EN", "", sw.mb_3, () =>
          apiCall("/api/toggle/switches.p.mb_3"),
        )}
        {tc("MB_P4_EN", "", sw.mb_4, () =>
          apiCall("/api/toggle/switches.p.mb_4"),
        )}
        {tc("MB_P5_EN", "", sw.mb_5, () =>
          apiCall("/api/toggle/switches.p.mb_5"),
        )}
        {tc(
          "PDE_P_OLR\n\nPDE_P_OLR\nSTATUS",
          "",
          sw.pde_p_olr,
          () => apiCall("/api/toggle/switches.p.pde_p_olr"),
          null,
          "black",
          false,
          true,
        )}
        {tc(
          "PDE_P_148\n\nPDE_P_148\nIN STATUS",
          "",
          sw.pde_p_148,
          () => apiCall("/api/toggle/switches.p.pde_p_148"),
          null,
          "black",
          false,
          true,
        )}
        {tc(
          "PDE_P_24V_INT\n\nPDE_P_PL\nSTATUS",
          "",
          sw.pde_p_24v_main,
          () => apiCall("/api/toggle/switches.p.pde_p_24v_main"),
          null,
          "black",
          false,
          true,
        )}
      </div>

      <div
        style={{
          width: "100%",
          height: "1px",
          background: "#333",
          margin: "20px 0",
          boxShadow: "0 1px 1px #000",
        }}
      ></div>

      <div
        style={{
          fontSize: "16px",
          fontWeight: "bold",
          color: "#000",
          fontFamily: "monospace",
        }}
      >
        SERVICE DROP WEIGHT SWITCHES
      </div>
      <div
        style={{
          display: "flex",
          gap: "40px",
          marginTop: "10px",
          justifyContent: "center",
          width: "100%",
        }}
      >
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
          }}
        >
          <div
            style={{
              display: "flex",
              gap: "12px",
              flexWrap: "nowrap",
              marginTop: "10px",
            }}
          >
            {[1, 2, 3, 4, 5].map((i) => (
              <div
                key={`sdwp_${i}`}
                style={{
                  display: "flex",
                  flexDirection: "column",
                  alignItems: "center",
                }}
              >
                <div
                  style={{
                    color: "#1a5f9a",
                    fontWeight: "bold",
                    fontSize: "22px",
                    marginBottom: "2px",
                  }}
                >
                  {i === 5 ? `SDW5_P_100kg` : `SDW${i}_P_50kg`}
                </div>
                <Toggle3Pos
                  labelTop={`PC ON`}
                  labelCenter={`OFF`}
                  labelBottom={`SC ON`}
                  value={sw[`sdwp_${i}`] ? 1 : sw[`sdws_${i}`] ? -1 : 0}
                  onToggle={() => {
                    const p = sw[`sdwp_${i}`];
                    const s = sw[`sdws_${i}`];
                    if (!p && !s) {
                      apiCall(`/api/toggle/switches.p.sdwp_${i}`);
                    } else if (p && !s) {
                      apiCall(`/api/toggle/switches.p.sdwp_${i}`);
                      apiCall(`/api/toggle/switches.p.sdws_${i}`);
                    } else if (!p && s) {
                      apiCall(`/api/toggle/switches.p.sdws_${i}`);
                    } else {
                      apiCall(`/api/toggle/switches.p.sdwp_${i}`);
                      apiCall(`/api/toggle/switches.p.sdws_${i}`);
                    }
                  }}
                />
              </div>
            ))}
            {[1, 2, 3, 4, 5].map((i) => {
              const sdwId = i + 5;
              return (
                <div
                  key={`sdws_${sdwId}`}
                  style={{
                    display: "flex",
                    flexDirection: "column",
                    alignItems: "center",
                  }}
                >
                  <div
                    style={{
                      color: "#ff1493",
                      fontWeight: "bold",
                      fontSize: "22px",
                      marginBottom: "2px",
                    }}
                  >
                    {i === 5 ? `SDW5_S_100kg` : `SDW${i}_S_50kg`}
                  </div>
                  <Toggle3Pos
                    labelTop={`PC ON`}
                    labelCenter={`OFF`}
                    labelBottom={`SC ON`}
                    value={
                      sw[`sdws_${sdwId}`] ? 1 : sw[`sdwp_${sdwId}`] ? -1 : 0
                    }
                    onToggle={() => {
                      const p = sw[`sdwp_${sdwId}`];
                      const s = sw[`sdws_${sdwId}`];
                      if (!p && !s) {
                        apiCall(`/api/toggle/switches.p.sdws_${sdwId}`);
                      } else if (!p && s) {
                        apiCall(`/api/toggle/switches.p.sdws_${sdwId}`);
                        apiCall(`/api/toggle/switches.p.sdwp_${sdwId}`);
                      } else if (p && !s) {
                        apiCall(`/api/toggle/switches.p.sdwp_${sdwId}`);
                      } else {
                        apiCall(`/api/toggle/switches.p.sdws_${sdwId}`);
                        apiCall(`/api/toggle/switches.p.sdwp_${sdwId}`);
                      }
                    }}
                  />
                </div>
              );
            })}
          </div>
        </div>
      </div>

      <div
        style={{
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          gap: "30px",
          marginTop: "20px",
          width: "100%",
        }}
      >
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
          }}
        >
          <div
            style={{ color: "#00cc66", fontWeight: "bold", fontSize: "10px" }}
          >
            SDW MASTER SWITCH_PORT
          </div>
          <div
            style={{
              color: "#ff1493",
              fontWeight: "bold",
              fontSize: "24px",
              marginTop: "2px",
            }}
          >
            PWR_P
          </div>
          <Toggle3Pos
            value={sw.sdw_master_p ? 1 : sw.sdw_master_s ? -1 : 0}
            onToggle={() => apiCall("/api/toggle/switches.p.sdw_master_p")}
          />
          <div
            style={{
              color: "#ff1493",
              fontWeight: "bold",
              fontSize: "24px",
              marginTop: "2px",
            }}
          >
            PWR_S
          </div>
        </div>
        <div
          style={{
            fontSize: "36px",
            fontWeight: "bold",
            color: "#ff1493",
            fontFamily: "monospace",
          }}
        >
          SERVICE DROP WEIGHT SWITCHES
        </div>
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
          }}
        >
          <div
            style={{ color: "#00cc66", fontWeight: "bold", fontSize: "10px" }}
          >
            SDW MASTER SWITCH_STBD
          </div>
          <div
            style={{
              color: "#ff1493",
              fontWeight: "bold",
              fontSize: "24px",
              marginTop: "2px",
            }}
          >
            PWR_S
          </div>
          <Toggle3Pos
            value={sw.sdw_master_stbd_s ? 1 : sw.sdw_master_stbd_p ? -1 : 0}
            onToggle={() => apiCall("/api/toggle/switches.p.sdw_master_stbd")}
          />
          <div
            style={{
              color: "#ff1493",
              fontWeight: "bold",
              fontSize: "24px",
              marginTop: "2px",
            }}
          >
            PWR_P
          </div>
        </div>
      </div>

      <div
        style={{
          position: "absolute",
          bottom: "20px",
          left: "20px",
          background: "#ff00ff",
          color: "#000",
          padding: "4px 8px",
          fontWeight: "bold",
          fontSize: "28px",
          border: "2px solid #000",
        }}
      >
        NAVIGATION PC
      </div>
    </div>
  );
}

// --- Starboard Side Layout ---
export function SwitchesSLayout({ appState, apiCall }) {
  const sw = appState.switches?.s || {};
  const swP = appState.switches?.p || {};
  return (
    <div
      style={{
        padding: "20px",
        flex: 1,
        minHeight: 0,
        overflowY: "auto",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
      }}
    >
      <div className="screws" style={{ top: "10px", left: "10px" }}></div>
      <div className="screws" style={{ top: "10px", right: "10px" }}></div>

      <div style={{ display: "flex", gap: "80px", marginTop: "40px" }}>
        <RotarySwitch
          label={"Power Selection\nEB_S"}
          pos1Label="E_BATT_S"
          pos2Label="UB_S"
          value={sw.e_batt_s ? 2 : 1}
          onChange={() => apiCall("/api/toggle/switches.s.e_batt_s")}
        />
        <RotarySwitch
          label={"Power Selection\nUB_S"}
          pos1Label="AB_S"
          pos2Label="24v_PDE_S"
          value={sw.ab_s ? 2 : 1}
          onChange={() => apiCall("/api/toggle/switches.s.ab_s")}
        />
      </div>

      <div
        style={{
          display: "flex",
          gap: "20px",
          marginTop: "40px",
          alignItems: "flex-start",
        }}
      >
        <YellowLedDisplay label="EB_S INSULATION" value={sw.eb_s_insulation} />
        <MastervoltDisplay label="EB_S STATUS" value={sw.eb_s_status} />
        <DigitalVoltageDisplay
          label="UB_S_VOLTAGE"
          value={sw.ub_voltage || 22.345}
        />
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
          }}
        >
          <CircuitBreaker
            isOn={sw.ub_mcb}
            onToggle={() => apiCall("/api/toggle/switches.s.ub_mcb")}
          />
          <div className="tape-label-real" style={{ marginTop: "5px" }}>
            UB_S MCB
          </div>
        </div>
      </div>

      <div style={{ display: "flex", gap: "40px", marginTop: "20px" }}>
        <div style={{ marginTop: "20px" }}>
          <LcdScreen />
        </div>

        <div style={{ display: "flex", flexDirection: "column", gap: "15px" }}>
          <div style={{ display: "flex", gap: "15px" }}>
            <BlackPushButton
              labelTop=""
              labelBottom="PDE_S_OLR_RESET"
              onClick={() => apiCall("/api/toggle/switches.s.pde_s_olr_rst")}
            />
            <BlackPushButton
              labelTop=""
              labelBottom="OIM_S_RESET"
              onClick={() => apiCall("/api/toggle/switches.s.oim_s_reset")}
            />
          </div>
          <div style={{ display: "flex", gap: "15px" }}>
            {tc("AB_S_BMS", "", sw.ab_s_bms, () =>
              apiCall("/api/toggle/switches.s.ab_s_bms"),
            )}
            {tc("AB_S", "", sw.ab_s_power, () =>
              apiCall("/api/toggle/switches.s.ab_s_power"),
            )}
            {tc("PDE_S_OIM", "", sw.pde_s_oim, () =>
              apiCall("/api/toggle/switches.s.pde_s_oim"),
            )}
          </div>
          <div style={{ display: "flex", gap: "15px" }}>
            {tc(
              "SPARE-2\nKEEP IN ON",
              "",
              sw.spare_2,
              () => apiCall("/api/toggle/switches.s.spare_2"),
              null,
              "black",
              true,
            )}
            {tc("IDE2", "", sw.ide_2, () =>
              apiCall("/api/toggle/switches.s.ide_2"),
            )}
            {tc("IDE1_S", "", sw.ide_s_1, () =>
              apiCall("/api/toggle/switches.s.ide_s_1"),
            )}
          </div>
          <div style={{ display: "flex", gap: "15px" }}>
            {tc("Wago", "", sw.wago, () => apiCall("/api/toggle/switches.s.wago"))}
            {tc("XX", "", sw.xx, () => apiCall("/api/toggle/switches.s.xx"))}
            {tc("OIM", "", sw.oim, () => apiCall("/api/toggle/switches.s.oim"))}
          </div>
        </div>
      </div>

      <div style={{ display: "flex", gap: "10px", marginTop: "40px", justifyContent: "space-between" }}>
        {tc(
          "SECONDARY\nPWR_S",
          "PRIMARY PDE-S\n24V CONTROL",
          sw.secondary,
          () => apiCall("/api/toggle/switches.s.secondary"),
        )}
        {tc("MB_S_BMS", "", sw.mb_s_bms, () =>
          apiCall("/api/toggle/switches.s.mb_s_bms"),
        )}
        {tc("MB_S_1", "", sw.mb_s_1, () =>
          apiCall("/api/toggle/switches.s.mb_s_1"),
        )}
        {tc("MB_S_2", "", sw.mb_s_2, () =>
          apiCall("/api/toggle/switches.s.mb_s_2"),
        )}
        {tc("MB_S_3", "", sw.mb_s_3, () =>
          apiCall("/api/toggle/switches.s.mb_s_3"),
        )}
        {tc("MB_S_4", "", sw.mb_s_4, () =>
          apiCall("/api/toggle/switches.s.mb_s_4"),
        )}
        {tc("MB_S_5", "", sw.mb_s_5, () =>
          apiCall("/api/toggle/switches.s.mb_s_5"),
        )}
        {tc(
          "PDE-S-OLR",
          "PDE-S OLR\nSTATUS",
          sw.pde_s_olr,
          () => apiCall("/api/toggle/switches.s.pde_s_olr"),
          null,
          "black",
          false,
          true,
        )}
        {tc(
          "MB_S-PDE_S",
          "PDE-S 148V\nIN STATUS",
          sw.mb_s_pde_s,
          () => apiCall("/api/toggle/switches.s.mb_s_pde_s"),
          null,
          "black",
          false,
          true,
        )}
        {tc(
          "24_MAIN_S",
          "PDE-S PL\nSTATUS",
          sw.main_24_s,
          () => apiCall("/api/toggle/switches.s.main_24_s"),
          null,
          "black",
          false,
          true,
        )}
      </div>

      <div
        style={{
          width: "100%",
          height: "1px",
          background: "#333",
          margin: "20px 0",
          boxShadow: "0 1px 1px #000",
        }}
      ></div>

      <div
        style={{
          fontSize: "36px",
          fontWeight: "bold",
          color: "#ff1493",
          fontFamily: "sans-serif",
        }}
      >
        General Control Switch
      </div>
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          gap: "20px",
          marginTop: "10px",
        }}
      >
        <div
          style={{
            display: "flex",
            gap: "15px",
            flexWrap: "wrap",
            justifyContent: "center",
          }}
        >
          {tc("INT_LED_P", "", swP.int_led_p, () =>
            apiCall("/api/toggle/switches.p.int_led_p"),
          )}
          {tc("UW_LED_S\nUW_CAM_S", "", sw.uw_camera_s, () =>
            apiCall("/api/toggle/switches.s.uw_camera_s"),
          )}
          {tc("UW_LED_P\nUW_CAM_P", "", swP.uw_camera_p, () =>
            apiCall("/api/toggle/switches.p.uw_camera_p"),
          )}
          {tc("APS-2", "", sw.aps_2, () =>
            apiCall("/api/toggle/switches.s.aps_2"),
          )}
          {tc(
            "Joystick_P\nAPS1_P,GPS_P\nSurface INS_P",
            "",
            swP.joystick_enable,
            () => apiCall("/api/toggle/switches.p.joystick_enable"),
          )}
          {tc("EMG_LED_S", "", sw.emg_led_s, () =>
            apiCall("/api/toggle/switches.s.emg_led_s"),
          )}
          {tc("CO2_SCRUB_S\nPWR_S", "PWR_P", sw.co2_scrubber_s, () =>
            apiCall("/api/toggle/switches.s.co2_scrubber_s"),
          )}
          {tc("CO2_SCRUB_P\nPWR_P", "", swP.co2_scrubber_p, () =>
            apiCall("/api/toggle/switches.p.co2_scrubber_p"),
          )}
        </div>
        <div
          style={{
            display: "flex",
            gap: "15px",
            flexWrap: "wrap",
            justifyContent: "center",
          }}
        >
          {tc("VHS_POW_S", "", sw.vhs_power_s, () =>
            apiCall("/api/toggle/switches.s.vhs_power_s"),
          )}
          {tc("VHS_POW_P", "", swP.vhs_power_p, () =>
            apiCall("/api/toggle/switches.p.vhs_power_p"),
          )}
          {tc("UWT\nPWR_P", "PWR_S", sw.uwt, () =>
            apiCall("/api/toggle/switches.s.uwt"),
          )}
          {tc("VHF\nPWR_S", "PWR_P", sw.vhf, () =>
            apiCall("/api/toggle/switches.s.vhf"),
          )}
          {tc("MBS_CTRL\nPWR_S", "PWR_P", sw.mbs_ctrl, () =>
            apiCall("/api/toggle/switches.s.mbs_ctrl"),
          )}
          {tc("DC FAN", "", sw.dc_fan, () =>
            apiCall("/api/toggle/switches.s.dc_fan"),
          )}
          {tc("EMG_LED_P", "", swP.emg_led_p, () =>
            apiCall("/api/toggle/switches.p.emg_led_p"),
          )}
          {tc("INT_LED_S", "", sw.int_led_s, () =>
            apiCall("/api/toggle/switches.s.int_led_s"),
          )}
        </div>
      </div>
      <div
        style={{
          position: "absolute",
          bottom: "20px",
          right: "20px",
          background: "#ff00ff",
          color: "#000",
          padding: "4px 8px",
          fontWeight: "bold",
          fontSize: "28px",
          border: "2px solid #000",
        }}
      >
        IMAGING PC
      </div>
    </div>
  );
}

// --- Pilot PC (SW-3) Layout ---
export function Switches3Layout({ appState, apiCall }) {
  const sw = appState.switches?.sw3 || {};
  return (
    <div
      style={{
        padding: "20px",
        flex: 1,
        minHeight: 0,
        overflowY: "auto",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
      }}
    >
      <div className="screws" style={{ top: "10px", left: "10px" }}></div>
      <div className="screws" style={{ top: "10px", right: "10px" }}></div>

      {/* Emergency Jettisoning Switches */}
      <div
        style={{
          border: "1px solid #777",
          padding: "10px",
          position: "relative",
          marginTop: "10px",
          width: "100%",
          boxSizing: "border-box",
        }}
      >
        <div
          style={{ position: "absolute", top: "-15px", left: "50%", transform: "translateX(-50%)", color: "#ff1493", fontSize: "24px", fontWeight: "bold", background: "#f0f0f0", padding: "0 10px" }}
        >
          EMERGENCY JETTISONING SWITCHES
        </div>

        <div
          style={{
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            gap: "20px",
            marginTop: "10px",
          }}
        >
          <div
            style={{
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
            }}
          >
            <div className="tape-label-real" style={{ marginBottom: "5px" }}>
              TRIM-EMG JET-STBD
            </div>
            <div style={{ display: "flex", gap: "15px" }}>
              <Toggle3Pos
                showLed={true}
                labelTop="T-EJ-P1"
                labelBottom="T-EJ-S1"
                value={sw.t_ej_p1 ? 1 : sw.t_ej_s1 ? -1 : 0}
                onToggle={() => {
                  if (!sw.t_ej_p1 && !sw.t_ej_s1)
                    apiCall("/api/toggle/switches.sw3.t_ej_p1");
                  else if (sw.t_ej_p1 && !sw.t_ej_s1) {
                    apiCall("/api/toggle/switches.sw3.t_ej_p1");
                    apiCall("/api/toggle/switches.sw3.t_ej_s1");
                  } else apiCall("/api/toggle/switches.sw3.t_ej_s1");
                }}
              />
              <Toggle3Pos
                showLed={true}
                labelTop="T-EJ-P2"
                labelBottom="T-EJ-S2"
                value={sw.t_ej_p2 ? 1 : sw.t_ej_s2 ? -1 : 0}
                onToggle={() => {
                  if (!sw.t_ej_p2 && !sw.t_ej_s2)
                    apiCall("/api/toggle/switches.sw3.t_ej_p2");
                  else if (sw.t_ej_p2 && !sw.t_ej_s2) {
                    apiCall("/api/toggle/switches.sw3.t_ej_p2");
                    apiCall("/api/toggle/switches.sw3.t_ej_s2");
                  } else apiCall("/api/toggle/switches.sw3.t_ej_s2");
                }}
              />
              <Toggle3Pos
                showLed={true}
                labelTop="T-EJ-P3"
                labelBottom="T-EJ-S3"
                value={sw.t_ej_p3 ? 1 : sw.t_ej_s3 ? -1 : 0}
                onToggle={() => {
                  if (!sw.t_ej_p3 && !sw.t_ej_s3)
                    apiCall("/api/toggle/switches.sw3.t_ej_p3");
                  else if (sw.t_ej_p3 && !sw.t_ej_s3) {
                    apiCall("/api/toggle/switches.sw3.t_ej_p3");
                    apiCall("/api/toggle/switches.sw3.t_ej_s3");
                  } else apiCall("/api/toggle/switches.sw3.t_ej_s3");
                }}
              />
              <Toggle3Pos
                showLed={true}
                labelTop="T-EJ-P4"
                labelBottom="T-EJ-S4"
                value={sw.t_ej_p4 ? 1 : sw.t_ej_s4 ? -1 : 0}
                onToggle={() => {
                  if (!sw.t_ej_p4 && !sw.t_ej_s4)
                    apiCall("/api/toggle/switches.sw3.t_ej_p4");
                  else if (sw.t_ej_p4 && !sw.t_ej_s4) {
                    apiCall("/api/toggle/switches.sw3.t_ej_p4");
                    apiCall("/api/toggle/switches.sw3.t_ej_s4");
                  } else apiCall("/api/toggle/switches.sw3.t_ej_s4");
                }}
              />
            </div>
          </div>

          <div
            style={{
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
            }}
          >
            <div
              style={{
                display: "flex",
                width: "100%",
                justifyContent: "space-between",
                marginBottom: "5px",
                padding: "0 40px",
              }}
            >
              <div className="tape-label-real">RELEASE PORT</div>
              <div className="tape-label-real" style={{ marginLeft: "-10px" }}>
                MARKER BUOY
              </div>
              <div className="tape-label-real">RELEASE STBD</div>
            </div>
            <div style={{ display: "flex", gap: "15px", position: "relative" }}>
              <Toggle3Pos
                showLed={true}
                labelTop="MB-EJ-P1"
                labelBottom="MB-EJ-S1"
                value={sw.mb_ej_p1 ? 1 : sw.mb_ej_s1 ? -1 : 0}
                onToggle={() => {
                  if (!sw.mb_ej_p1 && !sw.mb_ej_s1)
                    apiCall("/api/toggle/switches.sw3.mb_ej_p1");
                  else if (sw.mb_ej_p1 && !sw.mb_ej_s1) {
                    apiCall("/api/toggle/switches.sw3.mb_ej_p1");
                    apiCall("/api/toggle/switches.sw3.mb_ej_s1");
                  } else apiCall("/api/toggle/switches.sw3.mb_ej_s1");
                }}
              />
              <Toggle3Pos
                showLed={true}
                labelTop="MB-EJ-P2"
                labelBottom="MB-EJ-S2"
                value={sw.mb_ej_p2 ? 1 : sw.mb_ej_s2 ? -1 : 0}
                onToggle={() => {
                  if (!sw.mb_ej_p2 && !sw.mb_ej_s2)
                    apiCall("/api/toggle/switches.sw3.mb_ej_p2");
                  else if (sw.mb_ej_p2 && !sw.mb_ej_s2) {
                    apiCall("/api/toggle/switches.sw3.mb_ej_p2");
                    apiCall("/api/toggle/switches.sw3.mb_ej_s2");
                  } else apiCall("/api/toggle/switches.sw3.mb_ej_s2");
                }}
              />
              <Toggle3Pos
                showLed={true}
                labelTop="MB-EJ-P3"
                labelBottom="MB-EJ-S3"
                value={sw.mb_ej_p3 ? 1 : sw.mb_ej_s3 ? -1 : 0}
                onToggle={() => {
                  if (!sw.mb_ej_p3 && !sw.mb_ej_s3)
                    apiCall("/api/toggle/switches.sw3.mb_ej_p3");
                  else if (sw.mb_ej_p3 && !sw.mb_ej_s3) {
                    apiCall("/api/toggle/switches.sw3.mb_ej_p3");
                    apiCall("/api/toggle/switches.sw3.mb_ej_s3");
                  } else apiCall("/api/toggle/switches.sw3.mb_ej_s3");
                }}
              />
              <Toggle3Pos
                showLed={true}
                labelTop="MB-EJ-P4"
                labelBottom="MB-EJ-S4"
                labelCenter="OFF"
                value={sw.mb_ej_p4 ? 1 : sw.mb_ej_s4 ? -1 : 0}
                onToggle={() => {
                  if (!sw.mb_ej_p4 && !sw.mb_ej_s4)
                    apiCall("/api/toggle/switches.sw3.mb_ej_p4");
                  else if (sw.mb_ej_p4 && !sw.mb_ej_s4) {
                    apiCall("/api/toggle/switches.sw3.mb_ej_p4");
                    apiCall("/api/toggle/switches.sw3.mb_ej_s4");
                  } else apiCall("/api/toggle/switches.sw3.mb_ej_s4");
                }}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Manipulator + Sample Basket row */}
      <div
        style={{
          display: "flex",
          gap: "50px",
          marginTop: "20px",
          justifyContent: "center",
          alignItems: "flex-end",
        }}
      >
        {/* MANIPULATOR */}
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
          }}
        >
          <div className="tape-label-real" style={{ marginBottom: "4px" }}>
            MANIPULATOR
          </div>
          <div style={{ display: "flex", gap: "60px", marginBottom: "4px" }}>
            <div className="tape-label-real">PORT</div>
            <div className="tape-label-real">STBD</div>
          </div>
          <div style={{ display: "flex", gap: "12px" }}>
            <Toggle3Pos
              showLed={true}
              labelTop="EJM-P1"
              labelBottom="EJM-S1"
              value={sw.ejm_p1 ? 1 : sw.ejm_s1 ? -1 : 0}
              onToggle={() => {
                if (!sw.ejm_p1 && !sw.ejm_s1)
                  apiCall("/api/toggle/switches.sw3.ejm_p1");
                else if (sw.ejm_p1 && !sw.ejm_s1) {
                  apiCall("/api/toggle/switches.sw3.ejm_p1");
                  apiCall("/api/toggle/switches.sw3.ejm_s1");
                } else apiCall("/api/toggle/switches.sw3.ejm_s1");
              }}
            />
            <Toggle3Pos
              showLed={true}
              labelTop="EJM-P2"
              labelBottom="EJM-S2"
              value={sw.ejm_p2 ? 1 : sw.ejm_s2 ? -1 : 0}
              onToggle={() => {
                if (!sw.ejm_p2 && !sw.ejm_s2)
                  apiCall("/api/toggle/switches.sw3.ejm_p2");
                else if (sw.ejm_p2 && !sw.ejm_s2) {
                  apiCall("/api/toggle/switches.sw3.ejm_p2");
                  apiCall("/api/toggle/switches.sw3.ejm_s2");
                } else apiCall("/api/toggle/switches.sw3.ejm_s2");
              }}
            />
            <Toggle3Pos
              showLed={true}
              labelTop="EJM-P3"
              labelBottom="EJM-S3"
              value={sw.ejm_p3 ? 1 : sw.ejm_s3 ? -1 : 0}
              onToggle={() => {
                if (!sw.ejm_p3 && !sw.ejm_s3)
                  apiCall("/api/toggle/switches.sw3.ejm_p3");
                else if (sw.ejm_p3 && !sw.ejm_s3) {
                  apiCall("/api/toggle/switches.sw3.ejm_p3");
                  apiCall("/api/toggle/switches.sw3.ejm_s3");
                } else apiCall("/api/toggle/switches.sw3.ejm_s3");
              }}
            />
            <Toggle3Pos
              showLed={true}
              labelTop="EJM-P4"
              labelBottom="EJM-S4"
              value={sw.ejm_p4 ? 1 : sw.ejm_s4 ? -1 : 0}
              onToggle={() => {
                if (!sw.ejm_p4 && !sw.ejm_s4)
                  apiCall("/api/toggle/switches.sw3.ejm_p4");
                else if (sw.ejm_p4 && !sw.ejm_s4) {
                  apiCall("/api/toggle/switches.sw3.ejm_p4");
                  apiCall("/api/toggle/switches.sw3.ejm_s4");
                } else apiCall("/api/toggle/switches.sw3.ejm_s4");
              }}
            />
          </div>
        </div>

        {/* SAMPLE BASKET */}
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
          }}
        >
          <div className="tape-label-real" style={{ marginBottom: "28px" }}>
            SAMPLE BASKET
          </div>
          <div style={{ display: "flex", gap: "12px" }}>
            <Toggle3Pos
              showLed={true}
              labelTop="EJS-P1"
              labelBottom="EJS-S1"
              value={sw.ejs_p1 ? 1 : sw.ejs_s1 ? -1 : 0}
              onToggle={() => {
                if (!sw.ejs_p1 && !sw.ejs_s1)
                  apiCall("/api/toggle/switches.sw3.ejs_p1");
                else if (sw.ejs_p1 && !sw.ejs_s1) {
                  apiCall("/api/toggle/switches.sw3.ejs_p1");
                  apiCall("/api/toggle/switches.sw3.ejs_s1");
                } else apiCall("/api/toggle/switches.sw3.ejs_s1");
              }}
            />
            <Toggle3Pos
              showLed={true}
              labelTop="EJS-P2"
              labelBottom="EJS-S2"
              value={sw.ejs_p2 ? 1 : sw.ejs_s2 ? -1 : 0}
              onToggle={() => {
                if (!sw.ejs_p2 && !sw.ejs_s2)
                  apiCall("/api/toggle/switches.sw3.ejs_p2");
                else if (sw.ejs_p2 && !sw.ejs_s2) {
                  apiCall("/api/toggle/switches.sw3.ejs_p2");
                  apiCall("/api/toggle/switches.sw3.ejs_s2");
                } else apiCall("/api/toggle/switches.sw3.ejs_s2");
              }}
            />
            <Toggle3Pos
              showLed={true}
              labelTop="EJX-P1"
              labelBottom="ELX-S1"
              labelCenter="OFF"
              value={sw.ejx_p1 ? 1 : sw.ejx_s1 ? -1 : 0}
              onToggle={() => {
                if (!sw.ejx_p1 && !sw.ejx_s1)
                  apiCall("/api/toggle/switches.sw3.ejx_p1");
                else if (sw.ejx_p1 && !sw.ejx_s1) {
                  apiCall("/api/toggle/switches.sw3.ejx_p1");
                  apiCall("/api/toggle/switches.sw3.ejx_s1");
                } else apiCall("/api/toggle/switches.sw3.ejx_s1");
              }}
            />
            <Toggle3Pos
              showLed={true}
              labelTop="EJX-P2"
              labelBottom="EJX-S2"
              labelCenter="OFF"
              value={sw.ejx_p2 ? 1 : sw.ejx_s2 ? -1 : 0}
              onToggle={() => {
                if (!sw.ejx_p2 && !sw.ejx_s2)
                  apiCall("/api/toggle/switches.sw3.ejx_p2");
                else if (sw.ejx_p2 && !sw.ejx_s2) {
                  apiCall("/api/toggle/switches.sw3.ejx_p2");
                  apiCall("/api/toggle/switches.sw3.ejx_s2");
                } else apiCall("/api/toggle/switches.sw3.ejx_s2");
              }}
            />
          </div>
        </div>
      </div>

      {/* Main Lower Section */}
      <div
        style={{
          display: "flex",
          gap: "40px",
          marginTop: "40px",
          justifyContent: "center",
          alignItems: "flex-start",
          width: "100%",
        }}
      >
        {/* Column 1 */}
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
          }}
        >
          <div style={{ display: "flex", gap: "15px" }}>
            <Toggle3Pos
              showLed={true}
              labelTop="EDW_P1"
              labelBottom="EDW_S1"
              labelCenter="EDW OFF"
              value={sw.edw_p1 ? 1 : sw.edw_s1 ? -1 : 0}
              onToggle={() => {
                if (!sw.edw_p1 && !sw.edw_s1)
                  apiCall("/api/toggle/switches.sw3.edw_p1");
                else if (sw.edw_p1 && !sw.edw_s1) {
                  apiCall("/api/toggle/switches.sw3.edw_p1");
                  apiCall("/api/toggle/switches.sw3.edw_s1");
                } else apiCall("/api/toggle/switches.sw3.edw_s1");
              }}
            />
            <Toggle3Pos
              showLed={true}
              labelTop="EDW_P2"
              labelBottom="EDW_S2"
              labelCenter="EDW OFF"
              value={sw.edw_p2 ? 1 : sw.edw_s2 ? -1 : 0}
              onToggle={() => {
                if (!sw.edw_p2 && !sw.edw_s2)
                  apiCall("/api/toggle/switches.sw3.edw_p2");
                else if (sw.edw_p2 && !sw.edw_s2) {
                  apiCall("/api/toggle/switches.sw3.edw_p2");
                  apiCall("/api/toggle/switches.sw3.edw_s2");
                } else apiCall("/api/toggle/switches.sw3.edw_s2");
              }}
            />
          </div>
          <div
            style={{
              display: "flex",
              gap: "30px",
              marginTop: "40px",
              alignItems: "flex-start",
            }}
          >
            <div
              style={{
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
              }}
            >
              <div className="tape-label-real" style={{ marginBottom: "3px" }}>
                WATER LEAK
              </div>
              <div style={{ display: "flex", gap: "2px", marginBottom: "3px" }}>
                <div style={{ width: "44px" }}></div>
                <div
                  className="tape-label-real"
                  style={{
                    width: "38px",
                    textAlign: "center",
                    fontSize: "9px",
                  }}
                >
                  PORT
                </div>
                <div
                  className="tape-label-real"
                  style={{
                    width: "38px",
                    textAlign: "center",
                    fontSize: "9px",
                  }}
                >
                  STBD
                </div>
              </div>
              {[
                { l: "PS", p: sw.wl_ps },
                { l: "IDE", p: sw.wl_ide },
                { l: "PDE", p: sw.wl_pde },
                { l: "PJB", p: sw.wl_pjb },
                { l: "TJB", p: sw.wl_tjb },
                { l: "BAT", p: sw.wl_bat },
              ].map((row, i) => (
                <div
                  key={i}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    height: "40px",
                  }}
                >
                  <div
                    style={{
                      width: "40px",
                      textAlign: "right",
                      paddingRight: "4px",
                    }}
                  >
                    <div
                      className="tape-label-real"
                      style={{ fontSize: "9px" }}
                    >
                      {row.l}
                    </div>
                  </div>
                  <div style={{ margin: "0 4px" }}>
                    <AlarmIndicator label="" isOn={row.p} />
                  </div>
                  <div style={{ margin: "0 4px" }}>
                    <AlarmIndicator label="" isOn={false} />
                  </div>
                </div>
              ))}
            </div>
            <div>
              <Buzzer label="BUZZER_1" />
            </div>
          </div>
        </div>

        {/* Column 2 */}
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
          }}
        >
          <AxisCamera />
          <div
            style={{
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              marginTop: "15px",
            }}
          >
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(4, 1fr)",
                gap: "12px",
              }}
            >
              <BlackPushButton labelTop="MB" />
              <BlackPushButton labelTop="AB" />
              <BlackPushButton labelTop="HYD OIL" />
              <BlackPushButton labelTop="DEPTH" />
              <BlackPushButton labelTop="ALTITUDE" />
              <BlackPushButton labelTop="SPARE 2" />
              <BlackPushButton labelTop="SPARE 3" />
              <BlackPushButton labelTop="SPARE 4" />
              <BlackPushButton labelTop="SPARE 5" />
              <BlackPushButton labelTop="SPARE 6" />
              <BlackPushButton labelTop="SPARE 7" />
              <BlackPushButton labelTop="SPARE 8" />
            </div>
            <div className="tape-label-real" style={{ marginTop: "16px" }}>
              ALARM PANEL
            </div>
          </div>
        </div>

        {/* Column 3 */}
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
          }}
        >
          <div style={{ display: "flex", gap: "15px" }}>
            <Toggle3Pos
              showLed={true}
              labelTop="EDW_P3"
              labelBottom="EDW_S3"
              labelCenter="EDW OFF"
              value={sw.edw_p3 ? 1 : sw.edw_s3 ? -1 : 0}
              onToggle={() => {
                if (!sw.edw_p3 && !sw.edw_s3)
                  apiCall("/api/toggle/switches.sw3.edw_p3");
                else if (sw.edw_p3 && !sw.edw_s3) {
                  apiCall("/api/toggle/switches.sw3.edw_p3");
                  apiCall("/api/toggle/switches.sw3.edw_s3");
                } else apiCall("/api/toggle/switches.sw3.edw_s3");
              }}
            />
            <Toggle3Pos
              showLed={true}
              labelTop="EDW_P4"
              labelBottom="EDW_S4"
              labelCenter="EDW OFF"
              value={sw.edw_p4 ? 1 : sw.edw_s4 ? -1 : 0}
              onToggle={() => {
                if (!sw.edw_p4 && !sw.edw_s4)
                  apiCall("/api/toggle/switches.sw3.edw_p4");
                else if (sw.edw_p4 && !sw.edw_s4) {
                  apiCall("/api/toggle/switches.sw3.edw_p4");
                  apiCall("/api/toggle/switches.sw3.edw_s4");
                } else apiCall("/api/toggle/switches.sw3.edw_s4");
              }}
            />
          </div>
          <div
            style={{
              display: "flex",
              gap: "30px",
              marginTop: "40px",
              alignItems: "flex-start",
            }}
          >
            <div>
              <Buzzer label="BUZZER_2" />
            </div>
            <div
              style={{
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
              }}
            >
              <div className="tape-label-real" style={{ marginBottom: "3px" }}>
                INSULATION
              </div>
              <div style={{ display: "flex", gap: "2px", marginBottom: "3px" }}>
                <div
                  className="tape-label-real"
                  style={{
                    width: "38px",
                    textAlign: "center",
                    fontSize: "9px",
                  }}
                >
                  PORT
                </div>
                <div
                  className="tape-label-real"
                  style={{
                    width: "38px",
                    textAlign: "center",
                    fontSize: "9px",
                  }}
                >
                  STBD
                </div>
                <div style={{ width: "50px" }}></div>
              </div>
              {[
                { l: "PS_UB", p: sw.ins_p1, s: sw.ins_ps_ub },
                { l: "IDE", p: sw.ins_p2, s: sw.ins_ide },
                { l: "PDE", p: sw.ins_p3, s: sw.ins_pde },
                { l: "148V", p: sw.ins_p4, s: sw.ins_148v },
                { l: "PS_EB", p: sw.ins_p5, s: sw.ins_ps_eb },
                { l: "SPARE 1", p: sw.ins_p6, s: sw.ins_spare_1 },
              ].map((row, i) => (
                <div
                  key={i}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    height: "40px",
                  }}
                >
                  <div style={{ margin: "0 4px" }}>
                    <AlarmIndicator label="" isOn={row.p} />
                  </div>
                  <div style={{ margin: "0 4px" }}>
                    <AlarmIndicator label="" isOn={row.s} />
                  </div>
                  <div style={{ width: "50px", paddingLeft: "4px" }}>
                    <div
                      className="tape-label-real"
                      style={{ fontSize: "9px" }}
                    >
                      {row.l}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      <div
        style={{
          width: "100%",
          height: "1px",
          background: "#333",
          margin: "20px 0",
          boxShadow: "0 1px 1px #000",
        }}
      ></div>

      {/* Control Switches (Bottom Row) */}
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          gap: "16px",
          marginBottom: "10px",
          alignItems: "center",
        }}
      >
        <div style={{ display: "flex", gap: "20px", alignItems: "flex-start", flexWrap: "wrap" }}>
        <div style={{ display: "flex", gap: "8px" }}>
          <BlackPushButton labelTop="SUBMERSIBLE\nCTRL" />
          <BlackPushButton labelTop="WATER OUT" />
          <BlackPushButton labelTop="TRIM" />
        </div>
        <div style={{ display: "flex", gap: "4px" }}>
          {tc(
            "FREEBOARD_P",
            "",
            sw.freeboard_p,
            () => apiCall("/api/toggle/switches.sw3.freeboard_p"),
            null,
            "black",
            false,
            true,
          )}
          {tc(
            "FREEBOARD_S",
            "",
            sw.freeboard_s,
            () => apiCall("/api/toggle/switches.sw3.freeboard_s"),
            null,
            "black",
            false,
            true,
          )}
          {tc(
            "DIVE-IN-ON",
            "",
            sw.dive_in_on,
            () => apiCall("/api/toggle/switches.sw3.dive_in_on"),
            null,
            "black",
            false,
            true,
          )}
          {tc(
            "DIVE-IN-OFF",
            "",
            sw.dive_in_off,
            () => apiCall("/api/toggle/switches.sw3.dive_in_off"),
            null,
            "black",
            false,
            true,
          )}
          {tc(
            "HP-AP-ON",
            "",
            sw.hp_ap_on,
            () => apiCall("/api/toggle/switches.sw3.hp_ap_on"),
            null,
            "black",
            false,
            true,
          )}
          {tc(
            "HP-AP-OFF",
            "",
            sw.hp_ap_off,
            () => apiCall("/api/toggle/switches.sw3.hp_ap_off"),
            null,
            "black",
            false,
            true,
          )}
          {tc(
            "HP-BP-ON",
            "",
            sw.hp_bp_on,
            () => apiCall("/api/toggle/switches.sw3.hp_bp_on"),
            null,
            "black",
            false,
            true,
          )}
          {tc(
            "HP-BP-OFF",
            "",
            sw.hp_bp_off,
            () => apiCall("/api/toggle/switches.sw3.hp_bp_off"),
            null,
            "black",
            false,
            true,
          )}
        </div>
        </div>
        <div style={{ display: "flex", gap: "10px" }}>
          <KnobToggleSwitch label="FWD CTRL" value={sw.fwd_ctrl ? 2 : 1} onChange={() => apiCall("/api/toggle/switches.sw3.fwd_ctrl")} />
          <KnobToggleSwitch label="HEADING_CTRL" value={sw.heading_ctrl ? 2 : 1} onChange={() => apiCall("/api/toggle/switches.sw3.heading_ctrl")} />
          <KnobToggleSwitch label="DEPTH_CTRL" value={sw.depth_ctrl ? 2 : 1} onChange={() => apiCall("/api/toggle/switches.sw3.depth_ctrl")} />
          <KnobToggleSwitch label="LATERAL TRIM" value={sw.lat_trim ? 2 : 1} onChange={() => apiCall("/api/toggle/switches.sw3.lat_trim")} />
          <KnobToggleSwitch label="HP REG" value={sw.hp_reg ? 2 : 1} onChange={() => apiCall("/api/toggle/switches.sw3.hp_reg")} />
          <KnobToggleSwitch label="VBT CTRL" value={sw.vbt_ctrl ? 2 : 1} onChange={() => apiCall("/api/toggle/switches.sw3.vbt_ctrl")} />
          <KnobToggleSwitch label="PITCH CTRL" value={sw.pitch_ctrl ? 2 : 1} onChange={() => apiCall("/api/toggle/switches.sw3.pitch_ctrl")} />
        </div>
      </div>

      <div
        style={{
          position: "absolute",
          bottom: "20px",
          left: "20px",
          background: "#ff00ff",
          color: "#000",
          padding: "4px 8px",
          fontWeight: "bold",
          fontSize: "28px",
          border: "2px solid #000",
        }}
      >
        PILOT PC
      </div>
    </div>
  );
}
