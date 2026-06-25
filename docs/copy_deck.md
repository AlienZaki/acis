# Copy Deck

All user-facing text in the ACIS app. Grouped by screen. Use exactly as written unless the designer has a strong reason to propose an alternative.

---

## App Name

**Full name:** ACIS  
**Tagline:** Ambient Conversation Intelligence  
**Glasses display name:** ACIS

---

## S01 — Consent Screen

**Heading:** Before you begin  
**Body:**  
ACIS transcribes your conversations using Mistral AI. When a session is active, audio is sent to Mistral's servers for transcription. Transcripts and summaries are stored only on your device.

By continuing, you agree to Mistral AI's [data processing terms].

**Button:** Accept and continue  
**Link text:** data processing terms

---

## S02 — Session List

**Screen title:** ACIS  
**Session count:** `{n} sessions`  
**Empty state heading:** No sessions yet  
**Empty state body:** Tap Start to record your first session.  
**Start button:** Start  
**Language label:** `{Language}` (e.g. "Auto-detected", "English", "German")  
**Settings icon tooltip:** Settings  
**Prep Notes icon tooltip:** Prep Notes  
**Unread dot accessible label:** New session

---

## S03 — Language Picker

**Sheet title:** Spoken language  
**Footer:** Used for more accurate transcriptions  
**Confirm button:** Confirm  
**Default option:** Auto-detected  

**Language list (display names):**
Auto-detected · English · German · Spanish · French · Arabic · Chinese (Simplified) · Chinese (Traditional) · Catalan · Cantonese · Italian · Portuguese · Japanese · Korean · Dutch · Polish · Russian · Turkish · + all others supported by ASR

---

## S04 — Live Session

**Status label:** Listening…  
**Glasses connected badge:** Meta glasses connected  
**Glasses not connected badge:** Phone only  
**Offline banner:** Connection lost — buffering audio  
**Glasses disconnected banner:** Glasses disconnected — cues saved to app only  
**Stop button:** Stop  
**Recent cues label:** Recent cues  
**No cues yet:** Cues will appear here as they're detected

---

## S05 — Finalising

**Loading message:** Generating summary…  
**Subtext:** Usually takes 5–15 seconds  
**Error heading:** Summary unavailable  
**Error body:** Your transcript has been saved. Summary generation failed.  
**Retry button:** Retry

---

## S06 — Session Detail Header

**Export icon accessible label:** Export session  
**Duration label:** `{HH:MM:SS}`  
**Datetime format:** `{HH:MM} {YYYY/MM/DD}`

---

## S06a — AI Summary Tab

**Tab label:** AI summary  
**Section: Conversation summary** (label)  
**Section: Keypoints** (label)  
**Keypoints count:** `{n} keypoints`  
**Section: Action items** (label)  
**Action items count:** `{n} action items`  
**Share button:** `Share ({n}/{n}) ↗`  
**Section: AI cues** (label)  
**Cue type labels:** Concepts · Answers · Suggestions · Bios  
**Cue count badge:** `{n}`  
**Bios empty label:** Bios  
**Bios empty subtext:** No notable persons detected  

---

## S06b — Transcriptions Tab

**Tab label:** Transcriptions  
**Timestamp format:** `HH:MM:SS` (elapsed from session start)

---

## S07 — Cue Detail Modal

**Source badges:**
- From conversation
- From Prep Notes
- General knowledge

**Close button accessible label:** Close  

---

## S08 — Settings

**Screen title:** Settings  
**Back accessible label:** Back  

**Section: Voice input**  
Row: Voice input source  
Options: Glasses mic · Phone mic · Laptop mic  

**Section: Glasses interface**  
Row: Speak cues  
Description: Hear AI cues spoken through your Meta glasses.  

Row: Auto speak  
Description: When a new cue is detected, it will be spoken immediately through your glasses.  

Row: Cue verbosity  
Description: How much of each cue is spoken aloud.  
Options: Brief (title only) · Full (title + summary)  

Row: Live transcript on phone  
Description: Show a scrolling transcript on your phone screen during a session.  

**Section: Advanced**  
Row: Backend URL  
Placeholder: ws://192.168.1.x:8765  

Row: Audio output  
Options: Meta Glasses · Phone Speaker · Silent (app only)  

Row: ASR model  
Placeholder: voxtral-mini-transcribe-realtime-2602+1  

**Section: Privacy**  
Row: Data processed by  
Value: Mistral AI ↗  

**Settings note (glasses interface section footer):**  
These settings only affect the glasses audio. The app will still transcribe and generate a live AI summary.

---

## S08a — Cue Verbosity Picker

**Screen title:** Cue verbosity  
**Options:**  
- Brief *(Title only — e.g. "Concept: Twilio AMD.")*  
- Full *(Title + first body sentence)* *(Recommended)*  

---

## S09 — Prep Notes List

**Screen title:** Prep Notes  
**Add button:** + Add note  
**Active toggle label:** Active  
**Empty state heading:** No prep notes  
**Empty state body:** Add notes to give ACIS context before a session. Active notes help answer questions in real time.

---

## S10 — Prep Note Editor

**Screen title (new):** New note  
**Screen title (edit):** Edit note  
**Title placeholder:** Note title  
**Body placeholder:** Add context, briefing, or reference material…  
**Attach button:** Attach file  
**Supported formats note:** PDF, TXT, DOCX  
**Save button:** Save  
**Discard confirmation:** Discard changes?  
**Discard confirm:** Discard  
**Discard cancel:** Keep editing

---

## S11 — Export Sheet

**Sheet title:** Export session  
**Options:**  
- Export AI cues (.txt)  
- Export transcript (.txt)  
- Export summary (.txt)  
- Export all (3 files)  
**Cancel:** Cancel

---

## Error & System Messages

| Situation | Message |
|---|---|
| Mic permission denied | ACIS needs microphone access to record sessions. Enable it in Settings > Privacy > Microphone. |
| No internet on start | ACIS requires an internet connection for transcription. Connect and try again. |
| Glasses not found | Meta glasses not detected. You can continue without them — cues will be saved to the app only. |
| Session export failed | Export failed. Please try again. |
| Summary generation failed | Summary unavailable — your transcript has been saved. |
| Audio buffer overflow (rare) | Some audio was lost due to a slow connection. The transcript may have gaps. |

---

## Onboarding / Tooltips (if needed)

| Element | Tooltip text |
|---|---|
| Prep Notes icon | Load context before a session |
| Unread dot | New session — tap to review |
| Bios (greyed) | No notable persons were mentioned |
| Source badge: From conversation | This answer was found in what was said during this session |
| Source badge: From Prep Notes | This answer came from your Prep Notes |
