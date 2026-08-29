#!/usr/bin/env python3
"""Query the Croatian criminal-law knowledge base.

Usage:
  ask.py "question"                 -> ranked retrieval (citations only)
  ask.py "question" --llm           -> retrieval + DeepSeek answer
  ask.py "question" --llm --topk 6

Retrieval is hybrid, fully local:
  - vector leg:   fastembed (multilingual e5-large) embeddings
  - lexical leg:  keyword index over chunk text (exact statutory phrases)
  - fusion:       reciprocal-rank fusion (RRF)
  - English queries get an English->Croatian legal-term expansion so the
    lexical leg can match the statute's own wording.

The --llm answer uses DeepSeek (reads DEEPSEEK_API_KEY from env or
~/.hermes/.env; model from DEEPSEEK_MODEL env or ~/.hermes/config.yaml).
"""
import json
import os
import re
import sys
import unicodedata
from pathlib import Path

import numpy as np

BASE = Path(__file__).parent
VEC = BASE / "data" / "vectors.npy"
META = BASE / "data" / "vector_meta.json"

# English -> Croatian legal-term expansion (domain: Croatian criminal procedure).
# High-precision terms only — generic words (grounds, penalty, court, years…)
# cause false matches and are deliberately excluded.
GLOSSARY = {
    "pre-trial detention": "istražni zatvor",
    "pretrial detention": "istražni zatvor",
    "detention order": "određivanje istražnog zatvora",
    "ordered": "određivanje",
    "order": "određivanje",
    "detention": "istražni zatvor",
    "bail": "jamčevina",
    "appeal": "žalba",
    "appeals": "žalba",
    "appeal against": "žalba protiv",
    "duration": "trajanje",
    "how long": "trajanje najdulje",
    "maximum": "najdulje",
    "last": "trajati",
    "release": "ukidanje",
    "long-term imprisonment": "dugotrajni zatvor",
    "prosecution": "kazneni progon",
    "prosecutor": "državni odvjetnik",
    "state attorney": "državni odvjetnik",
    "chief state attorney": "glavni državni odvjetnik",
    "third-instance": "trećestupanjski",
    "third instance": "trećestupanjski",
    "second-instance": "drugostupanjski",
    "first-instance": "prvostupanjski",
    "statute of limitations": "zastara",
    "limitation period": "zastara",
    "trial": "rasprava",
    "judgment": "presuda",
    "convicted": "osuđenik",
    "defendant": "okrivljenik",
    "accused": "okrivljenik",
    "defense": "obrana",
    "defence": "obrana",
    "lawyer": "branitelj",
    "counsel": "branitelj",
    "victim": "žrtva",
    "witness": "svjedok",
    "evidence": "dokaz",
    "hearing": "ročište",
    "indictment": "optužnica",
    "investigation": "istraga",
    "interrogation": "ispitivanje",
    "questioning": "ispitivanje",
    "suspect": "osumnjičenik okrivljenik",
    "rights": "prava",
    "criminal complaint": "kaznena prijava",
    "report a crime": "kaznena prijava",
    "eight years": "osam godina",
    "five years": "pet godina",
    "three years": "tri godine",
    "two years": "dvije godine",
    "one year": "jednu godinu",
    "reopening": "obnova",
    "retrial": "obnova",
    "extraordinary": "izvanredni",
    "final judgment": "pravomoćna presuda",
    "supreme court": "vrhovni sud",
    "criminal offense": "kazneno djelo",
    "offense": "kazneno djelo",
    "murder": "ubojstvo",
    "aggravated murder": "teško ubojstvo",
    "theft": "krađa",
    "fraud": "prijevara",
    "robbery": "razbojništvo",
    "self-defense": "nužna obrana",
    "self-defence": "nužna obrana",
    "attempt": "pokušaj",
    "aiding": "pomaganje",
    "pre-trial": "istražni",
    "search": "pretraga",
    "warrant": "nalog o pretrazi",
    "search warrant": "nalog o pretrazi",
    "home search": "pretraga doma",
    "seizure": "oduzimanje predmeta",
    "seized": "oduzimanje predmeta",
    "wiretap": "nadzor i snimanje",
    "wiretapping": "nadzor i snimanje",
    "surveillance": "posebne dokazne radnje",
    "undercover": "prikriveni istražitelj",
    "special evidence": "posebne dokazne radnje",
    "expert": "vještak vještačenje",
    "expert witness": "vještak",
    "expertise": "vještačenje",
    "forensic": "vještačenje",
    "confession": "priznanje",
    "confessed": "priznanje",
    "deception": "obmana",
    "interrogation methods": "ispitivanje",
    "witness statement": "iskaz svjedoka",
    "read at trial": "čitanje zapisnika",
    "trial record": "zapisnik",
    "illegal": "nezakoniti",
    "illegally obtained": "nezakoniti dokazi",
}


