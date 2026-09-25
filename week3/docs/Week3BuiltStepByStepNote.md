# Week 3 — Detailed Build Notes

## Project

**Project:** WhatsApp-On-Cruise-Control
**Week:** 3
**Goal:** Build and test the decision pipeline before connecting the agent to real WhatsApp.

---

# PART 1 — Where Week 3 Started

Week 1 and Week 2 were completed before starting Week 3.

## Week 1 produced the Persona Brain

Week 1 established:

```text
WhatsApp exports
      ↓
Style extraction
      ↓
Persona
      ↓
Sample replies
```

Important Week 1 outputs included:

```text
persona/persona.json
persona/style_signals.json
persona/sample_outputs.md
data/raw_export/
docs/architecture_diagram.png
docs/architecture_diagram.excalidraw
```

The persona describes how the user communicates, including relationship-specific tone.

---

# PART 2 — Week 2 Produced the History Brain

Week 2 added the conversation-memory side of the project.

The flow became:

```text
WhatsApp conversation pairs
        ↓
Relationship mapping
        ↓
Multilingual embeddings
        ↓
ChromaDB
        ↓
Relationship-specific history
```

Important Week 2 outputs included:

```text
data/processed_pairs.jsonl
config/contact_relationship_map.json
ingestion/validate_relationship_map.py
ingestion/embed_to_chroma.py
ingestion/retrieval_demo.py
retrieval_results.txt
```

The ChromaDB collections included:

```text
history_family
history_friend
history_professional
history_unknown
```

Week 2 therefore answered:

> "What relevant conversation history should the agent remember?"

---

# PART 3 — Why Week 3 Was Needed

At the end of Week 2, the project could retrieve relevant history, but it still needed an actual decision-making layer.

The agent should not simply do:

```text
Message → AI → Reply
```

Instead, Week 3 introduces:

```text
Message
   ↓
Router
   ↓
Decision Engine
   ↓
Retrieval
   ↓
Persona + History
   ↓
Generator
```

The key idea is:

> **Do not spend an AI call or generate a reply when a simple rule already tells us what to do.**

---

# PART 4 — Creating Week 3

A separate Week 3 environment was created rather than reusing the Week 2 virtual environment.

Project location:

```text
C:\Users\psinh\Desktop\MasaiProjects\WhatsApp-On-Cruise-Control\week3
```

The Week 3 virtual environment was created with Python 3.13:

```powershell
cd C:\Users\psinh\Desktop\MasaiProjects\WhatsApp-On-Cruise-Control\week3
py -3.13 -m venv .venv
```

Then it was activated:

```powershell
.\.venv\Scripts\Activate.ps1
```

The environment was verified with:

```powershell
where.exe python
```

The first Python path was:

```text
...\WhatsApp-On-Cruise-Control\week3\.venv\Scripts\python.exe
```

Python was then checked:

```powershell
python --version
```

Result:

```text
Python 3.13.0
```

This confirmed that Week 3 was using its own virtual environment.

---

# PART 5 — Installing Week 3 Dependencies

The Week 3 dependencies were installed with:

```powershell
python -m pip install pytest python-dotenv google-genai chromadb sentence-transformers
```

The installation was verified using:

```powershell
python -c "import pytest, dotenv, google.genai, chromadb; from sentence_transformers import SentenceTransformer; print('Week 3 dependencies OK')"
```

Result:

```text
Week 3 dependencies OK
```

This confirmed that the required Python packages were available inside the Week 3 environment.

---

# PART 6 — Week 3 Folder Structure

The Week 3 project contained:

```text
week3/
├── .venv
├── agent
├── config
├── data
├── docs
├── ingestion
├── logs
├── persona
├── .env
├── README.md
├── retrieval_results.txt
└── test.py
```

The important new Week 3 working area was:

```text
agent/
```

Inside it:

```text
agent/
├── batch_test.py
├── decision_engine.py
├── generator.py
├── pipeline.py
├── router.py
├── test_pipeline.py
├── test_router.py
└── validate_relationship_map.py
```

Later, an empty package marker was added:

```text
agent/__init__.py
```

---

# PART 7 — Relationship Map

Week 3 uses:

```text
config/relationship_map.json
```

This is the live Router mapping used to identify relationships from WhatsApp phone numbers.

The older Week 2 file:

```text
config/contact_relationship_map.json
```

