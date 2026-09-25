# Week 4 — Go Live on WhatsApp

## Goal

The goal of Week 4 was to connect the AI agent built in Weeks 1–3 to WhatsApp and add the safety controls required for controlled automation.

By the beginning of Week 4, the project already had:

* Persona Brain
* History Brain
* Router
* Decision Engine
* Retrieval
* AI Generation
* Complete offline agent pipeline

Week 4 added the communication layer between the Python agent and WhatsApp.

The final flow became:

```text
WhatsApp
    ↓
Baileys
    ↓
Flask Bridge
    ↓
Router
    ↓
Decision Engine
    ↓
Retrieval
    ↓
Persona + Generation
    ↓
Safety Checks
    ↓
Human-like Delay
    ↓
Baileys
    ↓
WhatsApp Reply
```

---

# Session 4.1 — Connect the Agent to WhatsApp

## Flask Bridge

A Flask bridge was created in:

```text
agent/bridge.py
```

The bridge provides an HTTP endpoint:

```text
POST /process
```

running on:

```text
http://127.0.0.1:5001
```

Its purpose is to connect the Node.js WhatsApp layer with the Python AI agent.

The bridge receives information such as:

* WhatsApp JID
* message text
* message type
* forwarded-message status
* whether the message was sent by the user

It then passes the message through the existing Python agent pipeline.

---

# Flask Bridge Flow

```text
Baileys
   ↓
POST /process
   ↓
Flask Bridge
   ↓
Relationship Router
   ↓
Decision Engine
   ↓
Retrieval
   ↓
Generation
   ↓
Decision + Reply
   ↓
Flask Response
   ↓
Baileys
```

This allowed the Node.js WhatsApp layer and Python AI layer to communicate without moving the entire project into one programming language.

---

# Baileys WhatsApp Client

The WhatsApp client was created in:

```text
whatsapp/baileys_client.js
```

Baileys handles the WhatsApp connection and listens for incoming messages.

When a message arrives, the client extracts information such as:

* sender JID
* message text
* message type
* forwarded status

It then sends that information to the Flask bridge.

---

# WhatsApp JID

Baileys provides the sender's WhatsApp identifier as a JID.

For a normal one-to-one WhatsApp conversation, it has a structure similar to:

```text
PHONE_NUMBER@s.whatsapp.net
```

The system uses this identifier to:

1. identify the sender
2. extract the phone number
3. perform the relationship lookup
4. apply the allowlist
5. send the reply back to the correct WhatsApp conversation

Group JIDs are handled separately and are not processed as normal one-to-one conversations.

---

# Message Handling

The Baileys client handles different message types, including:

```text
text
image
audio
video
```

Text and supported media messages are forwarded to the Python bridge for processing.

Messages sent by the connected WhatsApp account itself are skipped.

Group messages are also skipped because the agent is designed around relationship-specific one-to-one conversations.

---

# Streamlit Console

A monitoring console was created in:

```text
console/app.py
```

The console provides visibility into the running agent.

It displays information such as:

* recent messages
* relationship
* reply/ignore decision
* decision reason
* generated reply
* retrieval trace
* message metrics

The console runs with:

```powershell
streamlit run .\console\app.py
```

---

# Live Feed

The console reads the agent's message records from:

```text
logs/console_feed.jsonl
```

This allows the UI to show recent processing activity.

The console also shows:

```text
Messages processed
Replies generated
```

These metrics describe the messages already recorded by the system; changing DRY RUN/LIVE mode itself does not generate or send a message.

---

# Retrieval Trace

For messages that use retrieval, the console can show the retrieval results.

This makes it possible to inspect which historical conversation examples were retrieved before generating the reply.

This is useful for debugging and understanding why the model produced a particular response.

---

# Session 4.2 — Safety Rails

After connecting the agent to WhatsApp, the next step was to add safety controls.

The four main controls are:

```text
1. DRY RUN / LIVE
2. Allowlist
3. Human-like delay
4. Kill switch
```

---

# Shared Settings

The project uses:

```text
config/settings.json
```

Example:

```json
{
  "dry_run": true,
  "min_delay_seconds": 5,
  "max_delay_seconds": 14
}
```

This file is shared between the Python and Node.js parts of the system.

It controls:

* whether messages are actually sent
* minimum reply delay
* maximum reply delay

The default development state is:

```text
DRY RUN
```

---

# Python Settings Wrapper

The Python settings wrapper is:

```text
config/settings.py
```

It provides functions for:

```text
load_settings()
is_dry_run()
is_kill_switch_active()
get_allowlist()
enforce_allowlist()
```

The wrapper uses safe defaults if the settings file is missing or invalid.

This prevents configuration errors from crashing the agent.

---

# DRY RUN Mode

DRY RUN is the safe default.

When:

```json
{
  "dry_run": true
}
```

the system:

