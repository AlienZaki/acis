# ACIS — Design Handover Docs

**Project:** Ambient Conversation Intelligence System (ACIS)  
**Version:** 1.0  
**Date:** 2026-06-25  
**Prepared by:** HCIS Lab, TU Clausthal  
**Handover to:** Design (UI/UX)

---

## What Is ACIS?

ACIS is a mobile app (iOS/Android) that listens to conversations in real time, speaks contextual AI cues through **Meta Ray-Ban smart glasses**, and produces a structured AI summary when the session ends. It is a research reimplementation of Even Realities' Conversate feature, targeting Meta glasses instead of the G2, built on Mistral AI services.

The user wears Meta Ray-Ban glasses, starts a session, and the glasses quietly speak relevant definitions, answers, suggestions, and background info as the conversation unfolds — without the user having to ask.

---

## Docs in This Folder

| File | Purpose |
|---|---|
| `product_brief.md` | What the app is, the problem it solves, key value propositions |
| `user_personas.md` | Three primary personas with goals, frustrations, and usage context |
| `user_flows.md` | Step-by-step flows for every key user journey |
| `information_architecture.md` | Full navigation structure and screen hierarchy |
| `screen_inventory.md` | Every screen listed with purpose, entry points, and primary actions |
| `feature_spec.md` | Every feature described from a user perspective (not as engineering requirements) |
| `hud_design_spec.md` | Glasses output spec (Meta Ray-Ban): audio-only output, spoken cue format, constraints |
| `component_inventory.md` | Every UI component needed, with description and usage context |
| `copy_deck.md` | All UI text — labels, descriptions, empty states, error messages, onboarding |
| `design_requirements.md` | Visual constraints, design principles, reference apps, non-negotiables |
| `accessibility.md` | Accessibility requirements and considerations |

---

## Key Decisions Already Made

- **Platform:** Mobile app (React Native), primary target iOS
- **ASR:** Mistral Voxtral Mini — audio streams to Mistral cloud, returns transcript
- **LLM:** Mistral medium (cues) + Mistral large (summary)
- **Glasses:** Meta Ray-Ban — audio output via open-ear speakers; no visual display
- **Storage:** Local SQLite — session data never leaves the device (only audio/transcript sent to Mistral during processing)
- **No code yet** — this folder is the design source of truth before implementation begins

## Source Material

Full requirements and technical design live in the lab vault:
- `TUC/writing/conversate_srs.md` — Software Requirements Specification
- `TUC/writing/conversate_rfc.md` — Technical RFC
- `TUC/concepts/even_realities_g2_conversate.md` — Conversate deep dive
- `TUC/concepts/even_realities_g2_capability_inventory.md` — G2 hardware specs
