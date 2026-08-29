---
name: web-scraping
description: Use when scraping websites or building web-data KBs.
version: 1.0.0
author: hermes
license: MIT
metadata:
  hermes:
    tags: [scraping, crawling, firecrawl, robots-txt, rag, legal-kb]
    related_skills: [grounded-citations, llm-wiki, blogwatcher]
---

# Web Scraping

## When to use
- User wants to scrape/crawl sites, extract data, or build a knowledge base from web content.
- Questions about scraping tooling (Firecrawl, ScraperAPI, Playwright, custom parsers, self-hosting).

## Workflow

### 1. Recon BEFORE any tooling decision (always)
Never recommend a stack before inspecting the actual targets. Batch independent checks in parallel:
- `curl -s https://site/robots.txt` — read it, don't just check it exists; note Disallow rules and sitemap references.
- Status probe: `curl -sL -o /dev/null -w "%{http_code} | %{size_download} | final: %{url_effective}" --max-time 20 -A "Mozilla/5.0 ..."` per target.
- Save one representative page to /tmp, then inventory its markup: `grep -o 'class="[^"]*"' file | sort | uniq -c | sort -rn | head -30` — sites often pre-chunk content semantically (per-article divs, list items), which decides the whole parsing strategy.
- Check for sitemaps and official APIs before scraping.
- Always use a realistic browser User-Agent in curl.

### 2. Tool choice: Firecrawl (or similar services) vs custom parser
**Use Firecrawl when:** JS-rendered content, anti-bot protection (Cloudflare etc.), or you need its crawl/map/extract pipeline and credits are acceptable.
**Skip it (use requests/curl + BeautifulSoup/parsel) when:**
- Static HTML, robots-friendly, no anti-bot — gov/legal sites are often exactly this.
- Content is already semantically structured (e.g., one div per article) — a ~50-line parser gets perfect semantic chunks; generic chunking would destroy them.
- Privacy matters or volume would burn credits.

**Self-hosting Firecrawl** is only economical for heavy sustained volume: it's a multi-container stack (API + workers + Playwright/Chromium + Redis + Postgres/pgvector, 4-8GB RAM), the maintainers call it dev-grade not production, and its hosted stealth/anti-bot is better than self-hosted. For occasional scraping, cloud credits or a custom script beat both.

### 3. Politeness & legality
- Public info ≠ unlimited hammering. Respect robots.txt and rate limits (add small sleeps between requests).
- Legislative/legal content is public record in most jurisdictions, but site ToS can still restrict scraping.
- Note which source is authoritative vs unofficial in the KB metadata; flag it to the user.

### 4. Parsing patterns
- Inventory CSS classes first (step 1) — semantic containers often exist (`cms-zakon-clanak`-style).
- For legal/statutory content: chunk by legal hierarchy (part → chapter → article) so citations stay meaningful for RAG. Never fixed-token chunks for law.
- Sanity-check coverage by counting markers (`grep -o 'Članak [0-9]*\.' file | wc -l`).
- Extract context around a match with byte offsets: `grep -b -o 'marker' file | head` then `dd if=file bs=1 skip=N count=M`.

### 5. Finding recent news coverage when search engines block you
Plain-curl search engines (Google HTML, DuckDuckGo, Bing, Brave, Mojeek) routinely return empty/garbage. Instead:
- **Google News RSS**: `https://news.google.com/rss/search?q=<query>` — use DEFAULT params (adding `hl/gl/ceid` often returns EMPTY). The EN edition (`hl=en&gl=US&ceid=US:en`) works.
- **Sitemap greps** (most reliable): fetch the sitemap index from robots.txt, then the per-period parts, then filter `<loc>` entries for the subject keyword.
- Parse sitemaps with `re.findall(r"<loc>(.*?)</loc>", body, re.S)` per entry — the XML is often one giant line; never regex `.*?kw.*?` across the raw blob (matches whole mega-chunks).
- Shortlinks (t.co etc.): resolve with `curl -sI` and the Location header. Social video from public posts: `yt-dlp` (no auth needed).
- **HTTP/curl-first**: only reach for the browser-use CLI when direct methods fail — it needs Chrome remote-debugging approval and hits the PYTHONPATH pitfall below.

## Pitfalls
- On macOS with Hermes, `browser-use` CLI crashes at import with `pydantic_core` errors because Hermes leaks PYTHONPATH into child processes — run it as `env -u PYTHONPATH <path-to-browser-use-bin> <<'PY' ... PY` (bin lives under ~/.cache/uv/archive-v0/*/bin/).
- Sitemap indexes point to per-category sub-sitemaps — fetch the index, then the relevant sub-sitemap.
- zakon.hr search is `https://www.zakon.hr/search?q=...` (not `/Search?searchText=`); guessing `/z/<id>/` URLs silently lands on unrelated laws — always verify the page `<title>`.
- `grep -o '.\{300\}'` fails with "maximum repetition exceeds 255" — use `grep -b -o` + `dd` instead.
- perl `-0777` lazy regexes (`.*?`) can silently return nothing on huge single-line HTML; the grep+dd byte-offset approach is more reliable.
- Portals can be down (curl exit 6 = DNS fail). Check alternates, note status, don't assume permanently dead.
- Croatian law specifics: `Članak N.` markers are `p.cms-zakon-clanak`, chapter headers are `h3.cms-zakon-h3` (`GLAVA ...`).

## References
- `references/croatian-legal-sources.md` — Croatia criminal-law KB project: verified sources, zakon.hr HTML structure, agreed RAG pipeline.
