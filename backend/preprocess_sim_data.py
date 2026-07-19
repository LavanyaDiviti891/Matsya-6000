import pandas as pd
import json
import glob
import os
import re

def normalize(text):
    if not isinstance(text, str): return ""
    return re.sub(r'[^a-z0-9]', '', text.lower())

sheet_headers = {
    "Ballast and Propulsion": "Date & Time, Date, Time, T1 Current, T3 Current, T5 Current, T7 Current, T2 Current, T4 Current, T6 Current, T8 Current, T2 Voltage, T2 C.Temp, T2 Speed, T4 Voltage, T4 C.Temp, T4 Speed, T6 Voltage, T6 C.Temp, T6 Speed, T8 Voltage, T8 C.Temp, T8 Speed, T1 Voltage, T1 Temp, T1 Speed, T3 Voltage, T3  Temp, T3 Speed, T5 Voltage, T5 Temp, T5 Speed, T7 Voltage, T7 Temp, T7 Speed",
    "Battery": "Date & Time, Date, Time, AUX_P Volt (V), AUX_P Current (A), AUX_P Power (KW), AUX_P Temp (deg C) , AUX_P SOC (%), AUX_S Current (A), AUX_S Power (KW), AUX_S Temp (deg C), AUX_S Volt (V), AUX_S SOC (%), MB_P Volt (V), MB_P Power (W), MB_P Current (A), MB_P SOC (%), MB_P Temp (deg C), MB_S Volt (V), MB_S Current (A), MB_S SOC (%), MB_S Temp (deg C), Current (A)_P, BAT CUR, BAT VOL, BAT SOC, BAT TEMP, Current_1, Voltage_1, ID Cell Max_1, Max Temp_1, ID Cell Min _1, Min Temp_1, Temp_1, SOC_1, SOH_1, Current_2, Voltage_2, ID Cell Max_2, Max Temp_2, ID Cell Min _2, Min Temp_2, Temp_2, SOC_2, SOH_2, Current_3, Voltage_3, ID Cell Max_3, Max Temp_3, ID Cell Min _3, Min Temp_3, Temp_3, SOC_3, SOH_3, Current_4, Voltage_4, ID Cell Max_4, Max Temp_4, ID Cell Min _4, Min Temp_4, Temp_4, SOC_4, SOH_4, Current_5, Voltage_5, ID Cell Max_5, Max Temp_5, ID Cell Min _5, Min Temp_5, Temp_5, SOC_5, SOH_5, Current_1 2, Voltage_1 2, ID Cell Max_1 2, Max Temp_1 2, ID Cell Min _1 2, Min Temp_1 2, Temp_1 2, SOC_1 2, SOH_1 2, Current_2 2, Voltage_2 2, ID Cell Max_2 2, Max Temp_2 2, ID Cell Min _2 2, Min Temp_2 2, Temp_2 2, SOC_2 2, SOH_2 2, Current_3 2, Voltage_3 2, ID Cell Max_3 2, Max Temp_3 2, ID Cell Min _3 2, Min Temp_3 2, Temp_3 2, SOC_3 2, SOH_3 2, Current_4 2, Voltage_4 2, ID Cell Max_4 2, Max Temp_4 2, ID Cell Min _4 2, Min Temp_4 2, Temp_4 2, SOC_4 2, SOH_4 2, Current_5 2, Voltage_5 2, ID Cell Max_5 2, Max Temp_5 2, ID Cell Min _5 2, Min Temp_5 2, Temp_5 2, SOC_5 2, SOH_5 2, BAT CUR 2, BAT VOL 2, BAT SOC 2, BAT TEMP 2",
    "Navigation and HSSS": "Date and Time, Date, Time, Heading, Roll, Pitch, Latitude, Longitude, Depth, Lateral speed , Vertical speed, Forward speed , Altitude, S_Heading, S_Roll, S_Pitch, S_Latitude, S_Longitude, S_Speed1, S_Speed2, S_Speed3, S_Depth, S_ALGSTS_M, S_ALGSTS_L, S_STATUS_M, S_STATUS_L, S_HTSTATUS, Altitude, GPS Latitude, GPS Longitude, Subea Temp_2, Conductivity, Salanity, pH, Turbidity, Oxygen_P, CO2_P , Presssure in mbar_P, Temp in Deg C_P, Hydrogen_P, Humidity_P in %, HP_B1 Pressure_P, HP_B2 Pressure_P, HP_B3 Pressure_P, LP_L Pressure_P, Oxygen_S, CO2_s, Presssure in mbar_S, Temp in Deg C_S, Humidity_S in %, Hydrogen_S, HP_B1 Pressure_S, HP_B2 Pressure_S, HP_B3 Pressure_S, LP_L Pressure_S, PDE_P_IR_Ext (Kohm), PDE_S_IR_Ext (Kohm), Depth Sensor Pri 2",
    "Power": "Date & Time, Date, Time, IDE_P Voltage (V), IDE_P_Voltage_2, IDE_P Temp (degC), IDE_P Current (A), IDE_P_Current_2, IDE_P WIS 1, IDE_P WIS 2, IDE_S Voltage (V), IDE_S_Voltage_2, IDE_S Temp (degC), IDE_S Current (A), IDE_S_Current_2, IDE_S WIS 1, IDE_S WIS 2, IDE_S IR  (Kohm), IDE_P IR (kohm), IDE_P IR Status, IDE_S IR Status, PDE_P Voltage (V), PDE_P Current (A), PDE_P 24 Voltage1 (V), PDE_P 24Current (A), PDE_P 24 Voltage2 (V), PDE_P BATS CUR, PDE_P WIS, PDE_P Temp (degC), PDE_S Voltage (V), PDE_S Current (A), PDE_S24VOL1, PDE_S24V CUR, PDE_S24VOL2, PDE_S BATS CUR, PDE_S WIS, PDE_S Temp (degC), PDE_S IR (Kohm), PDE_P_148 IR (Kohm), PDE_S IR_148 (Kohm), PDE_P IR (Kohm), PDE_S IR Status, PDE_P IR Status, FWD Ctrl, Heading trim, Depth trim, lateral trim, Hp Reg, UBT Ctrl, Pitch  ctrl, PSP Current (A), PSP Current2 (A), PSP Voltage (V), PSP Voltage 2(V), PSP WIS, PSP Temp (degC), PSP IR (Kohm), PSS Current (A), PSS Current 2(A), PSS Voltage (V), PSS Voltage 2(V), PSS Temp (degC), PSS WI, PSS IR (Kohm), PSS IR , PSP IR"
}

