---
name: croatian-criminal-law-research
description: Use for Croatian criminal-law Q&A with KZ/ZKP citations.
version: 1.0.0
author: hermes
license: MIT
metadata:
  hermes:
    tags: [croatia, criminal-law, zkp, kz, legal-research, rag, citation]
    related_skills: [web-scraping, grounded-citations, local-rag-knowledge-base]
---

# Croatian Criminal-Law Research (grounded in the user's KB)

## When to use
- User asks a Croatian criminal-law / criminal-procedure question (rights of suspects,
  detention, evidence, appeals, media/case interaction) and expects **precise article
  citations** (article + stavak + točka).
- Any session working with `~/hr-criminal-law-kb/` — answering, extending, or verifying.

## The KB (`~/hr-criminal-law-kb/`)
- `corpus/kz.md` — Kazneni zakon (all articles, Croatian), `corpus/zkp.md` — Zakon o
  kaznenom postupku (all articles).
- `ask.py` — RAG Q&A over embedded corpus (DeepSeek cloud). Good for open questions.
- `topics/*.md` — curated briefs (pre-trial detention, appeals, evidence). Add new briefs
  here when the user asks for deep dives.

## Workflow: grep-first citation (more precise than RAG for "which article says X")
1. `re.findall(r"Članak \d+[a-z]?\.", ...)` or plain `.find()` on the corpus for the exact
   provision phrase the question implies (e.g. `uvid u spis`, `pretpostavka nedužnosti`,
   `istražni zatvor`, `dokazni prijedlog`, `vještačenje`).
2. **Verify the enclosing article number**: search BACKWARD from the hit for the nearest
   `### Članak N.` header (`re.findall(r"### Članak \d+[a-z]?\.", corpus[:i])[-1]`).
3. Quote the provision text in the answer, cite `Članak N. st. X toč. Y` precisely.
4. Cross-check with `ask.py` only for interpretation questions; never cite from memory
   what the corpus contradicts.
5. Supplement (clearly labelled) with: Ustav RH (28 presumption of innocence, 35/38),
   ECHR Art. 6 case law (Allenet de Ribemont etc.), GDPR Art. 9/10 for data-protection
   angles, Zakon o elektroničkim medijima / ZPPO for media-police angles.
6. End with a one-line disclaimer ("informational, not legal advice") and offer (once —
   don't push) to save a topic brief.

## Corpus pitfalls (learned the hard way)
- Corpus is **linear markdown with merged amendment blocks** — headers like
  `### Članak 213.a (NN 145/13, 13/26)` and some blocks contain several amended versions
  inline. A provision's physical position under a header may not match its official
  number (e.g. the investigation-stage prigovor text sits inside the Art. 239 block in
  the corpus). Always report the header you verified, and if unsure, say so.
- Some articles are `Brisan.` (deleted) — they exist as headers with no content.
- Diacritics matter: search `nedužnost`, `tajnost`, `uskraćenog prava` exactly; also try
  the inflected form (`uvid u spis` vs `uvida u spise`).
- The `službena tajna` phrase appears as `službena su tajna` — search the substring form.

## Output conventions (user preferences)
- Answers in **English** with the Croatian statutory term in parentheses
  (e.g. "pre-trial detention (*istražni zatvor*)") and exact article citations.
- Practical tables are appreciated (who-can-do-what / stage-by-stage); keep prose tight.
- If case facts come from the user's message, flag what is asserted vs verified, and
  note discrepancies between sources.
- Offer archive of sources (see web-scraping skill) and topic briefs, but don't repeat
  the offer after a decline.

## Verified article map
`references/verified-articles.md` — articles verified against the corpus in Aug 2026
with one-line summaries and the exact quotes used.
