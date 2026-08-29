#!/usr/bin/env python3
"""Extract pre-trial evidence rules brief from the corpus.

Focus: evidence rules specific to the PRE-TRIAL phase (izvidi + istraga)
and the suspect's status before indictment, incl. the unlawful-evidence
rule and its detention interplay.

Included:
  - ZKP cl.10 (nezakoniti dokazi, Glava I)
  - Glava XVI IZVIDI I ISTRAZIVANJE (204-215)
  - Glava XVII ISTRAGA (216-239)
  - Glava XVIII general evidence-action rules (240-243) + examination of
    the accused (274-279); other dokazne radnje are listed in a summary
    section with article ranges only.
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


def pick(pred):
    return sorted([r for r in zkp if pred(r)], key=num)


selected = []
# cl. 10 unlawful evidence
selected += pick(lambda r: r["clanak"] == "10")
# Glava XVI izvidi
selected += pick(lambda r: 204 <= num(r) <= 215)
# Glava XVII istraga
selected += pick(lambda r: 216 <= num(r) <= 239)
# Glava XVIII: general rules + examination of the accused
selected += pick(lambda r: 240 <= num(r) <= 243 or 274 <= num(r) <= 279)

with (OUT / "evidence-pre-trial.md").open("w", encoding="utf-8") as f:
    f.write("# Pre-Trial Evidence Rules (izvidi, istraga, dokazne radnje)\n\n")
    f.write("Zakon o kaznenom postupku (NN 152/08 … 72/25) — consolidated on zakon.hr.\n")
    f.write("Scope: evidence rules specific to the pre-trial phase and the suspect's\n")
    f.write("status before indictment.\n\n")
    cur = None
    for r in selected:
        if r["glava"] != cur:
            cur = r["glava"]
            f.write(f"\n## {cur}\n\n")
        ann = f" ({r['amended']})" if r.get("amended") else ""
        f.write(f"### Članak {r['clanak']}.{ann} {r['title']}\n\n{r['text']}\n\n")
    # summary of the remaining dokazne radnje
    f.write("## Other dokazne radnje (Glava XVIII) — article ranges only\n\n")
    f.write("244-256 examination of witnesses · 257-266 expertise · 267-268 "
            "suočenje · 269-273 recognition, očevid, reconstruction, inspection "
            "· 280-301 further witness/expert rules · 302-306 recognition & "
            "confrontation · 307-329 searches (dom, osoba, računala) · 330-338 "
            "temporary seizure of objects/files · 332-340 special evidence "
            "actions (surveillance, undercover, data seizure).\n")
print(f"wrote {OUT / 'evidence-pre-trial.md'} — {len(selected)} articles")
