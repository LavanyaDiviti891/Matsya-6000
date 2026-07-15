import re

with open("components.py", "r") as f:
    content = f.read()

fmt_func = """
def fmt_val(val):
    try:
        return f"{float(val):.2f}"
    except (ValueError, TypeError):
        return str(val)

"""
if "def fmt_val" not in content:
    content = content.replace("import math\n", "import math\n" + fmt_func)

content = re.sub(r'str\(value\)', 'fmt_val(value)', content)
content = re.sub(r'str\((t\.[a-zA-Z_0-9]+)\)', r'fmt_val(\1)', content)
content = re.sub(r'f"\{([a-zA-Z_0-9]+):\.\df\}"', r'fmt_val(\1)', content)
content = re.sub(r'str\(int\((.*?)\)\)', r'fmt_val(\1)', content)

with open("components.py", "w") as f:
    f.write(content)
print("Done")
