# Week 3 — Build the Agent Brain

## Goal

The goal of Week 3 was to connect the **History Brain from Week 2** with the **Persona Brain from Week 1** and build the decision-making and generation pipeline.

Week 2 gave the system searchable conversation memory.

Week 3 added the logic needed to decide:

* Who is messaging?
* What relationship do they have with me?
* Should the agent reply?
* What previous conversations are relevant?
* What should the reply sound like?
* Should the system ignore the message?

The resulting pipeline became:

```text id="v9w3fz"
Incoming WhatsApp Message
          ↓
Router
          ↓
Decision Engine
          ↓
Retrieval
          ↓
Persona + Generation
          ↓
Reply / Ignore
```

At the end of Week 3, the agent pipeline could process messages in testing, but it was **not yet connected to real WhatsApp**.

---

# Session 3.1 — Live Relationship Router

The first component added in Week 3 was the live relationship router.

## Relationship Map

The live relationship map is stored in:

```text id="u4q3a7"
config/relationship_map.json
```

It maps a WhatsApp phone number to a relationship category.

Example structure:

```json
{
  "_default": "unknown",
  "CONTACT_NUMBER": "friend",
  "ANOTHER_CONTACT": "family",
  "ANOTHER_CONTACT": "professional"
}
```

Actual phone numbers are kept locally and should not be exposed publicly.

---

## Why Does the Live Router Use Phone Numbers?

The historical Week 2 data used conversation IDs/names from WhatsApp exports.

The live system receives a WhatsApp JID from Baileys, such as:

```text id="5o3h6v"
PHONE_NUMBER@s.whatsapp.net
```

The router extracts the phone number and uses it to find the relationship.

Therefore:

```text id="qg2qdu"
WhatsApp JID
      ↓
Phone number
      ↓
Relationship lookup
      ↓
family / friend / professional / unknown
```

---

# Router

The router is implemented in:

```text id="5x9k5m"
agent/router.py
```

Its responsibility is deliberately simple:

> Look up the sender's phone number in the relationship map and return the corresponding relationship.

The router does **not** need AI.

This keeps routing fast, predictable, and inexpensive.

---

# Router Validation

Router tests were created in:

```text id="k7u9w2"
agent/test_router.py
```

A validation script was also created:

```text id="p1d3x8"
agent/validate_relationship_map.py
```

The relationship map and router were tested before continuing to the rest of the pipeline.

---

# Retrieval Integration

The retrieval system created in Week 2 was connected to the Week 3 agent.

The retrieval module is:

```text id="z1a6xq"
ingestion/retrieval.py
```

It searches the ChromaDB collection corresponding to the sender's relationship.

For example:

```text id="j8v2c4"
Relationship = friend
        ↓
history_friend
        ↓
Search previous conversation history
```

This prevents the system from mixing unrelated relationship memories.

---

# Retrieval Flow

The Week 3 retrieval flow is:

```text id="r9k2b7"
Incoming message
       ↓
Router identifies relationship
       ↓
Select relationship-specific ChromaDB collection
       ↓
Semantic search
       ↓
Relevant historical messages
       ↓
Associated previous replies
```

The retrieved history is later provided to the generation system.

---

# Decision Engine

The Decision Engine was created in:

```text id="w2m6p9"
agent/decision_engine.py
```

Its purpose is to determine whether the agent should reply.

The design follows an important principle:

> **Use cheap rules first and make an AI call only when necessary.**

This avoids unnecessary generation calls and gives the system predictable safety behavior.

---

# Decision Engine Rules

The decision process considers information such as:

* whether the message was sent by the user
* whether the message is from a known relationship
* whether the message is a group message
* whether the message is forwarded
* whether the message is a simple acknowledgement
* whether the message contains media
* whether the message requires an actual response
* the detected intent of the message

The general flow is:

```text id="d6z0s1"
Incoming message
       ↓
Hard rules
       ↓
Signal rules
       ↓
Intent check
       ↓
Reply policy
       ↓
REPLY / IGNORE
```

---

# Cheap Rules First

The Decision Engine was tested without unnecessarily calling the generation model.

Examples included:

* messages sent by me
* one-word acknowledgements
* messages from unknown contacts
* media messages
* forwarded messages
* normal conversational messages

This allows obvious cases to be handled by deterministic rules before more expensive processing is used.

---

# Intent Detection

Intent detection was added for messages where the system needs more information about what the sender is asking or saying.

Examples tested included:

```text id="wq6e8r"
"Haan yaar, coffee pe chale?"
"Hey, kya kar rahi ho?"
"Can you send me 5000 rupees?"
```

The intent check helps the agent distinguish between different types of messages before generating a response.

---

# Media Handling

The pipeline was also tested with media messages.

Supported message types included:

```text id="9s6q5p"
image
audio
video
```

For appropriate media messages, the system can generate an acknowledgement rather than treating the message as ordinary text.

Example behavior:

```text id="6q0z4x"
Image
  ↓
Decision Engine
  ↓
Media acknowledgement
```

This allows the system to handle messages that do not contain normal text.

---

# Generator

The reply-generation component is implemented in:

```text id="g4n8s2"
agent/generator.py
```

The generator combines the available context to produce a response in the intended communication style.

The generation stage uses:

1. The incoming message
2. The sender's relationship
3. Relevant retrieved conversation history
4. Persona information

Conceptually:

```text id="x8m1r4"
Incoming message
      +
Relationship
      +
History Brain
      +
Persona Brain
      ↓
AI Generation
      ↓
Reply
```

---

# Why Retrieval and Persona Are Both Needed

The two systems provide different information.

