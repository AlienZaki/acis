"""Full AI-AI pipeline tests with real ASR.

Signal chain:
  Mistral (generator) → macOS TTS → Voxtral ASR → Mistral (cue extractor + summarizer)

Output is printed for human review.

    uv run pytest tests/ai_eval/test_asr_pipeline.py -v -s
    uv run pytest tests/ai_eval/test_asr_pipeline.py -v -s -k incident
"""

from __future__ import annotations

import asyncio
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
def asr(api_key):
    from acis.infrastructure.output_adapters.asr.voxtral import VoxtralASR
    from acis.settings import settings
    return VoxtralASR(api_key=api_key, model=settings.ACIS_ASR_MODEL)


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


# ── Helpers ───────────────────────────────────────────────────────────────────

async def _synthesize_and_transcribe(asr, utterances) -> tuple[str, list[str]]:
    from tests.ai_eval.speech_synthesizer import split_chunks, synthesize_script

    print("\n  [TTS] synthesizing…", flush=True)
    wav = await asyncio.to_thread(synthesize_script, utterances)

    chunks = split_chunks(wav)
    print(f"  [ASR] {len(chunks)} chunks → Voxtral", flush=True)

    parts: list[str] = []
    for i, chunk in enumerate(chunks):
        text = await asr.transcribe(chunk)
        label = text[:70] if text else "(silence)"
        print(f"    [{i+1:02d}/{len(chunks)}] {label}", flush=True)
        if text:
            parts.append(text)

    return " ".join(parts), parts


def _show(topic, utterances, asr_transcript, cues=(), summary=None):
    print(f"\n{'═'*60}")
    print(f"TOPIC: {topic}")
    print(f"{'═'*60}")

    print(f"\nORIGINAL SCRIPT ({len(utterances)} turns):")
    for u in utterances:
        print(f"  {u.text}")

    print("\nASR TRANSCRIPT:")
    print(f"  {asr_transcript or '(empty)'}")

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

    print()


# ── Scenario 1: incident postmortem ──────────────────────────────────────────

async def test_asr_incident_postmortem(generator, asr, extractor):
    """DB outage postmortem: TTS → Voxtral → cue extraction."""
    topic = "software incident postmortem — database outage that took down checkout for 45 minutes"
    utterances = await generator.generate(topic)

    asr_text, _ = await _synthesize_and_transcribe(asr, utterances)

    if not asr_text.strip():
        pytest.skip("ASR returned empty transcript — check audio synthesis")

    cues = await extractor.extract(asr_text, "eval-asr-incident")
    _show(topic, utterances, asr_text, cues)

    assert len(cues) >= 1, f"expected ≥1 cue from ASR transcript, got {len(cues)}"


# ── Scenario 2: full pipeline with summary ───────────────────────────────────

async def test_asr_full_pipeline(generator, asr, extractor, summarizer):
    """GTM strategy: full chain TTS → ASR → cues + summary in parallel."""
    from acis.domain.entities import Session, Utterance

    topic = "startup team planning their go-to-market strategy for a B2B SaaS product"
    utterances = await generator.generate(topic)

    asr_text, asr_parts = await _synthesize_and_transcribe(asr, utterances)

    if not asr_text.strip():
        pytest.skip("ASR returned empty transcript — check audio synthesis")

    asr_utterances = [
        Utterance(text=part, t_start=i * 3.0, t_end=(i + 1) * 3.0)
        for i, part in enumerate(asr_parts)
        if part
    ]

    cues, summary = await asyncio.gather(
        extractor.extract(asr_text, "eval-asr-gtm"),
        summarizer.summarize(Session(name="GTM strategy"), asr_utterances),
    )
    _show(topic, utterances, asr_text, cues, summary)

    assert len(cues) >= 1, f"expected ≥1 cue, got {len(cues)}"
    assert summary.prose, "summary prose is empty"
