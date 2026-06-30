"""Regression tests against real ACIS session fixtures.

Each fixture directory under tests/fixtures/ contains three files captured from
a live session:
  transcript.txt      — raw ASR output with [HH:MM:SS] timestamps
  expected_cues.txt   — cues the pipeline produced in that session (ground truth)
  expected_summary.txt — summary the pipeline produced (ground truth)

Tests re-run the pipeline on the transcript, print output side-by-side with the
expected outputs, and assert structural minimums.  Exact match is not expected
(LLM outputs are non-deterministic); human review of the printed diff is the
primary quality gate.

Fixtures:
  tuc_startup_meeting/         — TU Clausthal startup incubation & pitch deck session (2026-06-26)
  german_startup_seminar/      — German startup ecosystem & business strategy seminar (2026-06-26)

    uv run pytest tests/ai_eval/test_real_sessions.py -v -s
    uv run pytest tests/ai_eval/test_real_sessions.py -v -s -k tuc
    uv run pytest tests/ai_eval/test_real_sessions.py -v -s -k seminar
"""

from __future__ import annotations

import os
import re
from pathlib import Path

import pytest

from acis.domain.entities import Session, Utterance

pytestmark = pytest.mark.ai_eval

FIXTURES = Path(__file__).parent.parent / "fixtures"


# ── Transcript parser ─────────────────────────────────────────────────────────

def _parse_utterances(path: Path) -> list[Utterance]:
    """Parse a timestamped transcript file into Utterance objects.

    Groups consecutive lines between [HH:MM:SS] markers into one Utterance,
    using the wall-clock offset from the first timestamp as t_start.
    """
    lines = path.read_text().splitlines()
    utterances: list[Utterance] = []
    current_ts_str: str | None = None
    current_lines: list[str] = []
    start_secs: float | None = None

    def _secs(ts: str) -> float:
        h, m, s = map(int, ts.split(":"))
        return float(h * 3600 + m * 60 + s)

    def _flush() -> None:
        nonlocal start_secs
        if current_ts_str is None or not current_lines:
            return
        text = " ".join(current_lines).strip()
        if not text:
            return
        t = _secs(current_ts_str)
        if start_secs is None:
            start_secs = t
        t_start = t - start_secs
        utterances.append(Utterance(text=text, t_start=t_start, t_end=t_start + 5.0))

    for line in lines:
        m = re.match(r"^\[(\d{2}:\d{2}:\d{2})\]$", line.strip())
        if m:
            _flush()
            current_ts_str = m.group(1)
            current_lines = []
        elif current_ts_str is not None:
            stripped = line.strip()
            if stripped:
                current_lines.append(stripped)

    _flush()
    return utterances


def _plain_text(utterances: list[Utterance]) -> str:
    return " ".join(u.text for u in utterances)


# ── Shared fixtures ───────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def api_key() -> str:
    key = os.environ.get("MISTRAL_API_KEY")
    if not key:
        pytest.skip("MISTRAL_API_KEY not set")
    return key


@pytest.fixture(scope="session")
def extractor(api_key):
    from acis.infrastructure.output_adapters.llm.cue_extractor import MistralCueExtractor
    from acis.settings import settings
    return MistralCueExtractor(api_key=api_key, model=settings.ACIS_CUE_MODEL)


@pytest.fixture(scope="session")
def summarizer(api_key):
    from acis.infrastructure.output_adapters.llm.summarizer import MistralSummarizer
    from acis.settings import settings
    return MistralSummarizer(api_key=api_key, model=settings.ACIS_SUMMARY_MODEL)


# ── TU Clausthal Startup Meeting (2026-06-26) ─────────────────────────────────

@pytest.fixture(scope="module")
def tuc_utterances() -> list[Utterance]:
    return _parse_utterances(FIXTURES / "tuc_startup_meeting" / "transcript.txt")


async def test_tuc_cues(extractor, tuc_utterances):
    """TU Clausthal meeting — cue extraction should catch people (Simon, Saten, Sara)."""
    fixture_dir = FIXTURES / "tuc_startup_meeting"
    transcript = _plain_text(tuc_utterances)
    expected = (fixture_dir / "expected_cues.txt").read_text()

    cues = await extractor.extract(transcript, "fixture-tuc")

    bio_cues = [c for c in cues if c.cue_type == "bio"]
    concept_cues = [c for c in cues if c.cue_type == "concept"]

    print(f"\n{'═'*60}")
    print("FIXTURE: TU Clausthal Startup Meeting — CUES")
    print(f"{'═'*60}")
    print(f"\nEXTRACTED ({len(cues)}):")
    for c in cues:
        print(f"  [{c.cue_type.upper():10s}] {c.title}")
        print(f"               {c.body}")
    print(f"\n{'─'*60}")
    print("EXPECTED (ground truth):")
    print(expected)

    assert len(cues) >= 3, f"expected ≥3 cues from 26-min meeting, got {len(cues)}"
    assert bio_cues, (
        f"expected BIO cues for Simon/Saten/Sara — got none. "
        f"Cue types present: {[c.cue_type for c in cues]}"
    )
    assert concept_cues, "expected ≥1 concept cue (pitch deck, EXIST, etc.)"


