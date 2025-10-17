import json
from pathlib import Path

path = Path(__file__).resolve().parent.parent / "data" / "kuiying.json"
data = json.loads(path.read_text(encoding="utf-8"))
item = data["sections"][0]["items"][0]

def fix(value: str) -> str:
    try:
        return value.encode("latin1").decode("utf-8")
    except UnicodeError:
        try:
            return value.encode("latin1").decode("gb18030")
        except UnicodeError:
            return value

for key, val in item.items():
    if isinstance(val, str):
        fixed = fix(val)
    else:
        fixed = val
    print(f"{key!r} -> {fixed!r}")