### History Brain

Answers:

> "What have I said in similar situations before?"

It retrieves relevant previous conversations from ChromaDB.

### Persona Brain

Answers:

> "How do I generally communicate?"

It provides style, tone, phrasing, relationship-specific behavior, and examples.

The generation stage combines both.

```text id="n5k2v8"
History Brain
     +
Persona Brain
     ↓
Generation
```

This helps the reply be both **contextually relevant** and **consistent with the intended communication style**.

---

# Agent Pipeline

The complete Week 3 pipeline was created in:

```text id="u2d7m5"
agent/pipeline.py
```

The pipeline connects the major components:

```text id="b8q4t1"
Incoming Message
       ↓
Router
       ↓
Decision Engine
       ↓
Retrieval
       ↓
Persona + Generation
       ↓
Reply / Ignore
```

The pipeline also records decision information for later inspection.

---

# Batch Testing

A batch test was created in:

```text id="m6p9x3"
agent/batch_test.py
```

The batch tests covered different types of incoming messages, including:

### Unknown sender

The system should not automatically treat an unknown sender as an approved relationship.

### Group chat

Group messages should not be processed as normal one-to-one conversations.

### One-word acknowledgement

Messages such as simple acknowledgements can be ignored instead of generating unnecessary replies.

### Money-related message

Messages involving sensitive or unusual requests can be handled by the decision rules rather than blindly generating a response.

These tests helped verify that the decision layer was working before connecting the system to real WhatsApp.

---

# Decision Logging

Decision information was recorded in:

```text id="s8q4n1"
logs/decision_log.jsonl
```

This makes it possible to inspect:

* the incoming message
* the detected relationship
* the decision
* the reason
* generated responses
* other pipeline information

Logging is useful for debugging and evaluating why the agent replied or ignored a message.

---

# Week 3 Architecture

The Week 3 architecture can be summarized as:

```text id="j3r7w0"
                 ┌─────────────────┐
                 │ Incoming Message│
                 └────────┬────────┘
                          ↓
                 ┌─────────────────┐
                 │     Router      │
                 │ Relationship    │
                 │     Lookup      │
                 └────────┬────────┘
                          ↓
                 ┌─────────────────┐
                 │ Decision Engine │
                 │ Rules + Intent  │
                 └────────┬────────┘
                          ↓
                 ┌─────────────────┐
                 │    Retrieval    │
                 │    ChromaDB     │
                 └────────┬────────┘
                          ↓
                ┌──────────────────┐
                │ Persona + History│
                │     Context      │
                └────────┬─────────┘
                         ↓
                ┌──────────────────┐
                │  AI Generation   │
                └────────┬─────────┘
                         ↓
                  Reply / Ignore
```

---

# Testing Status

Before moving to Week 4, the following components were tested:

```text id="p4z7m2"
✅ Relationship map
✅ Router
✅ Router tests
✅ Retrieval
✅ Decision Engine
✅ Intent checking
✅ Media handling
✅ Generator
✅ Complete pipeline
✅ Batch testing
✅ Decision logging
```

---

# Important Design Decisions

## 1. Router uses no AI

The relationship is determined using the maintained phone-number mapping.

This makes the first stage predictable and inexpensive.

## 2. Cheap rules come first

The Decision Engine handles obvious cases before using more expensive AI processing.

## 3. Retrieval is relationship-specific

The system searches the ChromaDB collection corresponding to the sender's relationship.

For example:

```text
family → history_family
friend → history_friend
professional → history_professional
unknown → history_unknown
```

## 4. History and persona have different jobs

The History Brain provides relevant previous examples.

The Persona Brain provides communication style.

They are combined during generation.

## 5. The system was still offline

At the end of Week 3, the agent could process test messages and generate decisions/replies, but it was **not yet connected to real WhatsApp**.

The WhatsApp connection was the focus of Week 4.

---

# Week 3 Checkpoint — Key Understanding

### Why use a phone-number relationship map?

Because the live WhatsApp system receives a sender JID containing the contact's phone number.

The phone number can therefore be mapped directly to a relationship such as family, friend, or professional.

### Why should the router not use AI?

Relationship lookup is deterministic.

There is no need for an AI model to decide something that can be directly retrieved from a maintained mapping.

### Why use cheap rules first?

Many messages can be classified without an expensive AI generation call.

Handling obvious cases first makes the system faster, cheaper, and more predictable.

### Why search only the matching relationship's memory?

Different relationships have different communication styles and conversation histories.

Searching only the relevant collection reduces unrelated retrieval results.

### Why combine history with persona?

Historical retrieval tells the system what I have said in similar situations.

The persona tells the system how I generally communicate.

Both provide different types of context for generation.

---

# Week 3 Completion

```text id="c5v8q2"
✅ Live relationship map created
✅ Router implemented
✅ Router tests completed
✅ Retrieval integrated
✅ Decision Engine implemented
✅ Hard rules added
✅ Signal rules added
✅ Intent checking added
✅ Media handling added
✅ Generator integrated
✅ Complete pipeline created
✅ Batch tests completed
✅ Decision logging added
```

## Final Result

**Week 3 completed — the Agent Brain was created.**

At this stage, the project had:

```text id="n7x2m4"
Persona Brain       → Week 1
History Brain       → Week 2
Agent Brain         → Week 3
                         ↓
                  Ready for WhatsApp
                         ↓
                    Week 4
```

The system could now take an incoming test message, identify the relationship, decide whether to reply, retrieve relevant history, combine it with the persona, and generate a context-aware response.

**Real WhatsApp connectivity and the safety controls were added in Week 4.**