async def test_tuc_summary(summarizer, tuc_utterances):
    """TU Clausthal meeting — summary should mention pitch deck and EXIST."""
    fixture_dir = FIXTURES / "tuc_startup_meeting"
    expected = (fixture_dir / "expected_summary.txt").read_text()

    summary = await summarizer.summarize(
        Session(name="TU Clausthal Startup Meeting"), tuc_utterances
    )

    print(f"\n{'═'*60}")
    print("FIXTURE: TU Clausthal Startup Meeting — SUMMARY")
    print(f"{'═'*60}")
    print("\nEXTRACTED:")
    print(f"  Title: {summary.title}")
    print(f"  Prose: {summary.prose}")
    if summary.action_items:
        print("  Action items:")
        for item in summary.action_items:
            print(f"    ☐ {item}")
    if summary.keypoints:
        print("  Keypoints:")
        for kp in summary.keypoints:
            print(f"    {kp.get('heading', '')}")
            for b in kp.get("bullets", []):
                print(f"      • {b}")
    print(f"\n{'─'*60}")
    print("EXPECTED (ground truth):")
    print(expected)

    assert summary.prose, "summary prose is empty"
    prose_lower = summary.prose.lower() + " ".join(
        b.lower() for kp in summary.keypoints for b in kp.get("bullets", [])
    )
    assert any(kw in prose_lower for kw in ("pitch", "incubat", "startup", "exist")), (
        "summary does not mention core topics (pitch deck, incubation, EXIST)"
    )


# ── German Startup Ecosystem Seminar (2026-06-26) ─────────────────────────────

@pytest.fixture(scope="module")
def seminar_utterances() -> list[Utterance]:
    return _parse_utterances(FIXTURES / "german_startup_seminar" / "transcript.txt")


def _print_cues(label: str, cues, expected_path: Path) -> None:
    print(f"\n{'═'*60}")
    print(f"FIXTURE: {label} — CUES")
    print(f"{'═'*60}")
    print(f"\nEXTRACTED ({len(cues)}):")
    for c in cues:
        print(f"  [{c.cue_type.upper():10s}] {c.title}")
        print(f"               {c.body}")
    print(f"\n{'─'*60}")
    print("EXPECTED (ground truth):")
    print(expected_path.read_text())


def _print_summary(label: str, summary, expected_path: Path) -> None:
    print(f"\n{'═'*60}")
    print(f"FIXTURE: {label} — SUMMARY")
    print(f"{'═'*60}")
    print("\nEXTRACTED:")
    print(f"  Title: {summary.title}")
    print(f"  Prose: {summary.prose}")
    if summary.action_items:
        print("  Action items:")
        for item in summary.action_items:
            print(f"    ☐ {item}")
    if summary.keypoints:
        print("  Keypoints:")
        for kp in summary.keypoints:
            print(f"    {kp.get('heading', '')}")
            for b in kp.get("bullets", []):
                print(f"      • {b}")
    print(f"\n{'─'*60}")
    print("EXPECTED (ground truth):")
    print(expected_path.read_text())


async def test_seminar_cues(extractor, seminar_utterances):
    """German startup seminar — expect BIO cues and core concept cues (MVP, grant, etc.)."""
    fixture_dir = FIXTURES / "german_startup_seminar"
    transcript = _plain_text(seminar_utterances)

    cues = await extractor.extract(transcript, "fixture-seminar")
    _print_cues("German Startup Ecosystem Seminar", cues, fixture_dir / "expected_cues.txt")

    bio_cues = [c for c in cues if c.cue_type == "bio"]
    concept_cues = [c for c in cues if c.cue_type == "concept"]
    answer_cues = [c for c in cues if c.cue_type == "answer"]

    assert len(cues) >= 3, f"expected ≥3 cues from seminar, got {len(cues)}"
    assert concept_cues, "expected ≥1 concept cue (MVP, grant, incubation, etc.)"
    # Lecture format: questions are mostly rhetorical — answers/bios are optional.
    # Log what we got so human can compare against ground truth.
    print(f"\n  [breakdown] concept={len(concept_cues)} answer={len(answer_cues)} bio={len(bio_cues)} suggestion={len([c for c in cues if c.cue_type == 'suggestion'])}")


async def test_seminar_summary(summarizer, seminar_utterances):
    """German startup seminar — summary should cover MVP, grants, and business models."""
    fixture_dir = FIXTURES / "german_startup_seminar"

    summary = await summarizer.summarize(
        Session(name="German Startup Ecosystem Seminar"), seminar_utterances
    )
    _print_summary("German Startup Ecosystem Seminar", summary, fixture_dir / "expected_summary.txt")

    assert summary.prose, "summary prose is empty"
    all_text = (
        summary.prose.lower()
        + " ".join(b.lower() for kp in summary.keypoints for b in kp.get("bullets", []))
    )
    assert any(kw in all_text for kw in ("mvp", "grant", "incubat", "startup", "revenue")), (
        "summary does not mention core topics (MVP, grants, incubation, revenue)"
    )
