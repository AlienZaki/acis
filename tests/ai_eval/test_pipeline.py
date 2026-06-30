"""AI-AI pipeline evaluation — text injection (no ASR).

Generator AI (Mistral Small) writes a realistic conversation.
ACIS pipeline (Mistral Small + Large) processes it.
Output is printed for human review.

    uv run pytest tests/ai_eval/test_pipeline.py -v -s
    uv run pytest tests/ai_eval/test_pipeline.py -v -s -k tech
"""

from __future__ import annotations

import os

import pytest

pytestmark = pytest.mark.ai_eval


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def api_key() -> str:
    key = os.environ.get("MISTRAL_API_KEY")
    if not key:
        pytest.skip("MISTRAL_API_KEY not set")
    return key


@pytest.fixture(scope="session")
def generator(api_key):
    from tests.ai_eval.script_generator import ScriptGenerator
    return ScriptGenerator(api_key=api_key)


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


# ── Print helper ──────────────────────────────────────────────────────────────

def _show(topic, utterances, cues=(), summary=None):
    print(f"\n{'═'*60}")
    print(f"TOPIC: {topic}")
    print(f"{'═'*60}")
    print(f"\nSCRIPT ({len(utterances)} turns):")
    for u in utterances:
        print(f"  {u.text}")
    if cues:
        print(f"\nCUES ({len(cues)}):")
        for c in cues:
            print(f"  [{c.cue_type.upper():10s}] {c.title}")
            print(f"               {c.body}")
    if summary:
        print(f"\nSUMMARY: {summary.title}")
        print(f"  {summary.prose}")
        if summary.action_items:
            print("  Action items:")
            for item in summary.action_items:
                print(f"    ☐ {item}")
        if summary.keypoints:
            print("  Keypoints:")
            for kp in summary.keypoints:
                print(f"    {kp.get('heading','')}")
                for b in kp.get("bullets", []):
                    print(f"      • {b}")
    print()


# ── Scenario 1: tech architecture debate ─────────────────────────────────────

async def test_tech_architecture(generator, extractor):
    """Microservices debate → expect CONCEPT + SUGGESTION cues."""
    topic = "deciding whether to migrate our monolith to microservices"
    utterances = await generator.generate(topic)
    cues = await extractor.extract(
        " ".join(u.text for u in utterances), "eval-tech"
    )
    _show(topic, utterances, cues)

    assert len(cues) >= 2, f"got {len(cues)} cues"
    assert any(c.cue_type == "concept" for c in cues), "expected ≥1 concept cue"
    assert any(c.cue_type == "suggestion" for c in cues), "expected ≥1 suggestion cue"


# ── Scenario 2: project planning — summary quality ────────────────────────────

async def test_project_planning_summary(generator, summarizer):
    """Q4 roadmap → expect summary with action items."""
    from acis.domain.entities import Session

    topic = "Q4 product roadmap planning — features to cut, ship, or defer"
    utterances = await generator.generate(topic)
    summary = await summarizer.summarize(Session(name="Q4 roadmap"), utterances)
    _show(topic, utterances, summary=summary)

    assert summary.prose, "summary prose is empty"
    assert len(summary.action_items) >= 1, f"got {summary.action_items}"


# ── Scenario 3: full pipeline — cues + summary ───────────────────────────────

async def test_full_pipeline_research_meeting(generator, extractor, summarizer):
    """PhD results presentation → cues + summary in parallel."""
    import asyncio

    from acis.domain.entities import Session

    topic = "PhD student presenting NLP experiment results to their supervisor"
    utterances = await generator.generate(topic)
    transcript = " ".join(u.text for u in utterances)

    cues, summary = await asyncio.gather(
        extractor.extract(transcript, "eval-research"),
        summarizer.summarize(Session(name="Research sync"), utterances),
    )
    _show(topic, utterances, cues, summary)

    assert len(cues) >= 2, f"got {len(cues)} cues"
    assert summary.prose, "summary prose is empty"


# ── Scenario 4: sales call — bio + answer cues ───────────────────────────────

async def test_sales_call_cues(generator, extractor):
    """Enterprise sales call → expect BIO + ANSWER cues."""
    topic = "enterprise sales call — prospect asking about compliance and mentioning competitors"
    utterances = await generator.generate(topic)
    cues = await extractor.extract(
        " ".join(u.text for u in utterances), "eval-sales"
    )
    _show(topic, utterances, cues)

    assert len(cues) >= 1, f"got {len(cues)} cues"
    assert any(c.cue_type in ("answer", "bio") for c in cues), (
        f"expected answer or bio cue, got: {[c.cue_type for c in cues]}"
    )
