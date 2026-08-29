---
name: croatian-criminal-procedure
description: Use when answering Croatian criminal law questions.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [legal, croatia, criminal-procedure, detention, appeals, rag, kazneni-zakon]
    related_skills: [web-scrape-to-rag, grounded-citations]
---

# Croatian Criminal Procedure — expert Q&A playbook

## When to Use
- User asks about Croatian criminal law: penalties, offenses, procedure
  (Kazneni zakon / Zakon o kaznenom postupku).
- Questions about pre-trial detention (istražni zatvor), bail, appeals
  (redoviti/izvanredni pravni lijekovi), reopening, or any ZKP/KZ citation.
- Extending or refreshing the KB at `~/hr-criminal-law-kb`.

Answer questions grounded in the local KB at `~/hr-criminal-law-kb`, with
exact article citations. User's focus areas: **pre-trial detention (istražni
zatvor)** and **appeals (redoviti i izvanredni pravni lijekovi)**.

## How to query (from chat or terminal)

```bash
cd ~/hr-criminal-law-kb
PYTHONPATH= ./.venv/bin/python ask.py "question" --topk 6      # sources only
PYTHONPATH= ./.venv/bin/python ask.py "question" --llm         # + DeepSeek answer
```

- Retrieval is hybrid: vector (e5-large) + lexical (stemming, title boost,
  EN→HR glossary, weighted RRF). ALWAYS run with `PYTHONPATH=` prefix
  (Hermes shell leaks its py3.11 site-packages; see web-scrape-to-rag skill).
- For chat answers: run retrieval, read the top-6 sources' FULL texts, then
  answer in English citing (KZ, čl. N) / (ZKP, čl. N). Only cite what the
  retrieved text actually says. If sources don't cover it, say so.
- Full texts live in `corpus/kz.md`, `corpus/zkp.md`; topical briefs in
  `topics/pre-trial-detention.md`, `topics/appeals.md`.
- ZKP articles mostly have NO titles — retrieval relies on text/glossary,
  not rubrums.

## Pre-trial detention (istražni zatvor) — ZKP Glava IX (čl. 95–144)

- **Grounds (123(1))**: founded suspicion + one of: ① flight risk ②
  evidence/witness tampering ③ repeat-offense risk (potential sentence ≥5 yr)
  ④ necessity for undisturbed proceedings on very serious offenses ⑤ evading
  trial (čl. 132: max 1 month, renewable).
- **Mandatory at sentencing**: imposed sentence ≥5 years → detention ordered
  regardless of čl. 133 caps (123(2)); but never beyond the maximum duration
  (123(4)).
- **Who decides (127)**: investigating judge pre-indictment (12 h to decide;
  prosecutor appeals refusal within 24 h, panel within 48 h) → indictment
  panel (48 h hearing, 131(1)) → trial court; **the appellate panel when
  deciding the appeal (127(5))**.
- **Procedure (129)**: non-public oral hearing, all parties, video link OK;
  decision announced orally; every 2 months post-indictment the court
  reviews ex officio and extends/revokes by order (131(3)); appeal against
  that order does NOT stay it; the court must re-check grounds whenever it
  decides anything (129(7)).
- **Duration (130 pre-indictment, 133 post)**: 1 mo initial, +2 mo, +3 mo;
  6 mo pre-indictment cap (12 mo USKOK). Post-indictment caps by potential
  sentence: 2 mo (≤1 yr) / 3 mo (≤3 yr) / 6 mo (≤5 yr) / 12 mo (≤8 yr) /
  2 yr (>8 yr) / 3 yr (long-term). Extensions: +1/6 (categories 1–4) or
  +1/4 (5–6) after non-final conviction (133(3)); +6 mo if a further appeal
  is allowed (133(5)); +3/+6/+12 mo after quash for retrial (133(4)).
- **Appeal (134)**: 3 days, higher court decides within 3 days, **does NOT
  stay execution**; no appeal against second-instance detention rulings
  (except 127(5) novel orders); no appeal against refused release requests
  (128). Contrast: ordinary ruling appeals ARE suspensive (493).
- **Release (125)**: grounds lapsed / disproportionality / milder measure /
  prosecutor's request / prosecutorial delay (warning procedure to higher
  prosecutor first, 125(2)) / acquittal or sanction ≤ time served / expiry
  of caps / full confession + secured evidence (ground 2).
