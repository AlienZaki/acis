"""Stateful domain services — pure logic, no I/O."""

from __future__ import annotations

from dataclasses import dataclass, field

from .entities import Utterance


@dataclass
class TranscriptAccumulator:
    """Buffer utterances in a rolling window; signals when the extraction threshold is crossed.

    ``push()`` returns ``True`` the first time ``extract_threshold_words`` new words
    have accumulated since the last extraction — the caller should then fire
    ``ExtractCues``.  The counter resets automatically on each crossing.
    """

    max_utterances: int = 100
    extract_threshold_words: int = 50

    _utterances: list[Utterance] = field(default_factory=list, init=False, repr=False)
    _words_since_extract: int = field(default=0, init=False, repr=False)

    def push(self, utt: Utterance) -> bool:
        """Append utterance; returns True when extraction threshold is crossed."""
        self._utterances.append(utt)
        self._words_since_extract += len(utt.text.split())
        if len(self._utterances) > self.max_utterances:
            self._utterances = self._utterances[-self.max_utterances :]
        if self._words_since_extract >= self.extract_threshold_words:
            self._words_since_extract = 0
            return True
        return False

    @property
    def text(self) -> str:
        return " ".join(u.text for u in self._utterances)

    @property
    def is_empty(self) -> bool:
        return not self._utterances


@dataclass
class CueDeduplicator:
    """Suppresses duplicate cue titles for the whole session.

    The rolling extraction window re-reads overlapping transcript on every pass,
    so the LLM keeps re-deriving the same entities (a speaker's bio, a recurring
    concept). One ``CueDeduplicator`` lives per session, so remembering every
    title seen — not just a short window — is both correct and naturally bounded
    by the session's cue count.
    """

    _seen: set[str] = field(default_factory=set, init=False, repr=False)

    def is_duplicate(self, title: str) -> bool:
        return title.lower().strip() in self._seen

    def mark_seen(self, title: str) -> None:
        self._seen.add(title.lower().strip())


def _cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = sum(x * x for x in a) ** 0.5
    nb = sum(x * x for x in b) ** 0.5
    if na == 0.0 or nb == 0.0:
        return 0.0
    return dot / (na * nb)


@dataclass
class SemanticDeduplicator:
    """Drops cues whose meaning matches one already accepted, per cue type.

    Exact-title dedup misses paraphrases the LLM keeps producing — "How many
    companies are in the center?" vs "...in the Gründungszentrum?". Here each cue
    title is embedded and compared (cosine) against titles already accepted for
    the same cue type; anything at or above the type's threshold is a dup.
    Compared within type only, so an "answer" never suppresses a "concept".

    Thresholds are per type because the cue types differ in shape (tuned against
    real sessions): concepts/bios/answers are distinct enough that 0.88 avoids
    merging "Business Model" with "Business Plan", but suggestions are short and
    templated ("Clarify English workshop plans" vs "...frequency") and cluster at
    0.85–0.88, so they need a lower bar to collapse.
    """

    default_threshold: float = 0.88
    type_thresholds: dict[str, float] = field(default_factory=dict)

    _vectors: dict[str, list[list[float]]] = field(default_factory=dict, init=False, repr=False)

    def _threshold_for(self, cue_type: str) -> float:
        return self.type_thresholds.get(cue_type, self.default_threshold)

    def is_duplicate(self, cue_type: str, vector: list[float]) -> bool:
        threshold = self._threshold_for(cue_type)
        return any(_cosine(vector, seen) >= threshold for seen in self._vectors.get(cue_type, ()))

    def add(self, cue_type: str, vector: list[float]) -> None:
        self._vectors.setdefault(cue_type, []).append(vector)
