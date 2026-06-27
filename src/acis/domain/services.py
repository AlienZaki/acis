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
    """Suppresses duplicate cue titles within a rolling window of recently seen titles."""

    window: int = 5

    _recent: list[str] = field(default_factory=list, init=False, repr=False)

    def is_duplicate(self, title: str) -> bool:
        return title.lower().strip() in self._recent

    def mark_seen(self, title: str) -> None:
        self._recent.append(title.lower().strip())
        if len(self._recent) > self.window:
            self._recent = self._recent[-self.window :]