was retained because it belongs to the Week 2 history/ingestion foundation.

The two files should not be confused.

---

# PART 8 — Relationship Map Validation

The validation script was run:

```powershell
python .\agent\validate_relationship_map.py
```

Result:

```text
Checked: config\relationship_map.json
Phone-number entries: 3

✅ Relationship map validation passed
```

This confirmed that the Week 3 relationship map was valid.

Real personal phone numbers should remain local and should not be placed into public documentation.

---

# PART 9 — Router

The Router was already designed to be deterministic.

Its responsibility:

```text
WhatsApp JID
      ↓
Phone number extraction
      ↓
relationship_map.json
      ↓
relationship
```

Possible results include:

```text
family
friend
professional
unknown
group
```

The Router does not use AI.

This keeps relationship identification predictable and inexpensive.

---

# PART 10 — Router Tests

The Router tests were run with:

```powershell
pytest .\agent\test_router.py -v
```

The final result:

```text
5 passed in 0.18s
```

Tests covered:

```text
known number → correct relationship
unknown number → default/unknown
group JID → not resolved through personal relationship map
empty JID → safe fallback
malformed JID → safe fallback
```

---

# PART 11 — First Import Problem

When the Pipeline test was initially run:

```powershell
pytest .\agent\test_pipeline.py -v
```

Python reported:

```text
ModuleNotFoundError: No module named 'agent'
```

The same problem appeared when running:

```powershell
pytest -v
```

and:

```powershell
python .\agent\batch_test.py
```

The Router logic itself was not the problem.

The `agent` directory was missing:

```text
agent/__init__.py
```

An empty package marker was therefore created.

The file intentionally contains no code.

---

# PART 12 — Second Problem: Pytest Found Zero Tests

After fixing the package import, the Pipeline test produced:

```text
collected 0 items
```

The reason was that `test_pipeline.py` contained a top-level loop instead of pytest test functions.

The old structure was effectively:

```text
tests list
   ↓
for loop
   ↓
process_message()
```

Pytest does not count an ordinary top-level loop as a test.

The file was changed to proper pytest functions:

```text
test_unknown_sender()
test_group_chat()
test_one_word_ack()
test_money_message()
```

After the change, pytest successfully discovered:

```text
4 items
```

---

# PART 13 — Pipeline Test Behavior

The Pipeline tests were designed around the actual safety behavior.

### Unknown sender

```text
Relationship: unknown
Decision: ignore
Reason: sender not in allowlist
```

Expected:

```text
None
```

### Group chat

```text
Relationship: group
Decision: ignore
Reason: group chat, not allowlisted
```

Expected:

```text
None
```

### One-word acknowledgement

```text
Relationship: friend
Decision: ignore
Reason: low-signal ack, no reply needed
```

Expected:

```text
None
```

### Money message

The intent check attempted to use Gemini.

Gemini returned:

```text
503 UNAVAILABLE
```

The Decision Engine failed closed:

```text
Decision: ignore
Reason: intent check requires human
```

Expected:

```text
None
```

This is intentional safety behavior.

---

# PART 14 — Pipeline Tests Passed

The Pipeline test was run:

```powershell
pytest .\agent\test_pipeline.py -v
```

Final result:

```text
4 passed in 45.93s
```

This verified the expected ignore/fail-closed behavior.

---

# PART 15 — Full Week 3 Agent Tests

The complete Week 3 test suite was then run with:

```powershell
pytest .\agent -v
```

Result:

```text
collected 9 items

9 passed in 37.32s
```

Breakdown:

```text
Pipeline tests: 4 passed
Router tests:   5 passed
-------------------------
Total:          9 passed
```

This is the main automated Week 3 verification command.

---

# PART 16 — Why `pytest -v` Was Not Used for Week 3 Completion

Running:

```powershell
pytest -v
```

from the Week 3 root also discovered:

```text
persona/test_persona.py
```

That is an older Week 1 test.

That test makes a live Gemini API call during test collection.

Gemini returned:

```text
503 UNAVAILABLE
```

Therefore the complete root-level pytest command was not a clean Week 3 verification command.

The correct Week 3-specific command is:

```powershell
pytest .\agent -v
```

which produced:

```text
9 passed
```

---

# PART 17 — Batch Test Import Problem

Initially:

```powershell
python .\agent\batch_test.py
```

failed with:

```text
ModuleNotFoundError: No module named 'agent'
```

