# Rubika AI Bot (rubpy + OpenRouter)

A Rubika messenger bot that answers every incoming message using an AI
model through the [OpenRouter](https://openrouter.ai) API. It authenticates
with a **Rubika Bot Token** (no phone/QR login, no session file), so it's
built to run 24/7 unattended on a host like [Railway](https://railway.app).

## Project structure

```
main.py            # Entry point — run this to start the bot
config.py          # Reads all settings from environment variables
ai_handler.py       # Talks to OpenRouter and returns the AI's reply
bot_handlers.py      # Listens to Rubika messages and replies
requirements.txt     # Pinned Python dependencies
Procfile             # Declares the worker process (Heroku-style hosts)
railway.json          # Explicit Railway start command + restart policy
.env.example           # Template for local environment variables
.gitignore              # Keeps .env and other junk out of git
README.md                # This file
```

## Required environment variables

| Variable | Required? | Purpose |
|---|---|---|
| `RUBIKA_BOT_TOKEN` | **Yes** | Your Rubika bot token (from @BotFather on Rubika) |
| `OPENROUTER_API_KEY` | **Yes** | Your OpenRouter API key (https://openrouter.ai/keys) |
| `DEFAULT_MODEL` | No | AI model ID. Defaults to `meta-llama/llama-3.1-8b-instruct` (free) if unset |

`config.py` reads these directly from the environment. There is **no
hardcoded fallback value for the two required secrets** — if either is
missing, the bot refuses to start and prints exactly which variable is
missing (never the value) instead of failing later with a confusing error.

## 1. Local development

```bash
cp .env.example .env
# edit .env and fill in your real values
pip install -r requirements.txt
python main.py
```

`.env` is loaded automatically for local runs and is already listed in
`.gitignore`, so it never gets committed. **`.env` is never required or
read in production** — Railway (or any host that injects real environment
variables) always takes priority over anything in `.env`, and the bot
works with no `.env` file present at all.

You should see:
```
🤖 Rubika AI Bot is starting...
```

## 2. Deploy on Railway

1. Push this project to a GitHub repository (see step 3 below).
2. On [railway.app](https://railway.app), create a new project → **Deploy
   from GitHub repo** → select your repository.
3. Open the service's **Variables** tab and add:
   - `RUBIKA_BOT_TOKEN`
   - `OPENROUTER_API_KEY`
   - `DEFAULT_MODEL` *(optional)*
4. Deploy. `railway.json` already tells Railway exactly how to start the
   app (`python main.py`) and to restart it on failure — you shouldn't
   need to set a custom Start Command manually, but if Railway's UI asks,
   use `python main.py`.
5. Since the bot uses long-polling (not a web server), it needs no
   exposed HTTP port — it just runs continuously in the background.

## 3. Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit: Rubika AI bot"
git branch -M main
git remote add origin https://github.com/<your-username>/<your-repo>.git
git push -u origin main
```

Only `.env.example` (placeholder values) is committed — `.env` itself is
git-ignored, and no real credentials appear anywhere in the source code.

---

## Troubleshooting: "RUBIKA_BOT_TOKEN is not set" on Railway

If you see this even after adding the variable in Railway, it's almost
always one of these — check in order:

1. **Wrong service.** Railway variables are scoped per-service. If your
   project has more than one service (or you recreated the service at
   some point), make sure the variable is on the *exact* service that's
   actually running `main.py`, not a different/old one.
2. **Wrong environment.** Railway has separate "environments" (e.g.
   `production`, PR previews). Adding a variable in one environment does
   not add it to another. Confirm you're looking at the same environment
   that's deployed.
3. **Stale deploy.** After adding/changing a variable, Railway normally
   redeploys automatically — but if it doesn't (or you added it while a
   deploy was already in progress), trigger a manual redeploy so the new
   process actually picks it up.
4. **Typo in the variable name.** It must be exactly `RUBIKA_BOT_TOKEN`
   (no extra spaces, no different casing).
5. **Wrong start command.** If Railway wasn't actually running
   `python main.py` (e.g. it auto-detected a different entry point),
   `config.py` would never even get a chance to read the variable. This
   project now ships a `railway.json` that pins the start command
   explicitly, which removes this possibility going forward.

### What was actually wrong in the previous version of this project

Two real bugs were found and fixed, independent of Railway configuration:

- **`bot_handlers.py` imported `from rubpy.bot.models import Update`.**
  That class isn't part of rubpy's public API — importing it raises
  `ImportError` (confirmed against rubpy's actual published source), which
  can crash the app before it ever gets a chance to run. The bot now uses
  rubpy's real, documented handler signature (`client, message`) instead.
- **`main.py` wrapped rubpy's `BotClient.run()` in `asyncio.run(...)`.**
  `BotClient.run()` manages its own event loop internally and is meant to
  be called as a plain, synchronous, top-level call — not awaited inside
  another `asyncio.run()`. The two event loops fighting each other is a
  common source of a bot that appears to "hang" or exit immediately on
  startup. `main.py` now calls `client.run()` exactly the way rubpy's own
  documentation does.
- **A missing token used to just `print(...)` and `return`**, which exits
  the process with code 0 — Railway then quietly restarts it forever,
  repeating the same message with no obvious "crash" in the logs. Missing
  variables now raise `RuntimeError` and exit with code 1, which is much
  clearer to spot in Railway's deploy logs.

## Customizing the bot

- **Personality** — edit `SYSTEM_PROMPT` in `config.py`.
- **Model** — set the `DEFAULT_MODEL` environment variable.
- **Reply only in private chats (not groups)** — in `bot_handlers.py`, change:
  ```python
  @client.on_update(filters.text)
  ```
  to:
  ```python
  @client.on_update(filters.text, filters.private)
  ```
- **Ignore certain chats** — add their chat IDs to `IGNORED_CHAT_GUIDS` in `config.py`.
- **Reply length/creativity** — edit `MAX_TOKENS` and `TEMPERATURE` in `config.py`.

## What was tested, and what couldn't be

This environment has no outbound network access, so the real Rubika and
OpenRouter APIs could not be called directly. Everything below **was**
verified:

- Every file compiles with no syntax errors.
- `config.py`'s validation correctly raises a clear, secret-free error
  when required variables are missing, and correctly loads real values
  when they're set (tested with the credentials you provided).
- A local `.env` file was confirmed to **never** override real,
  already-set environment variables (simulating Railway's behavior).
- `main.py` and `bot_handlers.py` were run end-to-end against a mock of
  rubpy's `BotClient`/`filters` built from rubpy's actual published
  source and documentation — confirming the whole import → register →
  run chain works, and confirming the **old** `bot_handlers.py` genuinely
  fails (`ImportError: No module named 'rubpy.bot.models'`) against that
  same accurate mock, which is why it was rewritten.
- `ai_handler.py` was tested against a mock OpenRouter endpoint for the
  success case, a missing-API-key case, and an HTTP 401 error case — all
  return the correct, user-facing message.

**Not tested (requires live network access you'll need to verify
yourself after deploying):** an actual authenticated call to the real
Rubika Bot API with `RUBIKA_BOT_TOKEN`, and an actual authenticated call
to the real OpenRouter endpoint with `OPENROUTER_API_KEY`. The request
formats for both are the officially documented ones, but only a real
deploy (or a local run with network access) can confirm the live
credentials themselves are valid and unexpired.
