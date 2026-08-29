# Croatian legal sources (zakon.hr et al.) — verified Aug 2026

## Source inventory
- **zakon.hr** — *de facto* consolidated Croatian statutes; robots.txt wide open, sitemap published (`/s/tmp/sitemap/sitemap.xml`, per-category indexes). Static HTML, no anti-bot. Unofficial but the standard working source; official texts are in Narodne novine.
- **Narodne novine** (narodne-novine.nn.hr) — official gazette; reachable, mostly crawl-permitted.
- **propisi.hr / zakonodavstvo.gov.hr** — official consolidated-text portal (reachable).
- **Sudska praksa** (sudskapraksa.csup.hr / sudskapraksa.pravosudje.hr) — case-law portals: DNS down as of 2026-08. zakon.hr's own "SUDSKA PRAKSA:" blocks after articles are empty link labels → strip.

## Key laws & zakon.hr IDs
- **Kazneni zakon** (Criminal Code): `/z/98/kazneni-zakon` — **414 article records** (incl. deleted/"Brisan." headings), chapters GLAVA I–XXXV. NN series: 125/11, 144/12, 56/15, 61/15, 101/17, 118/18, 126/19, 84/21, 114/22, 114/23, 36/24, **136/25** (in force 13.11.2025 — rewrote KZ 190: st. 2 is now conduct-based trafficking/possession-for-sale, 3–12 yrs; "veća količina" removed), 75/26 (per earlier notes).
- **Zakon o kaznenom postupku** (Criminal Procedure Act): `/z/174/Zakon-o-kaznenom-postupku` — **678 article records** (incl. "Brisan." headings), Glava I–XXXI. NN series: 152/08, 76/09, 80/11, 121/11, 91/12, 143/12, 56/13, 145/13, 152/14, 70/17, 126/19, 130/20, 80/22, 36/24, **72/25**; newer amendment references include **13/26**.
- Related: `/z/179` Zakon o izvršavanju kazne zatvora; `/z/180` Zakon o sudovima za mladež.

## Markup & parse quirks
- Article number: `<p class="cms-zakon-clanak">Članak N.</p>`; amended articles carry `(NN ...)` annotation in the same line with per-NN links: `Članak 240. (NN 125/11, 144/12)`.
  Regex: `^Članak\s+(\d+[a-z]?)\.?(?:\s*\(([^)]*)\))?\s*(.*?)\s*$` — group 2 = amendment metadata; group 3 = trailing text. Trailing text matters: deleted articles read `Članak 271. (NN ...) Brisan.` in ONE heading p (keep them, title="Brisan."), and some headings are malformed (`Članak 164. NN 143/12)` — missing open paren; tolerate, don't skip).
- **SUDSKA PRAKSA blocks (case-law link lists)**: appear between/inside paragraphs in multiple shapes — marker+links in one `<p>`, marker in `<strong>` with links as siblings, links in their own `<p>`, or marker mid-paragraph (e.g. after st. 2). NEVER truncate at the first marker (that silently deleted st. 2+ of 125 KZ articles in the original parser). Fix: decompose `<a class="parsedCmsBlockLink">` by LINK LABEL (`Presuda|Rješenje|Odluka|Mišljenje|Zaključak|USRH|PresudaiRješenje|Rješenje USRH|Odluka USRH`) — NOT by href (amendment-number links like "76/09" share the `cms.htm` href and must survive); then strip the `SUDSKA\s+PRAKSA` marker and all trailing nodes in the element; drop elements left empty or punctuation-only.
- Article title (rubrum): following `<p class="cms-zakon-clanak"><strong>...</strong></p>`. Many ZKP articles have NO rubrum.
- Chapters: `<h3 class="cms-zakon-h3">GLAVA PRVA (I.) TEMELJNE ODREDBE</h3>` (sometimes h4).
- Law text container: class `tekst-zakona`.
- **Duplicate article numbers**: amending acts' transitional provisions (glava like "Prijelazne i završne odredbe iz NN 36/24 od 25.03.2024.") are appended with colliding numbers — 11 dups in KZ, 24 in ZKP. Filter by glava containing "Prijelazne" for clean normative text, or disambiguate citations.

## Topical map (for briefs / focused KBs)
- **Pre-trial detention (istražni zatvor)**: ZKP Glava IX, čl. 95–144 — mjere opreza (95–97), jamčevina/bail (98–104), istražni zatvor (122–139: grounds 123, order 124, release 125, competence 127, hearing 129, duration 130/133, appeal 134, execution/rights 135–141); rokovi Glava VIII (89–94).
- **Appeals**: Glava XXIII redoviti pravni lijekovi čl. 463–496 (15-day appeal, grounds 467–471, appellate powers 480–489, third-instance 490, appeals against rulings 491–496 — 3 days, suspensive by default, unlike detention appeals); Glava XXIV izvanredni pravni lijekovi čl. 497–519 (obnova/reopening 497–508 incl. ECtHR-based 30-day; zaštita zakonitosti 509–514 — only Glavni državni odvjetnik, Vrhovni sud; izvanredno preispitivanje 515–519 — 1 month, Vrhovni sud, requires prior regular appeal).

## Verification anchors (known-answer test questions)
- "penalty for murder" → KZ čl. 110 Ubojstvo (≥5 years)
- "aggravated murder" → KZ čl. 111 (≥10 years or long-term imprisonment)
- "pre-trial detention duration" → ZKP čl. 130/133
- "appeal deadline against judgment" → ZKP čl. 463 (15 days)
