import re

with open("main.py", "r") as f:
    content = f.read()

# Replace bottom tabs list
content = content.replace('"Switches",', '"Switches_P",\n                "Switches_S",')

# Replace routes
route_switches = """@rt("/switches")
def get_switches():
    return Title("MATSYA 6000 View - Switches"), Div(
        AppLayout(active_tab="Switches"), id="ws-container", hx_ext="ws", ws_connect="/ws"
    )"""

route_p_s = """@rt("/switches-p")
def get_switches_p():
    return Title("MATSYA 6000 View - Switches_P"), Div(
        AppLayout(active_tab="Switches_P"), id="ws-container", hx_ext="ws", ws_connect="/ws"
    )

@rt("/switches-s")
def get_switches_s():
    return Title("MATSYA 6000 View - Switches_S"), Div(
        AppLayout(active_tab="Switches_S"), id="ws-container", hx_ext="ws", ws_connect="/ws"
    )"""

content = content.replace(route_switches, route_p_s)

# Extract the block for Switches
start_str = '    elif active_tab == "Switches":\n'
end_str = '    else:\n        main_content_area = Div('
start_idx = content.find(start_str)
end_idx = content.find(end_str)

block = content[start_idx:end_idx]

# Create _P block
block_p = block.replace('active_tab == "Switches"', 'active_tab == "Switches_P"')
block_p = block_p.replace('sw = s.switches.state', 'sw = s.switches.p')
block_p = block_p.replace('id=f"tog-sw-{state_key.replace(\'_\', \'-\')}"', 'id=f"tog-sw-p-{state_key.replace(\'_\', \'-\')}"')
block_p = block_p.replace('hx_post=f"/api/toggle/switches.state.{state_key}"', 'hx_post=f"/api/toggle/switches.p.{state_key}"')

# Create _S block
block_s = block.replace('active_tab == "Switches"', 'active_tab == "Switches_S"')
block_s = block_s.replace('sw = s.switches.state', 'sw = s.switches.s')
block_s = block_s.replace('id=f"tog-sw-{state_key.replace(\'_\', \'-\')}"', 'id=f"tog-sw-s-{state_key.replace(\'_\', \'-\')}"')
block_s = block_s.replace('hx_post=f"/api/toggle/switches.state.{state_key}"', 'hx_post=f"/api/toggle/switches.s.{state_key}"')

# Safely replace _P with _S and _p with _s for UI labels and variables
# Variables only:
vars_to_replace = [
    "hp_ap_on_off", "hp_bp_on_off", "freeboard_p", "co2_scrubber_p",
    "vhs_power_p", "uw_camera_p", "em_drop_weight_p1_sc", "em_drop_weight_p2_pc",
    "mb_p_1", "mb_p_2", "mb_p_3", "mb_p_4", "mb_p_5", "ab_p_bms", "mb_p_bms",
    "ab_p_power_selection", "mb_p_pde_p"
]

for var in vars_to_replace:
    # replace in python attribute accesses
    block_s = block_s.replace(f"sw.{var}", f"sw.{var.replace('_p', '_s')}")
    # replace in string literals (for state_key)
    block_s = block_s.replace(f'"{var}"', f'"{var.replace("_p", "_s")}"')
    
# UI Labels (we only want to replace _P with _S if it's the exact suffix or part of the name like _P1)
# Looking at the original block, the labels that have _P are:
# FreeBoard_P, Co2 scrubber_P, VHS_Power_P, UW Camera _P, Emergency Jettisoning_P, Emergency Drop Weight_P1(SC), Emergency Drop Weight_P2(PC), MB_P_1*, MB_P_2*... AB_P_BMS*
block_s = block_s.replace('FreeBoard_P', 'FreeBoard_S')
block_s = block_s.replace('scrubber_P', 'scrubber_S')
block_s = block_s.replace('Power_P', 'Power_S')
block_s = block_s.replace('Camera _P', 'Camera _S')
block_s = block_s.replace('Jettisoning_P', 'Jettisoning_S')
block_s = block_s.replace('Drop Weight_P1', 'Drop Weight_S1')
block_s = block_s.replace('Drop Weight_P2', 'Drop Weight_S2')
block_s = block_s.replace('MB_P', 'MB_S')
block_s = block_s.replace('AB_P', 'AB_S')
block_s = block_s.replace('PDE_P', 'PDE_S')
block_s = block_s.replace('CONTROL_PORT', 'CONTROL_STARBOARD')
block_s = block_s.replace('HP_AP', 'HP_AS')
block_s = block_s.replace('HP_BP', 'HP_BS')

content = content[:start_idx] + block_p + block_s + content[end_idx:]

with open("main.py", "w") as f:
    f.write(content)
