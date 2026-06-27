/**
 * CueQueue — serialises audio cue delivery so cues never overlap.
 *
 * Max depth: 3.  When the queue is full incoming cues are dropped (the full
 * cue is always visible in the app — this is just the audio delivery queue).
 *
 * Usage:
 *   const queue = new CueQueue(verbosity, speakFn)
 *   queue.enqueue(cueNewMsg)   // called from WS handler
 */

import type { CueNew } from "../lib/protocol";
import { formatCueForSpeech, type CueVerbosity } from "./cueFormatter";

const MAX_DEPTH = 3;

export class CueQueue {
  private _queue: CueNew[] = [];
  private _speaking = false;
  private _verbosity: CueVerbosity;
  private _speak: (text: string) => Promise<void>;

  constructor(verbosity: CueVerbosity, speak: (text: string) => Promise<void>) {
    this._verbosity = verbosity;
    this._speak = speak;
  }

  enqueue(cue: CueNew): void {
    if (this._queue.length >= MAX_DEPTH) return;
    this._queue.push(cue);
    if (!this._speaking) this._drain();
  }

  setVerbosity(v: CueVerbosity): void {
    this._verbosity = v;
  }

  clear(): void {
    this._queue = [];
  }

  private async _drain(): Promise<void> {
    this._speaking = true;
    while (this._queue.length > 0) {
      const cue = this._queue.shift()!;
      const text = formatCueForSpeech(cue, this._verbosity);
      try {
        await this._speak(text);
      } catch {
        // TTS failure — continue to next cue
      }
    }
    this._speaking = false;
  }
}
