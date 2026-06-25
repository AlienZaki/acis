# User Personas

---

## Persona 1 — The Researcher in the Field

**Name:** Zaki  
**Role:** PhD researcher, HCI / AI  
**Location:** TU Clausthal, Germany  
**Tech comfort:** High — uses Claude Code, Obsidian, VS Code daily  

### Context of Use
Attends weekly supervision meetings, seminars, and conference talks. Conversations are dense with terminology from adjacent fields (systems, HCI, ML). Takes notes on a laptop which forces visual split attention. Misses follow-ups because action items aren't captured in the moment.

### Goals
- Understand unfamiliar terms from adjacent research fields without interrupting
- Have action items automatically extracted after every meeting
- Review what was discussed when writing up meeting notes later

### Frustrations
- Pulling out a phone to Google a term mid-conversation is awkward
- Note-taking competes with listening — can't do both well
- Meeting notes are incomplete because the moment to write them has passed

### How They Use ACIS
Wears Meta glasses glasses into supervision meetings. Starts ACIS from the phone app before entering the room. Glances at cues as they appear on the glasses. After the meeting, reviews the keypoints and exports action items.

### What They Need from the UI
- Quick session start from the home screen (one tap)
- Clean, uncluttered session list — scan past sessions fast
- Action items prominent in the summary view
- Prep Notes to load context for recurring meetings

---

## Persona 2 — The Lab Operator / Study Coordinator

**Name:** Matthias  
**Role:** Postdoc, study coordinator  
**Location:** TU Clausthal HCIS lab  
**Tech comfort:** High — configures research setups, familiar with APIs  

### Context of Use
Sets up ACIS for participant studies. Configures microphone source, language, and glasses audio settings before handing the glasses to a participant. Monitors that the system is running correctly during the study. Reviews session exports afterwards.

### Goals
- Configure the system reliably before each study session
- Verify data is being captured and the glasses audio is active
- Export session data for analysis

### Frustrations
- Settings changes that don't persist between sessions waste time
- Unclear system status during a live session
- Having to explain to participants what data is being captured

### How They Use ACIS
Opens settings before each study run to select microphone source and language. Starts the session on behalf of participants or instructs them. Exports session files post-study for analysis.

### What They Need from the UI
- Settings screen that is clearly organised and persists
- Obvious session status indicator (live / stopped)
- Easy export of the three text files (transcript, cues, summary)
- Consent / data disclosure visible somewhere in the app

---

## Persona 3 — The Developer / Integration Engineer

**Name:** Alex  
**Role:** Lab engineer, implements ACIS on new hardware  
**Tech comfort:** Very high — reads SRS/RFC, writes Python and TypeScript  

### Context of Use
Integrates ACIS into a new experimental setup (e.g. laptop screen instead of Meta glasses, or a different mic setup). Needs the app to be configurable enough to swap components.

### Goals
- Understand how each component connects without reading all the code
- Configure the audio output adapter and microphone source without hardcoding
- Add new cue types or modify prompts for specific studies

### How They Use ACIS
Primarily interacts with settings and the backend config file. Uses the phone speaker audio adapter (no glasses required) during development. Tests sessions on a laptop.

### What They Need from the UI
- Settings screen that exposes backend URL, audio output adapter choice, ASR model
- A dev/debug mode indicator
- Clear error states when connectivity fails
