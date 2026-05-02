# Telegram Update Detector Bot

Detects schedule/location updates in Telegram chat messages using semantic similarity, with optional SMS forwarding via TextBee.

## Features
- Context-aware detection using a rolling message window
- Two-stage semantic matching (bi-encoder filter + cross-encoder verification)
- Ignores question-style messages to reduce false positives
- Duplicate update suppression
- Optional TextBee SMS forwarding (currently commented out in code)

## How It Works
1. Incoming messages are buffered for a short time window.
2. The buffered context is embedded and compared to example update phrases.
3. A cross-encoder verifies whether the context is likely an update.
4. If verified, the bot responds and logs the update.

## Project Structure
- main.py: Telegram bot entry point and message handler
- logic.py: Update detection logic and model configuration
- config.py: API tokens and settings
- requirements.txt: Base Python dependencies

## Requirements
- Python 3.9+
- Telegram bot token
- (Optional) TextBee account and device ID

## Setup
1. Create and activate a virtual environment.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Install ML dependencies used by the detection logic:
   ```bash
   pip install sentence-transformers numpy torch
   ```
4. Update config.py with your credentials:
   - api_token: Telegram bot token
   - TEXTBEE_API_KEY: TextBee API key (optional)
   - TEXTBEE_DEVICE_ID: TextBee device ID (optional)
   - phone_number: SMS recipient (optional)

## Run
```bash
python main.py
```

## Configuration and Tuning
Adjust thresholds and behavior in logic.py:
- SIMILARITY_THRESHOLD (bi-encoder filter)
- MAX_MESSAGES (context size)
- TIME_WINDOW_MINUTES (buffer window)

Update example phrases in update_examples to match your domain.

## Enable SMS Forwarding (Optional)
The TextBee SMS sending logic is present but commented out in main.py. Uncomment the block under the "TextBee API setup" section to enable forwarding.

## Security Notes
Do not commit real tokens. Consider moving secrets to environment variables or a .env file and loading them in config.py.

## Troubleshooting
- If model downloads take a while, this is normal on first run.
- If you see missing package errors, install the listed ML dependencies.
