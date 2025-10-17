import json
from pathlib import Path
from collections import Counter

def inspect(path: Path):
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        sections = data.get("sections", [])
    else:
        sections = data

    key_counter = Counter()
    for section in sections:
        if isinstance(section, dict):
            items = section.get("items") or section.get("entries") or section.get("data") or []
        else:
            items = []
        for item in items:
            if isinstance(item, dict):
                key_counter.update(item.keys())
    print(f"=== Keys in {path.name} ===")
    for key, count in key_counter.most_common():
        print(f"{key!r} ({count}) -> {[hex(ord(ch)) for ch in key]}")

if __name__ == "__main__":
    base = Path(__file__).resolve().parent.parent / "data"
    for file in base.glob("*.json"):
        inspect(file)
