import re

with open("legacy/main.py", "r") as f:
    lines = f.readlines()

components = set()
for line in lines:
    matches = re.findall(r'([A-Z][a-zA-Z0-9_]+)\(', line)
    for m in matches:
        components.add(m)

print(sorted(list(components)))