CRO_SUFFIXES = [
    "ovima", "evima", "stava", "stva", "ama", "ima", "oga", "ome",
    "om", "em", "oj", "iju", "ije", "ju", "a", "e", "i", "o", "u",
]


def light_stem(word: str) -> str:
    """Aggressive-but-guarded suffix stripper for Croatian inflectional endings."""
    if len(word) <= 4:
        return word
    for suf in CRO_SUFFIXES:
        if word.endswith(suf) and len(word) - len(suf) >= 3:
            return word[: -len(suf)]
    return word


def tokenize(text: str) -> list[str]:
    """Lowercase tokenizer with light Croatian stemming (diacritics intact)."""
    text = unicodedata.normalize("NFC", text.lower())
    return [light_stem(t) for t in re.findall(r"[\w\u00C0-\u017F]+", text)]


def expand_question(question: str) -> str:
    """Append Croatian legal terms for English queries so lexical leg can match."""
    q = question
    for en, hr in GLOSSARY.items():
        if re.search(rf"\b{re.escape(en)}\b", question, re.IGNORECASE):
            q += f" {hr}"
    return q


class LexicalIndex:
    """Inverted index with title-match boost: token -> [(chunk_idx, tf)]."""

    def __init__(self, texts: list[str], titles: list[str]):
        self.df: dict[str, int] = {}
        self.postings: dict[str, list[tuple[int, int]]] = {}
        self.n_docs = len(texts)
        self.title_tokens = [set(tokenize(t)) for t in titles]
        for i, t in enumerate(texts):
            seen = set()
            for tok in tokenize(t):
                if tok not in seen:
                    seen.add(tok)
                    self.df[tok] = self.df.get(tok, 0) + 1
                lst = self.postings.setdefault(tok, [])
                if lst and lst[-1][0] == i:
                    lst[-1] = (i, lst[-1][1] + 1)
                else:
                    lst.append((i, 1))

    def score(self, query_tokens: list[str]) -> np.ndarray:
        qt = set(query_tokens)
        scores = np.zeros(self.n_docs, dtype=np.float64)
        for tok in qt:
            df = self.df.get(tok, 0)
            if not df:
                continue
            idf = np.log((self.n_docs + 1) / (df + 0.5))
            for idx, tf in self.postings.get(tok, []):
                scores[idx] += idf * (1 + np.log(tf))
        # title boost: exact title overlap is the strongest citation signal
        for idx, tt in enumerate(self.title_tokens):
            ov = qt & tt
            if ov and tt:
                scores[idx] += 2.0 * len(ov) / len(tt)
        return scores


MAX_TOKENS = {
    "intfloat/multilingual-e5-large": 512,
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2": 512,
    "jinaai/jina-embeddings-v3": 8192,
    "nomic-ai/nomic-embed-text-v1.5": 8192,
}


def chunk_text(text: str, max_chars: int) -> list[str]:
    """Mirror of embed.py: paragraph-boundary chunking."""
    if len(text) <= max_chars:
        return [text]
    paras = [p for p in text.split("\n\n") if p.strip()]
    chunks, cur = [], ""
    for p in paras:
        if cur and len(cur) + len(p) > max_chars:
            chunks.append(cur.strip())
            cur = p
        else:
            cur = f"{cur}\n\n{p}".strip()
    if cur:
        chunks.append(cur)
    return chunks


def load_index():
    with META.open(encoding="utf-8") as f:
        meta = json.load(f)
    vecs = np.load(VEC)
    rows = meta["rows"]
    max_chars = MAX_TOKENS.get(meta["model"], 512) * 3
    chunk_texts = []
    for r in rows:
        full = r.get("full") or r["text"]
        chunks = chunk_text(full, max_chars)
        chunk_texts.append(chunks[r["chunk"]] if r["chunk"] < len(chunks) else full)
    lex = LexicalIndex(chunk_texts, [r["title"] for r in rows])
    return meta, vecs, lex


