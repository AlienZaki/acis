# Glasses Output Spec (Meta Ray-Ban)

This document replaces the original G2 HUD spec. ACIS targets **Meta Ray-Ban smart glasses** as the wearable output device. The output model is fundamentally different from the G2: Meta Ray-Ban has no visual display — cues are delivered via **audio through the open-ear speakers**, and the live transcript is displayed on the phone screen only.

---

## Hardware Capabilities (Meta Ray-Ban)

| Property | Value |
|---|---|
| Display | ❌ None (no HUD, no visual overlay) |
| Speakers | ✅ Open-ear speakers (audio output to user) |
| Microphone | ✅ 5-mic array (beamforming, noise reduction) |
| Camera | ✅ 12 MP + 4K60 video (front-facing) |
| Connectivity | Bluetooth 5.3 + WiFi (via Meta View app) |
| Companion app | Meta View (iOS + Android) |
| AI integration | Meta AI (built-in, not our target) |
| Battery life | ~4 hours with heavy AI use |

---

## Output Model for ACIS

Because there is no visual display, ACIS delivers cues in two ways:

### 1. Audio cue delivery (primary wearable output)
When a cue is detected, ACIS speaks a brief audio summary through the glasses' open-ear speakers. The user hears the cue without looking at a screen.

**Audio cue format:**
- Cue type announced first: "Concept:", "Answer:", "Suggestion:", "Bio:"
- Then the title and a condensed 1-sentence version of the body
- Total spoken duration: 5–8 seconds per cue

**Example:**
> "Concept: Twilio AMD. Answering Machine Detection — uses audio signals to determine if a human or voicemail answered a call."

**Auto Pop-Up equivalent:** If Auto Speak is ON, cues are spoken immediately. If OFF, they queue and the user taps the glasses frame to hear the next cue.

### 2. Phone screen (secondary / review)
- Live transcript scrolls on the phone screen during a session (for the operator/researcher looking at the phone)
- Post-session: full summary, keypoints, action items, cue chips — all on the phone app
- The phone app is the visual interface; the glasses are the ambient audio interface

---

## What This Means for the App Design

| G2 (old) | Meta Ray-Ban (new) |
|---|---|
| HUD settings: AI Cues on HUD toggle | Audio settings: Auto Speak toggle |
| HUD settings: Live Transcription on HUD toggle | Live Transcript on Phone toggle (glasses have no screen) |
| HUD settings: Auto Pop-Up toggle | Auto Speak toggle |
| HUD settings: Cue Duration | Cue speech speed / verbosity |
| "Glasses connected" indicator | "Meta glasses connected" indicator |
| ASCII icon prefixes [C], [?], [*], [B] | Spoken type labels "Concept:", "Answer:", "Suggestion:", "Bio:" |

---

## Audio Cue Design Considerations

The designer should consider how audio delivery changes the user experience:

- **Mic source matters for audio quality:** Bluetooth A2DP (high-quality output) and HFP (glasses mic) are mutually exclusive. If the user selects glasses mic, cue audio degrades to 8 kHz mono. The settings UI should surface this tradeoff — default to phone mic.
- **Cue verbosity:** Should Suggestions be spoken in full? Or just the title, with the full text available on phone? Consider a "Brief" vs "Full" audio mode setting.
- **Interruption model:** If a cue arrives while the user is actively speaking, it should not be spoken over them. ACIS should detect voice activity before playing. This is a product decision the designer should surface in settings.
- **Volume and voice:** The text-to-speech voice and volume should be configurable. Consider whether cues use the device TTS voice or a custom one.
- **Queue management:** If 3 cues arrive in rapid succession, ACIS should queue them and play sequentially, not all at once. Should there be a maximum queue depth?

---

## Camera (Future Use)

The Meta Ray-Ban camera is available to apps via the Wearables DAT (Device Access Toolkit). ACIS v1 does **not** use the camera. In Phase 2, camera input could enable:
- Visual context for cues (e.g. reading a whiteboard and surfacing a Concept cue for an equation on it)
- Scene-aware suggestions (e.g. detecting a business card and generating a Bio cue)

This is out of scope for the current design. Do not design for it. Note it exists.

---

## Meta View App Integration

ACIS requires the Meta AI companion app to be installed and the glasses to be paired. Audio cues are delivered via Bluetooth A2DP through the Wearables Device Access Toolkit (DAT). The glasses mic (HFP) is not used by default — see the A2DP/HFP constraint in the RFC §6.

The designer does not need to design the Meta View pairing flow — it is the user's responsibility to pair glasses before using ACIS. ACIS should detect whether glasses are paired and show an appropriate state if not.

---

## Glasses Connection States (for UI)

| State | What the user sees | What ACIS does |
|---|---|---|
| Connected | "Meta glasses connected" badge (green) | Speaks cues through glasses |
| Not connected | "Phone only" badge (grey) | Plays cues through phone speaker (or silently queues for phone review only) |
| Mid-session disconnect | Banner: "Glasses disconnected — cues saved to app" | Queues cues in app; resumes speaking if glasses reconnect |