1. receives the message
2. runs the agent
3. generates a reply
4. displays/logs what would have been sent
5. does **not** call WhatsApp's `sendMessage`

The console displays the generated reply while keeping the actual sending disabled.

---

# LIVE Mode

The Streamlit console provides a LIVE toggle.

When LIVE mode is enabled:

```json
{
  "dry_run": false
}
```

the system is allowed to send replies, subject to the other safety checks.

The toggle changes only the `dry_run` value and preserves the configured delay values.

A fresh development session should always begin in DRY RUN mode.

---

# Configurable Human-like Delay

The console provides controls for:

```text
Minimum delay
Maximum delay
```

The settings are stored in:

```text
config/settings.json
```

For example:

```json
{
  "dry_run": true,
  "min_delay_seconds": 5,
  "max_delay_seconds": 14
}
```

Before sending a reply, the Baileys client selects a random delay between the configured minimum and maximum values.

This avoids sending every reply immediately after the incoming message.

The console also validates that:

```text
minimum delay < maximum delay
```

and that both values are positive.

---

# Allowlist

The allowlist prevents the agent from automatically sending replies to contacts that are not explicitly approved.

The relationship map is:

```text
config/relationship_map.json
```

A contact is allowed when its relationship is not:

```text
unknown
```

and is not missing.

The Python implementation provides:

```text
enforce_allowlist(jid)
```

The JID is stripped before the `@` symbol and checked against the configured relationship map.

---

# Independent Node.js Allowlist Check

The Baileys client performs its own allowlist check directly from:

```text
config/relationship_map.json
```

This is intentionally independent from the Python-side allowlist.

The check happens immediately before `sock.sendMessage()`.

If the check fails, the message is blocked and the client logs:

```text
[BLOCKED] failed independent allowlist check
```

This creates a second safety layer at the actual WhatsApp sending point.

---

# Kill Switch

The project uses a repository-root file:

```text
kill_switch.flag
```

The existence of this file means:

> Stop WhatsApp processing.

The Streamlit console provides a prominent:

```text
🛑 KILL SWITCH
```

button.

Activating it creates the empty `kill_switch.flag` file.

The console then displays a warning that the kill switch is active.

---

# Clearing the Kill Switch

The console also provides:

```text
Clear kill switch
```

This deletes:

```text
kill_switch.flag
```

and removes the warning from the console.

---

# Kill Switch in Baileys

The Baileys client checks for the kill-switch file before processing incoming messages.

If the file exists, it logs:

```text
[KILL SWITCH] active, skipping all processing
```

and skips processing.

There is also a safety check again before sending after the human-like delay.

This prevents a message from being sent if the kill switch is activated while the system is waiting.

---

# Dynamic Settings

The Baileys client reads:

```text
config/settings.json
```

fresh while processing messages.

This means changes made through the Streamlit console can be picked up without hardcoding the mode or delay values into the Node.js source.

If the settings file cannot be read or is invalid, safe defaults are used:

```text
dry_run = true
min_delay_seconds = 3
max_delay_seconds = 12
```

---

# Atomic Settings Writes

The Streamlit console writes settings using a temporary file and then replaces the original settings file.

Conceptually:

```text
settings.json
     ↓
write temporary settings file
     ↓
replace settings.json
```

This reduces the risk of leaving a partially written settings file if something goes wrong during the write.

---

# Final Week 4 Architecture

The complete final system can be represented as:

```text
                    WhatsApp
                       │
                       ↓
                 ┌───────────┐
                 │  Baileys  │
                 └─────┬─────┘
                       │
                       ↓
                 ┌───────────┐
                 │   Flask   │
                 │   Bridge  │
                 └─────┬─────┘
                       │
                       ↓
                 ┌───────────┐
                 │  Router   │
                 └─────┬─────┘
                       │
                       ↓
              ┌─────────────────┐
              │ Decision Engine │
              └────────┬────────┘
                       │
                       ↓
                ┌─────────────┐
                │  Retrieval  │
                │  ChromaDB   │
                └──────┬──────┘
                       │
                       ↓
             ┌───────────────────┐
             │ Persona Injection │
             └─────────┬─────────┘
                       │
                       ↓
                ┌────────────┐
                │     LLM    │
                │ Generation  │
                └──────┬─────┘
                       │
                       ↓
              ┌─────────────────┐
              │ Safety Checks   │
              │ • DRY RUN/LIVE │
              │ • Allowlist    │
              │ • Kill Switch  │
              └────────┬────────┘
                       │
                       ↓
                Human-like Delay
                       │
                       ↓
                 ┌───────────┐
                 │  Baileys  │
                 │ sendMessage│
                 └─────┬─────┘
                       │
                       ↓
                    WhatsApp
```

---

# The Four Safety Layers

The final sending process is intentionally protected by multiple controls:

