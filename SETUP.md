# SETUP — install this distribution on a new machine

This repo is a Hermes **profile distribution** containing six skills
(two Croatian criminal-law + four web-scraping). Follow these steps on the
machine where you want them.

## 1. Give this machine SSH access (one-time)

The repo is private, so each machine needs its own access. A read-only
**deploy key** is the cleanest option — scoped to this repo only, not your
whole account.

1. Generate a key if this machine has none (press Enter through the prompts):
   ```bash
   ssh-keygen -t ed25519 -C "$(hostname)-croatlaw"
   ```
2. Print the public key:
   ```bash
   cat ~/.ssh/id_ed25519.pub
   ```
3. Add it as a **deploy key** (not an account SSH key):
   https://github.com/prevoind/croat_law/settings/keys → **Add deploy key** →
   paste the key → leave **"Allow write access" unticked** (tick it only if
   this machine will also push updates back to the repo).

## 2. Install the skills

```bash
hermes profile install git@github.com:prevoind/croat_law.git --name croatlaw -y
```

- Use the **`git@…` SSH URL** — the `github.com/user/repo` shorthand clones
  over HTTPS, which needs a token on a private repo.
- `--name croatlaw` sets a friendly profile name (the default would be
  `croatian-criminal-law-agent`).
- `-y` skips the manifest-confirmation prompt.

The six skills install into `~/.hermes/profiles/croatlaw/skills/` and are usable
immediately — e.g. the `/croatian-criminal-procedure` slash command, or just ask
a Croatian criminal-law question normally.

## 3. (Optional) Knowledge base + DeepSeek answers

The skills answer statutory questions from the corpus in `kb/`. Set it up if you
want local RAG querying:

```bash
# place the data at the path the skills reference
cp -r <wherever-you-cloned-the-repo>/kb ~/hr-criminal-law-kb

cd ~/hr-criminal-law-kb
python3 -m venv .venv
./.venv/bin/pip install -r requirements.txt
./.venv/bin/python embed.py          # rebuild embeddings (one-time model download)
```

Query it:

```bash
PYTHONPATH= ./.venv/bin/python ask.py "penalty for murder in Croatia"
```

The `PYTHONPATH=` prefix matters (Hermes leaks its py3.11 site-packages into the
shell) — see `kb/README.md`.

For DeepSeek-backed answers (`--llm`), add your key — it's **only** needed for
`--llm`; plain retrieval needs no key:

```bash
echo 'DEEPSEEK_API_KEY=sk-…' >> ~/.hermes/.env
```

## 4. Update later

```bash
hermes profile update croatlaw        # pull new skills from the repo
```

Updates never touch `memories/`, `sessions/`, `.env`, or `auth.json`.

## Notes

- **API keys are never shipped** in this distribution (no `.env`, no `auth.json`).
- The `kb/` folder is reference data in the repo — it is **not** installed into
  the profile (`distribution_owned: [skills]`).
- Full pipeline and corpus details: see `README.md` and `kb/README.md`.
