#!/usr/bin/env python3
"""
Fetch thumbnail URLs from PRTS wiki for the embedded iconId values.

Usage:
    python scripts/fetch_icon_thumbnails.py --output thumbnails.json --size 256

Requires:
    pip install requests
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Dict, Iterable, Optional

import requests

API_ENDPOINT = "https://prts.wiki/api.php"
DATA_SCRIPT_ID = 'data-json'


def load_icon_ids(html_path: Path) -> Iterable[str]:
    raw_html = html_path.read_text(encoding="utf-8")
    pattern = rf'<script\s+id="{DATA_SCRIPT_ID}"[^>]*>(.*?)</script>'
    match = re.search(pattern, raw_html, flags=re.S | re.I)
    if not match:
        raise RuntimeError(f"Unable to locate <script id=\"{DATA_SCRIPT_ID}\"> in {html_path}")
    payload = json.loads(match.group(1))
    icon_ids = set()
    for theme in payload.values():
        for section in theme.get("sections", []):
            for item in section.get("items", []):
                icon_id = item.get("iconId") or item.get("icon_id")
                if icon_id:
                    icon_ids.add(icon_id.strip())
    return sorted(icon_ids)


def lookup_file_title(icon_id: str) -> Optional[str]:
    params = {
        "action": "query",
        "list": "prefixsearch",
        "psnamespace": 6,
        "pslimit": 1,
        "pssearch": icon_id,
        "format": "json",
    }
    response = requests.get(API_ENDPOINT, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()
    hits = data.get("query", {}).get("prefixsearch", [])
    if not hits:
        return None
    return hits[0]["title"]


def fetch_thumbnail_url(file_title: str, size: int) -> Optional[str]:
    params = {
        "action": "query",
        "titles": file_title,
        "prop": "imageinfo",
        "iiprop": "url",
        "iiurlwidth": size,
        "format": "json",
    }
    response = requests.get(API_ENDPOINT, params=params, timeout=10)
    response.raise_for_status()
    pages = response.json().get("query", {}).get("pages", {})
    for page in pages.values():
        info = page.get("imageinfo")
        if not info:
            continue
        entry = info[0]
        return entry.get("thumburl") or entry.get("url")
    return None


def build_thumbnail_map(icon_ids: Iterable[str], size: int) -> Dict[str, str]:
    results: Dict[str, str] = {}
    for icon_id in icon_ids:
        title = lookup_file_title(icon_id)
        if not title:
            print(f"[WARN] No wiki file found for iconId: {icon_id}")
            continue
        url = fetch_thumbnail_url(title, size)
        if not url:
            print(f"[WARN] No thumbnail URL returned for {title} ({icon_id})")
            continue
        results[icon_id] = url
        print(f"[OK] {icon_id} -> {url}")
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch PRTS wiki thumbnail URLs for iconId values.")
    parser.add_argument("--html", default="index.html", help="Path to the page that embeds data-json (default: index.html)")
    parser.add_argument("--output", default="thumbnails.json", help="Output JSON file to store iconId->URL mapping")
    parser.add_argument("--size", type=int, default=256, help="Thumbnail width in pixels (default: 256)")
    args = parser.parse_args()

    html_path = Path(args.html)
    icon_ids = load_icon_ids(html_path)
    print(f"Discovered {len(icon_ids)} unique iconId entries.")
    mapping = build_thumbnail_map(icon_ids, args.size)

    output_path = Path(args.output)
    output_path.write_text(json.dumps(mapping, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved {len(mapping)} thumbnail URLs to {output_path}")


if __name__ == "__main__":
    main()
