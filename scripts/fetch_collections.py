import json
from pathlib import Path
from typing import Dict, Any, List

import mwparserfromhell
import requests

API_URL = "https://prts.wiki/api.php"

PAGES = {
    "傀影与猩红孤钻": "傀影与猩红孤钻/珍藏陈列室",
    "水月与深蓝之渊": "水月与深蓝之渊/珍藏陈列室",
    "探索者的银凇止境": "探索者的银凇止境/珍藏陈列室",
    "岁的界园志异": "岁的界园志异/珍玩集册",
}


def fetch_wikitext(title: str) -> str:
    resp = requests.get(
        API_URL,
        params={
            "action": "parse",
            "page": title,
            "prop": "wikitext",
            "format": "json",
        },
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    if "error" in data:
        raise RuntimeError(f"Failed to fetch {title}: {data['error']}")
    return data["parse"]["wikitext"]["*"]


def clean_text(value: mwparserfromhell.wikicode.Wikicode) -> str:
    text = value.strip_code().strip()
    return text.replace("\u200b", "").replace("\xa0", " ").strip()


def parse_collection(name: str, wikitext: str) -> Dict[str, Any]:
    code = mwparserfromhell.parse(wikitext)
    sections: List[Dict[str, Any]] = []
    current_section: Dict[str, Any] | None = None

    for node in code.nodes:
        if isinstance(node, mwparserfromhell.nodes.heading.Heading):
            title = clean_text(node.title)
            if not title:
                continue
            current_section = {"title": title, "items": []}
            sections.append(current_section)
        elif isinstance(node, mwparserfromhell.nodes.template.Template):
            if not node.name.matches("收藏品"):
                continue
            if current_section is None:
                current_section = {"title": "未分组", "items": []}
                sections.append(current_section)
            item: Dict[str, Any] = {}
            for param in node.params:
                key = str(param.name).strip()
                value = clean_text(param.value)
                item[key] = value
            current_section["items"].append(item)

    return {"theme": name, "sections": sections}


def main():
    output_dir = Path(__file__).resolve().parent.parent / "data" / "normalized"
    output_dir.mkdir(parents=True, exist_ok=True)

    all_data = {}
    for theme, page in PAGES.items():
        print(f"Fetching {theme} ...")
        wikitext = fetch_wikitext(page)
        data = parse_collection(theme, wikitext)
        out_path = output_dir / f"{theme}.json"
        out_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        all_data[theme] = data

    combined_path = output_dir / "all_collections.json"
    combined_path.write_text(json.dumps(all_data, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Done. Saved to", output_dir)


if __name__ == "__main__":
    main()
