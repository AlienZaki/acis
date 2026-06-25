# Design Requirements

Non-negotiable constraints, principles, and references the designer must know before starting.

---

## Platform & Form Factor

- **Target platform:** iOS (primary), Android (secondary)
- **Device:** Phone app — portrait orientation, standard mobile screen sizes
- **Companion device:** Meta Ray-Ban smart glasses — delivers cues via audio through open-ear speakers; no visual display. The designer does NOT design any glasses screen; see `hud_design_spec.md`
- **Use context:** Worn during meetings and conversations — the user is not looking at their phone. The phone is a setup and review tool, not a real-time tool.

---

## Hard Constraints

1. **No coding.** This folder is for design only. Nothing is implemented yet.
2. **Mobile-first.** The app is a React Native mobile app. Design for phone screens.
3. **The glasses audio output is out of scope for design.** Meta Ray-Ban has no visual display. Audio cue delivery is handled by the SDK. Do not design any glasses screens.
4. **Portrait only.** No landscape layouts needed.
5. **No custom animations defined yet.** Keep interaction notes to simple descriptions (e.g. "slides up", "fades in"). No Lottie files or motion specs needed at this stage.

---

## Design Principles

### 1. The glasses are the product; the phone is the backstage
The phone app exists for: setup (settings, prep notes, language), and review (session detail, transcript, summary). It should not compete for attention during a live session. The Live Session screen in particular should be minimal — the user's face is pointed at a conversation, not a phone.

### 2. Information density without visual noise
Sessions can contain 20+ cue chips, 5 keypoints, 8+ action items. The design must handle dense content without feeling cluttered. Use typography weight, whitespace, and hierarchy — not decorative elements.

### 3. One primary action per screen
Start on the home screen. Stop on the live session screen. Review on the detail screen. Each screen has one obvious thing to do.

### 4. Cues are the product's identity
The four cue types — Concepts, Answers, Suggestions, Bios — are the core UX primitives. Their visual language (icon + title + body) should be immediately recognisable and consistent from the app to the export files.

### 5. Trust through transparency
The app handles audio and sends it to the cloud. The data flow must be clearly stated at first launch and findable in settings. Don't bury this.

---

## Visual Direction

**Tone:** Professional, focused, trustworthy. Not playful or consumer-app-style. Research-tool aesthetic — closer to Notion or Linear than Instagram or TikTok.

**Colour:** Minimal palette. Black, white, grey as defaults. One accent colour for active states and the Start button. Meta's design language uses blues and whites — consider whether to harmonise with or contrast that. The Even Realities Conversate app (the functional reference) uses a dark theme with green accents.

**Typography:** Clear hierarchy. Bold titles, light/regular body. Monospace for timestamps.

**Iconography:** Use an established icon set (SF Symbols recommended for iOS). Cue type icons are fixed: 📋 Concept, ? Answer, 💡 Suggestion, 👤 Bio.

**Cards / surfaces:** Rounded corners throughout. Card-based layout for session list, cue chips, and modals.

---

## Reference Apps

| App | What to study |
|---|---|
| **Even Realities Conversate** | Primary functional reference — session list, session detail, cue chip layout, accordion sections, modal style. 21 screenshots available in the lab. (Note: Conversate uses G2 glasses with a visual display; ACIS uses Meta glasses with audio output — the phone app patterns are directly transferable.) |
| **Otter.ai** | Session list pattern, transcript view, action items |
| **Notion** | AI summary block, keypoints visual style |
| **Linear** | Task/action item row style |
| **Apple Voice Memos** | Simple, focused recording UI |

---

## Accessibility Non-Negotiables

- Minimum contrast ratio 4.5:1 for all body text
- Tap targets ≥ 44×44 pt
- All interactive elements have accessible labels
- Do not rely on colour alone to communicate state (e.g. the unread dot needs more than just colour — use position or shape too if needed)
- VoiceOver support for all primary flows (see `accessibility.md`)

---

## What Does NOT Need to Be Designed (Yet)

- Glasses audio output (no visual display to design)
- Onboarding beyond the consent screen
- Push notifications
- Account / login screens (no auth in v1)
- Dark mode (single theme for v1)
- Tablet or iPad layout
- Landscape orientation
- Apple Watch companion
