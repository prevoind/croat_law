# Croatian Criminal Law Knowledge Base

A local, self-contained RAG knowledge base for Croatian criminal law,
built from the consolidated statutes on [zakon.hr](https://www.zakon.hr)
(robots.txt explicitly permits crawling; sitemap published).

## Contents

| File | Purpose |
|---|---|
| `scrape.py` | Fetch law pages from zakon.hr into `data/raw/` (cached, polite, 1 req/law) |
| `parse.py` | Parse HTML into article-level records → `data/articles.jsonl` + `corpus/*.md` |
| `embed.py` | Embed articles with fastembed (ONNX, no torch) → `data/vectors.npy` + `vector_meta.json` |
| `ask.py` | Query: local retrieval with citations, optional DeepSeek answer (`--llm`) |
| `make_topics.py` | Extract topical briefs (detention, appeals) into `topics/*.md` |
| `data/articles.jsonl` | 995 articles: KZ (398) + ZKP (597), each with law, glava, članak, title, amended, text |
| `corpus/kz.md`, `corpus/zkp.md` | Human-readable consolidated text, chapter-organized |

## Corpus

- **Kazneni zakon** (Criminal Code) — NN 125/11 … 36/24 — 398 articles
- **Zakon o kaznenom postupku** (Criminal Procedure Act) — NN 152/08 … 36/24 — 597 articles

Each article record: `law, law_id, url, nn (NN series), glava (chapter),
clanak (article no., incl. lettered variants), title, amended (NN of
amendments), text, full`.

## Usage

```bash
# build (after cloning):
.venv/bin/python scrape.py && .venv/bin/python parse.py
.venv/bin/python embed.py            # intfloat/multilingual-e5-large, one-time model download

# query — hybrid retrieval (vector + lexical, local, fast):
.venv/bin/python ask.py "penalty for murder in Croatia"

# query — retrieval + DeepSeek answer (reads DEEPSEEK_API_KEY from ~/.hermes/.env):
.venv/bin/python ask.py "what is pre-trial detention?" --llm
```

## Retrieval design (hybrid, all local)

- **Vector leg**: fastembed `intfloat/multilingual-e5-large` (multilingual, e5 `query:`/`passage:` prefixes).
- **Lexical leg**: inverted index with IDF, light Croatian suffix stemming, and an
  article-title overlap boost.
- **Fusion**: reciprocal-rank fusion; the lexical leg is weighted ×2.5 for non-Croatian
  (English) queries, where the cross-lingual vector leg is weak.
- **Glossary**: English→Croatian legal-term expansion in `ask.py` (`GLOSSARY`) so English
  queries can hit the statute's own wording. Add domain terms there as needed.

## Notes & caveats

- **Source**: zakon.hr is the standard *de facto* consolidated source but is
  unofficial. Official texts: Narodne novine (narodne-novine.nn.hr). The NN
  amendment series is captured per law and per amended article.
- **Embeddings run locally** (ONNX via fastembed: `intfloat/multilingual-e5-large`, 512-token ctx,
  e5 `query:`/`passage:` prefixes applied). Cross-lingual English-query → Croatian-corpus retrieval
  requires a *multilingual* model — do not use `nomic-embed-text-v1.5` (English-centric) for this.
  Avoid `jinaai/jina-embeddings-v3` via fastembed on this machine: 8192-token activations blew up
  to ~49GB RSS. Zero token cost for retrieval.
- **Chat answers** use DeepSeek (`deepseek-v4-flash`, a reasoning model — it emits
  `reasoning_content` before `content`, so give it a large `max_tokens` budget or you get
  empty answers with `finish_reason: length`). Config supports switching to a local
  endpoint (LM Studio at http://192.168.1.131:1234/v1) by changing the `--llm` call's base URL / model.
- The assistant is a research tool grounded in statute text, not legal advice.
- **PYTHONPATH pitfall**: this machine's shell leaks the Hermes venv
  (`~/.hermes/hermes-agent/venv/lib/python3.11/site-packages`) via
  `PYTHONPATH`, which breaks Python 3.13 venvs (cp311 numpy). Always run with
  `PYTHONPATH= ./.venv/bin/python ...`.

## Refresh

Re-run `scrape.py && parse.py && embed.py` to pick up amendments. The NN
series in `parse.py` should be updated when the law changes (or verify via
the page metadata).
