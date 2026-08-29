#!/usr/bin/env python3
"""QA check for the Croatian law KB corpus: find articles truncated by the
zakon.hr 'SUDSKA PRAKSA' link-list parsing bug.

Usage: python3 check_corpus_truncation.py [kb_dir]   (default ~/hr-criminal-law-kb)

Compares per-article paragraph ((N)) counts between corpus/<law>.md and
data/raw/<law>.html for both kz and zkp. Any corpus article with fewer
paragraphs than raw is truncated (the parser dropped text after the first
'SUDSKA PRAKSA: Presuda, Rješenje, ...' link list inside the article).

Known state (Aug 2026): KZ 125/387 articles affected, ZKP 22 affected —
including KZ Art 190 (only st. 1 of 9 kept) and ZKP Art 133 (detention
durations). Fix for the pipeline: strip SUDSKA PRAKSA blocks from the raw
HTML before parsing, e.g. re.sub(r'SUDSKA PRAKSA:.*?(?=<p|<h2|Članak N)', '',
raw, flags=re.S), then re-run parse + embed.

Stdlib only; exit code 1 when truncation is found.
"""
import re
import os
import sys

KB = os.path.expanduser(sys.argv[1] if len(sys.argv) > 1 else "~/hr-criminal-law-kb")


def html_to_text(raw: str) -> str:
    raw = re.sub(r"<script.*?</script>", " ", raw, flags=re.S)
    raw = re.sub(r"<style.*?</style>", " ", raw, flags=re.S)
    raw = re.sub(r"<[^>]+>", " ", raw)
    return re.sub(r"\s+", " ", raw)


def raw_segment(raw_txt: str, num: int) -> str:
    """Return the raw text of article num, up to the next article."""
    m = re.search(r"Članak %d\.(?!\d)" % num, raw_txt)
    if not m:
        return None
    nxt = re.search(r"Članak \d+\.(?!\d)", raw_txt[m.end():])
    end = m.end() + (nxt.start() if nxt else 4000)
    return raw_txt[m.start():end]


def check(law: str):
    corpus_path = os.path.join(KB, "corpus", law + ".md")
    raw_path = os.path.join(KB, "data", "raw", law + ".html")
    if not (os.path.exists(corpus_path) and os.path.exists(raw_path)):
        print(f"[{law}] missing corpus or raw file — skipped")
        return 0
    corpus = open(corpus_path, encoding="utf-8").read()
    raw = html_to_text(open(raw_path, encoding="utf-8", errors="replace").read())

    bad = []
    for chunk in re.split(r"(?=### Članak )", corpus):
        m = re.match(r"### Članak (\d+)\.", chunk)
        if not m:
            continue
        num = int(m.group(1))
        c_st = len(re.findall(r"\(\d+\)", chunk))
        seg = raw_segment(raw, num)
        r_st = len(re.findall(r"\(\d+\)", seg)) if seg else 0
        if c_st < r_st:
            bad.append((num, c_st, r_st))

    print(f"[{law}] {len(bad)} truncated articles of {len(re.findall(r'### Članak \\d+\\.', corpus))} in corpus")
    for num, c, r in bad[:15]:
        print(f"   Art {num}: corpus {c} st. vs raw {r} st.")
    if len(bad) > 15:
        print(f"   ... and {len(bad) - 15} more")
    return 1 if bad else 0


if __name__ == "__main__":
    rc = 0
    for law in ("kz", "zkp"):
        rc |= check(law)
    sys.exit(rc)
