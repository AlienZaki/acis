# Information Architecture

## Top-Level Navigation

ACIS has no persistent bottom tab bar during a session. Navigation is context-driven.

```
App Launch
    │
    ▼
┌─────────────────────────────┐
│        SESSION LIST          │  ← Home screen
│  [Language picker]           │
│  [Start button]              │
└───────────┬─────────────────┘
            │
    ┌───────┴──────────┐
    │                  │
    ▼                  ▼
LIVE SESSION      SESSION DETAIL
(glasses active)  (past session)
    │                  │
    │         ┌────────┴─────────┐
    │         ▼                  ▼
    │    AI SUMMARY TAB    TRANSCRIPTIONS TAB
    │         │
    │    ┌────┴─────────────────┐
    │    │  Conversation summary │
    │    │  Keypoints (accordion)│
    │    │  Action items        │
    │    │  AI cues (accordion) │
    │    └──────────────────────┘
    │
    ▼
POST-SESSION
(auto-navigate to session detail on stop)
```

## Full Screen Map

```
Root
├── Session List (Home)
│   ├── Language Picker (bottom sheet)
│   └── → Session Detail (tap session card)
│
├── Live Session (replaces Home while recording)
│   └── → Session Detail (on stop, auto-navigate)
│
├── Session Detail
│   ├── Tab: AI Summary
│   │   ├── Conversation summary (prose)
│   │   ├── Keypoints (collapsible accordion items)
│   │   │   └── Sub-bullets (inline, expanded)
│   │   ├── Action items (checkbox list)
│   │   │   └── Share to export (sheet)
│   │   └── AI cues (collapsible accordion by type)
│   │       ├── Concepts
│   │       ├── Answers
│   │       ├── Suggestions
│   │       └── Bios (greyed if empty)
│   │           └── Cue detail modal (tap any cue chip)
│   └── Tab: Transcriptions
│       └── Scrollable utterance list
│
├── Settings
│   ├── Voice input section
│   │   └── Mic source picker (glasses / phone / laptop)
│   ├── Glasses interface section
│   │   ├── Speak Cues toggle
│   │   ├── Auto Speak toggle
│   │   ├── Cue Verbosity → sub-screen picker (Brief / Full)
│   │   └── Live Transcript on Phone toggle
│   └── Advanced (developer section)
│       ├── Backend URL
│       ├── Audio output picker (Glasses / Phone / Silent)
│       └── ASR model
│
└── Prep Notes
    ├── Prep Notes list
    ├── Create / Edit Prep Note
    │   ├── Text input
    │   └── File attachment
    └── → Active on session start
```

## Entry Points to Each Screen

| Screen | How to reach it |
|---|---|
| Session List | App launch; back button from anywhere |
| Language Picker | Tap language label on Session List bottom bar |
| Live Session | Tap Start button on Session List |
| Session Detail | Tap any session card; auto-navigate after session stops |
| AI Summary tab | Default tab when Session Detail opens |
| Transcriptions tab | Tap "Transcriptions" tab in Session Detail |
| Cue detail modal | Tap any cue chip in AI cues accordion |
| Settings | Tap settings icon (top right of Session List) |
| Prep Notes | Tap prep notes icon or link on Session List |

## Data Displayed per Screen

| Screen | Primary data |
|---|---|
| Session List | Session cards: title, datetime, location, unread dot |
| Session Detail header | Full title, datetime, location, duration |
| AI Summary | Prose, keypoints, action items, cue chips |
| Transcriptions | Utterances with elapsed timestamps |
| Settings | Current values for all config options |
| Prep Notes | List of notes with title and preview |
