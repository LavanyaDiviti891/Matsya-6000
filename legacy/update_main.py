import re

with open("main.py", "r") as f:
    content = f.read()

# Replace BottomTabsNav
content = content.replace(
    '"Switches_P",\n                "Switches_S",',
    '"Switches_P1",\n                "Switches_P2",\n                "Switches_S1",\n                "Switches_S2",'
)

# Replace generic_toggle
content = content.replace(
    'await broadcast(AppLayout(active_tab="Switches_P"))\n    await broadcast(AppLayout(active_tab="Switches_S"))',
    'await broadcast(AppLayout(active_tab="Switches_P1"))\n    await broadcast(AppLayout(active_tab="Switches_P2"))\n    await broadcast(AppLayout(active_tab="Switches_S1"))\n    await broadcast(AppLayout(active_tab="Switches_S2"))'
)

# Replace routes
routes_old = """@rt("/switches-p")
def get_switches_p():
    return Title("MATSYA 6000 View - Switches_P"), Div(
        AppLayout(active_tab="Switches_P"), id="ws-container", hx_ext="ws", ws_connect="/ws"
    )

@rt("/switches-s")
def get_switches_s():
    return Title("MATSYA 6000 View - Switches_S"), Div(
        AppLayout(active_tab="Switches_S"), id="ws-container", hx_ext="ws", ws_connect="/ws"
    )"""

routes_new = """@rt("/switches-p1")
def get_switches_p1():
    return Title("MATSYA 6000 View - Switches_P1"), Div(
        AppLayout(active_tab="Switches_P1"), id="ws-container", hx_ext="ws", ws_connect="/ws"
    )

@rt("/switches-p2")
def get_switches_p2():
    return Title("MATSYA 6000 View - Switches_P2"), Div(
        AppLayout(active_tab="Switches_P2"), id="ws-container", hx_ext="ws", ws_connect="/ws"
    )

@rt("/switches-s1")
def get_switches_s1():
    return Title("MATSYA 6000 View - Switches_S1"), Div(
        AppLayout(active_tab="Switches_S1"), id="ws-container", hx_ext="ws", ws_connect="/ws"
    )

@rt("/switches-s2")
def get_switches_s2():
    return Title("MATSYA 6000 View - Switches_S2"), Div(
        AppLayout(active_tab="Switches_S2"), id="ws-container", hx_ext="ws", ws_connect="/ws"
    )"""

content = content.replace(routes_old, routes_new)

# We also need to split Switches_P into Switches_P1 and Switches_P2
# Switches_P has col1, col2, col3, col4, col5, col6, col7.
# Let's write a regex or just split on string literals.

def split_panel(panel_code, name):
    # This function takes the block for Switches_P (or S) and splits it into P1 and P2
    
    # We want to extract col1 to col4 for P1, and col5 to col7 for P2
    # P1:
    p1_code = panel_code.split('col5 = Div(')[0]
    p1_code = p1_code.replace(f'active_tab == "{name}"', f'active_tab == "{name}1"')
    # Add switches_panel and main_content_area
    p1_code += f"""        switches_panel = Div(
            Div(col1, col2, col3, col4, style="display:grid; grid-template-columns: repeat(4, 1fr); gap: 15px; padding: 15px; overflow-y: auto; flex: 1; min-height: 0;"),
            cls="mcc-panel",
            style="display: flex; flex-direction: column;"
        )

        main_content_area = Div(
            Div(
                switches_panel,
                sidebar_col,
                cls="main-content"
            ),
            cls="main-content-wrapper"
        )
"""
    
    # P2:
    p2_code = f'    elif active_tab == "{name}2":\n'
    # we need to copy the `sw = s.switches...` and `def ToggleBlock...`
    # which is at the beginning of the panel block
    header = panel_code.split('col1 = Div(')[0]
    header = header.replace(f'elif active_tab == "{name}":', '')
    p2_code += header
    
    cols_5_7 = '        col5 = Div(' + panel_code.split('col5 = Div(')[1].split('switches_panel = Div(')[0]
    p2_code += cols_5_7
    
    p2_code += f"""        switches_panel = Div(
            Div(col5, col6, col7, style="display:grid; grid-template-columns: repeat(3, 1fr); gap: 15px; padding: 15px; overflow-y: auto; flex: 1; min-height: 0;"),
            cls="mcc-panel",
            style="display: flex; flex-direction: column;"
        )

        main_content_area = Div(
            Div(
                switches_panel,
                sidebar_col,
                cls="main-content"
            ),
            cls="main-content-wrapper"
        )
"""
    return p1_code + "\n" + p2_code

# Extract Switches_P block
start_p = content.find('    elif active_tab == "Switches_P":')
start_s = content.find('    elif active_tab == "Switches_S":')
start_else = content.find('    else:\n        main_content_area = Div(')

if start_p != -1 and start_s != -1 and start_else != -1:
    block_p = content[start_p:start_s]
    block_s = content[start_s:start_else]
    
    new_block_p = split_panel(block_p, "Switches_P")
    new_block_s = split_panel(block_s, "Switches_S")
    
    content = content[:start_p] + new_block_p + new_block_s + content[start_else:]

with open("main.py", "w") as f:
    f.write(content)

