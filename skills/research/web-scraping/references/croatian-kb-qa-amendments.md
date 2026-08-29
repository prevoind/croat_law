# Croatian KB — corpus QA, KZ amendments, legal-research routes

**Supersedes the status parts of `croatian-legal-sources.md`** (that file still describes the KB as "build pending"; it is in fact BUILT and running, see below). Verified live Aug 2026.

## KB status (as of Aug 2026)

Built pipeline: scrape zakon.hr → `parse.py` → `corpus/kz.md` + `corpus/zkp.md` (398 + 597 articles) → `embed.py` (fastembed `intfloat/multilingual-e5-large` — NOT nomic, English-centric) → `data/vectors.npy` → `ask.py` (DeepSeek cloud; user wants answers in English). Topic briefs in `topics/` (pre-trial detention, appeals). **Known defect below — verify RAG answers on affected articles.**

## ⚠️ Corpus truncation bug (find it, then fix it)

zakon.hr injects `SUDSKA PRAKSA: Presuda, Rješenje, ...` link lists INSIDE articles, between stavci. The KB parser drops everything after the first such list:
- **KZ: 125/387 articles truncated** (Art 3: 1 st. vs 5 raw; Art 55: 2 vs 9; **Art 190: only st. 1 of 9 kept**).
- **ZKP: 22 articles truncated** — incl. **Art 133 (detention durations: 2 vs 6)** and Art 575 (0 vs 7).

Detection: `scripts/check_corpus_truncation.py` (per-article stavak counts corpus vs raw; run after every re-parse).
Fix: strip the link lists before parsing, e.g. `re.sub(r'SUDSKA PRAKSA:.*?(?=<p|<h2|Članak \d+\.)', '', raw, flags=re.S)`, then re-run parse + embed, re-verify with the script.

## KZ 190 — amended by NN 136/25, in force 13.11.2025 (READ BEFORE ANALYZING DRUG CHARGES)

Current consolidated structure:
1. Unauthorized production/processing — 6 mo – 5 yr.
2. **Production/possession of substances "namijenjene neovlaštenoj prodaji" (trafficking / possession-for-sale) — 3 – 12 yr. NO quantity threshold.**
3. Sale to mentally impaired / children / at schools or institutions / by officials — 3 – 15 yr.
4. Organizing a dealer network — ≥ 3 yr.
5. Causing serious harm to many / death — ≥ 5 yr.
6. Precursor equipment/material — 6 mo – 5 yr.
7. Cultivation of source plants = production. 8. Confiscation. 9. Voluntary disclosure → possible sentence remission.

- **"veća količina" is GONE from KZ 190** (0 occurrences in the current text). The pre-2025 st. 2 quantity gate (1–12 yr) is history.
- DORH charge format `čl. 190. st. 2. u vezi st. 1` = possession for sale → **3–12 yr exposure**.
- Historical "veća količina" per-substance benchmarks (widely cited in practice, **NOT verified from a primary source** — they appear in no published VSRH conclusion): ~40 g heroin, ~30 g cocaine, ~30 g amphetamine, ~30 g MDMA, ~100 g cannabis. Verify in IUS-INFO/EDUS/Notarius or *Informator* before citing.
- Amendment markers on zakon.hr: per-article inline `(NN 144/12, 56/15, 136/25)` after the article number; law page states in-force date ("na snazi od 13.11.2025") — parse that for version date.

## VSRH legal-research routes (curl-friendly unless noted)

- vsrh.hr: `/pravna-shvacanja-i-zakljucci.aspx` → Kazneni odjel subpages (`/pravna-shvacanja-kazneni-odjel.aspx`, `/zakljucci-kazneni-odjel.aspx`). PDFs under `/custompages/static/HRV/files/PravnaShvacanja-Zakljucci/...` — curl + pypdf extractable (`python3 -m pip install --user pypdf`).
- **Verified: published VSRH Kazneni odjel conclusions (2015–2024) contain NO drug-quantity thresholds.**
- zakon.hr sudska praksa (`/c/sudska-praksa/<id>/<slug>`, e.g. Kž 132/2015): VSRH decisions, but quantities often redacted ("... grama").
- ANON case search (`vsrh.hr/trazilica-sudskih-odluka-anon.aspx`) and IUS-INFO/EDUS/Notarius are JS/paywalled → browser-use CLI (see SKILL.md) or user access.
- narodne-novine.nn.hr: urllib needs `ssl._create_unverified_context()`; issue-TOC pages may be JS-gated.

## Key ZKP article map (verified from corpus — fast grep targets for procedural questions)

- **3** presumption of innocence · **5(2)** defense at state expense · **10** unlawful evidence · **65(3)** relatives may engage a branitelj for the accused (unless accused objects) · **65(4)** only odvjetnik as branitelj (county court) · **66** mandatory defense (incl. detention) · **74** branitelj file access per 184(4)–(5) · **123** istražni zatvor grounds · **133** detention durations · **183** uvid u spis (review/copy/photo/record; secret proceedings → participants only; disclosure warned as crime) · **184** file access rights + timing (accused & branitelj from first examination / investigation order / Art 213(2) notice; 30-day withholding possible) · **204(4)** suspect identity data = službena tajna · **213.a(3)–(4)** pre-trial phase "nejavno"; unauthorized disclosure of investigative content = criminal offense · **239(3)–(6)** prigovor vs state attorney denials → investigating judge can order action done/repeated · **317** renewed expert examination only if report nejasan/nepotpun/proturječan · **419** parties propose evidence · **440(2)** panel rejection of evidence motion closes evidentiary phase · **468(3) + 468(1)(12)** appeal grounds (right-of-defense breach; fair-trial violation).
