#!/usr/bin/env python3
"""Parse zakon.hr law pages into article-level structured records.

zakon.hr markup (verified against live pages):
  <h3 class="cms-zakon-h3">GLAVA ... </h3>          -> chapter (also h4)
  <p class="cms-zakon-clanak">Članak 118.</p>       -> article number
  <p class="cms-zakon-clanak"><strong>...</strong></p> -> article title (rubrum)
  <div><p>...</p></div>                             -> body paragraphs

Output: data/articles.jsonl (one JSON object per article) + corpus/*.md
"""
import json
import re
from pathlib import Path

from bs4 import BeautifulSoup, NavigableString, Tag

BASE = Path(__file__).parent
RAW_DIR = BASE / "data" / "raw"
OUT_JSONL = BASE / "data" / "articles.jsonl"
CORPUS_DIR = BASE / "corpus"

LAWS = {
    "KZ": "Kazneni zakon",
    "ZKP": "Zakon o kaznenom postupku",
}

ART_RE = re.compile(
    r"^Članak\s+(\d+[a-z]?)\.?(?:\s*\(([^)]*)\))?\s*(.*?)\s*$"
)

# NN series: verified from the pages' own metadata (amendment history)
NN_SERIES = {
    "KZ": "NN 125/11, 144/12, 56/15, 61/15, 101/17, 118/18, 126/19, 84/21, 114/22, 114/23, 36/24, 75/26",
    "ZKP": "NN 152/08, 76/09, 80/11, 121/11, 91/12, 143/12, 56/13, 145/13, 152/14, 70/17, 126/19, 130/20, 80/22, 36/24, 72/25",
}


def extract_nn_series(soup: BeautifulSoup) -> str | None:
    """Best-effort: find the 'Narodne novine', br. ... series near the top."""
    text = soup.get_text(" ", strip=True)
    m = re.search(r"Narodne novine.{0,20}?br\.\s*([\d/.,\s]+?)\)", text[:8000])
    if m:
        return "NN " + re.sub(r"\s+", " ", m.group(1)).strip().rstrip(",")
    return None


def clean(text: str) -> str:
    text = text.replace("\xa0", " ").replace("\u200b", "")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def walk_text(el: Tag, parts: list[str]) -> None:
    """Recursively collect text of an element, one line per <p>/<li>/<div>-block."""
    for child in el.children:
        if isinstance(child, NavigableString):
            t = clean(str(child))
            if t:
                parts.append(t)
        elif isinstance(child, Tag):
            if child.name in ("p", "li", "h3", "h4", "h5", "div", "br"):
                walk_text(child, parts)
                # paragraph boundary
                if parts and not parts[-1].endswith("\n\n"):
                    parts[-1] += "\n\n"
            elif child.name in ("ul", "ol"):
                walk_text(child, parts)
            else:
                walk_text(child, parts)


