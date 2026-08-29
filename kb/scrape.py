#!/usr/bin/env python3
"""Scrape Croatian criminal-law statutes from zakon.hr into local HTML cache.

Polite: one request per law, cached on disk, identifiable UA, small delay.
"""
import time
import urllib.request
from pathlib import Path

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) hr-criminal-law-kb/0.1 (personal research; robots.txt respected)"

LAWS = [
    {
        "id": "KZ",
        "name": "Kazneni zakon",
        "url": "https://www.zakon.hr/z/98/kazneni-zakon",
    },
    {
        "id": "ZKP",
        "name": "Zakon o kaznenom postupku",
        "url": "https://www.zakon.hr/z/174/Zakon-o-kaznenom-postupku",
    },
]

RAW_DIR = Path(__file__).parent / "data" / "raw"


def fetch(url: str, dest: Path) -> bool:
    if dest.exists() and dest.stat().st_size > 50_000:
        print(f"  cached: {dest} ({dest.stat().st_size} bytes)")
        return False
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    print(f"  fetching {url}")
    with urllib.request.urlopen(req, timeout=60) as r:
        body = r.read()
    dest.write_bytes(body)
    print(f"  saved {len(body)} bytes -> {dest}")
    time.sleep(1.0)  # polite delay between requests
    return True


def main():
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    for law in LAWS:
        dest = RAW_DIR / f"{law['id'].lower()}.html"
        fetch(law["url"], dest)


if __name__ == "__main__":
    main()
