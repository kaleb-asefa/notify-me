from datetime import datetime, timedelta
from typing import List, Tuple

import numpy as np
from sentence_transformers import CrossEncoder, SentenceTransformer

# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

bi_encoder: SentenceTransformer = SentenceTransformer("all-MiniLM-L6-v2")
cross_verifier: CrossEncoder = CrossEncoder("cross-encoder/stsb-distilroberta-base")

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

SIMILARITY_THRESHOLD: float = 0.45
MAX_MESSAGES: int = 3
TIME_WINDOW_MINUTES: int = 4

# ---------------------------------------------------------------------------
# Update examples (domain-specific phrases to match against)
# ---------------------------------------------------------------------------

UPDATE_EXAMPLES: List[str] = [
    "the class is in room 304",
    "lecture moved to room 102",
    "class is cancelled today",
    "exam postponed until monday",
    "the new location is 304",
    "meeting in room 205",
]

_example_embeddings: np.ndarray = bi_encoder.encode(UPDATE_EXAMPLES)

# ---------------------------------------------------------------------------
# Mutable state
# ---------------------------------------------------------------------------

_message_buffer: List[Tuple[str, datetime]] = []
_last_update_text: str = ""

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _is_question(text: str) -> bool:
    """Return True if *text* looks like a question."""
    indicators = ["?", "where", "when", "who", "how", "is there", "do we"]
    lower = text.lower().strip()
    return any(indicator in lower for indicator in indicators)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def process_message(text: str) -> bool:
    """
    Process an incoming message and decide whether it describes a
    schedule / location update.

    Returns ``True`` when an update is detected, ``False`` otherwise.
    """
    global _message_buffer, _last_update_text

    now = datetime.now()

    # 1. Append current message to rolling buffer
    _message_buffer.append((text, now))

    # 2. Evict messages outside the time window
    _message_buffer[:] = [
        (msg, ts)
        for msg, ts in _message_buffer
        if now - ts <= timedelta(minutes=TIME_WINDOW_MINUTES)
    ]

    # 3. Skip questions (but keep them in the buffer for context)
    if _is_question(text):
        return False

    # 4. Build context string from buffered messages
    context = " ".join(msg for msg, _ in _message_buffer)

    # 5. Bi-encoder pre-filter
    ctx_emb = bi_encoder.encode(context)
    similarities = [
        np.dot(ctx_emb, ex)
        / (np.linalg.norm(ctx_emb) * np.linalg.norm(ex))
        for ex in _example_embeddings
    ]
    max_bi_sim = max(similarities)

    if max_bi_sim < 0.4:
        return False

    # 6. Cross-encoder verification
    pairs = [[context, ex] for ex in UPDATE_EXAMPLES]
    scores = cross_verifier.predict(pairs)
    max_score = float(max(scores))

    if max_score > 0.6:
        # Suppress consecutive duplicates
        if text.lower().strip() == _last_update_text.lower().strip():
            return False

        _last_update_text = text
        return True

    return False
