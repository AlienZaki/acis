"""Fixtures for ACIS smoke tests.

All smoke tests hit the real Mistral API and are skipped automatically when
MISTRAL_API_KEY is absent.

Run:
    uv run pytest tests/smoke/ -v          # all smoke tests
    uv run pytest -m smoke -v              # same via marker
    uv run pytest -m "not smoke" -v        # exclude smoke from a full run
"""
from __future__ import annotations

import math
import os
import struct
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio

# ── Skip gate ─────────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def api_key() -> str:
    key = os.environ.get("MISTRAL_API_KEY")
    if not key:
        pytest.skip("MISTRAL_API_KEY not set — skipping smoke tests")
    return key


# ── WAV fixture ───────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def sine_wav() -> bytes:
    """3-second 440 Hz sine wave, 16 kHz mono 16-bit PCM WAV.

    Voxtral will likely return an empty transcript (not speech), but a valid
    non-error response confirms the model endpoint exists and the format is
    accepted.
    """
    sample_rate = 16_000
    num_samples = sample_rate * 3
    pcm = struct.pack(
        f"<{num_samples}h",
        *[int(32767 * math.sin(2 * math.pi * 440 * i / sample_rate)) for i in range(num_samples)],
    )
    data_size = len(pcm)
    header = struct.pack(
        "<4sI4s4sIHHIIHH4sI",
        b"RIFF", 36 + data_size, b"WAVE",
        b"fmt ", 16,
        1,               # PCM
        1,               # mono
        sample_rate,
        sample_rate * 2, # byte rate
        2,               # block align
        16,              # bits per sample
        b"data", data_size,
    )
    return header + pcm


# ── Collecting event bus ──────────────────────────────────────────────────────

class CollectingBus:
    """AudioEventBus that accumulates events and supports typed async waiting."""

    def __init__(self) -> None:
        self.events: list[dict] = []
        self._waiters: dict[str, list] = {}

    async def broadcast(self, event: dict) -> None:
        self.events.append(event)
        event_type = event.get("type", "")
        for fut in self._waiters.pop(event_type, []):
            if not fut.done():
                fut.set_result(event)

    async def wait_for(self, event_type: str, timeout: float = 15.0) -> dict:
        """Return the first event of `event_type`, waiting up to `timeout` seconds.

        Checks events already received before creating a future, so there is no
        race between broadcast() and wait_for().
        """
        import asyncio
        for event in self.events:
            if event.get("type") == event_type:
                return event
        loop = asyncio.get_running_loop()
        fut = loop.create_future()
        self._waiters.setdefault(event_type, []).append(fut)
        return await asyncio.wait_for(fut, timeout=timeout)

    def of_type(self, event_type: str) -> list[dict]:
        return [e for e in self.events if e.get("type") == event_type]


@pytest.fixture
def collecting_bus() -> CollectingBus:
    return CollectingBus()


# ── Service factory ───────────────────────────────────────────────────────────

def _build_services(api_key: str, db_path: str, bus):
    """Wire concrete adapters into the use-case tree with a custom db path.

    Mirrors settings/injection.py but accepts an explicit db_path so each
    test gets its own SQLite file.
    """
    from acis.application.use_cases.extract_cues import ExtractCues
    from acis.application.use_cases.process_chunk import ProcessChunk
    from acis.application.use_cases.start_session import StartSession
    from acis.application.use_cases.stop_session import StopSession
    from acis.infrastructure.input_interfaces.ws.router import Services
    from acis.infrastructure.output_adapters.asr.voxtral import VoxtralASR
    from acis.infrastructure.output_adapters.llm.cue_extractor import MistralCueExtractor
    from acis.infrastructure.output_adapters.llm.summarizer import MistralSummarizer
    from acis.infrastructure.repositories.sqlite import SQLiteSessionRepository
    from acis.settings import settings

    repo = SQLiteSessionRepository(db_path=db_path)
    asr = VoxtralASR(api_key=api_key, model=settings.ACIS_ASR_MODEL)
    extractor = MistralCueExtractor(api_key=api_key, model=settings.ACIS_CUE_MODEL)
    summarizer = MistralSummarizer(api_key=api_key, model=settings.ACIS_SUMMARY_MODEL)

    return Services(
        start=StartSession(repo=repo, bus=bus),
        stop=StopSession(repo=repo, summarizer=summarizer, bus=bus),
        process=ProcessChunk(asr=asr, repo=repo, bus=bus),
        extract=ExtractCues(extractor=extractor, repo=repo, bus=bus),
        repo=repo,
    )


@pytest.fixture
def tmp_db_path(tmp_path) -> str:
    return str(tmp_path / "smoke.db")


# ── Live WebSocket server ─────────────────────────────────────────────────────

@pytest_asyncio.fixture
async def ws_server(api_key: str, tmp_db_path: str) -> AsyncGenerator[str, None]:
    """Start a real `acis serve` instance on 127.0.0.1:<OS-assigned port>.

    Both this fixture and tests that request tmp_db_path will share the same
    temp SQLite path (pytest deduplicates function-scoped fixtures within a test).
    """
    import websockets

    from acis.infrastructure.input_interfaces.ws.app import WebSocketEventBus, handle_connection

    bus = WebSocketEventBus()
    services = _build_services(api_key, tmp_db_path, bus)

    async def handler(ws):
        await handle_connection(ws, services=services, bus=bus)

    server = await websockets.serve(handler, "127.0.0.1", 0)
    port = server.sockets[0].getsockname()[1]
    try:
        yield f"ws://127.0.0.1:{port}"
    finally:
        server.close()
        await server.wait_closed()
