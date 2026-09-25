# Week 3 — Build the Decision Pipeline

## WhatsApp-On-Cruise-Control

Week 3 turns the persona and conversation-history foundations from Weeks 1 and 2 into a working message-processing pipeline.

The goal is to decide **whether the AI should reply at all** before spending resources on retrieval and generation. The system first identifies the sender relationship, then applies deterministic safety and reply rules, and only uses AI when a message is genuinely ambiguous. If an AI service is unavailable, the system fails closed instead of generating an unsafe or uncertain reply.

---

## 1. What Was Built

Week 3 introduces the core agent flow:

```text
Incoming WhatsApp Message
        ↓
Router
        ↓
Relationship
        ↓
Decision Engine
        ↓
Retrieve Relevant History
        ↓
Persona + Context
        ↓
Generator
        ↓
Reply / Ignore
```

The important principle is:

> **Cheap, deterministic rules first. Use AI only when necessary.**

The system should not automatically reply to every incoming message.

---

## 2. Week 3 Starting Point

Week 1 created the persona foundation:

* WhatsApp conversation exports
* style signals
* relationship-specific persona
* sample replies
* architecture documentation

Week 2 added the conversation-history layer:

* processed conversation pairs
* relationship mapping
* multilingual embeddings
* ChromaDB collections
* relationship-specific retrieval

Week 3 combines these foundations into the first working decision pipeline.

### Foundation from previous weeks

```text
Week 1
Persona Brain
    ↓
How should I sound?

Week 2
History Brain
    ↓
What have I previously said?

Week 3
Decision Pipeline
    ↓
Should I reply?
What kind of message is this?
Which relationship does it belong to?
```

---

## 3. Week 3 Project Structure

```text
week3/
│
├── agent/
│   ├── __init__.py
│   ├── batch_test.py
│   ├── decision_engine.py
│   ├── generator.py
│   ├── pipeline.py
│   ├── router.py
│   ├── test_pipeline.py
│   ├── test_router.py
│   └── validate_relationship_map.py
│
├── config/
│   ├── constants.py
│   ├── contact_relationship_map.json
│   └── relationship_map.json
│
├── data/
│
├── docs/
│
├── ingestion/
│
├── logs/
│
├── persona/
│
├── .env
├── README.md
├── retrieval_results.txt
└── test.py
```

### Important Week 3 files

| File                                 | Purpose                                                    |
| ------------------------------------ | ---------------------------------------------------------- |
| `agent/router.py`                    | Identifies the relationship from the WhatsApp JID          |
| `agent/decision_engine.py`           | Decides whether a message should be ignored or processed   |
| `agent/pipeline.py`                  | Connects the Week 3 processing stages                      |
| `agent/generator.py`                 | Generates a persona-style reply when generation is allowed |
| `agent/batch_test.py`                | Runs multiple realistic message scenarios                  |
| `agent/test_router.py`               | Tests relationship routing and safety cases                |
| `agent/test_pipeline.py`             | Tests pipeline decision behavior                           |
| `agent/validate_relationship_map.py` | Validates the phone-number relationship map                |
| `config/relationship_map.json`       | Maps known phone numbers to relationships                  |
| `config/constants.py`                | Stores project constants                                   |
| `agent/__init__.py`                  | Marks `agent` as a Python package                          |

---

# 4. Router

The Router is intentionally **not AI-based**.

It takes a WhatsApp JID and determines the relationship.

Example:

```text
phone number
     ↓
relationship_map.json
     ↓
family / friend / professional / unknown
```

Groups are handled separately and are not resolved through the personal relationship map.

This keeps the first stage cheap, predictable, and deterministic.

---

# 5. Decision Engine

After routing, the Decision Engine determines whether the message should proceed.

The logic follows the principle:

```text
Hard rules
    ↓
Signal rules
    ↓
Intent check
    ↓
Reply policy
```

Examples of messages that can be ignored:

* messages sent by the account itself
* group messages
* unknown senders
* media-only messages without useful text
* forwarded content
* low-signal acknowledgements such as "thanks" or "Okay"

The purpose is to avoid unnecessary AI calls and unwanted replies.

---

# 6. AI Intent Check

For messages that cannot be confidently classified using cheap rules, the Decision Engine can use an AI intent check.

However, AI is treated as a secondary layer rather than the first step.

If the AI service fails, the system uses a **fail-closed** behavior:

```text
AI unavailable
     ↓
Do not guess
     ↓
Ignore / require human handling
```

During Week 3 testing, Gemini returned temporary:

```text
503 UNAVAILABLE
```

The application handled this safely by returning an ignore decision instead of crashing or sending an uncertain reply.

---

# 7. Generator

The Generator is responsible for producing a reply after the pipeline has decided that a reply is appropriate.

It uses the relationship context and persona/history information to produce a response in the user's style.

The generator also handles API failures safely.

During testing, Gemini returned a temporary `503 UNAVAILABLE` response. The Generator caught the error and returned its configured fallback response instead of terminating the application.