sheet_data = {name: [c.strip() for c in headers.split(',')] for name, headers in sheet_headers.items()}

system_vars = [
    "header.dive_num", "header.mission_time", "header.present_time", "header.heading", "header.depth", "header.altitude", 
    "header.mb_p_soc", "header.mb_s_soc",
    "imu.roll", "imu.pitch", "imu.heading_p",
    "bottom.east_speed", "bottom.vert_speed", "bottom.north_speed", "bottom.ship_heading",
    "propulsion.t1_rpm", "propulsion.t2_rpm", "propulsion.t3_rpm", "propulsion.t4_rpm", 
    "propulsion.t5_rpm", "propulsion.t6_rpm", "propulsion.t7_rpm", "propulsion.t8_rpm",
    "propulsion.latitude", "propulsion.longitude",
    *[f"propulsion_detail.{t}.{field}" for t in [f"t{i}" for i in range(1,9)] for field in ["rpm", "voltage", "current", "temp"]],
    "environment.o2", "environment.co2", "environment.temp", "environment.pressure",
    *[f"hsss.{side}.{field}" for side in ["p", "s"] for field in ["co2", "oxygen", "pressure", "temp", "humidity", "hydrogen", "lp_l_pressure", "hp_b1_pressure", "hp_b2_pressure", "hp_b3_pressure"]],
    "ballast.main_ballast.act3_pos", "ballast.main_ballast.act3_pos2", "ballast.main_ballast.act3_pos3",
    "ballast.main_ballast.read_pressure_s", "ballast.main_ballast.read_pressure_p",
    "ballast.vbs.hpu_pressure", "ballast.vbs.hpu_temp", "ballast.vbs.tank_level",
    "ballast.trim.position_mm", "ballast.trim.voltage", "ballast.trim.current", "ballast.trim.temp", "ballast.trim.speed",
    *[f"power.{batt}.{field}" for batt in ["mb_p", "aux_p", "mb_s", "aux_s"] for field in ["voltage", "current", "power", "soc", "temp"]],
    *[f"power.{enc}.{field}" for enc in ["pde_p", "ide_p", "pde_s", "ide_s"] for field in ["voltage", "current", "temp", "ir"]],
    *[f"kwh.port.{b}.{field}" for b in [f"bat{i}" for i in range(1,6)] for field in ["cur", "vot", "temp", "soc"]],
    *[f"kwh.stbd.{b}.{field}" for b in [f"bat{i}" for i in range(6,11)] for field in ["cur", "vot", "temp", "soc"]],
]

