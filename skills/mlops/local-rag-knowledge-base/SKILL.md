---
name: local-rag-knowledge-base
description: "Use when building a local RAG KB from scraped websites."
version: 1.0.0
author: hermes-curator
license: CC-BY-4.0
metadata:
  hermes:
    tags: [rag, embeddings, scraping, knowledge-base, fastembed, retrieval]
    related_skills: [product-price-monitor, blogwatcher, arxiv]
---

# Local RAG Knowledge Base

Turn a set of websites/documents into a queryable, citation-grounded Q&A corpus — fully local except optional LLM answer synthesis. Proven on a Croatian legal corpus (zakon.hr, 995 articles) but generalizes to any document class with semantic structure (legislation, docs sites, manuals).

## When to use
- "Scrape some websites" into a knowledge base / expert agent
- RAG over public documents; agent that answers from a corpus with citations
- Any "build me a tailored knowledge base" request

## Pipeline (follow in order)

1. **Recon before choosing tooling** (cheap, decisive — never skip):
   - `curl -s <site>/robots.txt` — crawling allowed? Respect it (also check sitemap.xml).
   - Probe target pages: HTTP status + size (`curl -sL -o /dev/null -w "%{http_code} %{size_download}"`).
   - Inspect HTML structure: count class patterns (`grep -o 'class="[^"]*"' | sort | uniq -c`). Is it static HTML with semantic markup? JS-rendered?
   - Decision rule: **static HTML + semantic containers → custom parser** (requests + BeautifulSoup, ~50 lines) beats Firecrawl/Playwright/Scrapy. Firecrawl's value (JS rendering, stealth, LLM extraction) is irrelevant on robots-friendly static sites, and its generic chunking destroys semantic structure.
   - Use a real browser UA, ~1s delay, cache raw HTML to disk.

2. **Parse into semantic units, not fixed-size chunks**:
   - Find the site's own semantic containers (articles, sections, chapters) in the HTML classes and chunk by them — this is free, perfect chunking.
   - Extract metadata alongside text: source, chapter, item number, title, amendment/version info.
   - Strip UI noise (e.g., link-label lists appended to content blocks). **Pitfall found on zakon.hr (Aug 2026)**: "SUDSKA PRAKSA:" case-law link blocks appear BETWEEN (or inside) article paragraphs, in several DOM shapes — marker+links in one `<p>`, marker in `<strong>` with links as siblings, links alone in their own `<p>`, or marker mid-paragraph. A parser that truncates text at the first marker (or only handles one shape) silently DROPS every later paragraph — 125/387 KZ articles were affected. Robust fix: decompose `<a class="parsedCmsBlockLink">` by LINK LABEL (Presuda/Rješenje/Odluka/Mišljenje/Zaključak/USRH variants — NOT by href: amendment-number links like "76/09" share the cms.htm href and must be kept), strip the "SUDSKA PRAKSA" marker + all trailing nodes in the same element, drop elements left empty/punctuation-only, and keep a per-line defensive regex.
   - Watch for duplicate numbering (e.g., amending acts' transitional provisions) — filter or disambiguate.
   - Spot-check parsed output against known content before proceeding.

3. **Embed locally with fastembed** (ONNX, no torch; ~100MB install):
   - Model names differ from HF: always check `TextEmbedding.list_supported_models()` first — unsupported names raise at init.
   - **Cross-lingual rule**: English queries over a non-English corpus REQUIRE a multilingual model (`intfloat/multilingual-e5-large`, `paraphrase-multilingual-MiniLM-L12-v2`). English-centric models (nomic-embed-text-v1.5) return flat scores (~0.5) and wrong hits — the #1 silent failure in cross-lingual RAG.
   - e5-family needs `query: ` / `passage: ` prefixes — fastembed does NOT add them; prepend at embed and query time (store model name in index meta to branch on it).
   - Long-context models are memory traps: jina-embeddings-v3 via fastembed hit ~49GB RSS on 8192-token sequences at batch 64 (sequence-length × batch × layers activations). Use small batches or lighter models on 32GB machines.
   - Pass `batch_size` explicitly (e.g., 64); print per-batch progress with `flush=True`.
   - Model downloads come from HF Hub (unauthenticated = slower; fine).

4. **Index + retrieve** (no vector DB needed under ~10k chunks):
   - `vectors.npy` (float32) + `vector_meta.json` (row-aligned dicts: model, dim, rows[]). np.save + json.
   - Cosine similarity (normalize query + rows); dedupe hits by (source, item id) keeping best chunk per item; top-k 6–10.
   - Known-answer retrieval test BEFORE declaring done: e.g. "penalty for murder" → expect the murder article at top with score separation. Flat scores = wrong model or missing prefixes.

5. **Agent with citations**:
   - Retrieval-only mode (print ranked hits) + `--llm` mode stuffing retrieved chunks into the system prompt.
   - Prompt rules: answer ONLY from provided sources, cite exact identifiers, say "not in sources" rather than guessing, quote original-language terms in parentheses.
   - Reuse the user's existing LLM credentials (see pitfalls) instead of asking for new keys; make engine an env-var switch (cloud vs local endpoint).

## Pitfalls
- **Hermes PYTHONPATH leak (this user's machine)**: shell exports `PYTHONPATH=~/.hermes/hermes-agent:.../venv/lib/python3.11/site-packages`, leaking a cp311 numpy into py3.13 venvs → "Importing the numpy C-extensions failed" / `_multiarray_umath.cpython-311-darwin.so`. ALWAYS run project venvs with `PYTHONPATH= ./.venv/bin/python ...`. Polluted venv fix: `PYTHONPATH= pip install --no-cache-dir --force-reinstall numpy <pkgs>`.
- **Background process output buffering**: piping a python job through `grep` hides stdout progress (buffered). Watch the OUTPUT FILE (mtime) or `ps %CPU` instead of poll output.
- **SIGKILL'd embeds**: check `sample <pid>` "Physical footprint" before assuming OOM — a single process at 49GB on a 32GB machine explains kills even when "system free" looks OK. Fix the memory source, not the retry count.
- **json.loads on a file handle** (`json.loads(open(...))`) — use `json.load(f)`; easy to hit when building query tools.
- Background long jobs: use `background=true` + `notify_on_complete=true`; don't burn turns polling.

## Verification checklist
- [ ] robots.txt respected; polite fetch with cache
- [ ] parse spot-checked (article numbers/titles match known content)
- [ ] embedding model multilingual if cross-lingual queries expected
- [ ] known-answer retrieval test passes (right item at top, score separation)
- [ ] LLM answer cites real identifiers from the corpus

## Support files
- `references/croatian-legal-sources.md` — zakon.hr / Narodne novine specifics: markup, parse quirks, NN amendment series, topical maps (detention, appeals)
