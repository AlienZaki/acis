"""Unit tests for domain services (no I/O)."""

from acis.domain.entities import Utterance
from acis.domain.services import CueDeduplicator, SemanticDeduplicator, TranscriptAccumulator


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

    def test_remembers_titles_for_whole_session(self):
        # The rolling extraction window re-derives the same entities repeatedly,
        # so a title seen early must stay deduped no matter how many follow it.
        dedup = CueDeduplicator()
        dedup.mark_seen("A")
        for title in ("B", "C", "D", "E", "F", "G"):
            dedup.mark_seen(title)
        assert dedup.is_duplicate("A") is True
        assert dedup.is_duplicate("B") is True


class TestSemanticDeduplicator:
    def test_new_vector_not_duplicate(self):
        dedup = SemanticDeduplicator(default_threshold=0.88)
        assert dedup.is_duplicate("answer", [1.0, 0.0, 0.0]) is False

    def test_identical_vector_is_duplicate(self):
        dedup = SemanticDeduplicator(default_threshold=0.88)
        dedup.add("answer", [1.0, 0.0, 0.0])
        assert dedup.is_duplicate("answer", [1.0, 0.0, 0.0]) is True

    def test_near_vector_above_threshold_is_duplicate(self):
        dedup = SemanticDeduplicator(default_threshold=0.88)
        dedup.add("answer", [1.0, 0.0, 0.0])
        # cosine ≈ 0.997 — a paraphrase of the same cue.
        assert dedup.is_duplicate("answer", [1.0, 0.08, 0.0]) is True

    def test_distinct_vector_below_threshold_kept(self):
        dedup = SemanticDeduplicator(default_threshold=0.88)
        dedup.add("answer", [1.0, 0.0, 0.0])
        # cosine ≈ 0.71 — genuinely different cue.
        assert dedup.is_duplicate("answer", [1.0, 1.0, 0.0]) is False

    def test_dedup_is_scoped_per_cue_type(self):
        dedup = SemanticDeduplicator(default_threshold=0.88)
        dedup.add("answer", [1.0, 0.0, 0.0])
        # Same vector, different type → not a duplicate.
        assert dedup.is_duplicate("concept", [1.0, 0.0, 0.0]) is False

    def test_per_type_threshold_override(self):
        # Suggestions use a looser bar so near-paraphrases collapse, while the
        # same vector pair stays distinct under the stricter default.
        # cosine([1,0,0], [1,0.6,0]) ≈ 0.857 — between 0.84 and 0.88.
        dedup = SemanticDeduplicator(default_threshold=0.88, type_thresholds={"suggestion": 0.84})
        anchor = [1.0, 0.0, 0.0]
        borderline = [1.0, 0.60, 0.0]
        dedup.add("suggestion", anchor)
        dedup.add("answer", anchor)
        assert dedup.is_duplicate("suggestion", borderline) is True   # looser bar catches it
        assert dedup.is_duplicate("answer", borderline) is False      # stricter bar keeps it
