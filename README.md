# Croatian Criminal Law Agent

A reusable Hermes Agent **profile distribution** for Croatian criminal-law
research, built on a local RAG knowledge base scraped from
[zakon.hr](https://www.zakon.hr) (robots.txt permits crawling).

This repo is two things in one:

1. **A Hermes profile distribution** — `skills/`, installable with
   one command so another Hermes instance gains the Croatian-law and
   scraping skills.
2. **A standalone data project** — `kb/`, the KZ/ZKP corpus + scraping →
   parsing → embedding → query pipeline that produced the case-law knowledge.

## What's inside

| Path | What it is |
|---|---|
| `distribution.yaml` | Distribution manifest (name, version, env vars, install scope) |
| `skills/research/croatian-criminal-law-research/` | Citation-grounded Q&A workflow over the KB |
| `skills/research/croatian-criminal-procedure/` | Deep playbook: detention, bail, appeals, remedies, evidence |
| `skills/research/web-scraping/` | Scraping etiquette + Croatian legal-source maps (zakon.hr) |
| `skills/research/web-scrape-to-rag/` | Scrape → parse → embed → RAG pipeline notes |
| `skills/research/blocked-page-recovery/` | Fallbacks for blocked/paywalled sources |
| `skills/mlops/local-rag-knowledge-base/` | Local RAG KB build/query patterns |
| `kb/` | The data + pipeline (corpus, articles, raw HTML, topics, scripts) |

The corpus: **Kazneni zakon** (Criminal Code, NN 125/11 … 36/24, 398 articles)
and **Zakon o kaznenom postupku** (Criminal Procedure Act, NN 152/08 … 36/24,
597 articles) — 995 article records total.

## Install (the skills)

On any machine with Hermes ≥ 0.20.0:

```bash
hermes profile install git@github.com:prevoind/croat_law.git --name croatlaw -y
```

This installs the six skills into a fresh profile named `croatlaw` (the manifest
default is `croatian-criminal-law-agent`). Use the `git@…` SSH URL — the repo is
private, and the `github.com/user/repo` shorthand clones over HTTPS (needs a
token). API keys are **never** shipped.

> Full walkthrough incl. the one-time deploy key: see **`SETUP.md`**.

## Install (the knowledge base)

The skills reference the KB at `~/hr-criminal-law-kb/`, so place the data there
(any of these work):

```bash
# clone the repo and symlink the data into place
git clone git@github.com:prevoind/croat_law.git
ln -s ~/croat_law/kb ~/hr-criminal-law-kb

# …or just copy it
cp -r croat_law/kb ~/hr-criminal-law-kb
```

The corpus, `articles.jsonl`, and raw HTML are already committed — you only need
to rebuild the embeddings (one-time; downloads `intfloat/multilingual-e5-large`):

```bash
cd ~/hr-criminal-law-kb
python3 -m venv .venv && ./.venv/bin/pip install -r requirements.txt
./.venv/bin/python embed.py
```

(Re-run `scrape.py && parse.py` only to refresh from zakon.hr.)

Query it:

```bash
PYTHONPATH= ./.venv/bin/python ask.py "penalty for murder in Croatia"           # sources only
PYTHONPATH= ./.venv/bin/python ask.py "what is pre-trial detention?" --llm      # + DeepSeek answer
```

> The `PYTHONPATH=` prefix matters: Hermes leaks its Python 3.11 site-packages
> into the shell, which breaks Python 3.13 venvs (cp311 numpy). See `kb/README.md`.

## Repo hygiene

- `kb/data/vectors.npy` + `kb/data/vector_meta.json` are **regenerable** and
  git-ignored — rebuild them with `embed.py` after cloning (they're tied to the
  fastembed/model version anyway).
- No API keys, OAuth tokens, memories, or session history are committed.
- Skills' `author` field is `hermes`/`Hermes Agent` because the agent authored
  them in-session; their `version` is `1.0.0`.

## Legal note

The KB is grounded in the unofficial consolidated text on zakon.hr. Official
texts are published in Narodne novine. This is a research tool, not legal
advice.

## Updating

Edit → `git tag v1.1.0 && git push --tags`; recipients run
`hermes profile update croatlaw`. For the KB data, re-run
`scrape.py && parse.py && embed.py` and update the NN series in `parse.py`.
