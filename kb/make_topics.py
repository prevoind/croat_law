#!/usr/bin/env python3
"""Extract topical briefs from the corpus into topics/*.md.

Topics:
  pre-trial-detention: ZKP Glava VIII (rokovi) + Glava IX (mjere osiguranja
                       prisutnosti: mjere opreza, jamčevina, istražni zatvor)
  appeals:             ZKP Glava XXIII (redoviti pravni lijekovi) +
                       Glava XXIV (izvanredni pravni lijekovi)
"""
import json
from pathlib import Path

BASE = Path(__file__).parent
OUT = BASE / "topics"
OUT.mkdir(exist_ok=True)

rows = [json.loads(l) for l in (BASE / "data" / "articles.jsonl").open(encoding="utf-8")]
zkp = [r for r in rows if r["law_id"] == "ZKP" and "Prijelazne" not in r["glava"]]


def num(r):
    return int("".join(ch for ch in r["clanak"] if ch.isdigit()))


def extract(name, title, glava_filter, lo, hi, extra=()):
    arts = [r for r in zkp if glava_filter(r["glava"]) and lo <= num(r) <= hi]
    for r in extra:
        if r not in arts:
            arts.append(r)
    arts.sort(key=num)
    with (OUT / f"{name}.md").open("w", encoding="utf-8") as f:
        f.write(f"# {title}\n\nZakon o kaznenom postupku (NN 152/08 … 72/25) — consolidated on zakon.hr\n\n")
        cur = None
        for r in arts:
            if r["glava"] != cur:
                cur = r["glava"]
                f.write(f"\n## {cur}\n\n")
            ann = f" ({r['amended']})" if r.get("amended") else ""
            f.write(f"### Članak {r['clanak']}.{ann} {r['title']}\n\n{r['text']}\n\n")
    print(f"wrote {OUT / (name + '.md')} — {len(arts)} articles")


extract(
    "pre-trial-detention",
    "Pre-Trial Detention & Precautionary Measures",
    lambda g: g.startswith("Glava IX") or g.startswith("Glava VIII"),
    89, 144,
)

extract(
    "appeals",
    "Appeals & Legal Remedies (Redoviti i izvanredni pravni lijekovi)",
    lambda g: g.startswith("Glava XXIII") or g.startswith("Glava XXIV"),
    463, 519,
)