def retrieve(question: str, topk: int = 8):
    from fastembed import TextEmbedding

    meta, vecs, lex = load_index()
    emb = TextEmbedding(model_name=meta["model"])

    # vector leg
    qtext = question
    if meta["model"].startswith("intfloat/") or meta["model"].startswith("sentence-transformers/paraphrase"):
        qtext = "query: " + question
    q = np.asarray(next(emb.embed([qtext])), dtype=np.float32)
    q = q / (np.linalg.norm(q) + 1e-9)
    norms = np.linalg.norm(vecs, axis=1, keepdims=True)
    sims = (vecs @ q) / (norms[:, 0] + 1e-9)

    # lexical leg (with English->Croatian expansion)
    q_exp = expand_question(question)
    lex_scores = lex.score(tokenize(q_exp))

    # reciprocal rank fusion; boost the lexical leg for non-Croatian queries,
    # where the (multilingual) vector leg is the weak one
    lex_weight = 2.5 if not re.search(r"[čćžšđČĆŽŠĐ]", question) else 1.0
    k = 60
    vec_order = np.argsort(-sims)[:200]
    lex_order = np.argsort(-lex_scores)[:200]
    rrf = {}
    for rank, idx in enumerate(vec_order):
        rrf[idx] = rrf.get(idx, 0) + 1.0 / (k + rank + 1)
    for rank, idx in enumerate(lex_order):
        rrf[idx] = rrf.get(idx, 0) + lex_weight / (k + rank + 1)

    seen, hits = set(), []
    for idx in sorted(rrf, key=rrf.get, reverse=True):
        row = meta["rows"][idx]
        key = (row["law_id"], row["clanak"])
        if key in seen:
            continue
        seen.add(key)
        hits.append((float(sims[idx]), idx, row, rrf[idx]))
        if len(hits) >= topk:
            break
    return hits


def render_hit(score: float, row: dict) -> str:
    ann = f" ({row['amended']})" if row.get("amended") else ""
    head = f"[{row['law_id']} čl.{row['clanak']}{ann}] {row['title']} — {row['law']} (Glava: {row['glava']})"
    text = row["text"].replace("\n\n", "\n")
    if len(text) > 900:
        text = text[:900] + " …"
    return f"{head}\n{text}"


def build_prompt(question: str, hits) -> str:
    ctx = "\n\n".join(
        f"=== SOURCE {i+1}: {h[2]['law']}, članak {h[2]['clanak']}. {h[2]['title']} "
        f"(Glava: {h[2]['glava']}) ===\n{h[2]['full']}"
        for i, h in enumerate(hits)
    )
    return f"""You are an expert assistant on Croatian criminal law, grounded ONLY in the statute text provided below (Kazneni zakon and Zakon o kaznenom postupku, as consolidated on zakon.hr).

Rules:
- Answer in English. Quote Croatian legal terms in parentheses when relevant.
- Base every claim on the provided articles and cite them as (KZ, čl. N) or (ZKP, čl. N). Never cite an article that is not in the sources.
- If the sources do not answer the question, say so clearly instead of guessing.
- If the question asks about a penalty, give the exact statutory range and any conditions (attempt, aiding, etc.) only if stated in the sources.
- Do not give general legal advice beyond what the statute text supports.

Question: {question}

=== STATUTE SOURCES ===
{ctx}
"""


def get_deepseek_config() -> tuple[str, str]:
    key = os.environ.get("DEEPSEEK_API_KEY", "")
    env_file = Path.home() / ".hermes" / ".env"
    if not key and env_file.exists():
        for line in env_file.read_text().splitlines():
            if line.startswith("DEEPSEEK_API_KEY="):
                key = line.split("=", 1)[1].strip().strip('"').strip("'")
                break
    model = os.environ.get("DEEPSEEK_MODEL", "")
    cfg = Path.home() / ".hermes" / "config.yaml"
    if not model and cfg.exists():
        m = re.search(r"^\s*default:\s*(\S+)", cfg.read_text(), re.MULTILINE)
        if m:
            model = m.group(1)
    return key, model or "deepseek-chat"


def llm_answer(question: str, hits) -> str:
    import urllib.request

    key, model = get_deepseek_config()
    if not key:
        return "ERROR: DEEPSEEK_API_KEY not found (env or ~/.hermes/.env)"
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": build_prompt(question, hits)},
            {"role": "user", "content": question},
        ],
        "temperature": 0.1,
        "max_tokens": 6000,  # deepseek-v4-flash is a reasoning model: reasoning_content + answer both draw on this
    }
    req = urllib.request.Request(
        "https://api.deepseek.com/chat/completions",
        data=json.dumps(payload).encode(),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {key}",
        },
    )
    with urllib.request.urlopen(req, timeout=120) as r:
        resp = json.loads(r.read().decode())
    return resp["choices"][0]["message"]["content"]


def main():
    import argparse

    ap = argparse.ArgumentParser(description="Query the Croatian criminal-law KB")
    ap.add_argument("question")
    ap.add_argument("--topk", type=int, default=8)
    ap.add_argument("--llm", action="store_true", help="also produce a DeepSeek answer")
    args = ap.parse_args()

    hits = retrieve(args.question, topk=args.topk)
    print(f"TOP {len(hits)} SOURCES for: {args.question}\n")
    for score, _, row, rrf in hits:
        print(f"score={score:.3f} rrf={rrf:.3f}  {render_hit(score, row)}\n")

    if args.llm:
        print("=" * 70)
        print("DEEPSEEK ANSWER\n")
        print(llm_answer(args.question, hits))


if __name__ == "__main__":
    main()
