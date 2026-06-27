/**
 * GlassesAudioAdapter — TTS wrapper using expo-speech with A2DP route awareness.
 *
 * expo-speech works in both Expo Go and EAS-built apps.
 * The native AudioSessionManager bridge (AudioSessionManager.swift) handles the
 * AVAudioSession category switch to keep output routed via A2DP when the phone mic
 * is in use.  That bridge is built in EAS; in Expo Go the try/catch silences it
 * and TTS still works through the phone speaker.
 *
 * A2DP / HFP mutual-exclusion note (iOS):
 *   When glasses mic is active (HFP), output also goes through SCO at 8 kHz mono.
 *   When phone mic is in use (no HFP), set .playback category → A2DP route → 44.1 kHz.
 *   Default ACIS config: phone mic + A2DP = best quality TTS.
 */

import * as Speech from "expo-speech";

export type AudioOutput = "glasses" | "phone" | "silent";

export interface GlassesAudioAdapterOptions {
  output: AudioOutput;
  rate?: number;  // 0.0 – 1.0, default 0.9
  pitch?: number; // default 1.0
}

export class GlassesAudioAdapter {
  private _output: AudioOutput;
  private _rate: number;
  private _pitch: number;

  constructor(options: GlassesAudioAdapterOptions) {
    this._output = options.output;
    this._rate = options.rate ?? 0.9;
    this._pitch = options.pitch ?? 1.0;
  }

  async speak(text: string): Promise<void> {
    if (this._output === "silent") return;

    // Request A2DP session via native bridge (EAS build only; no-ops in Expo Go).
    if (this._output === "glasses") {
      await this._activateA2DPSession();
    }

    return new Promise((resolve, reject) => {
      Speech.speak(text, {
        rate: this._rate,
        pitch: this._pitch,
        onDone: resolve,
        onError: reject,
      });
    });
  }

  stop(): void {
    Speech.stop();
  }

  setOutput(output: AudioOutput): void {
    this._output = output;
  }

  private async _activateA2DPSession(): Promise<void> {
    try {
      // eslint-disable-next-line @typescript-eslint/no-var-requires
      const { NativeModules } = require("react-native") as typeof import("react-native");
      if (NativeModules.AudioSessionManager?.activateA2DPSession) {
        await NativeModules.AudioSessionManager.activateA2DPSession();
      }
    } catch {
      // Native module absent (Expo Go) — TTS still works on phone speaker.
    }
  }
}
