# Croatian Criminal Law KB — sources, markup, and article maps

Project: `~/hr-criminal-law-kb` — local RAG KB for Croatian criminal law
(Kazneni zakon + Zakon o kaznenom postupku, 995 articles).
Pipeline: `scrape.py` → `parse.py` → `embed.py` → `ask.py` (see project README).
User's focus topics: pre-trial detention (istražni zatvor) and appeals.

## Sources (verified live, Aug 2026)
- **zakon.hr** — consolidated statutes; robots.txt wide open, sitemap
  published (`/s/tmp/sitemap/sitemap.xml` index). PRIMARY source.
- **narodne-novine.nn.hr** — official gazette; reachable, mostly crawl-permitted.
  Use for official verification of NN series.
- **propisi.hr / zakonodavstvo.gov.hr** — official consolidated-text portal;
  reachable.
- **sudskapraksa.csup.hr / sudskapraksa.pravosudje.hr** — case-law portals
  DNS-failed (down or moved); case law deferred.

## Law URLs (zakon.hr)
- Kazneni zakon (KZ): `/z/98/kazneni-zakon`
- Zakon o kaznenom postupku (ZKP): `/z/174/Zakon-o-kaznenom-postupku`
- Satellites (not yet in KB): izvršavanje kazne zatvora `/z/179`,
  sudovi za mladež `/z/180`

## zakon.hr HTML structure (verified)
- Chapter header: `<h3 class="cms-zakon-h3">GLAVA PRVA (I.) …</h3>` (also h4)
- Article number: `<p class="cms-zakon-clanak">Članak 118.</p>` — amended
  articles carry annotation: `Članak 240. (NN 125/11, 144/12)` with links
  inside; `get_text()` flattens them. Regex: `^Članak\s+(\d+[a-z]?)\.?(?:\s*\(([^)]*)\))?\s*$`
- Article title (rubrum): `<p class="cms-zakon-clanak"><strong>…</strong></p>`
- Body: `<div><p>…</p></div>` paragraphs; article = number + title + body
  until next `Članak N.` or chapter header.
- **Noise**: "SUDSKA PRAKSA: Presuda, Rješenje, …" link-label block appended
  to many articles — strip from `SUDSKA PRAKSA:` onward (no useful content).
- **Duplicate article numbers**: amending acts' "Prijelazne i završne odredbe"
  (transitional provisions) reuse main-law numbers; their glava is e.g.
  "Prijelazne i završne odredbe iz NN 36/24 od 25.03.2024." KZ had 11 dup
  numbers, ZKP 24. Exclude or disambiguate for clean citations.
- ZKP articles mostly have NO titles (empty rubrum); lettered variants exist
  ("123.b", "98.a").

## ZKP chapter map (article ranges as parsed)
- Glava VIII ROKOVI 89–94 · Glava IX MJERE OSIGURANJA PRISUTNOSTI 95–144
  (mjere opreza 95–97, jamčevina ~98–104, istražni zatvor 122–139)
- Glava XVI IZVIDI I ISTRAŽIVANJE 204–215 · Glava XVII ISTRAGA 216–239 ·
  Glava XVIII DOKAZNE RADNJE 240–340 (pretrage 240–250, ispitivanje
  okrivljenika 272–282, suočenje 278–279, posebne radnje 332–340)
- Glava XXIII REDOVITI PRAVNI LIJEKOVI 463–496 (žalba na presudu 463–489,
  treći stupanj 490, žalba na rješenje 491–496)
- Glava XXIV IZVANREDNI PRAVNI LIJEKOVI 497–519

## Key detention articles (ZKP)
- 122 principles (proportionality; detention exceptional for pregnant/disabled/
  70+); 123 grounds (founded suspicion + flight / evidence-tampering /
  repeat-offense ≥5yr / necessity for long-term-imprisonment offenses /
  evading trial); 124 order contents (incl. jamčevina alternative);
  125 release grounds (incl. full confession); 127 who decides (istražni
  sudac pre-indictment → optužno vijeće → raspravno vijeće); 129 non-public
  oral hearing (video link OK); 130 duration pre-indictment (1mo +2mo +3mo,
  6mo cap, USKOK 12mo); 131 re-exam every 2 months post-indictment;
  133 caps by max sentence (2mo/3mo/6mo/12mo/2y/3y; +1/6–1/4 after
  nepravomoćna presuda; +6mo if further appeal allowed; +1yr after quash);
  134 appeal 3 days, higher court 3 days, NO stay; 141 release if term
  expired; 135–140 regime/rights (8h rest, 2h air, visits, confidential
  counsel, ombudsman complaint unrestricted).