---

# 8. Week 3 Batch Testing

The batch test covers different types of incoming messages.

Test scenarios included:

* own message
* group message
* unknown sender
* media-only message
* forwarded message
* low-signal acknowledgement
* money-related message
* casual friend message
* family message
* professional message

The batch test completed successfully:

```text
WEEK 3 BATCH TEST — ROUTER → DECISION ENGINE → GENERATOR

BATCH TEST COMPLETE
```

---

# 9. Automated Tests

Week 3 uses `pytest`.

The Week 3-specific test command is:

```powershell
pytest .\agent -v
```

Final result:

```text
collected 9 items

9 passed
```

### Router tests

```text
5 passed
```

The Router tests verify:

* known number resolution
* unknown-number fallback
* group JID handling
* empty JID safety
* malformed JID safety

### Pipeline tests

```text
4 passed
```

The Pipeline tests verify:

* unknown sender is ignored
* group chat is ignored
* low-signal acknowledgement is ignored
* money/ambiguous message fails closed when the intent service is unavailable

### Final Week 3 test result

```text
9 passed in 37.32s
```

---

# 10. Running Week 3

Activate the Week 3 environment:

```powershell
cd C:\Users\psinh\Desktop\MasaiProjects\WhatsApp-On-Cruise-Control\week3
.\.venv\Scripts\Activate.ps1
```

Verify Python:

```powershell
python --version
```

Expected:

```text
Python 3.13.0
```

Run Week 3 tests:

```powershell
pytest .\agent -v
```

Run the batch test:

```powershell
python -m agent.batch_test
```

The `-m` form is important because `batch_test.py` imports the `agent` package from the Week 3 project root.

---

# 11. Why `python -m agent.batch_test` Is Used

Running:

```powershell
python .\agent\batch_test.py
```

caused:

```text
ModuleNotFoundError: No module named 'agent'
```

The problem was Python's import path when executing the file directly.

The correct package-aware command is:

```powershell
python -m agent.batch_test
```

This runs `batch_test` as part of the `agent` package and allows imports such as:

```python
from agent.router import resolve_relationship
```

to work correctly.

---

# 12. Package Initialization

The `agent` directory initially did not contain:

```text
agent/__init__.py
```

It was created as an empty file.

Its purpose is to identify `agent` as a Python package.

No code is required inside this file.

---

# 13. Week 3 Safety Principle

The most important behavior introduced in Week 3 is:

> **The system should prefer silence over an uncertain automated reply.**

The pipeline therefore uses:

```text
Known + safe
      ↓
Continue

Unknown / unsafe / ambiguous
      ↓
Ignore or require human handling

AI unavailable
      ↓
Fail closed
```

This behavior becomes especially important before connecting the agent to real WhatsApp messages in Week 4.

---

# 14. Week 3 Completion Checklist

* [x] Created dedicated Week 3 virtual environment
* [x] Installed Week 3 dependencies
* [x] Verified Python environment
* [x] Created/verified relationship map
* [x] Added Router
* [x] Added Router tests
* [x] Added Decision Engine
* [x] Added Pipeline
* [x] Added Generator
* [x] Added Pipeline tests
* [x] Added `agent/__init__.py`
* [x] Fixed package imports
* [x] Fixed pytest test discovery
* [x] Validated Router
* [x] Validated Pipeline
* [x] Ran batch test
* [x] Tested Generator fallback behavior
* [x] Confirmed 9/9 Week 3 automated tests pass
* [x] Confirmed fail-closed behavior when Gemini is unavailable

## Week 3 Status

**COMPLETE — Core Week 3 agent pipeline verified.**

The system is now ready for Week 4 integration with WhatsApp/Baileys, where the focus will be connecting the agent to actual WhatsApp messages while keeping DRY_RUN, allowlisting, delays, and kill-switch protections in place.




python -m pip install python-dotenv google-genai chromadb sentence-transformers
already done in week1 (python-dotenv google-genai) & week2 (chromadb sentence-transformers)
In Week3 install-
python -m pip install pytest 

python .\agent\validate_relationship_map.py
pytest .\agent\test_router.py -v
pytest .\agent\test_pipeline.py -v
pytest -v
python .\agent\batch_test.py
python -c "from agent.generator import generate_reply; print(generate_reply('friend', 'Hello yaar'))"
pytest .\agent -v
---------------------------------
where.exe python
python --version

python -c "import pytest, dotenv, google.genai, chromadb; from sentence_transformers import SentenceTransformer; print('Week 3 dependencies OK')"

python .\agent\validate_relationship_map.py

pytest .\agent\test_router.py -v

pytest .\agent\test_pipeline.py -v

pytest -v

python .\agent\batch_test.py

Get-Content .\logs\decision_log.jsonl -Tail 10

python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('GEMINI_API_KEY loaded:', bool(os.getenv('GEMINI_API_KEY')))"