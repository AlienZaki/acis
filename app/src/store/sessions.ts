/**
 * Session store — Zustand slice.
 *
 * Manages:
 *  - stored sessions list (fetched from backend on mount)
 *  - active session state (live cues, transcript deltas, summary)
 *  - WS connection lifecycle
 */

import { create } from "zustand";
import { AcisWebSocket } from "../lib/ws";
import type { CueNew, SummaryReady, TranscriptDelta } from "../lib/protocol";
import { GlassesAudioAdapter } from "../glasses/GlassesAudioAdapter";
import { CueQueue } from "../glasses/cueQueue";
import { useSettingsStore } from "./settings";

export interface StoredSession {
  id: string;
  name: string;
  started_at: string;
  ended_at?: string | null;
  elapsed?: string;
  cues?: CueNew[];
  utterances?: { text: string; t_start: number }[];
  summary?: SummaryReady | null;
}

interface SessionState {
  sessions: StoredSession[];
  ws: AcisWebSocket | null;
  startSession: () => Promise<string>;
  stopSession: (id: string) => Promise<void>;
  _onCueNew: (msg: CueNew) => void;
  _onTranscriptDelta: (msg: TranscriptDelta) => void;
  _onSummaryReady: (msg: SummaryReady) => void;
}

let _audioAdapter: GlassesAudioAdapter | null = null;
let _cueQueue: CueQueue | null = null;

function getAudioPipeline() {
  const s = useSettingsStore.getState().settings;
  if (!_audioAdapter) {
    _audioAdapter = new GlassesAudioAdapter({ output: s.audioOutput });
  }
  if (!_cueQueue) {
    _cueQueue = new CueQueue(s.cueVerbosity, (text) => _audioAdapter!.speak(text));
  }
  return _cueQueue;
}

export const useSessionStore = create<SessionState>((set, get) => ({
  sessions: [],
  ws: null,

  startSession: async () => {
    const settings = useSettingsStore.getState().settings;
    const ws = new AcisWebSocket(`ws://${settings.backendUrl}`);

    ws.on("session.started", (msg) => {
      set((s) => ({
        sessions: [
          { id: msg.session_id, name: msg.name, started_at: msg.started_at, cues: [], utterances: [] },
          ...s.sessions,
        ],
      }));
    });
    ws.on("cue.new", (msg) => get()._onCueNew(msg));
    ws.on("transcript.delta", (msg) => get()._onTranscriptDelta(msg));
    ws.on("summary.ready", (msg) => get()._onSummaryReady(msg));

    ws.connect();
    ws.send({ type: "session.start" });
    set({ ws });

    // Return the new session id — resolved when session.started fires.
    return new Promise((resolve) => {
      ws.on("session.started", (msg) => resolve(msg.session_id));
    });
  },

  stopSession: async (id) => {
    const { ws } = get();
    ws?.send({ type: "session.stop" });
    ws?.disconnect();
    set({ ws: null });
    _cueQueue?.clear();
  },

  _onCueNew: (msg) => {
    set((s) => ({
      sessions: s.sessions.map((sess) =>
        sess.id === msg.session_id ? { ...sess, cues: [...(sess.cues ?? []), msg] } : sess
      ),
    }));
    const settings = useSettingsStore.getState().settings;
    if (settings.speakCues) {
      getAudioPipeline().enqueue(msg);
    }
  },

  _onTranscriptDelta: (msg) => {
    set((s) => ({
      sessions: s.sessions.map((sess) =>
        sess.id === msg.session_id
          ? { ...sess, utterances: [...(sess.utterances ?? []), { text: msg.text, t_start: msg.t_start }] }
          : sess
      ),
    }));
  },

  _onSummaryReady: (msg) => {
    set((s) => ({
      sessions: s.sessions.map((sess) => (sess.id === msg.session_id ? { ...sess, summary: msg } : sess)),
    }));
  },
}));