## Key appeal articles (ZKP)
- 463: 15-day deadline from service (+15 extension in complex serious cases);
  appeal STAYS execution. 464: who may appeal (incl. family pro-accused,
  prosecutor both ways, oštećenik limited). 466: content. 467: grounds
  (essential procedural violations / law violation / factual findings /
  sanction decision). 468: list of essential violations (incl. unlawful
  evidence, Art. 13 ne bis in idem). 469: law-violation list (incl. zastara,
  amnesty, res judicata). 470: factual grounds. 472–473: filing + 8-day reply.
  475–475b: panel session / appellate hearing. 476: review scope + ex officio
  checks; no reformatio in peius; 479: benefit extends to non-appealing
  co-accused. 480–486: outcomes — dismiss / reject / quash (max ONE remand;
  appellate court holds second retrial itself, 484a) / amend (486).
  484(3) & 486(2): detention rulings by appellate court NOT appealable.
  488: 3-month deadline to return file when accused detained. 490: third
  instance only (long-term imprisonment / different facts after appellate
  hearing / acquittal reversed). 491–496: ruling appeals — 3 days, suspensive
  (unlike detention appeals).

## Extraordinary remedies (ZKP Glava XXIV, 497–519 — verified Aug 2026)
- Obnova postupka (reopening) 497–508: in favor of convicted — false evidence,
  prosecutorial/judicial crime, genuinely new facts (501); to detriment only
  for dismissal-type judgments (503, 1-month limit); ECtHR/Constitutional
  Court decisions ground reopening (502, 30-day deadline from ECtHR finality);
  allowed even after sentence served, limitation irrelevant (504); decided by
  original first-instance panel, deciding judge excluded (505); if allowed →
  execution stays, detention may be re-ordered under 123 (507).
- Zaštita zakonitosti (protection of legality) 509–514: ONLY the Chief State
  Attorney may file; Vrhovni sud decides (extended panel possible); in favor
  of convicted → no reformatio in peius; against convicted → violation merely
  declared, final decision untouched (513).
- Izvanredno preispitivanje pravomoćne presude (extraordinary review)
  515–519: convicted (imprisonment / juvenile imprisonment / compulsory
  psychiatric placement), must have used regular remedy; grounds must have
  been raised in appeal (517); 1 month from receipt of final judgment (518);
  Vrhovni sud decides; execution may be stayed.

## NN series (verify from page metadata each refresh; as of Aug 2026)
- KZ: NN 125/11, 144/12, 56/15, 61/15, 101/17, 118/18, 126/19, 84/21,
  114/22, 114/23, 36/24, **75/26** (implements EU 2024/2679)
- ZKP: NN 152/08, 76/09, 80/11, 121/11, 91/12, 143/12, 56/13, 145/13,
  152/14, 70/17, 126/19, 130/20, 80/22, 36/24, **72/25** (23.4.2025);
  **13/26** refs appear in amended articles (e.g. 98, 468) — a newer
  amendment; verify against gazette.

## Run commands (venv quirk)
The Hermes shell exports PYTHONPATH → `~/.hermes/hermes-agent/venv/lib/python3.11/site-packages`,
which breaks py3.13 venvs (cp311 numpy ImportError). Always run:
`PYTHONPATH= ./.venv/bin/python scrape.py` (and parse/embed/ask alike).
Embeddings (FINAL working config): fastembed `intfloat/multilingual-e5-large`
(1024-dim, multilingual — REQUIRED for English-query → Croatian-corpus
retrieval; nomic-embed-text-v1.5 was tried and FAILS cross-lingual: flat
~0.49 scores, wrong top hits). e5 needs manual `query:`/`passage:` prefixes.
Retrieval is HYBRID in ask.py: vector leg + lexical leg (inverted index,
light Croatian suffix stemming, article-title boost, EN→HR GLOSSARY
expansion, reciprocal-rank fusion with ×2.5 lexical weight for non-Croatian
queries). Rebuild: `embed.py intfloat/multilingual-e5-large 64`.
jina-embeddings-v3 was tried first and blew up to ~49GB physical footprint on
the 32GB Mac (SIGKILL ×2, swap thrash) — do not go back to it.
Check `TextEmbedding.list_supported_models()` — bge-m3/e5-small NOT supported
in the pinned fastembed build. LLM answers: DeepSeek via `ask.py --llm`
(key read from `~/.hermes/.env` DEEPSEEK_API_KEY; model from hermes
config.yaml `model.default` = deepseek-v4-flash — a REASONING model: needs
≥6000 max_tokens or reasoning_content eats the budget and content returns
EMPTY). User chose DeepSeek cloud over local LM Studio for answer quality;
LM Studio box (192.168.1.131:1234) was up with bonsai-27b / gemma-4-26b /
nomic-embed loaded.
Domain playbook: see the `croatian-criminal-procedure` skill.
