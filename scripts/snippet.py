from pathlib import Path

path = Path(__file__).resolve().parent.parent / "data" / "kuiying.json"
raw = path.read_text(encoding="utf-8")
idx = raw.find("rogue_1_relic_r01")
print(raw[idx - 80: idx + 80])
