import argparse
import json
import sys
from pathlib import Path


def parse_wiki(raw_text: str, default_section: str | None = None, stop_headings: list[str] | None = None):
    lines = raw_text.splitlines()
    sections: list[dict] = []
    current_section: dict | None = None

    if default_section:
        current_section = {"title": default_section, "entries": []}
        sections.append(current_section)

    theme_name: str | None = None

    it = iter(range(len(lines)))
    idx = 0
    while idx < len(lines):
        raw_line = lines[idx]
        stripped = raw_line.strip()

        if not stripped:
            idx += 1
            continue

        if stripped.startswith("==") and stripped.endswith("=="):
            heading = stripped.strip("=").strip()
            if stop_headings and any(stop in heading for stop in stop_headings):
                break
            current_section = {"title": heading, "entries": []}
            sections.append(current_section)
            idx += 1
            continue

        if stripped.startswith("{{收藏品"):
            block = [raw_line]
            idx += 1
            while idx < len(lines):
                block_line = lines[idx]
                block.append(block_line)
                if block_line.strip().endswith("}}"):
                    idx += 1
                    break
                idx += 1

            entry_data = parse_block(block)
            if not theme_name and entry_data.get("主题"):
                theme_name = entry_data["主题"]

            if current_section is None:
                # If no section encountered yet, group into unnamed section ordered by IDs
                current_section = {"title": default_section or "未分组", "entries": []}
                sections.append(current_section)

            current_section["entries"].append(normalize_entry(entry_data))
            continue

        idx += 1

    return {
        "theme": theme_name or "",
        "sections": sections,
    }


def parse_block(block_lines: list[str]) -> dict:
    data: dict[str, str] = {}
    current_key: str | None = None

    for raw in block_lines[1:]:
        stripped = raw.strip()
        if stripped == "}}":
            break

        if stripped.startswith("|"):
            content = stripped.lstrip("|")
            parts = content.split("|")
            for part in parts:
                if not part:
                    continue
                if "=" in part:
                    key, value = part.split("=", 1)
                    key = key.strip()
                    value = value.strip()
                    data[key] = value
                    current_key = key
                else:
                    data[part.strip()] = ""
                    current_key = part.strip()
        else:
            if current_key:
                existing = data.get(current_key, "")
                if existing:
                    data[current_key] = f"{existing}\n{stripped}"
                else:
                    data[current_key] = stripped

    return data


KNOWN_FIELD_MAP = {
    "ID": "id",
    "名称": "name",
    "iconId": "iconId",
    "稀有度": "rarity",
    "售价": "price",
    "效果": "effect",
    "描述": "description",
    "条件": "condition",
    "获取": "obtain",
    "可否购买": "purchasable",
    "备注": "notes",
    "角标": "badge",
    "可否购买=": "purchasable",
    "可否购买？": "purchasable",
}


def normalize_entry(raw_entry: dict) -> dict:
    entry: dict = {}
    extra: dict = {}

    for key, value in raw_entry.items():
        if key == "主题":
            # handled at top level
            continue

        mapped = KNOWN_FIELD_MAP.get(key)
        if mapped:
            entry[mapped] = value
        else:
            extra[key] = value

    if "rarity" in entry:
        entry["rarity"] = parse_int(entry["rarity"])

    if extra:
        entry["extra"] = extra

    return entry


def parse_int(value: str):
    try:
        return int(value)
    except (ValueError, TypeError):
        return value


def main():
    parser = argparse.ArgumentParser(description="Convert Arknights wiki relic data to JSON.")
    parser.add_argument("--input", required=True, help="Path to the raw wiki text file.")
    parser.add_argument("--output", required=True, help="Path to write the JSON output.")
    parser.add_argument("--default-section", required=False, help="Title for entries before first heading.")
    parser.add_argument("--theme", required=False, help="Override theme name.")
    parser.add_argument(
        "--stop-heading",
        action="append",
        dest="stop_headings",
        help="Heading keyword that stops parsing (e.g., 图标差异). Can be provided multiple times.",
    )

    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    raw_text = input_path.read_text(encoding="utf-8")
    parsed = parse_wiki(raw_text, default_section=args.default_section, stop_headings=args.stop_headings)

    if args.theme:
        parsed["theme"] = args.theme

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(parsed, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
