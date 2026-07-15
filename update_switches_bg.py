with open('/home/blank/Documents/github/personal/niot/frontend/src/components/SwitchesLayout.jsx', 'r') as f:
    content = f.read()

# Remove realistic-panel-bg class
content = content.replace('className="realistic-panel-bg" ', '')

# Change dark text on metal to light text on dark dashboard
content = content.replace("color: '#111'", "color: '#eee'")
content = content.replace("textShadow: '1px 1px 0 #fff'", "textShadow: '1px 1px 2px #000'")
content = content.replace("boxShadow: '0 1px 1px #fff'", "boxShadow: '0 1px 1px #000'")
content = content.replace("background: '#888'", "background: '#333'")

with open('/home/blank/Documents/github/personal/niot/frontend/src/components/SwitchesLayout.jsx', 'w') as f:
    f.write(content)