def find_match(full_var):
    parts = full_var.split('.')
    leaf = parts[-1]
    parent = parts[-2]
    grand = parts[-3] if len(parts) > 2 else ""
    
    norm_leaf = normalize(leaf)
    norm_parent = normalize(parent)
    
    if parent in ["header", "imu", "bottom"]:
        mapping = {
            "heading": "Heading", "depth": "Depth", "altitude": "Altitude",
            "roll": "Roll", "pitch": "Pitch",
            "east_speed": "Lateral speed", "vert_speed": "Vertical speed", "north_speed": "Forward speed",
            "ship_heading": "S_Heading", "latitude": "Latitude", "longitude": "Longitude"
        }
        target = mapping.get(leaf)
        if target:
            for col in sheet_data["Navigation and HSSS"]:
                if normalize(target) == normalize(col): return ("Navigation and HSSS", col)

    if grand == "hsss":
        suffix = f"_{parent.upper()}"
        for col in sheet_data["Navigation and HSSS"]:
            if normalize(leaf) in normalize(col) and suffix in col:
                return ("Navigation and HSSS", col)
        if leaf == "temp":
            target = f"Temp in Deg C{suffix}"
            for col in sheet_data["Navigation and HSSS"]:
                if target in col: return ("Navigation and HSSS", col)

    if parent.startswith("bat"):
        bat_num = int(re.search(r'\d+', parent).group())
        field_map = {"cur": "Current", "vot": "Voltage", "temp": "Temp", "soc": "SOC"}
        field = field_map.get(leaf, leaf)
        if grand == "port":
            target = f"{field}_{bat_num}"
            for col in sheet_data["Battery"]:
                if normalize(target) == normalize(col) and " 2" not in col: return ("Battery", col)
        else:
            target = f"{field}_{bat_num - 5} 2"
            for col in sheet_data["Battery"]:
                if normalize(target) == normalize(col): return ("Battery", col)

    if parent.startswith("t") and len(parent) <= 2:
        field_map = {"rpm": "Speed", "voltage": "Voltage", "current": "Current", "temp": "Temp"}
        field = field_map.get(leaf, leaf)
        target = f"{parent.upper()} {field}"
        for col in sheet_data["Ballast and Propulsion"]:
            if normalize(target) in normalize(col): return ("Ballast and Propulsion", col)

    for sheet_name in ["Battery", "Power"]:
        for col in sheet_data[sheet_name]:
            if normalize(parent) in normalize(col):
                tokens = [norm_leaf]
                if norm_leaf == "voltage": tokens.append("volt")
                if norm_leaf == "current": tokens.append("cur")
                if any(t in normalize(col) for t in tokens):
                    return (sheet_name, col)

    return None

def normalize_sheet_name(name):
    return name.lower().replace('&', 'and').replace(' ', '')

def map_actual_sheets(excel_sheets):
    sheet_map = {}
    for actual_name in excel_sheets:
        norm_actual = normalize_sheet_name(actual_name)
        for expected_name in sheet_headers.keys():
            if normalize_sheet_name(expected_name) == norm_actual:
                sheet_map[expected_name] = actual_name
    return sheet_map

def process_all():
    os.makedirs('sim_data_processed', exist_ok=True)
    files = glob.glob('sim_data/*.xlsx')
    for file in files:
        print(f"Processing {file}...")
        try:
            dfs = pd.read_excel(file, sheet_name=None)
            sheet_map = map_actual_sheets(dfs.keys())
            
            # Use the length of the first available sheet
            min_rows = float('inf')
            for sheet_name in sheet_map.values():
                if len(dfs[sheet_name]) < min_rows:
                    min_rows = len(dfs[sheet_name])
            num_rows = min_rows if min_rows != float('inf') else 0
            
            print(f"Found {num_rows} rows.")
            
            # Figure out exactly which actual columns map to which vars
            var_mapping = {} # system_var -> (actual_sheet, actual_col)
            for var in system_vars:
                match = find_match(var)
                if match:
                    expected_sheet, expected_col = match
                    actual_sheet = sheet_map.get(expected_sheet)
                    if actual_sheet:
                        # Find the actual col that matches the normalized expected_col
                        df = dfs[actual_sheet]
                        norm_expected_col = normalize(expected_col)
                        actual_col = None
                        for col in df.columns:
                            if normalize(col) == norm_expected_col:
                                actual_col = col
                                break
                        if actual_col:
                            var_mapping[var] = (actual_sheet, actual_col)
            
            print(f"Mapped {len(var_mapping)} variables.")
            
            # Now build the list of dicts over time
            records = []
            
            # Find a 'Time' column somewhere to use as present_time
            time_col = None
            time_sheet = None
            for s_name, df in dfs.items():
                if 'Time' in df.columns:
                    time_sheet = s_name
                    time_col = 'Time'
                    break

            for i in range(num_rows):
                row_data = {}
                for var, (actual_sheet, actual_col) in var_mapping.items():
                    val = dfs[actual_sheet][actual_col].iloc[i]
                    if pd.notna(val):
                        # Convert numpy types to native Python
                        row_data[var] = val.item() if hasattr(val, 'item') else val
                
                if time_sheet and time_col:
                    t_val = dfs[time_sheet][time_col].iloc[i]
                    if pd.notna(t_val):
                        row_data["header.present_time"] = str(t_val)
                        
                records.append(row_data)
                
            out_name = os.path.basename(file).replace('.xlsx', '.json')
            out_path = os.path.join('sim_data_processed', out_name)
            with open(out_path, 'w') as f:
                json.dump(records, f)
            print(f"Saved to {out_path}")
        except Exception as e:
            print(f"Error on {file}: {e}")

if __name__ == '__main__':
    process_all()
