import json
from pathlib import Path

KEY_MAP = {
    "主题": "theme",
    "名称": "name",
    "iconId": "iconId",
    "稀有度": "rarity",
    "售价": "price",
    "效果": "effect",
    "描述": "description",
    "获取": "obtain",
    "条件": "condition",
    "备注": "notes",
    "角标": "badge",
    "可否购买": "purchasable",
}


def normalize_file(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        sections = data.get("sections") or data.get("entries") or []
    else:
        sections = data
    normalized_sections = []
    for section in sections:
        if not isinstance(section, dict):
            continue
        title = section.get("title", "")
        items = []
        for raw_item in section.get("items", []):
            item = {}
            for key, value in raw_item.items():
                mapped_key = KEY_MAP.get(key, key)
                if isinstance(value, str):
                    value = value.strip()
                item[mapped_key] = value
            item_id = str(item.pop("ID", raw_item.get("ID", ""))).zfill(3)
            item["id"] = item_id
            items.append(item)
        normalized_sections.append({"title": title, "items": items})
    return {"sections": normalized_sections}


def main():
    data_dir = Path(__file__).resolve().parent.parent / "data"
    out_dir = data_dir / "normalized"
    out_dir.mkdir(exist_ok=True)

    result = {}
    for file in ["kuiying.json", "shuiyue.json", "sami.json", "jieyuan.json"]:
        path = data_dir / file
        theme_name = path.stem
        result[theme_name] = normalize_file(path)
        (out_dir / file).write_text(json.dumps(result[theme_name], ensure_ascii=False, indent=2), encoding="utf-8")

    (out_dir / "all.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
