// AUTO-GENERATED skeleton — run `just gen-types` to regenerate from acis/protocol.py.
// Edit the Python source, not this file.

// ── Inbound (app → brain) ──────────────────────────────────────────────────

export interface Hello {
  type: "hello";
}

export interface SessionStart {
  type: "session.start";
  name?: string | null;
}

export interface SessionStop {
  type: "session.stop";
}

export interface AudioChunk {
  type: "audio.chunk";
  data_b64: string;
  sample_rate?: number;
}

export interface Ping {
  type: "ping";
}

export type Inbound = Hello | SessionStart | SessionStop | AudioChunk | Ping;

// ── Outbound (brain → app) ─────────────────────────────────────────────────

export interface HelloOk {
  type: "hello.ok";
}

export interface SessionStarted {
  type: "session.started";
  session_id: string;
  name: string;
  started_at: string;
}

export interface SessionStopped {
  type: "session.stopped";
  session_id: string;
}

export interface TranscriptDelta {
  type: "transcript.delta";
  session_id: string;
  text: string;
  t_start: number;
  t_end: number;
}

export type CueType = "concept" | "answer" | "suggestion" | "bio";

export interface CueNew {
  type: "cue.new";
  session_id: string;
  cue_id: string;
  cue_type: CueType;
  title: string;
  body: string;
}

export interface Keypoint {
  heading: string;
  bullets: string[];
}

export interface SummaryReady {
  type: "summary.ready";
  session_id: string;
  title: string;
  prose: string;
  keypoints: Keypoint[];
  action_items: string[];
}

export interface AcisError {
  type: "error";
  message: string;
}

export interface Pong {
  type: "pong";
}

export type Outbound =
  | HelloOk
  | SessionStarted
  | SessionStopped
  | TranscriptDelta
  | CueNew
  | SummaryReady
  | AcisError
  | Pong;
