# memeapp — Meme Reply Bot

A Streamlit chat app that answers what you tell it with reaction GIFs and a
one-line caption. Describe what happened ("My boss scheduled a meeting at 5pm
on a Friday...") and the bot replies in the tone you pick.

## How it works

1. **Plan** — an OpenAI model (`gpt-5.4-mini`, set by `MODEL` in
   `meme_bot.py`) turns your message into up to 3 short GIF search phrases
   that match the selected mode. If the model's reply can't be parsed, the bot
   falls back to keywords taken from your own message.
2. **Search** — each phrase is searched on DuckDuckGo images (via `ddgs`),
   keeping only `.gif` results. Near-duplicate searches are skipped.
3. **Caption** — the model writes a short reply line in the mode's voice.

The app shows up to 2 GIFs per reply.

### Meme modes

Pick one in the sidebar:

| Mode | Style |
| --- | --- |
| 🤗 Friendly (default) | warm, supportive, on your side |
| 😈 Mean | savage roast, zero sympathy |
| 🙃 Sarcastic | dry, deadpan, heavy eye-roll |
| 🎭 Dramatic | everything is a catastrophe |
| 🤪 Chaotic | unhinged, random, no thoughts |

## Run it locally

```bash
pip install -r requirements.txt
mkdir -p .streamlit
echo 'OPENAI_API_KEY = "sk-..."' > .streamlit/secrets.toml
streamlit run streamlit_app.py
```

The app stops with an error message if `OPENAI_API_KEY` is missing.
`.streamlit/secrets.toml` is listed in `.gitignore` so the key is not
committed by accident.

### Streamlit Community Cloud

Deploy the repo with `streamlit_app.py` as the main file, then add
`OPENAI_API_KEY` under **Settings → Secrets**.

## Tests

```bash
python -m unittest discover tests
```

The tests cover the phrase parser in `meme_bot.py`. They stub out
`streamlit`, `ddgs` and `langchain`, so they need only the standard library
and never call the model or the network.

## Files

- `streamlit_app.py` — the chat UI (mode picker, chat history, clear button)
- `meme_bot.py` — planning, GIF search, caption and the parsing helpers
- `tests/` — unit tests
