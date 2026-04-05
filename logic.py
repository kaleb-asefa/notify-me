from sentence_transformers import SentenceTransformer, CrossEncoder
import numpy as np
from datetime import datetime, timedelta

bi_encoder = SentenceTransformer('all-MiniLM-L6-v2')
# Using a model better suited for "Natural Language Inference" (is A related to B?)
cross_verifier = CrossEncoder('cross-encoder/stsb-distilroberta-base')

# ---- SETTINGS ----
SIMILARITY_THRESHOLD = 0.45 
MAX_MESSAGES = 3
TIME_WINDOW_MINUTES = 4

message_buffer = []
last_update_text = ""

update_examples = [
    "the class is in room 304", "lecture moved to room 102",
    "class is cancelled today", "exam postponed until monday",
    "the new location is 304", "meeting in room 205"
]
example_embeddings = bi_encoder.encode(update_examples)

def is_question(text):
    question_indicators = ['?', 'where', 'when', 'who', 'how', 'is there', 'do we']
    t = text.lower().strip()
    return any(indicator in t for indicator in question_indicators)

def process_message(text):
    global message_buffer, last_update_text
    
    # 1. ALWAYS ADD TO BUFFER (Crucial for context!)
    now = datetime.now()
    message_buffer.append((text, now))
    
    # Cleanup old messages
    message_buffer[:] = [(m, t) for m, t in message_buffer 
                         if now - t <= timedelta(minutes=TIME_WINDOW_MINUTES)]
    
    # 2. IF IT'S A QUESTION, DON'T TRIGGER ALERT (but keep in buffer)
    if is_question(text):
        print(f"[DEBUG] Context updated: {text}")
        return False

    # 3. BUILD CONTEXT
    # We look at the last few messages to see if they "support" the current statement
    context = " ".join([m for m, t in message_buffer])
    
    # 4. PRE-FILTER (Bi-Encoder)
    emb_ctx = bi_encoder.encode(context)
    bi_sims = [np.dot(emb_ctx, ex) / (np.linalg.norm(emb_ctx) * np.linalg.norm(ex)) for ex in example_embeddings]
    max_bi_sim = max(bi_sims)

    if max_bi_sim < 0.4: # Very loose filter
        return False

    # 5. CROSS-ENCODER VERIFICATION
    # Compare context against our "Update Examples"
    pairs = [[context, ex] for ex in update_examples]
    scores = cross_verifier.predict(pairs)
    max_score = max(scores)

    print(f"[DEBUG] Bi-Sim: {max_bi_sim:.2f} | Cross-Score: {max_score:.2f}")

    # 6. FINAL DECISION
    # STS-B Cross-Encoders usually scale 0 to 1. 0.6 is a strong match.
    if max_score > 0.6:
        # Avoid repeating the exact same message
        if text.lower().strip() == last_update_text.lower().strip():
            return False
            
        last_update_text = text
        print(f"✅ NEW UPDATE: {text} (Context: {context})")
        # Don't clear buffer immediately, but maybe shorten it
        return True

    return False