- **Rights (136–141)**: 8 h rest, 2 h air, visits, confidential counsel
  (139(5)), unrestricted Ombudsman complaints (139(6)), weekly judicial
  visits with mandatory release if the order lapsed (141(4)), consular
  access (139(2), 142). Disciplinary restrictions never touch
  counsel/consular contact (140).
- **Credit**: detention counts 1:1 toward imprisonment and fines (KZ 54).
- **Victim chain on release (125(2)–(4))**: court→police→victim immediately
  (unless it endangers the released person); applies even when the accused
  stays locked up for another case; prison must pre-announce first release.

## Bail & cautionary measures (jamčevina / mjere opreza — ZKP 98–104)

- **Bail (102)**: ONLY for the flight-risk ground (123(1)1); amount by
  offense gravity, personal circumstances, means; forms: cash, securities,
  valuables, movables, mortgage (103); 3-day appeal on amount/form; release
  on posting + promise; breach → forfeiture (104).
- **Mjere opreza (98)**: 11 types (residence ban, area ban, reporting duty,
  no-contact, travel-doc/driving-license seizure, no-stalking, removal from
  home, internet ban…); replace detention when the same purpose is served;
  standalone after detention caps expire (98-a); 2-month ex officio review
  (not while a bail condition); violation → detention; žalba no stay (98(8)).

## Appeals — regular (ZKP Glava XXIII, čl. 463–496)

- 15 days from service (later of accused/counsel service, 463(3)); +15 days
  extension possible in complex serious cases (463(2)); **stays execution**
  (463(4)). Who: parties, counsel, oštećenik (limited), family in accused's
  favor (464).
- **Grounds (467)**: essential procedural violations (468 — incl. unlawful
  evidence, ne bis in idem) / law violations (469 — incl. zastara, amnesty,
  res judicata) / erroneous-incomplete facts (470) / sanction decisions
  (471). 8-day reply (473); panel session or appellate hearing (475).
- **Scope (476)**: review only challenged part + grounds, but ex officio
  checks listed violations and law violations to the accused's detriment;
  **no reformatio in peius**; benefit extends to non-appealing co-accused
  (479).
- **Outcomes (480–486)**: dismiss / reject / **quash-remand (max ONE remand;
  appellate court holds the second retrial itself, 484-a(1))** / amend (486).
  Detention rulings by the appellate court on quash/amend: NOT appealable
  (484(3), 486(2)). File return within 3 months when accused detained (488).
- **Third instance (490)**: only ① long-term imprisonment imposed/affirmed ②
  different facts established at the appellate hearing ③ acquittal reversed.
- **Ruling appeals (491–496)**: 3 days, suspensive by default (493).

## Extraordinary remedies (ZKP Glava XXIV, čl. 497–519)

- **Obnova (reopening, 497–508)**: only against FINAL judgments (497); in
  favor — false evidence, prosecutorial/judicial crime, genuinely new facts
  (501); no deadline, even after sentence served (504); to detriment ONLY
  for dismissal-type judgments, 1-month limit (503); ECtHR/Court-based: 30
  days from ECtHR finality (502); in-absentia: 1 year (497(3)); decided by
  original first-instance panel, judge excluded (505); allowed → execution
  stays, detention re-orderable (507); reformatio-in-peius ban (508(6)).
- **Zaštita zakonitosti (509–514)**: ONLY the Chief State Attorney; Vrhovni
  sud (extended panel possible); in favor → no reformatio in peius; against
  → violation merely declared, verdict untouched (513(2)).
- **Izvanredno preispitivanje (515–519)**: convicted person; MUST have used
  the regular remedy (515(2)); grounds must have been raised in the appeal
  (517(2)); 1 month from receipt of final judgment (518); Vrhovni sud.

## Pre-trial evidence rules (izvidi, istraga, dokazne radnje)

- **Unlawful evidence (10)**: decisions can't rest on it. Unlawful = ① torture/
  inhuman-treatment violations (absolute) ② defense-rights/privacy violations
  (legalizable via proportionality test) ③ express statutory sanctions ④
  derivative evidence (unless obtainable lawfully elsewhere). A decision may
  not rest EXCLUSIVELY on category-② evidence (10(3)).
- **Phases**: izvidi (secret, 204–215) → istraživanje (≤5 yr offenses, accused
  notified within 3 days, 213) → istraga (>5 yr; mandatory >15 yr/long-term/
  non-accountability, 216). Prosecutor leads; investigator can't examine the
  accused in županijski-sud cases (219(3)).
