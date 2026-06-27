/**
 * cueFormatter — converts a CueNew event into a spoken string.
 *
 * Full verbosity: "{Type}: {title}. {first sentence of body}."
 * Brief verbosity: "{Type}: {title}."
 *
 * Total spoken duration is calibrated to 5-8 seconds at normal TTS speed.
 */

import type { CueNew } from "../lib/protocol";

export type CueVerbosity = "full" | "brief";

const CUE_LABEL: Record<CueNew["cue_type"], string> = {
  concept: "Concept",
  answer: "Answer",
  suggestion: "Suggestion",
  bio: "Bio",
};

/** Return the first sentence from a body string. */
function firstSentence(text: string): string {
  const match = text.match(/^[^.!?]+[.!?]/);
  return match ? match[0].trim() : text.trim();
}

export function formatCueForSpeech(cue: CueNew, verbosity: CueVerbosity): string {
  const label = CUE_LABEL[cue.cue_type];
  if (verbosity === "brief") {
    return `${label}: ${cue.title}.`;
  }
  const sentence = firstSentence(cue.body);
  return `${label}: ${cue.title}. ${sentence}`;
}
