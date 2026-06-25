# Accessibility Requirements

---

## Standards

Target: **WCAG 2.1 AA** compliance across all screens.  
Platform: iOS VoiceOver support for all primary flows.

---

## Colour & Contrast

| Element | Minimum contrast |
|---|---|
| Body text on background | 4.5:1 |
| Large text (≥ 18pt regular / ≥ 14pt bold) | 3:1 |
| Active tab indicator | Must not rely on colour alone — use underline or weight change |
| Unread dot | Must not rely on colour alone — use position + ARIA label "New session" |
| Glasses status badge (App only / Glasses connected) | Icon or text change in addition to colour |
| Error banners | 4.5:1; must not be red-only indication |

---

## Touch Targets

All interactive elements must meet iOS minimum touch target guidelines:
- Minimum tap area: **44 × 44 pt**
- Applies to: toggles, accordion headers, cue chips, action item checkboxes, tab bar, navigation items
- Cue chips in the wrapped grid must not be so small they become difficult to tap — minimum chip width ~120 pt

---

## VoiceOver Labels

All interactive elements must have explicit accessible labels. Examples:

| Element | Accessible label |
|---|---|
| Unread dot on session card | "New session" |
| Start button | "Start session" |
| Stop button | "Stop session" |
| Cue chip (e.g. "Twilio AMD") | "Concept: Twilio AMD — tap to read" |
| Cue detail modal ✕ | "Close" |
| KeypointAccordion (collapsed) | "Keypoint: {heading}, collapsed, tap to expand" |
| KeypointAccordion (expanded) | "Keypoint: {heading}, expanded, tap to collapse" |
| Action item checkbox | "[Name] {task text}, checked" or "{task text}, checked" |
| Toggle (on) | "{Label}, on" |
| Toggle (off) | "{Label}, off" |
| Export button | "Share {n} of {n} action items" |
| Glasses status badge | "Glasses connected" or "No glasses — app only mode" |
| Session card | "{Title}, {datetime}, {location}, {new or previously viewed}" |

---

## Screen Reader Flow

The following flows must be fully usable with VoiceOver (eyes-closed test):

1. **Start a session** — open app → navigate to Start button → activate
2. **Stop a session** — navigate to Stop button → activate
3. **Read a summary** — navigate through Keypoints accordion → expand → read sub-bullets → navigate to Action items
4. **Read a transcript** — navigate to Transcriptions tab → scroll through utterances with timestamps
5. **Open and close a cue modal** — navigate to cue chip → activate → read modal content → activate close button

---

## Dynamic Type

All text must respond to iOS Dynamic Type size settings.
- Body text must reflow at larger sizes — no truncation without overflow handling
- Session card titles truncate at 40 chars normally; at large type sizes, allow wrapping to 2 lines before truncating
- Cue chips must wrap text or allow full-row layout at large sizes
- Timestamps (monospace) must scale with system font size

---

## Motion & Animation

- Respect iOS "Reduce Motion" setting
- When Reduce Motion is ON: accordion expand/collapse uses cross-fade instead of height animation; modal appears without slide-up animation
- ListeningIndicator (pulsing animation on Live Session) must pause or simplify under Reduce Motion

---

## Offline / Error States

- Error banners must be announced to VoiceOver automatically on appearance (`accessibilityAnnouncement`)
- Loading states ("Generating summary…") must be announced on appearance
- Offline banner ("Connection lost — buffering audio") must be announced immediately

---

## Colour-Blindness Considerations

- Unread dot: do not rely on yellow alone — use shape (circle) and position (top-left corner of card)
- Glasses status badge "Glasses connected" vs "App only": use text + icon, not just colour
- Active tab indicator: underline must be present in addition to text colour change
- Action item checkboxes: filled vs unfilled must differ by shape/fill, not just colour