- **Pre-trial-STATUS-specific rules**:
  - Info from detainees re: OTHERS' crimes (208(2)-(3)): prosecutor approval
    (judge if custody extended), counsel PRESENT; istražni zatvor → written
    prosecutor proposal + investigating judge/panel-president approval.
  - Detention order is a rights-warning trigger (239(2)6).
  - Detention requested at istraga opening (217(5)); release AUTOMATIC on
    discontinuance (224(2), 226(2)).
  - Detained accused is BROUGHT to defense-proposed evidence actions or joins
    by video link (234(3)).
  - Diligence coupling: prosecutor reports investigation progress at every
    detention hearing (129(4)); dilatoriness → release (125(1)5).
  - Evidence-tampering detention ends on confession/secured evidence (125(1)8).
- **Examination rights**: silence + no adverse inference (239(1)2, 208.a);
  counsel pause 3 h (police, 208.a(5)) / 2 h (istraga, 274); mandatory
  AV recording (police 208.a(6), istraga 275 — 3 copies, statement not
  transcribed); unwarned/unrecorded statements inadmissible (208.a(8));
  no force/threat/deception (276(5)); no leading questions (277).
- **Defense evidence**: propose actions (234); dokazno ročište for
  non-repeatable evidence (235-238; judge 48 h, appeal 24 h, panel 48 h);
  prigovor for denied rights → prosecutor 8 d → judge 8 d.
- **Deadlines**: istraga decision 48 h after examining accused (216(4));
  istraga order served + appealable within 8 d (218); istraga finish 6 mo
  (+6+6, 229); indictment 1 mo after istraga, silence = abandonment + 8 d
  dismissal (230); prijava decision 6 mo (206.b); search order 4 h/8 h/12 h,
  executed within 3 d or void (242).

## Evidence admissibility — the grill results

- **Police statement (208.a)**: admissible only with the full ritual — rights
  warning (counsel, interpreter, silence with NO adverse inference, leave
  anytime), counsel pause ≤3 h, mandatory AV recording; violation → statement
  INADMISSIBLE (208.a(8)). Istraga-stage examination: 3 recordings, statement
  not transcribed (275). Non-suspect "obavijesti" statements are excluded
  from the file (208(4), 86(3)).
- **Warrantless search (246)**: within 8 h of discovery during očevid, for
  life/health/property danger or securing traces — but NEVER a home (except
  special-law entry, 246(2)). Otherwise judge's order (242): 4 h decision,
  8 h prosecutor appeal, 12 h panel, 3-day execution or the order dies.
  Home = dwelling rooms; covers movables + persons found (252); order shown
  first, voluntary surrender invited (243).
- **Special evidence actions (332–338)**: closed offense list (334),
  subsidiarity — only if inquiries can't proceed otherwise (332); prosecutor's
  written request + investigating judge's order; recordings admissible
  (333(1)); undercover/informant testimony admissible BUT a judgment may not
  rest EXCLUSIVELY on it (333(3)); no collateral use against third parties
  (338(1)); sealed originals at the prosecutor's office + excerpts in file
  (338(2)); ongoing judge supervision (337).
- **Investigation statements at trial (431)**: hearsay gate — records
  readable only for: undisputed facts / witness dead-ill-unfindable-unable /
  refusal without legal basis / warned privilege; same gate for expert
  findings and co-accused/convicted-accomplice statements.
- **Unlawful evidence machinery**: file exclusion (86 — investigating judge /
  indictment-panel president, decision ≤3 days, special appeal, sealed away)
  + merits exclusion (10 — 4 categories, derivative evidence with
  lawful-alternative exception, exclusive-reliance ban in 10(3)).
- **Vještačenje (308–328)**: written order (309), duty to appear (310),
  witness-incompetent persons excluded (311), findings entered in record
  (314); unclear/incomplete → clarification (317); doubt → re-expertise
  (318); special regimes: bodily injury (324), sanity/neubrojivost (325),
  DNA (327), business books (328).
- **Confession by deception**: force/threat/deception prohibited (276(5)),
  no leading questions or presumed guilt (277), retraction → reasons (277(2));
  torture conduct itself = KZ 104.

## Media publicity & trial fairness (leak scenario)

