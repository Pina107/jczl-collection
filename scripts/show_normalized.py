import json
from pathlib import Path

path = Path(__file__).resolve().parent.parent / "data" / "normalized" / "kuiying.json"
data = json.loads(path.read_text(encoding="utf-8"))
print(data["sections"][0]["items"][0])
