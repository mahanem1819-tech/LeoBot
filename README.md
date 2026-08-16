# Rubika AI Bot (rubpy + OpenRouter)

A simple Rubika messenger bot that answers every incoming message using
an AI model through the [OpenRouter](https://openrouter.ai) API.

This bot authenticates with a **Rubika Bot Token** (not a personal
account/session login), so it can run 24/7 unattended on a host like
[Railway](https://railway.app) with zero interactive setup.

## Project structure

```
rubika_ai_bot/
├── main.py            # Entry point — run this to start the bot
├── config.py           # All settings: reads env vars, with local fallbacks
├── ai_handler.py        # Talks to OpenRouter and returns the AI's reply
├── bot_handlers.py      # Listens to Rubika messages and replies
├── requirements.txt     # Python dependencies
├── .env.example         # Template for local environment variables
├── .gitignore           # Keeps .env and other junk out of git
├── Procfile             # Tells Railway how to run the bot
└── README.md            # This file
```

## 1. Get your Rubika Bot Token

1. Open Rubika and start a chat with [@BotFather](https://rubika.ir/BotFather).
2. Create a new bot and follow its instructions.
3. Copy the **Bot Token** it gives you — you'll need it below.

There is no phone-number login, QR code, or session file involved —
the bot token is all the bot needs to authenticate.

## 2. Get your OpenRouter API key

Sign up at [openrouter.ai](https://openrouter.ai) and create a key at
https://openrouter.ai/keys.

## 3. Where do these values go?

`config.py` reads both secrets from **environment variables first**:

- `OPENROUTER_API_KEY`
- `RUBIKA_BOT_TOKEN`
- `DEFAULT_MODEL` (optional — defaults to `meta-llama/llama-3.1-8b-instruct`, a free model)

If an environment variable isn't set, it falls back to the placeholder
string inside `config.py` — which is only meant for quick local testing,
never for a real deployment.

### Local development (recommended way)

1. Copy `.env.example` to a new file named `.env`:
   ```bash
   cp .env.example .env
   ```
2. Open `.env` and fill in your real values:
   ```
   OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   RUBIKA_BOT_TOKEN=123456:AbCdEf...
   DEFAULT_MODEL=meta-llama/llama-3.1-8b-instruct
   ```
3. `config.py` automatically loads `.env` on startup (via `python-dotenv`).
   `.env` is already listed in `.gitignore`, so it will never be committed.

### Local development (quick-and-dirty alternative)

If you don't want to use a `.env` file, you can instead paste your
values directly into the fallback strings in `config.py`:

```python
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "PUT_YOUR_OPENROUTER_API_KEY_HERE")
RUBIKA_BOT_TOKEN = os.getenv("RUBIKA_BOT_TOKEN", "PUT_YOUR_RUBIKA_BOT_TOKEN_HERE")
```

Just replace the placeholder strings. **Do not do this if you plan to
push this project to a public GitHub repository** — use the `.env`
method instead so your secrets stay out of git.

## 4. Install dependencies and run locally

```bash
pip install -r requirements.txt
python main.py
```

You should see:
```
🤖 Rubika AI Bot is starting...
```

The bot then listens for new incoming text messages, sends each one to
the AI model configured in `config.py`, and replies in the same chat.
Press `Ctrl+C` to stop it.

## 5. Upload the project to GitHub

1. Create a new (private, if you prefer) repository on GitHub.
2. Make sure `.env` is **not** included — it's already in `.gitignore`,
   so a normal `git add .` will skip it automatically.
3. Push the project:
   ```bash
   git init
   git add .
   git commit -m "Initial commit: Rubika AI bot"
   git branch -M main
   git remote add origin https://github.com/<your-username>/<your-repo>.git
   git push -u origin main
   ```

Only `.env.example` (with placeholder values) goes to GitHub — your
real `OPENROUTER_API_KEY` and `RUBIKA_BOT_TOKEN` never leave your machine
except as Railway environment variables (next step).

## 6. Deploy on Railway

1. Go to [railway.app](https://railway.app) and create a new project.
2. Choose **"Deploy from GitHub repo"** and select the repository you
   just pushed.
3. Railway will detect it's a Python project and install
   `requirements.txt` automatically.
4. Open the project's **Variables** tab and add:

   | Variable | Value |
   |---|---|
   | `OPENROUTER_API_KEY` | your real OpenRouter key |
   | `RUBIKA_BOT_TOKEN` | your real Rubika bot token |
   | `DEFAULT_MODEL` | *(optional)* e.g. `meta-llama/llama-3.1-8b-instruct` |

5. Under the service's settings, make sure the **Start Command** runs
   the bot: `python main.py`
   (The included `Procfile` already declares this as a `worker`
   process — if Railway asks you to pick a start command explicitly,
   use `python main.py`.)
6. Deploy. Since the bot uses long-polling (not a web server), it
   doesn't need an exposed HTTP port — it will just run continuously
   in the background, 24/7, reconnecting automatically.

That's it — no login prompts, no session files, nothing else to
configure. The bot will start responding as soon as the deploy
finishes.

## 7. Customizing the bot

- **Change the AI's personality/behavior** — edit `SYSTEM_PROMPT` in `config.py`.
- **Change the model** — set the `DEFAULT_MODEL` environment variable, or edit the fallback in `config.py`.
- **Reply only in private chats (not groups)** — in `bot_handlers.py`, change:
  ```python
  @client.on_update(filters.text)
  ```
  to:
  ```python
  @client.on_update(filters.text, filters.private)
  ```
- **Ignore certain chats** — add their chat IDs to `IGNORED_CHAT_GUIDS` in `config.py`.
- **Adjust reply length/creativity** — edit `MAX_TOKENS` and `TEMPERATURE` in `config.py`.

## Notes

- The bot skips messages sent by other bots to avoid reply loops.
- If the OpenRouter API key is missing or invalid, the bot replies
  with a clear warning message instead of crashing.
- Network or API errors are caught and reported back as a chat message
  rather than stopping the bot.
- If `RUBIKA_BOT_TOKEN` is missing, the bot prints a clear error and
  exits instead of starting.
- `rubpy`'s public API can change between versions; if `main.py` or
  `bot_handlers.py` raise an error about a missing method/attribute,
  check your installed `rubpy` version's documentation
  (https://rubpy.shayan-heidari.ir/) and adjust the client calls
  accordingly.