Scenario: a court official posts police-raid footage on social media before
trial. Statutory response:
- Pre-trial phases are secret; disclosure of izvidi/istraga content WITH THE
  PURPOSE of making it public IS a crime (206, 213(3), 231(1)); KZ privacy
  offenses: unauthorized sound/video recording (143/144), professional-secret
  disclosure (145).
- Presumption of innocence (1(1)); equal examination of incriminating and
  exculpatory facts (9(1)); fair-trial violation = essential procedural
  violation (468(1)12).
- Remedies ladder: criminal complaint vs. the official → change of venue
  (delegacija, 26–28 — "iz važnih razloga" before end of trial) → recusal
  (32) → evidence exclusion (10/86 — footage may expose an unlawful
  search/seizure, use it against the prosecution) → appeal on 468(1)12 /
  468(3) → quash-remand (483). Trial publicity controlled via 388.
- KB has no case law (portals down) — this is statutory analysis, not
  jurisprudence.

## Verified nuances & traps

- Bail ≠ general alternative to detention — flight-risk ground only.
- Detention appeals never suspend; ordinary ruling appeals do. Two regimes.
- You can't skip the ladder: extraordinary review requires a prior appeal;
  obnova requires finality + statutory grounds (no re-argument).
- ZKP articles mostly lack titles; lettered variants ("123.b", "98.a") and
  merged "133 + 133.a" records exist — cite the base number.
- NN series (Aug 2026): KZ through 75/26 (EU 2024/2679); ZKP through 72/25,
  with 13/26 refs in amended articles (98, 468, 510, 517) — verify against
  gazette before relying on 13/26 content.
- Case-law portals (sudskapraksa.*) were DNS-dead — statutory answers only.

## QA battery (run after any corpus/retrieval change)

`ask.py` top-3 should include: murder→KZ 110 · aggravated murder→111 ·
zastara→KZ 81 · detention grounds→ZKP 123 · bail→ZKP 98–104 · criminal
complaint→ZKP 204/205 · fraud→KZ 236 · self-defense→KZ 21 · theft→KZ 228 ·
interrogation rights→ZKP 270–280 · detention duration→ZKP 133 · detention
appeal→ZKP 134 · quash+detention→ZKP 484/127 · Chief State Attorney→ZKP
509/510 · third instance→ZKP 490 · reopening→ZKP 501 · unlawful evidence→ZKP
10 · police interrogation of suspect→ZKP 208.a · istraga deadlines→ZKP 229/230
· evidence from detainees→ZKP 208 · dokazno ročište→ZKP 235/236 ·
warrantless search→ZKP 246 · search order→ZKP 242 · special evidence
actions→ZKP 332/333 · read investigation statements at trial→ZKP 431 ·
expertise→ZKP 309 · coerced confession→ZKP 276/277 · file exclusion
(izdvajanje)→ZKP 86 · change of venue→ZKP 26 · fair-trial violation→ZKP
468(1)12 · disclosure of pre-trial content→ZKP 231(1).

## Extending the glossary (retrieval tuning)

English→Croatian legal-term expansion lives in `ask.py` `GLOSSARY`. Add
high-precision domain terms only (generic words cause false matches — see
the "grounds"→"osnove" bail/appeal misfire). After adding, re-run the QA
battery. Croatian stemming is a light suffix stripper (CRO_SUFFIXES) —
extend for other inflections if lexical recall degrades.

## Refresh procedure

```bash
cd ~/hr-criminal-law-kb
PYTHONPATH= ./.venv/bin/python scrape.py   # re-fetch (cached, polite)
PYTHONPATH= ./.venv/bin/python parse.py    # re-parse → articles.jsonl
PYTHONPATH= ./.venv/bin/python embed.py    # re-embed (e5-large)
PYTHONPATH= ./.venv/bin/python make_topics.py
# update NN_SERIES in parse.py from page metadata; re-run QA battery
```

## References

- `~/hr-criminal-law-kb/README.md` — pipeline docs & pitfalls
- `~/hr-criminal-law-kb/topics/pre-trial-detention.md` (57 articles, full text)
- `~/hr-criminal-law-kb/topics/appeals.md` (57 articles, full text)
- `~/hr-criminal-law-kb/topics/evidence-pre-trial.md` (47 articles, full text)
- Source maps, zakon.hr markup, chapter maps and NN series: see the
  `web-scrape-to-rag` skill's reference file (croatian-criminal-law.md).
