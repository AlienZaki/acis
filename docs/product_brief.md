# Product Brief

## The Problem

In meetings, lectures, negotiations, and technical conversations, people constantly encounter terms they don't know, questions they can't immediately answer, and context they wish they had — but checking a phone breaks the social dynamic and signals disengagement. Existing solutions (Otter.ai, Notion, Zoom) are meeting-recording tools, not real-time augmentation tools.

## The Solution

ACIS turns conversation into an ambient intelligence stream. The user wears **Meta Ray-Ban glasses**, starts a session, and the glasses quietly speak:
- Spoken definitions of unfamiliar terms the moment they're spoken
- Spoken answers to questions asked in the room
- Spoken suggestions of relevant topics, risks, and follow-ups
- Spoken backgrounds on notable people mentioned

No prompting required. No phone-checking. The user hears the intelligence through their glasses, eyes forward, without breaking conversation.

When the meeting ends, ACIS produces a clean structured summary with keypoints and action items.

## Who It's For

Primarily researchers and professionals who attend meetings, interviews, and presentations where domain-specific knowledge density is high and stakes are real.

Initially deployed for: TU Clausthal HCIS lab researchers attending seminars, supervision meetings, and conference talks.

## Key Value Propositions

1. **Ambient, not intrusive** — cues are spoken through the glasses; the user never breaks eye contact or touches a phone
2. **Proactive, not reactive** — the system surfaces what's relevant before the user thinks to ask
3. **Full session record** — every session produces a searchable transcript, structured summary, and action items
4. **Known, disclosed AI** — unlike Even Realities Conversate, ACIS uses Mistral AI (EU-based, auditable) as the only external data processor

## What It Is Not

- Not a meeting recorder or transcription service (those exist already)
- Not a voice assistant (no "Hey ACIS" wake word in v1)
- Not a real-time translator (deferred to v2)
- Not a always-on background listener (sessions are explicitly started and stopped)

## Core Loop

```
User starts session
→ Mic captures conversation
→ Audio streams to Mistral Voxtral for transcription
→ Transcript feeds Mistral LLM every ~8 seconds
→ LLM extracts cue (Concept / Answer / Suggestion / Bio)
→ Cue spoken through Meta glasses speakers
→ Cue auto-dismisses after a few seconds
→ User stops session
→ Mistral generates summary + keypoints + action items
→ Session saved locally
```

## Session Output

After every session the user has:
- **Transcript** — timestamped utterances, no speaker labels
- **AI cues** — all cues grouped by type (Concepts, Answers, Suggestions, Bios)
- **Conversation summary** — 1–2 sentence overview
- **Keypoints** — 4–6 thematic sections, each with Context + specific sub-bullets
- **Action items** — tasks with inferred speaker attribution (e.g. `[Greg] Create incident channel`)

## Comparable Apps (Design References)

| App | What to borrow |
|---|---|
| **Even Realities Conversate** | The cue card format, session list layout, AI summary structure (primary reference) |
| **Otter.ai** | Session list pattern, transcript view |
| **Notion AI** | Summary block visual style |
| **Apple Notes** | Clean, minimal list design |
| **Superhuman** | Focus and speed — nothing decorative |