def parse_law(law_id: str, html_path: Path) -> list[dict]:
    soup = BeautifulSoup(html_path.read_text(encoding="utf-8", errors="replace"), "html.parser")

    law_name = LAWS[law_id]
    url = {
        "KZ": "https://www.zakon.hr/z/98/kazneni-zakon",
        "ZKP": "https://www.zakon.hr/z/174/Zakon-o-kaznenom-postupku",
    }[law_id]
    nn = NN_SERIES.get(law_name) or extract_nn_series(soup)

    # The law text lives inside the container with class "tekst-zakona" (fall back to body)
    container = soup.find(class_="tekst-zakona") or soup.body
    assert container is not None

    articles: list[dict] = []
    cur_glava = ""
    cur = None  # dict being built
    pending_number = None
    pending_title = None

    def close_article():
        nonlocal cur
        if cur and (cur["text"] or cur["title"]):
            cur["text"] = clean(cur["text"])
            # defensive: drop any leftover standalone "SUDSKA PRAKSA" lines
            # (blocks are normally stripped/decomposed before collection)
            cur["text"] = re.sub(r"(?m)^SUDSKA\s+PRAKSA.*$", "", cur["text"])
            cur["text"] = clean(cur["text"])
            ann = f" ({cur['amended']})" if cur.get("amended") else ""
            cur["full"] = clean(
                f"Članak {cur['clanak']}.{ann}\n{cur['title']}\n\n{cur['text']}"
            )
            articles.append(cur)
        cur = None

    # zakon.hr interleaves case-law link lists between (or inside) paragraphs:
    #   <p><strong>SUDSKA PRAKSA:</strong> <a class="parsedCmsBlockLink">Presuda</a>, ...</p>
    #   <p>SUDSKA PRAKSA : <a>Presuda</a></p>
    #   <p>(2) ... SUDSKA PRAKSA <a>Presuda</a></p>
    # Sometimes marker and links sit in separate <p>s. Case-law links point to
    # zakon.hr/cms.htm (amendment-marker links point to /c/zakon/... and must be
    # kept). Strategy: drop case-law links by class+href, strip the marker and
    # everything after it in the same element, then drop emptied elements.
    sudska_re = re.compile(r"SUDSKA\s+PRAKSA", re.IGNORECASE)
    caselaw_label = re.compile(
        r"^(?:Presuda|Rješenje|Odluka|Mišljenje|Zaključak|USRH|"
        r"PresudaiRješenje|Rješenje USRH|Odluka USRH)$"
    )

    def strip_sudska_praksa(el) -> bool:
        """Remove 'SUDSKA PRAKSA ...' marker + all trailing content in-element."""
        nodes = list(el.descendants)
        for i, node in enumerate(nodes):
            if isinstance(node, NavigableString) and sudska_re.search(node):
                m = sudska_re.search(node)
                if getattr(node, "parent", None) is not None:
                    node.replace_with(node[: m.start()])
                for n in nodes[i + 1:]:
                    if getattr(n, "parent", None) is not None:
                        n.decompose()
                return True
        return False

    # Body text lives in <p>s (divs only wrap them), so process <p>s only.
    # Discriminate by LINK LABEL, not href: case-law entries are labelled
    # "Presuda"/"Rješenje"/... while amendment-marker links (also cms.htm)
    # are labelled with NN numbers ("76/09", "136/25") and must be kept.
    for el in list(container.find_all("p")):
        for a in list(el.find_all("a", class_="parsedCmsBlockLink")):
            label = a.get_text(" ", strip=True)
            if caselaw_label.match(label):
                a.decompose()
        if sudska_re.search(el.get_text(" ")):
            strip_sudska_praksa(el)
        # drop elements left empty or punctuation-only (orphaned link lists)
        if not re.sub(r"[\s,./:;·–—]", "", el.get_text(" ", strip=True)):
            el.decompose()

    for el in container.descendants:
        if not isinstance(el, Tag):
            continue
        if el.name in ("h3", "h4") and "cms-zakon-" in " ".join(el.get("class", [])):
            close_article()
            cur_glava = clean(el.get_text(" "))
            continue
        if el.name == "p" and "cms-zakon-clanak" in " ".join(el.get("class", [])):
            txt = clean(el.get_text(" "))
            m = ART_RE.match(txt)
            if m:
                close_article()
                pending_number = m.group(1)
                # trailing text in the heading (e.g. "Brisan." on deleted
                # articles, or a malformed amendment marker) becomes the title
                pending_title = clean(m.group(3) or "")
                if pending_title.startswith("NN"):
                    pending_title = ""  # malformed amendment marker, not a title
                cur = {
                    "law": law_name,
                    "law_id": law_id,
                    "url": url,
                    "nn": nn,
                    "glava": cur_glava,
                    "clanak": pending_number,
                    "title": pending_title,
                    "amended": m.group(2).strip() if m.group(2) else "",
                    "text": "",
                }
                continue
            # non-number clanak p -> the article's title (rubrum)
            if cur is not None and txt and not cur["title"]:
                cur["title"] = txt
                continue
            continue
        # body content belongs to the current article
        if cur is not None and el.name in ("p", "div", "ul", "ol", "li") and el.parent is not None:
            # only take direct text containers, avoid re-processing nested p inside div
            if el.name == "p":
                t = clean(el.get_text(" "))
                if t and t not in ("", " ", "\xa0"):
                    cur["text"] += t + "\n\n"
            elif el.name == "div" and not el.find(["p", "div"], recursive=False):
                t = clean(el.get_text(" "))
                if t:
                    cur["text"] += t + "\n\n"
    close_article()
    return articles


def main():
    all_articles = []
    for law_id, html_name in (("KZ", "kz.html"), ("ZKP", "zkp.html")):
        src = RAW_DIR / html_name
        if not src.exists():
            print(f"SKIP {law_id}: missing {src} (run scrape.py first)")
            continue
        arts = parse_law(law_id, src)
        print(f"{LAWS[law_id]}: {len(arts)} articles")
        all_articles.extend(arts)

    OUT_JSONL.parent.mkdir(parents=True, exist_ok=True)
    CORPUS_DIR.mkdir(parents=True, exist_ok=True)
    with OUT_JSONL.open("w", encoding="utf-8") as f:
        for a in all_articles:
            f.write(json.dumps(a, ensure_ascii=False) + "\n")

    # human-readable corpus, one markdown file per law
    by_law = {}
    for a in all_articles:
        by_law.setdefault(a["law"], []).append(a)
    for law, arts in by_law.items():
        slug = "kz" if law == "Kazneni zakon" else "zkp"
        with (CORPUS_DIR / f"{slug}.md").open("w", encoding="utf-8") as f:
            f.write(f"# {law}\n\n{arts[0]['nn']}\n\n")
            cur_glava = None
            for a in arts:
                if a["glava"] != cur_glava:
                    cur_glava = a["glava"]
                    f.write(f"\n## {cur_glava}\n\n")
                f.write(f"### Članak {a['clanak']}. {a['title']}\n\n{a['text']}\n\n")

    print(f"total: {len(all_articles)} articles -> {OUT_JSONL}")


if __name__ == "__main__":
    main()
