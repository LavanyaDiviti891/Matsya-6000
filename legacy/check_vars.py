import pandas as pd
import json

required_vars = [
    "header.dive_num", "header.mission_time", "header.present_time", "header.heading", "header.depth", "header.altitude", "header.mb_p_soc", "header.mb_s_soc",
    "imu.roll", "imu.pitch", "imu.heading_p",
    "bottom.east_speed", "bottom.vert_speed", "bottom.north_speed", "bottom.ship_heading",
    "propulsion.t1_rpm", "propulsion.t2_rpm", "propulsion.t3_rpm", "propulsion.t4_rpm", "propulsion.t5_rpm", "propulsion.t6_rpm", "propulsion.t7_rpm", "propulsion.t8_rpm",
    "propulsion.latitude", "propulsion.longitude",
    "environment.o2", "environment.co2", "environment.temp", "environment.pressure",
    "hsss.p.co2", "hsss.p.oxygen", "hsss.p.pressure", "hsss.p.temp", "hsss.p.humidity", "hsss.p.hydrogen", "hsss.p.lp_l_pressure", "hsss.p.hp_b1_pressure", "hsss.p.hp_b2_pressure", "hsss.p.hp_b3_pressure",
    "hsss.s.co2", "hsss.s.oxygen", "hsss.s.pressure", "hsss.s.temp", "hsss.s.humidity", "hsss.s.hydrogen", "hsss.s.lp_l_pressure", "hsss.s.hp_b1_pressure", "hsss.s.hp_b2_pressure", "hsss.s.hp_b3_pressure",
    "ballast.main_ballast.act3_pos", "ballast.main_ballast.act3_pos2", "ballast.main_ballast.act3_pos3", "ballast.main_ballast.read_pressure_s", "ballast.main_ballast.read_pressure_p",
    "ballast.vbs.hpu_pressure", "ballast.vbs.hpu_temp", "ballast.vbs.tank_level",
    "ballast.trim.position_mm", "ballast.trim.voltage", "ballast.trim.current", "ballast.trim.temp", "ballast.trim.speed",
    "power.mb_p.voltage", "power.mb_p.current", "power.mb_p.power", "power.mb_p.soc", "power.mb_p.temp",
    "power.aux_p.voltage", "power.aux_p.current", "power.aux_p.power", "power.aux_p.soc", "power.aux_p.temp",
    "power.mb_s.voltage", "power.mb_s.current", "power.mb_s.power", "power.mb_s.soc", "power.mb_s.temp",
    "power.aux_s.voltage", "power.aux_s.current", "power.aux_s.power", "power.aux_s.soc", "power.aux_s.temp",
    "power.pde_p.voltage", "power.pde_p.current", "power.pde_p.temp", "power.pde_p.ir",
    "power.ide_p.voltage", "power.ide_p.current", "power.ide_p.temp", "power.ide_p.ir",
    "power.pde_s.voltage", "power.pde_s.current", "power.pde_s.temp", "power.pde_s.ir",
    "power.ide_s.voltage", "power.ide_s.current", "power.ide_s.temp", "power.ide_s.ir",
    "kwh.port.bat1.cur", "kwh.port.bat1.vot", "kwh.port.bat1.temp", "kwh.port.bat1.soc",
]

xls = pd.ExcelFile('sim_data/dive 1 merged data.xlsx')
all_cols = []
for sheet in xls.sheet_names:
    all_cols.extend(pd.read_excel(xls, sheet_name=sheet, nrows=0).columns.tolist())

all_cols_lower = [c.lower().strip() for c in all_cols]

mapping = {
    "header.heading": "heading",
    "header.depth": "depth",
    "header.altitude": "altitude",
    "imu.roll": "roll",
    "imu.pitch": "pitch",
    "propulsion.latitude": "latitude",
    "propulsion.longitude": "longitude",
    "bottom.east_speed": "lateral speed",
    "bottom.vert_speed": "vertical speed",
    "bottom.north_speed": "forward speed",
    "bottom.ship_heading": "s_heading",
    "hsss.p.lp_l_pressure": "lp_l pressure_p",
    "hsss.p.hp_b1_pressure": "hp_b1 pressure_p",
    "hsss.p.hp_b2_pressure": "hp_b2 pressure_p",
    "hsss.p.hp_b3_pressure": "hp_b3 pressure_p",
    "hsss.s.lp_l_pressure": "lp_l pressure_s",
    "hsss.s.hp_b1_pressure": "hp_b1 pressure_s",
    "hsss.s.hp_b2_pressure": "hp_b2 pressure_s",
    "hsss.s.hp_b3_pressure": "hp_b3 pressure_s",
    "header.mb_p_soc": "mb_p soc",
    "header.mb_s_soc": "mb_s soc",
}

results = {}
missing = []

for var in required_vars:
    matched = False
    
    # Check explicit mapping
    if var in mapping:
        target = mapping[var]
        if target in all_cols_lower:
            results[var] = all_cols[all_cols_lower.index(target)]
            matched = True
            
    if not matched:
        parts = var.split('.')
        name = parts[-1].lower()
        parent = parts[-2].lower() if len(parts) > 1 else ""
        
        # Try some heuristics
        for i, col_l in enumerate(all_cols_lower):
            if name == col_l:
                results[var] = all_cols[i]
                matched = True
                break
            if name in col_l and parent in col_l:
                results[var] = all_cols[i]
                matched = True
                break
        
    if not matched:
        # Special case for thrusters
        if "t" in var and "rpm" in var:
            t_num = var.split('.')[-1].split('_')[0].upper()
            target = f"{t_num} speed".lower()
            if target in all_cols_lower:
                results[var] = all_cols[all_cols_lower.index(target)]
                matched = True

    if not matched:
        missing.append(var)

print("Found matches count:", len(results))
print("\nMissing variables:")
for m in missing:
    print(m)