```text
Incoming message
       ↓
Kill Switch
       ↓
Agent Decision
       ↓
Generated Reply
       ↓
DRY RUN check
       ↓
Independent Allowlist
       ↓
Human-like Delay
       ↓
Kill Switch check again
       ↓
WhatsApp send
```

The system therefore does not treat generation and sending as the same operation.

Generating a reply does not automatically mean that the reply will be sent.

---

# Final Runtime Components

A normal development session uses four main processes:

### Terminal 1 — ChromaDB

```powershell
chroma run --path .\chroma_data --port 8000
```

### Terminal 2 — Flask Bridge

```powershell
python -m agent.bridge
```

### Terminal 3 — Streamlit Console

```powershell
streamlit run .\console\app.py
```

### Terminal 4 — Baileys

```powershell
node .\whatsapp\baileys_client.js
```

ChromaDB should be started before the Python agent performs retrieval.

---

# Final Project Flow

The completed project now works conceptually as follows:

```text
1. A contact sends a WhatsApp message
              ↓
2. Baileys receives the message
              ↓
3. Baileys sends the message to Flask
              ↓
4. Router identifies the relationship
              ↓
5. Decision Engine decides whether to reply
              ↓
6. Relevant history is retrieved from ChromaDB
              ↓
7. Persona information is added
              ↓
8. AI generates the response
              ↓
9. DRY RUN / LIVE is checked
              ↓
10. Independent allowlist is checked
              ↓
11. Human-like delay is applied
              ↓
12. Kill switch is checked again
              ↓
13. Baileys sends the response
              ↓
14. The contact receives the WhatsApp reply
```

---

# Safety and Responsible Use

⚠️ **USE RESPONSIBLY**

This project uses Baileys to automate WhatsApp Web interactions.

For controlled testing and demonstrations:

* Prefer a dedicated or secondary WhatsApp number rather than a primary personal account.
* Keep message volume low.
* Use human-like delays.
* Automate only appropriate conversations.
* Use consent where applicable.
* Start every fresh session in DRY RUN mode.
* Keep the kill switch available.
* Verify the allowlist before enabling LIVE mode.
* Understand that aggressive or inappropriate automation may result in a WhatsApp account being restricted or banned.

This project is intended for educational, experimental, and controlled demonstration purposes.

---

# Pre-Demo Checklist

Before a real demonstration:

```text
[ ] kill_switch.flag is absent

[ ] config/settings.json deliberately set to:
    "dry_run": false

[ ] Demo contact exists in:
    config/relationship_map.json

[ ] Demo contact has a non-unknown relationship

[ ] ChromaDB is running

[ ] Flask bridge is running

[ ] Streamlit console is running

[ ] Baileys is connected

[ ] Recording software is ready

[ ] Test contact has consented to the demonstration
```

For development and normal testing, keep:

```text
dry_run = true
```

---

# Demonstration Flow

The intended demonstration is approximately 60–90 seconds.

### 1. Show the console

Open the Streamlit console and show that the system is ready.

### 2. Enable LIVE mode deliberately

Only after checking the safety conditions.

### 3. Send a real test message

A consenting test contact sends a WhatsApp message.

### 4. Show the processing

The console should show information such as:

* relationship
* decision
* reason
* retrieval results
* generated reply

### 5. Show the WhatsApp result

The contact receives the generated reply.

### 6. Activate the Kill Switch

Return to the console and activate:

```text
🛑 KILL SWITCH
```

This demonstrates that processing can be stopped immediately.

---

# Important Final Files

The major Week 4 files are:

```text
config/
├── settings.json
└── settings.py

agent/
└── bridge.py

whatsapp/
└── baileys_client.js

console/
└── app.py

kill_switch.flag
```

`kill_switch.flag` is created only when the kill switch is activated and is excluded from Git.

---

# Week 4 Completion

```text
✅ Flask bridge created
✅ Baileys WhatsApp client connected
✅ Incoming messages routed to Python
✅ Streamlit monitoring console created
✅ DRY RUN / LIVE toggle implemented
✅ Shared settings file implemented
✅ Configurable reply delays implemented
✅ Python allowlist implemented
✅ Independent Node.js allowlist implemented
✅ Kill switch implemented
✅ Kill switch clear operation implemented
✅ Dynamic settings loading implemented
✅ Atomic settings writes implemented
✅ Safety checks added before sending
✅ Final runtime flow tested
```

# Final Result

**Week 4 completed — the Agent Brain was connected to the WhatsApp communication layer and protected with safety controls.**

The four-week project now combines:

```text
Week 1
Persona Brain
      +
Week 2
History Brain
      +
Week 3
Agent Brain
      +
Week 4
WhatsApp + Safety Layer
      ↓
WhatsApp Cruise Control
```

The final system is designed to generate replies using both **my communication style** and **relevant conversation history**, while keeping the actual WhatsApp sending process behind explicit safety controls.
