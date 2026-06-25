# User Flows

---

## Flow 1 — First Launch

**Trigger:** User opens ACIS for the first time  
**Goal:** Onboard user and reach Session List ready to start

```
Open app
    ↓
Consent screen
  "ACIS processes your audio using Mistral AI to transcribe
   conversations. Audio chunks are sent to Mistral's servers
   and not stored. Transcripts are stored locally on your device."
  [Accept and continue]
    ↓
Session List (empty state)
  "No sessions yet. Tap Start to begin your first session."
  [Start button]
```

**Notes:**
- Consent screen shown once only; cannot be dismissed without accepting
- Settings icon is visible on empty state so user can configure mic before first session

---

## Flow 2 — Start a Session

**Trigger:** User taps Start on Session List  
**Goal:** Session is recording; glasses audio active

```
Tap [Start]
    ↓
Mic permission check
  → If denied: show permission prompt linking to system settings
  → If granted: continue
    ↓
Session starts
  - Microphone begins capturing
  - Audio streaming to Voxtral for transcription
  - Cue extraction pipeline starts
  - Meta glasses audio activates (if glasses connected and Speak Cues enabled)
  - Live Session screen replaces Session List
    ↓
Live Session screen
  - Timer counting up (HH:MM:SS)
  - "Listening..." status indicator
  - Recent cues shown as they arrive (optional live feed)
  - [Stop] button prominent
```

**Error states:**
- No internet connection on start → "ACIS requires an internet connection for transcription. Connect and try again."
- Glasses not connected → session still starts (phone-only mode); cues generated and saved in app but not spoken through glasses; banner: "Glasses not connected — cues saved to app only"

---

## Flow 3 — Stop a Session

**Trigger:** User taps Stop on Live Session screen  
**Goal:** Summary generated; user lands on Session Detail

```
Tap [Stop]
    ↓
"Generating summary..." loading state
  - Microphone stops
  - Final transcript flushed
  - Mistral generates: prose summary, keypoints, action items, session title
  (typically 5–15 seconds)
    ↓
Auto-navigate to Session Detail
  - AI Summary tab active by default
  - Session title auto-generated
  - Unread indicator NOT shown (just created = already "read")
```

**Error state:**
- Summary generation fails (API error) → session saved without summary; "Summary unavailable — transcript saved" banner; retry button

---

## Flow 4 — Review a Past Session

**Trigger:** User taps a session card on Session List  
**Goal:** User reviews summary and transcript

```
Tap session card
    ↓
Session Detail opens — AI Summary tab
  - Unread dot removed immediately
  - Prose summary visible at top
  - Keypoints collapsed by default
    ↓
Tap a keypoint heading
  - Expands to show sub-bullets with bold labels
    ↓
Tap "Transcriptions" tab
  - Full transcript with elapsed timestamps
  - Scrollable
    ↓
Tap any cue chip (in AI cues accordion)
  - Modal opens with full cue card (icon + title + body)
  - Tap outside or [×] to dismiss
```

---

## Flow 5 — Export Action Items

**Trigger:** User taps "Share to export" in Action Items section  
**Goal:** Action items exported as text

```
Tap [Share (N/N) ↗]
    ↓
Checkboxes become individually selectable (all checked by default)
  - User can uncheck specific items
    ↓
Tap [Export selected]
    ↓
OS share sheet opens
  - Options: Copy to clipboard, Share via Messages/Mail/Notes/etc.
  - File format: plain text or JSON (configurable in settings)
```

---

## Flow 6 — Export Full Session Files

**Trigger:** User taps export icon from Session Detail header  
**Goal:** Three .txt files produced and shared

```
Tap [⬆ Export session]
    ↓
Export options sheet
  [Export AI cues (.txt)]
  [Export transcript (.txt)]
  [Export summary (.txt)]
  [Export all (3 files)]
    ↓
OS share sheet with selected file(s)
```

---

## Flow 7 — Add Prep Notes

**Trigger:** User opens Prep Notes before a session  
**Goal:** Notes loaded as context for the upcoming session

```
Tap [Prep Notes] on Session List
    ↓
Prep Notes list (empty or existing notes)
    ↓
Tap [+ Add note]
    ↓
Note editor
  - Title field
  - Body text area
  - [Attach file] (PDF, TXT, DOCX)
  - [Save]
    ↓
Note appears in list with toggle (active / inactive)
  - Active notes are injected into Answer cue prompts during sessions
  - Inactive notes are saved but not used
```

---

## Flow 8 — Change Language

**Trigger:** User taps language label on Session List bottom bar  
**Goal:** Language updated before next session start

```
Tap [Language: Auto-detected]
    ↓
Bottom sheet opens — scrollable language picker wheel
  Options include: Auto-detected, English, German, Spanish, French,
                   Arabic, Chinese (Simplified), Chinese (Traditional),
                   Catalan, Cantonese, + all ASR-supported languages
    ↓
Scroll to desired language
Tap [Confirm]
    ↓
Bottom sheet closes; label updates to selected language
```

---

## Flow 9 — Configure Settings

**Trigger:** User taps Settings icon  
**Goal:** Settings updated and persisted

```
Tap [⚙ Settings]
    ↓
Settings screen
  Voice input section:
    Mic source: [Glasses] [Phone] [Laptop] — radio group
  Glasses interface section:
    Speak Cues: toggle (on/off)
    Auto Speak: toggle (on/off)
    Cue Verbosity: [Full ›] → sub-screen
      Sub-screen: picker (Brief / Full)
    Live Transcript on Phone: toggle (on/off)
  Advanced:
    Backend URL: text input
    Audio Output: [Meta Glasses] [Phone Speaker] [Silent]
    ASR Model: text input (defaults to Voxtral model ID)
    ↓
Changes save immediately (no "Save" button needed)
```

---

## Flow 10 — First-Time Glasses Connection

**Trigger:** User attempts to start a session with glasses not yet paired  
**Goal:** Glasses paired and session starts

```
Tap [Start]
    ↓
System checks for connected glasses
  → Glasses not found
    ↓
Banner: "Meta glasses not detected"
  [Continue without glasses] — starts phone-only session
  [Connect glasses] → opens system Bluetooth settings or Meta View app
    ↓
User pairs glasses via Meta View
  ↓
Returns to app → session starts with glasses audio active
```
