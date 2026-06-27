"""Dependency wiring — build the runtime Services from settings + adapters.

This is the composition root: every port-to-adapter binding happens here, and
only here. Use cases and handlers never construct adapters themselves.
"""

from __future__ import annotations

from ..domain.ports import AudioEventBus
from ..infrastructure.output_adapters.asr.voxtral import VoxtralASR
from ..infrastructure.output_adapters.llm.cue_extractor import MistralCueExtractor
from ..infrastructure.output_adapters.llm.summarizer import MistralSummarizer
from ..infrastructure.repositories.sqlite import SQLiteSessionRepository
from . import settings


def build_repository() -> SQLiteSessionRepository:
    return SQLiteSessionRepository(db_path=settings.ACIS_DB_PATH)


def build_services(bus: AudioEventBus):
    """Wire all ports to concrete adapters and return the assembled Services."""
    from ..application.use_cases.extract_cues import ExtractCues
    from ..application.use_cases.process_chunk import ProcessChunk
    from ..application.use_cases.start_session import StartSession
    from ..application.use_cases.stop_session import StopSession
    from ..infrastructure.input_interfaces.ws.router import Services

    if settings.MISTRAL_API_KEY is None:
        raise RuntimeError("MISTRAL_API_KEY is not set — copy .env.example to .env and fill it in")

    repo = build_repository()
    key, base = settings.MISTRAL_API_KEY, settings.MISTRAL_BASE_URL
    asr = VoxtralASR(api_key=key, base_url=base, model=settings.ACIS_ASR_MODEL)
    extractor = MistralCueExtractor(api_key=key, base_url=base, model=settings.ACIS_CUE_MODEL)
    summarizer = MistralSummarizer(api_key=key, base_url=base, model=settings.ACIS_SUMMARY_MODEL)

    return Services(
        start=StartSession(repo=repo, bus=bus),
        stop=StopSession(repo=repo, summarizer=summarizer, bus=bus),
        process=ProcessChunk(asr=asr, repo=repo, bus=bus),
        extract=ExtractCues(extractor=extractor, repo=repo, bus=bus),
        repo=repo,
    )
