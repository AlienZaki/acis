"""Unit tests for domain services (no I/O)."""

from acis.domain.entities import Utterance
from acis.domain.services import CueDeduplicator, TranscriptAccumulator


class TestTranscriptAccumulator:
    def test_push_returns_false_below_threshold(self):
        acc = TranscriptAccumulator(extract_threshold_words=10)
        utt = Utterance(text="hello world", t_start=0.0, t_end=2.0)  # 2 words
        assert acc.push(utt) is False

    def test_push_returns_true_at_threshold(self):
        acc = TranscriptAccumulator(extract_threshold_words=5)
        words = "one two three four five"
        assert acc.push(Utterance(text=words, t_start=0.0, t_end=3.0)) is True

    def test_counter_resets_after_threshold(self):
        acc = TranscriptAccumulator(extract_threshold_words=5)
        # Cross the threshold once
        acc.push(Utterance(text="one two three four five", t_start=0.0, t_end=3.0))
        # Next push with fewer words should be False again
        assert acc.push(Utterance(text="hello", t_start=3.0, t_end=4.0)) is False

    def test_text_joins_utterances(self):
        acc = TranscriptAccumulator()
        acc.push(Utterance(text="hello", t_start=0.0, t_end=1.0))
        acc.push(Utterance(text="world", t_start=1.0, t_end=2.0))
        assert acc.text == "hello world"

    def test_rolling_window_evicts_old_utterances(self):
        acc = TranscriptAccumulator(max_utterances=2)
        acc.push(Utterance(text="first", t_start=0.0, t_end=1.0))
        acc.push(Utterance(text="second", t_start=1.0, t_end=2.0))
        acc.push(Utterance(text="third", t_start=2.0, t_end=3.0))
        assert "first" not in acc.text
        assert acc.text == "second third"

    def test_is_empty_initially(self):
        assert TranscriptAccumulator().is_empty is True

    def test_not_empty_after_push(self):
        acc = TranscriptAccumulator()
        acc.push(Utterance(text="x", t_start=0.0, t_end=1.0))
        assert acc.is_empty is False


class TestCueDeduplicator:
    def test_new_title_not_duplicate(self):
        dedup = CueDeduplicator()
        assert dedup.is_duplicate("Twilio AMD") is False

    def test_seen_title_is_duplicate(self):
        dedup = CueDeduplicator()
        dedup.mark_seen("Twilio AMD")
        assert dedup.is_duplicate("Twilio AMD") is True

    def test_case_insensitive(self):
        dedup = CueDeduplicator()
        dedup.mark_seen("twilio amd")
        assert dedup.is_duplicate("TWILIO AMD") is True

    def test_rolling_window_evicts_old_titles(self):
        dedup = CueDeduplicator(window=2)
        dedup.mark_seen("A")
        dedup.mark_seen("B")
        dedup.mark_seen("C")  # evicts "A"
        assert dedup.is_duplicate("A") is False
        assert dedup.is_duplicate("B") is True
