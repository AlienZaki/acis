# Feature Spec

Features described from the user's perspective. Each feature has: what it does, how it behaves, edge cases, and design notes.

---

## F01 — Session List

The home screen shows all past sessions in reverse chronological order. Each session card shows the AI-generated title (truncated at ~40 characters with "..."), the start time and date, and the location (City, Country reverse-geocoded from GPS at session start).

Sessions that have never been opened show a small yellow dot indicator (unread). The dot disappears the moment the session detail is opened.

The screen header shows the total session count.

**Empty state:** A centred message "No sessions yet. Tap Start to begin."  
**Design note:** This is a dense information list — keep visual weight low so the eye goes to titles, not UI chrome.

---

## F02 — Start / Stop Session

A single prominent Start button lives in the bottom bar. One tap starts everything: mic capture, transcription, cue generation, and glasses audio output. No confirmation screen.

Stopping requires one tap on the Stop button shown during the live session. No confirmation either — the cost of accidental stop is low (summary is still generated).

**Design note:** Start should feel like pressing record on a camera — immediate, confident, clear state change.

---

## F03 — Live Session Screen

While a session is active, the app shows a running timer, a "Listening…" status, a recent cue feed (last few cues as small chips), and the Stop button. The user rarely looks at this screen — the glasses are the primary display. The phone screen is a reassurance interface.

**Cue feed:** Shows the last 2–3 cues that arrived, fading out as new ones push in. Not interactive — tap goes to full session detail after stopping.

**Glasses status badge:** Shows whether Meta glasses are connected. If not connected, a non-intrusive banner reads "Cues saved to app only".

---

## F04 — AI Cue Generation (Background, Always On)

Every ~8 seconds, the latest transcript is sent to Mistral which extracts any new cues. This runs invisibly. Users see cues appear on their glasses and in the app — they don't see or control the extraction process directly.

**Four cue types:**
- **Concept** — defines a term, acronym, or jargon. Can also handle ASR errors ("Likely a phonetic transcription error for frontend developer..."). Expected: 3–8 per 30-min session.
- **Answer** — responds to a question asked aloud. Can be grounded in the conversation itself, in Prep Notes, or in general knowledge. Expected: 2–6 per 30-min session.
- **Suggestion** — the broadest type. Covers actionable follow-ups, named entity background (companies, products), compliance/legal flags (auto-generated, not prompted), and technical context. Expected: 10–22 per 30-min session.
- **Bio** — background on a publicly notable person mentioned by name. 0–3 per session typical; section greyed if none.

**Cross-type overlap:** The same topic can appear as both a Concept and a Suggestion — this is expected, not a bug. They serve different purposes (Concept = what is this; Suggestion = what to do about it).

---

## F05 — Audio Cue Delivery (Meta Glasses)

When a cue is generated, ACIS speaks it through the Meta Ray-Ban open-ear speakers. The user hears a brief spoken cue — type label, title, and a condensed 1-sentence body — without looking at their phone.

**Example spoken cue:**
> "Concept: Twilio AMD. Answering Machine Detection — detects whether a human or voicemail answered a call."

If **Auto Speak** is ON, cues play immediately as they arrive. If OFF, cues are queued and the user taps the glasses frame to hear the next one.

Multiple cues arriving quickly are queued and played sequentially, not simultaneously.

The phone screen shows the live transcript and a live cue feed during the session — but the primary wearable experience is audio.

**Design note:** Meta Ray-Ban has no visual display. The designer does not design any glasses screen. See `hud_design_spec.md` for the full audio output model.

---

## F06 — Post-Session AI Summary

Immediately after a session stops, Mistral generates a structured summary. It takes 5–15 seconds. The result has four parts:

**Conversation summary:** 1–2 dense sentences capturing all major themes. One sentence is the norm.

**Keypoints:** 4–6 thematic sections (not chronological). Each section has a heading and 5–10 sub-bullets. The first sub-bullet is always "Context:" explaining why the topic came up. Remaining sub-bullets are specific decisions, facts, or outcomes with concrete names and details.

**Action items:** Tasks extracted from the transcript with inferred attribution. Attributed items show `[Name]` prefix. Unattributed items have no prefix (never "Unassigned:").

**Session title:** 5–10 word specific title naming team/project and topics (e.g. "Quadrivia Engineering, On-Call, and Operations Sync"). Never generic.

---

## F07 — Transcript View

The Transcriptions tab shows the raw transcript from the session. Utterances are in chronological order, each preceded by its elapsed timestamp (HH:MM:SS from session start). No speaker labels — this is confirmed consistent with how Conversate works.

Disfluencies (false starts, em-dashes) are preserved as-is from the ASR output.

---

## F08 — Cue Detail

Tapping any cue chip in the AI Summary opens a modal showing the full cue card: icon, title, and 2–3 sentence body. For Answer cues, a small badge shows the source: "From conversation", "From Prep Notes", or "General knowledge".

---

## F09 — Action Item Export

The action items section has a "Share to export (N/N) ↗" button. All items are checked by default. The user can uncheck specific items, then tap Export. The OS share sheet opens with the selected items as formatted text.

---

## F10 — Session File Export

From any Session Detail header, a share icon exports the full session as three separate text files:
- `{title}_ai_cues.txt` — cues grouped by type
- `{title}_transcript.txt` — timestamped utterances
- `{title}_summary.txt` — prose, keypoints, action items

---

## F11 — Prep Notes

Before a session, the user can load context notes. During the session, Mistral uses these to answer questions with user-specific information (e.g. "Who is on-call?" answered using names from a prep note listing the team).

Notes can be text or attached files. They can be toggled active/inactive without deleting them. Active notes are injected into every Answer cue prompt for the session.

Spoken prep notes (solo session mode, as in Conversate) are deferred to Phase 2.

---

## F12 — Language Selection

Before starting a session, the user can set the spoken language for more accurate transcription. Default is "Auto-detected". Changing language does not require a restart — takes effect on the next session start.

---

## F13 — Settings: Glasses Audio Behaviour

Four controls govern what is spoken through the glasses:
- **Speak Cues** — if OFF, cues still generated and saved in app, but not spoken through glasses
- **Auto Speak** — if ON, each new cue is spoken through glasses immediately; if OFF, cues are stored silently
- **Cue Verbosity** — Brief (type + title only) or Full (type + title + first body sentence)
- **Live Transcript on Phone** — shows/hides the live transcript on the phone screen during a session (glasses have no display)

The settings description text: *"These will only affect the glasses audio. The app will still transcribe and generate a live AI summary."*

---

## F14 — Offline Handling

ACIS requires internet (Mistral API for both ASR and LLM). If connection drops mid-session:
- Audio chunks are buffered locally
- ASR and cue generation pause
- Banner shows: "Connection lost — buffering audio"
- On reconnect, buffered audio is submitted and the transcript gap is filled
- Session is never lost due to connectivity

---

## F15 — Unread Indicator

New sessions (never opened) show a yellow dot on their session list card. The dot is removed the moment the session detail is opened. There is no bulk "mark all as read".
