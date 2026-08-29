# Croatian legal sources — criminal law KB project

**Project**: user is building a tailored legal knowledge base + expert RAG agent on Croatian criminal law ("agent that is an expert on Croatian criminal law"). Recon complete (Aug 2026); build pending user's scope answers: which laws (KZ only vs KZ+ZKP+satellites), answer language (Croatian/English/both), interface (CLI / chat / project folder).

## Verified source status (probed live, Aug 2026)

| Source | Status | Role |
|---|---|---|
| `zakon.hr` | ✅ crawl-friendly | **PRIMARY**. Unofficial consolidated (pročišćeni tekst) versions. Static HTML, robots.txt allows all, sitemap published. |
| `narodne-novine.nn.hr` | ✅ reachable | Official gazette — authoritative verification + amendment texts. robots.txt mostly open (only a few specific Disallow entries). |
| `propisi.hr` / `zakonodavstvo.gov.hr` | ✅ reachable | Official consolidated-text portal — cross-check source. |
| `sudskapraksa.csup.hr`, `sudskapraksa.pravosudje.hr` | ❌ DNS fail (curl exit 6) | Case law — unavailable; defer (user's current scope is legislative content anyway). |

## zakon.hr law-page structure (verified on Kazneni zakon, `/z/98/kazneni-zakon`)

- **Whole law = one static HTML page** (~983KB for KZ), no pagination. Title: `<title>Kazneni zakon - Zakon.hr</title>`.
- Article number: `<p class="cms-zakon-clanak">Članak 1.</p>` (count: 414 article numbers in KZ).
- Article title (rubrum): `<p class="cms-zakon-clanak"><strong>Temelj i ograničenje kaznenopravne prisile</strong></p>` — every article emits TWO `cms-zakon-clanak` elements (number + title); total count of the class ≈ 2× article count.
- Body paragraphs: `<div><p>...</p></div>` following the title, until the next `Članak N.` marker.
- Chapters: `<h3 class="cms-zakon-h3">GLAVA PRVA (I.)&nbsp;&nbsp; TEMELJNE ODREDBE</h3>` (37 h3s; KZ has 20+ glave).
- Law text container: class `tekst-zakona`. Amendment history (`Narodne novine«, br. ...`) appears in page metadata — KZ history runs NN 125/11 → 36/24.
- Parse algorithm: iterate elements; start new article on each `Članak N.` p; next `cms-zakon-clanak` (strong) = title; plain divs = body until next number; track current h3 as `glava`.
- Sitemap: `https://www.zakon.hr/s/tmp/sitemap/sitemap.xml` is an index → per-category sub-sitemaps (`sitemap-11-*.xml` likely holds law pages).

## Agreed architecture (decided with user, not yet built)

1. **Scrape** zakon.hr laws politely (1 request per law, rate-limited) → per-article records `{law, glava, članak, title, text, NN history}` → JSON/markdown files + SQLite index.
2. **Embed locally** (free/private): `intfloat/multilingual-e5-small` or `BAAI/bge-m3` (both handle Croatian well).
3. **RAG agent**: reasoning via DeepSeek (user's default model) or LM Studio server at `192.168.1.131:1234` (only if a model is loaded there). Agent MUST cite exact članak numbers and answer only from corpus (no hallucinated statutes).
4. **Maintenance**: cron refresh to catch amendments (Croatian law changes often).

## Scope recommendation given to user

- Core: **Kazneni zakon + Zakon o kaznenom postupku** (procedure is essential for criminal-law expertise). Optional satellites: Zakon o zaštiti od nasilja u obitelji, Zakon o sudovima za mladež, prekršaji.
- Caveats to repeat: zakon.hr is unofficial (de facto standard, but verify NN references against official sources); agent is a research assistant, not a substitute for a Croatian lawyer.

## Tooling verdict (evidence-based, already delivered)

Firecrawl (hosted or self-hosted) rejected for this project: static HTML, no anti-bot, robots-friendly, and the site already pre-chunks by article — a ~50-line BeautifulSoup parser beats Firecrawl's generic chunking for legal RAG. Self-hosting Firecrawl = multi-container overhead solving problems that don't exist here.
