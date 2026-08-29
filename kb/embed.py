#!/usr/bin/env python3
"""Embed articles (data/articles.jsonl) into a local vector index.

Uses fastembed (ONNX runtime, no torch). Default model: BAAI/bge-m3
(8192-token context, strong multilingual retrieval). Fallback:
intfloat/multilingual-e5-small (512 tokens; long articles get
paragraph-chunked automatically).

Outputs:
  data/vectors.npy       float32 matrix [N, dim]
  data/vector_meta.json  list of article dicts aligned with rows
"""
import json
import sys
from pathlib import Path

import numpy as np

BASE = Path(__file__).parent
ARTICLES = BASE / "data" / "articles.jsonl"
OUT_VEC = BASE / "data" / "vectors.npy"
OUT_META = BASE / "data" / "vector_meta.json"

MODEL = sys.argv[1] if len(sys.argv) > 1 else "intfloat/multilingual-e5-large"
FALLBACK = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
PASSAGE_PREFIX = "passage: "
QUERY_PREFIX = "query: "
MAX_TOKENS = {
    "intfloat/multilingual-e5-large": 512,
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2": 512,
    "jinaai/jina-embeddings-v3": 8192,
    "nomic-ai/nomic-embed-text-v1.5": 8192,
}


def chunk_text(text: str, max_chars: int) -> list[str]:
    """Split over-long article text on paragraph boundaries."""
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


def main():
    from fastembed import TextEmbedding

    rows = [json.loads(l) for l in ARTICLES.open(encoding="utf-8")]
    print(f"loading {len(rows)} articles")

    model = MODEL
    try:
        emb = TextEmbedding(model_name=model)
    except Exception as e:  # model unsupported/unavailable -> fallback
        print(f"WARN {model} failed ({e}); falling back to {FALLBACK}")
        model = FALLBACK
        emb = TextEmbedding(model_name=model)

    max_chars = MAX_TOKENS.get(model, 512) * 3  # ~3 chars/token for Croatian

    texts, meta = [], []
    for r in rows:
        full = r.get("full") or r["text"]
        for i, chunk in enumerate(chunk_text(full, max_chars)):
            texts.append(PASSAGE_PREFIX + chunk)
            m = dict(r)
            m["chunk"] = i
            m["n_chunks"] = len(chunk_text(full, max_chars))
            meta.append(m)

    print(f"embedding {len(texts)} chunks with {model} ...", flush=True)
    batch_size = int(sys.argv[2]) if len(sys.argv) > 2 else 64
    vecs = []
    for i in range(0, len(texts), batch_size):
        batch = list(emb.embed(texts[i : i + batch_size]))
        vecs.append(np.asarray(batch, dtype=np.float32))
        print(f"  batch {i // batch_size + 1}/{(len(texts) + batch_size - 1) // batch_size} "
              f"({len(texts[i:i+batch_size])} chunks)", flush=True)
    vecs = np.vstack(vecs)
    np.save(OUT_VEC, vecs)
    with OUT_META.open("w", encoding="utf-8") as f:
        json.dump({"model": model, "dim": int(vecs.shape[1]), "rows": meta}, f, ensure_ascii=False)
    print(f"saved {OUT_VEC} shape={vecs.shape} -> {OUT_META}")


if __name__ == "__main__":
    main()