The reason was the way Python sets its import path when a file inside the package is executed directly.

The correct command was:

```powershell
python -m agent.batch_test
```

This tells Python to run `batch_test` as a module inside the `agent` package.

---

# PART 18 — Batch Test

The batch test was successfully executed:

```powershell
python -m agent.batch_test
```

It loaded the multilingual embedding model and executed the Week 3 scenarios.

The test completed with:

```text
BATCH TEST COMPLETE
```

The scenarios included:

```text
own message
group chat
unknown sender
media-only message
forwarded content
low-signal acknowledgement
money-related message
friend message
family message
professional message
```

---

# PART 19 — Gemini 503 During Batch Test

Several ambiguous messages reached the AI intent-check stage.

Gemini returned:

```text
503 UNAVAILABLE
```

The application did not crash.

Instead:

```text
Gemini unavailable
       ↓
fail closed
       ↓
ignore / human handling
```

This is an important Week 3 safety property.

---

# PART 20 — Generator Test

The Generator was tested independently with:

```powershell
python -c "from agent.generator import generate_reply; print(generate_reply('friend', 'Hello yaar'))"
```

The embedding model loaded successfully.

Gemini returned:

```text
503 UNAVAILABLE
```

The Generator caught the API failure and returned its safe fallback:

```text
Sorry, thoda busy hoon abhi. Baad mein reply karti hoon.
```

Therefore the Generator was confirmed to handle API failure without crashing.

---

# PART 21 — Hugging Face Warning

During embedding-model loading, a warning appeared:

```text
Warning: You are sending unauthenticated requests to the HF Hub.
```

This was a warning about Hugging Face authentication/rate limits.

The model still loaded successfully:

```text
Loading weights: 100%
```

Therefore this was not treated as a Week 3 code failure.

---

# PART 22 — Week 3 Architecture

The resulting Week 3 architecture is:

```text
WhatsApp Message
       ↓
     Router
       ↓
Relationship
       ↓
Decision Engine
       ↓
Cheap deterministic rules
       ↓
Intent check when necessary
       ↓
Reply / Ignore
       ↓
Retrieval
       ↓
History Brain
       +
Persona Brain
       ↓
Generator
       ↓
Reply
```

The important architectural separation is:

```text
Router
→ Who is this?

Decision Engine
→ Should I reply?

Retrieval
→ What relevant history do I have?

Persona
→ How should I sound?

Generator
→ What should I say?
```

---

# PART 23 — Final Week 3 Verification

## Environment

```text
Python 3.13.0
Week 3 .venv
```

## Dependencies

```text
pytest
python-dotenv
google-genai
chromadb
sentence-transformers
```

## Relationship Map

```text
3 phone-number entries
Validation passed
```

## Router

```text
5/5 tests passed
```

## Pipeline

```text
4/4 tests passed
```

## Combined Week 3 tests

```text
9/9 passed
```

## Batch Test

```text
BATCH TEST COMPLETE
```

## Generator

```text
API failure handled with fallback
```

## Gemini

```text
Temporary 503 observed
Fail-closed behavior verified
```

---

# PART 24 — Week 3 Completion Status

**Week 3 Core Implementation: COMPLETE**

The Week 3 agent can now:

1. Receive a structured WhatsApp-style message.
2. Identify the sender relationship.
3. Handle groups separately.
4. Reject unknown/unallowlisted senders.
5. Ignore low-signal messages.
6. Ignore forwarded/media-only content where appropriate.
7. Use AI only when deterministic rules are insufficient.
8. Fail closed when the AI service is unavailable.
9. Connect the decision stage to the generation stage.
10. Handle generator API failure with a fallback.
11. Pass the complete Week 3 automated test suite.

Final automated result:

```text
9 passed
```

---

# PART 25 — What Week 4 Will Add

Week 3 is intentionally not connected to live WhatsApp yet.

Week 4 will add:

```text
Real WhatsApp
      ↓
Baileys
      ↓
Week 3 Agent
      ↓
Decision
      ↓
Reply
      ↓
Baileys
      ↓
WhatsApp
```

with safety controls such as:

```text
DRY_RUN
Allowlist
Human-like delay
Kill switch
Live/DRY_RUN setting
Independent send-time safety check
```

The recommended development sequence is to keep the system in **DRY_RUN** while testing the real WhatsApp connection before considering any live sending.
