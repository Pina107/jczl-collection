import json
from pathlib import Path

path = Path(__file__).resolve().parent.parent / "data" / "kuiying.json"
data = json.loads(path.read_text(encoding="utf-8"))

section = data["sections"][0]
item = section["items"][0]

print(section["title"])
for key, value in item.items():
    print(f"{key!r}: {value!r}")

key_list = list(item.keys())
key0 = key_list[0]
print("First key equality with '主题':", key0 == "主题")
print("Key0 code points:", [hex(ord(ch)) for ch in key0])
