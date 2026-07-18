# Telegram Update Detector Bot

A Telegram bot that intelligently detects schedule and location updates in group chat messages using semantic similarity. Built with Sentence Transformers (bi-encoder + cross-encoder pipeline) and optionally forwards detected updates via SMS through the TextBee API.

## Features

- **Two-stage semantic matching** — A lightweight bi-encoder pre-filters messages, then a cross-encoder verifies them, reducing false positives.
- **Rolling context window** — Maintains a short-term buffer of recent messages so the model can evaluate each message in context.
- **Question suppression** — Messages framed as questions are kept in context but never trigger an alert.
- **Duplicate suppression** — Consecutive identical updates are silently ignored.
- **Optional SMS forwarding** — Detected updates can be forwarded via SMS (TextBee gateway).

## Architecture

| Layer | Component | Purpose |
|-------|-----------|---------|
| Ingestion | `pyTelegramBotAPI` | Listens for incoming group messages |
| Filter | `all-MiniLM-L6-v2` bi-encoder | Quick relevance pre-filter (cosine similarity) |
| Verifier | `stsb-distilroberta-base` cross-encoder | Final confirmation (STS score > 0.6) |
| Notification | TextBee REST API | Optional SMS dispatch |

### Detection pipeline

```
Incoming message
       │
       ▼
Append to rolling buffer (4 min window)
       │
       ▼
Is the message a question? ──Yes──► Keep in buffer, no alert
       │No
       ▼
Bi-encoder: compare context against example updates
       │
       ▼
Max similarity ≥ 0.4? ──No──► Discard
       │Yes
       ▼
Cross-encoder: verify context against examples
       │
       ▼
Max score > 0.6? ──No──► Discard
       │Yes
       ▼
Duplicate of last alert? ──Yes──► Suppress
       │No
       ▼
  ✅ Update detected
```

## Project structure

```
.
├── main.py              # Bot entrypoint, Telegram handler, SMS gateway
├── logic.py             # Detection pipeline and model configuration
├── config.py            # Secrets and settings (git-ignored)
├── .env.example         # Template for environment variables
├── requirements.txt     # Python dependencies
└── README.md
```

## Requirements

- Python 3.9+
- A Telegram bot token (from [@BotFather](https://t.me/botfather))
- (Optional) A [TextBee](https://textbee.dev) account for SMS forwarding

## Setup

1. **Clone the repository**

   ```bash
   git clone <repo-url>
   cd telegram-update-detector
   ```

2. **Create and activate a virtual environment**

   ```bash
   python -m venv .venv
   source .venv/bin/activate   # Linux / macOS
   .venv\Scripts\activate      # Windows
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   pip install sentence-transformers numpy torch
   ```

4. **Configure credentials** — Copy `.env.example` to `.env` and fill in your tokens, or edit `config.py` directly (the file is git-ignored).

   ```bash
   cp .env.example .env
   # Then edit .env with your tokens
   ```

5. **Run the bot**

   ```bash
   python main.py
   ```

   The first run will download the pre-trained models (~90 MB combined).

## Customisation

Tune behaviour in `logic.py`:

| Setting | Default | Description |
|---------|---------|-------------|
| `SIMILARITY_THRESHOLD` | 0.45 | Bi-encoder cosine similarity cutoff |
| `MAX_MESSAGES` | 3 | Number of recent messages kept in context |
| `TIME_WINDOW_MINUTES` | 4 | How long messages stay in the buffer |
| `UPDATE_EXAMPLES` | 6 phrases | Domain-specific phrases the model matches against |

Edit the `UPDATE_EXAMPLES` list to adapt the detector to your specific domain (e.g. classroom changes, meeting room updates, etc.).

## Enabling SMS forwarding

The SMS logic is fully implemented but **commented out** in `main.py`. To enable it:

1. Uncomment the `forward_to_sms` handler in `main.py`.
2. Ensure `TEXTBEE_API_KEY`, `TEXTBEE_DEVICE_ID`, and `SMS_RECIPIENT` are set in your config.

## Security

- `config.py` and `.env` are git-ignored — keep secrets out of version control.
- Consider switching to environment variables or a secrets manager for production deployments.

## Troubleshooting

| Problem | Likely cause |
|---------|--------------|
| Model download hangs | First run downloads models; this is normal |
| `ModuleNotFoundError` | Missing ML dependencies — run `pip install sentence-transformers numpy torch` |
| No detection | Tune `SIMILARITY_THRESHOLD` or expand `UPDATE_EXAMPLES` |

## License

MIT
