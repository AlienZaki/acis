/**
 * Settings store — persisted via AsyncStorage.
 */

import { create } from "zustand";
import type { AudioOutput } from "../glasses/GlassesAudioAdapter";
import type { CueVerbosity } from "../glasses/cueFormatter";

export type MicSource = "glasses" | "phone" | "laptop";

export interface AcisSettings {
  micSource: MicSource;
  speakCues: boolean;
  autoSpeak: boolean;
  cueVerbosity: CueVerbosity;
  audioOutput: AudioOutput;
  liveTranscriptOnPhone: boolean;
  backendUrl: string;
}

const DEFAULTS: AcisSettings = {
  micSource: "phone",
  speakCues: true,
  autoSpeak: false,
  cueVerbosity: "full",
  audioOutput: "glasses",
  liveTranscriptOnPhone: true,
  backendUrl: "localhost:8765",
};

interface SettingsState {
  settings: AcisSettings;
  update: (patch: Partial<AcisSettings>) => void;
}

export const useSettingsStore = create<SettingsState>((set) => ({
  settings: DEFAULTS,
  update: (patch) => set((s) => ({ settings: { ...s.settings, ...patch } })),
}));
