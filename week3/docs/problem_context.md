# Problem Context

## Project Name
WhatsApp Cruise Control

## Problem Statement
The project aims to automate WhatsApp conversations in a way that feels personal, context-aware, and human-like without relying on raw AI decision-making for the entire flow. The system is designed to process incoming WhatsApp messages, determine the relevant relationship or contact, apply business rules, retrieve stored context, inject persona-aware details, and send a natural reply.

## Why This Exists
The core challenge is building a messaging assistant that can:
- respond appropriately to different people and relationship types,
- preserve conversational memory via stored context,
- enforce rules before generating a response,
- make replies feel natural instead of robotic,
- operate through WhatsApp in near-real time.

## High-Level Workflow
The project follows a multi-stage pipeline:

1. Incoming WhatsApp message enters the system.
2. The message is routed and normalized.
3. The sender number is extracted.
4. The system looks up the relationship associated with that number.
5. A decision engine evaluates whether the message should be processed, ignored, or responded to.
6. Retrieval logic queries a matching relationship-specific ChromaDB collection for relevant history.
7. Persona context is injected into the prompt so the reply matches the intended identity or style.
8. A language model generates the final message.
9. A human-like delay is added before sending.
10. The message is delivered through Baileys.

## Architectural Idea
The system is described as a Two-Brain Pipeline:

- Rule-based logic (plain logic, no AI):
  - message intake
  - number extraction
  - relationship lookup
  - decision engine
  - hard rules
  - signal rules
  - intent checks
  - reply policy
  - human-like delay

- History brain:
  - retrieval
  - lookup from relationship-specific database collection

- Persona brain:
  - persona injection
  - persona context for tone, memory, and identity

- Generation layer:
  - LLM-based final response generation using memory + persona context

## Decision Logic
The decision engine is responsible for filtering and controlling response behavior using plain rule-based logic rather than general-purpose AI. This includes:
- hard rules,
- signal rules,
- intent checks,
- reply policy.

This suggests the system tries to keep deterministic controls around when and how a message should be answered, with AI being used only for the generation stage rather than the full decision-making process.

## Memory and Context
The system stores conversational or relational memory in a retrieval layer. The architecture specifically mentions querying the matching relationship’s ChromaDB collection, indicating that the assistant uses relationship-specific context rather than a single global memory.

This is important because the assistant is expected to remember who is messaging, what prior interactions existed, and how that relationship should shape the reply.

## Persona Awareness
A separate persona-injection layer ensures that the generated output reflects the intended identity or communication style for the target relationship. Rather than sending generic replies, the model receives relationship-aware context and produces a more tailored output.

## Expected Outcome
The desired result is a WhatsApp assistant that behaves like a context-aware personal communication layer: it can route messages correctly, remember relationship context, apply explicit rules, produce believable replies, and send them in a human-like cadence.

## Summary
The project is essentially a WhatsApp messaging automation system built around a hybrid architecture:
- deterministic rules for routing and policy,
- vector-based retrieval for memory,
- persona injection for personalization,
- LLM-based generation for natural responses,
- Baileys for message delivery.

This design aims to balance control, personalization, and realism while keeping the system operationally structured and relationship-aware.
