# Screen Inventory

Every screen in the ACIS app, with purpose, entry point, exit points, and primary actions.

---

## S01 — Consent Screen

**Purpose:** One-time disclosure that audio is processed by Mistral AI; required before first use  
**Entry:** First app launch only  
**Exit:** Accept → Session List  
**Primary action:** Accept and continue  
**Secondary action:** None (cannot be skipped)  
**Content:**
- App name + logo
- Short plain-language explanation of what data is sent where
- Link to Mistral AI data policy
- Accept button

---

## S02 — Session List (Home)

**Purpose:** Central hub; browse past sessions; start a new session  
**Entry:** App launch (after onboarding); back button from any screen  
**Exit:** Tap session card → Session Detail; Tap Start → Live Session; Tap Settings → Settings; Tap Prep Notes → Prep Notes  
**Primary action:** Tap [Start]  
**Secondary actions:** Tap session card, tap settings icon, tap prep notes icon  
**Persistent elements:**
- Bottom bar: language label (left) + Start button (right)
- Top bar: Prep Notes icon (left) + Settings icon (right) + session count
**Content:**
- Scrollable list of session cards, newest first
- Each card: title (truncated ~40 chars), datetime (HH:MM YYYY/MM/DD), location (City, Country), unread dot
**Empty state:** "No sessions yet. Tap Start to begin."

---

## S03 — Language Picker (Bottom Sheet)

**Purpose:** Select the spoken language for ASR accuracy  
**Entry:** Tap language label on S02 bottom bar  
**Exit:** Tap Confirm → return to S02; swipe down → dismiss unchanged  
**Primary action:** Select language from picker wheel; tap Confirm  
**Content:**
- Scrollable picker wheel
- "Auto-detected" as default first option
- Full list of supported languages
- Footer: "Used for more accurate transcriptions"
- Confirm button

---

## S04 — Live Session

**Purpose:** Active session display; shows the system is listening  
**Entry:** Tap Start on S02  
**Exit:** Tap Stop → S05 (generating); auto-exit if session finalised  
**Primary action:** Tap [Stop]  
**Content:**
- Timer (counting up from 00:00:00)
- Status: "Listening…"
- Glasses status badge (Meta glasses connected / Phone only)
- Recent cue feed (last 3 cues as small chips, newest on top)
- Stop button (prominent, centre or bottom)
**States:**
- Normal: timer running, listening indicator active
- Degraded (no internet): banner "Connection lost — buffering audio"
- Glasses disconnected mid-session: banner "Glasses disconnected — cues saved to app only"

---

## S05 — Finalising Session (Loading)

**Purpose:** Transition state while Mistral generates summary  
**Entry:** Auto-shown after Stop tapped on S04  
**Exit:** Auto-exit to S06 when summary ready  
**Content:**
- "Generating summary…" message
- Progress indicator (indeterminate spinner)
- Estimated time: "Usually takes 5–15 seconds"
**Error state:** If generation fails → show S06 with error banner + retry

---

## S06 — Session Detail

**Purpose:** View full session output — summary and transcript  
**Entry:** Tap session card on S02; auto-navigate from S05  
**Exit:** Back button → S02  
**Primary action:** None forced; browse tabs  
**Header (always visible):**
- Full session title
- Datetime (HH:MM YYYY/MM/DD)
- Location (City, Country)
- Duration (HH:MM:SS)
- Export icon (⬆)
**Tabs:** AI Summary (default) | Transcriptions

---

## S06a — Session Detail / AI Summary Tab

**Purpose:** Structured AI output: summary, keypoints, action items, cues  
**Sections (top to bottom):**
1. **Conversation summary** — grey section label + 1–2 sentence prose
2. **Keypoints** — grey section label + count; collapsible accordion items
   - Each item: heading as collapsed label; expands to sub-bullet list
   - Sub-bullets: bold label + grey description text
3. **Action items** — grey section label + count; checkbox list
   - Each item: pre-checked dark checkbox + task text (+ [Name] prefix if attributed)
   - Share to export button: "Share to export (N/N) ↗"
4. **AI cues** — grey section label; four collapsible accordion sections
   - Concepts | Answers | Suggestions | Bios
   - Each section shows count badge when collapsed
   - Expanded: pill-shaped cue chips in wrapped grid (2 per row max)
   - Bios section greyed/disabled if 0 bios

---

## S06b — Session Detail / Transcriptions Tab

**Purpose:** Read the full raw transcript  
**Content:**
- Scrollable list of utterances
- Each utterance: elapsed timestamp (HH:MM:SS) on its own line; text below
- Disfluencies preserved as-is
- No speaker labels
**Empty state:** N/A — every session with audio has a transcript

---

## S07 — Cue Detail Modal

**Purpose:** Read the full cue card for a tapped cue  
**Entry:** Tap any cue chip in S06a AI cues accordion  
**Exit:** Tap outside modal or tap ✕  
**Content:**
- Type icon (large)
- Title (bold, large)
- Body text (2–3 sentences)
- Source badge (for Answer cues only): "From conversation" / "From Prep Notes" / "General knowledge"
**Visual style:** White card, large rounded corners, centred over blurred background

---

## S08 — Settings

**Purpose:** Configure microphone, glasses audio behaviour, advanced options  
**Entry:** Settings icon on S02  
**Exit:** Back button → S02  
**Sections:**
1. **Voice input** — mic source radio group (Glasses / Phone / Laptop)
2. **Glasses interface** — toggles: Speak Cues, Auto Speak, Cue Verbosity (Brief/Full), Live Transcript on Phone
3. **Advanced** — backend URL, audio output target, ASR model
4. **Privacy** — "Data processed by Mistral AI" + link to DPA
**Behaviour:** Changes take effect immediately, persisted automatically

---

## S08a — Cue Verbosity Picker

**Purpose:** Set how much of each cue is spoken aloud through Meta glasses  
**Entry:** Tap Cue Verbosity row in S08  
**Exit:** Back button → S08  
**Content:** Selection list: Auto-adjusted (recommended) / 3 seconds / 5 seconds / 8 seconds / 12 seconds  
**Checkmark on selected option**

---

## S09 — Prep Notes List

**Purpose:** Create and manage pre-session context notes  
**Entry:** Prep Notes icon on S02  
**Exit:** Back button → S02  
**Primary action:** Tap [+ Add note]  
**Content:**
- List of saved notes: title + preview + active/inactive toggle
- Empty state: "Add notes to give ACIS context before a session. Active notes are used to answer questions in real time."

---

## S10 — Prep Note Editor

**Purpose:** Create or edit a single Prep Note  
**Entry:** Tap + Add note or tap existing note in S09  
**Exit:** Save → S09; discard → S09  
**Content:**
- Title text field
- Body text area (multiline, large)
- Attach file button (PDF, TXT, DOCX)
- Attached files list (removable)
- Save button

---

## S11 — Export Sheet

**Purpose:** Export session files (triggered from Session Detail)  
**Entry:** Tap ⬆ export icon on S06 header  
**Exit:** Share or cancel → return to S06  
**Content:**
- Export AI cues (.txt)
- Export transcript (.txt)
- Export summary (.txt)
- Export all (3 files)
- Each option opens OS share sheet
