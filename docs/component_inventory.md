# Component Inventory

All UI components needed in ACIS. Grouped by category. For each: what it is, where it's used, and any design notes.

---

## Navigation & Layout

### AppShell
The root container. Provides top bar (title + left/right actions) and optional bottom bar. Used on every screen.

### BottomBar
Fixed bottom strip on Session List containing: language label (left, tappable) + Start button (right). Always visible on the home screen.

### TabBar
Two-tab switcher in Session Detail: "AI summary" | "Transcriptions". Active tab has underline indicator + black text. Inactive tab grey text.

### BottomSheet
Slides up from bottom. Used for: Language Picker, Export options. Dismissable by swipe down or tapping outside.

---

## Session List

### SessionCard
The primary list item on the home screen.  
Contents: title (truncated, bold), datetime (HH:MM YYYY/MM/DD), location (City, Country), unread dot (yellow, left edge or top-right corner).  
States: default, unread (dot visible), pressed/highlighted.

### UnreadDot
Small yellow circle indicating a session has not been opened. Appears on SessionCard. Disappears on first open.

### SessionListEmpty
Empty state component for when no sessions exist.  
Content: icon, "No sessions yet. Tap Start to begin."

### SessionCount
Small counter in the header area showing total number of sessions.

---

## Live Session

### SessionTimer
Large elapsed time display in HH:MM:SS format. Counts up from 00:00:00.

### ListeningIndicator
Animated indicator ("Listening…") showing the mic is active. Subtle animation — pulsing dot or waveform.

### LiveCueFeed
Shows the last 2–3 cue chips as they arrive during a session. Auto-scrolls newest to top. Read-only.

### GlassesStatusBadge
Small badge showing Meta glasses connection state. States: "Meta glasses connected" (green), "Phone only" (grey).

### StopButton
Primary CTA on the live session screen. Large, prominent. Red or stop-icon style.

### OfflineBanner
Full-width banner for degraded connectivity. Text: "Connection lost — buffering audio". Dismissable? No — auto-hides when reconnected.

---

## Session Detail

### SessionDetailHeader
Appears at the top of Session Detail. Contains: full title, datetime, location, duration, export icon (⬆).

### SectionLabel
Grey, uppercase or small-caps label used before each section in AI Summary: "Conversation summary", "Keypoints", "Action items", "AI cues".

### ProseBlock
The 1–2 sentence conversation summary. Body text style, comfortable reading size.

### KeypointAccordion
Collapsible list item for each keypoint. Collapsed: shows heading text + chevron. Expanded: shows sub-bullet list.

### KeypointSubBullet
A single sub-bullet row inside an expanded KeypointAccordion.  
Layout: bold label + regular-weight description on same line, or label on top / description below.

### ActionItemRow
A single action item in the action items list.  
Layout: filled dark checkbox (pre-checked) + text. Text may start with `[Name]` in grey or different weight.

### ShareExportButton
"Share to export (N/N) ↗" — inline button in Action Items section. Shows selected count / total.

### CueTypeAccordion
Collapsible section for each of the four cue types within the AI cues section.  
Collapsed: type name + count badge. Expanded: chip grid.

### CueChipGrid
Wrapped grid of CueChip items inside an expanded CueTypeAccordion. Up to 2 per row; wider chips take full row.

### CueChip
Pill-shaped chip representing a single cue.  
Contents: type icon (emoji) + title text.  
States: default (light grey bg), pressed.  
Tap → opens CueDetailModal.

### CueDetailModal
Overlay modal for a full cue card.  
Contents: type icon (large), title (bold, large), body text (2–3 sentences). For Answer cues: source badge ("From conversation" / "From Prep Notes" / "General knowledge").  
Style: white background, large corner radius (≥16px), centred, blurred/dimmed background.  
Dismiss: tap outside or ✕ button.

### BiosDisabledState
The Bios accordion when no bios were detected. Greyed out label, no count badge. Not expandable.

---

## Transcriptions

### TranscriptList
Scrollable list of TranscriptRow items.

### TranscriptRow
A single utterance in the transcript.  
Layout: timestamp (HH:MM:SS, monospace or distinct weight, grey) on its own line, then utterance text below. Blank space between utterances.

---

## Settings

### SettingsSection
A labelled group of settings items with a visual divider between groups.

### SettingsMicSourcePicker
Radio-button group for microphone source selection. Options: Glasses / Phone / Laptop. Only one selectable at a time.

### SettingsToggleRow
A single labelled toggle (on/off switch).  
Layout: label (left), toggle (right). Optional description text in grey below label.

### SettingsNavRow
A row that navigates to a sub-screen.  
Layout: label (left), current value + chevron (right). Used for: Cue Verbosity.

### CueVerbosityPicker
Selection list on a sub-screen. Options: Brief (title only) / Full (title + first body sentence, default). Checkmark on selected item.

### SettingsTextInput
Text input field for: Backend URL, ASR model ID.

### SettingsAudioOutputPicker
Segmented or radio group for audio output target: Meta Glasses / Phone Speaker / Silent (app only).

### PrivacyRow
Non-interactive row in Settings showing "Processed by Mistral AI" with an external link icon → opens Mistral DPA URL.

---

## Prep Notes

### PrepNoteCard
List item in the Prep Notes list.  
Contents: title, preview (first ~80 chars of body), active/inactive toggle.

### PrepNoteEditor
Full-screen editor for a single prep note. Contains: title field, body text area, attach file button, attached files list, Save button.

### AttachedFileRow
A single attached file within the PrepNoteEditor. Shows filename + remove (✕) button.

### PrepNotesEmpty
Empty state: icon + "Add notes to give ACIS context before a session."

---

## Global / Utility

### LoadingOverlay
Full-screen or modal loading state. Used during session finalisation ("Generating summary…").

### ConsentScreen
First-launch only. App name, explanation paragraph, Mistral link, Accept button.

### ErrorBanner
Inline banner for non-blocking errors (e.g. summary failed, glasses disconnected).  
Style: full-width, coloured background (warning/error), dismiss button.

### StartButton
The primary session-start CTA in the BottomBar. Should be visually dominant — the most important action in the app.

### LanguageLabel
Tappable label in BottomBar showing the current language. Tap → LanguagePicker sheet.

### LanguagePickerWheel
Scrollable wheel picker inside the BottomSheet. Long list (20+ options).
