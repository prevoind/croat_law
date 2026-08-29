---
name: web-scrape-to-rag
description: Use when scraping websites into a local RAG knowledge base.
version: 1.0.0
author: hermes
license: MIT
metadata:
  hermes:
    tags: [scraping, rag, embeddings, knowledge-base, legal]
    related_skills: [grounded-citations, huggingface-hub]
---

# Web Scrape → Local RAG Knowledge Base

## When to Use
- User asks to scrape one or more sites into a searchable corpus / knowledge base.
- User wants a Q&A agent or RAG grounded in a specific document set (statutes,
  regulations, docs, article collections).
- User is weighing a scraping service (Firecrawl etc.) against direct scraping.

Build a self-contained, queryable knowledge base from public websites:
scrape → parse at semantic units → embed locally → retrieve with citations.
Zero-LLM-token architecture: indexing and retrieval run fully local; an LLM
is used only (optionally) for answer synthesis.

## 0. Decision: direct scraping vs Firecrawl
Evaluate the source BEFORE choosing tooling:
- robots.txt open + sitemap published → the site wants crawling
- static HTML, no JS rendering → Playwright/stealth unnecessary
- semantic markup (article/section divs) → generic chunking would destroy it

If ALL three hold, direct scraping (requests + BeautifulSoup) beats Firecrawl
cloud or self-hosted: cheaper, private, preserves semantic structure. Firecrawl
earns its keep only for JS-heavy, anti-bot-protected, or unstructured sites.
(Verdict from the Croatian legal KB build: zakon.hr was static, robots-open,
and pre-chunked per article — Firecrawl would have added cost and destroyed
the structure. Self-hosting it meant Postgres+Redis+Playwright+workers to
solve problems that didn't exist.)

## 1. Recon before fetching anything
- Fetch robots.txt and sitemap; note Disallow rules (crawl budget + etiquette).
- Probe live mirrors with status/size checks; DNS failures mean find alternates.
- Grep the HTML for structural class names BEFORE writing the parser — the
  site's own markup IS your chunking plan.

## 2. Parse at semantic units, not byte counts
- One record per semantic unit (article, section), never fixed-size chunks.
- Keep hierarchy metadata per record (chapter/part/heading) for context.
- Capture amendment/version annotations if present (e.g. "(NN 125/11)").
- Strip UI noise blocks (link lists, "related" sections) — hunt for them.
- Expect duplicate unit ids from appended/transitional sections; disambiguate
  by section header or an occurrence counter.

## 3. Local embeddings (zero token cost)
- fastembed (ONNX, no torch). ALWAYS check `TextEmbedding.list_supported_models()`
  first — supported names vary per version (bge-m3 and e5-small were NOT
  supported in the pinned build; jinaai/jina-embeddings-v3 was).
- Model choice is a RETRIEVAL-LANGUAGE question, not just a corpus-language one:
  - Corpus AND queries in the same language, corpus mostly English →
    `nomic-ai/nomic-embed-text-v1.5` (8192-token ctx, ~120MB, 768-dim) is fine.
  - Queries in a DIFFERENT language than the corpus (e.g. English queries →
    Croatian statutes) → nomic FAILS: flat similarity (~0.49), wrong top hits.
    Use `intfloat/multilingual-e5-large` instead (multilingual, strong
    cross-lingual; 512-token ctx → paragraph-chunk long documents at ~3
    chars/token). e5 models need MANUAL `query: `/`passage: ` prefixes on
    query/corpus texts — fastembed does NOT add them automatically.
- AVOID `jinaai/jina-embeddings-v3` under fastembed/onnxruntime on macOS: it
  ballooned to a ~49GB physical footprint on a 32GB Mac (SIGKILL ×2, swap
  thrash) — long-sequence (8192) transformer activations at batch 64 explode
  memory. Diagnose suspected stalls with `sample <pid> 1` and read the
  "Physical footprint" line before assuming OOM vs hung.
- Batch the embed loop (batch_size arg, flush=True progress prints) so a
  killed run loses nothing and progress is visible; model files cache after
  first download so re-runs are cheap.
- Save vectors.npy + aligned JSON metadata; cosine similarity is fine up to
  ~100k rows — no FAISS/chroma needed at KB scale.

## 4. Query tool + optional LLM synthesis
- Retrieval-only mode prints ranked hits with citations (score, source, unit).
- Dedupe chunks by (source, unit-id), keep best chunk per unit.
- CROSS-LINGUAL queries (English → non-English corpus): vector-only retrieval
  is not enough — even a multilingual model ranks the right article ~#60.
  Build a HYBRID retriever:
  1. lexical leg: inverted index over chunk text (IDF), light suffix
     stemmer for the corpus language (Croatian: strip ovima/ima/oga/om/em/a/e/
     i/o/u with min-stem-length guard), plus an article-TITLE overlap boost
     (short exact-title matches beat long titles containing the term).
  2. English→corpus-language GLOSSARY expansion appended to the query
     (domain terms only; generic words like "grounds"/"penalty" cause false
     matches — keep the glossary high-precision).
  3. fuse with reciprocal-rank fusion, but weight the lexical leg ×2.5 for
     non-Croatian (i.e. non-corpus-language) queries — the vector leg is the
     weak one there. Note RRF cannot fix "great in one leg, absent in the
     other" vs "mediocre in both" — accept top-8 recall over top-1 precision;
     the LLM picks the right source from context.
  4. store/recompute chunk texts deterministically (same chunk fn at index
     and query time) so the lexical index matches what was embedded.
- LLM prompt contract: answer ONLY from retrieved sources; exact citation per
  claim; explicit "sources don't cover this" fallback; no outside knowledge.
- Reasoning-model gotcha (deepseek-v4-flash etc.): they emit
  `reasoning_content` BEFORE `content`; with a small max_tokens the budget is
  consumed by reasoning and content comes back EMPTY with
  finish_reason=length. Give reasoning models ≥6000 output tokens.
- Reuse existing credentials (e.g. read DEEPSEEK_API_KEY from ~/.hermes/.env)
  instead of asking the user for new keys.

## 5. Verify end-to-end before declaring done
- Spot-check parsed records against known facts (real article numbers/titles).
- Build a known-answer battery (question → expected source unit) and run it;
  correct your expected answers from the corpus, not from memory.
- Verify version/series metadata from the page itself — laws and docs amend.

## Pitfalls
- PYTHONPATH leak (macOS/Hermes): the Hermes shell exports PYTHONPATH pointing
  at its py3.11 venv; any new py3.13 venv then imports cp311 wheels (numpy
  ImportError). Fix: run project venvs with `PYTHONPATH= ./.venv/bin/python …`.
- fastembed: never hardcode model names; verify against list_supported_models().
- Truncation: model context must exceed the longest document (or paragraph-chunk).
- Real-world gov sites have noise blocks and duplicate section numbers — plan
  for them in the parser, don't discover them in QA.
- Background jobs: always use notify_on_complete; stale/late kill
  notifications impersonate the current job — verify against the CURRENT
  proc id. Healthy CPU-bound work shows >100% %CPU (multi-core); a stalled
  job needs `sample <pid> 1` before concluding anything.
- Never LLM-enrich the corpus (per-doc summaries/translations) — that is
  where "millions of tokens" actually goes; raw text retrieval is more
  precise and free. Only chat synthesis burns tokens.

## References
- references/croatian-criminal-law.md — source map, zakon.hr markup details,
  ZKP chapter/article map, NN series, run commands for the Croatian
  criminal-law KB project (~/hr-criminal-law-kb).
