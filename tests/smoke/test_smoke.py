"""ACIS smoke tests — hit the real Mistral API end-to-end.

Skipped automatically when MISTRAL_API_KEY is absent. Run with:

    uv run pytest tests/smoke/ -v
    uv run pytest tests/smoke/ -v -s      # show server stderr (useful for debugging)

Each test is independent and uses its own temp SQLite database.
"""
from __future__ import annotations

import asyncio
import base64
import json

import pytest
import websockets as ws_lib

pytestmark = pytest.mark.smoke


# ── Helpers ────────────────────────────────────────────────────────────────────

async def _drain_until(ws, event_type: str, timeout: float) -> tuple[list[dict], bool]:
    """Collect WS messages until `event_type` appears or `timeout` expires.

    Returns (collected_messages, found) where found is True if the target type
    was seen before the timeout.
    """
    collected: list[dict] = []
    deadline = asyncio.get_event_loop().time() + timeout
    while True:
        remaining = deadline - asyncio.get_event_loop().time()
        if remaining <= 0:
            return collected, False
        try:
            raw = await asyncio.wait_for(ws.recv(), timeout=remaining)
            msg = json.loads(raw)
            collected.append(msg)
            if msg.get("type") == event_type:
                return collected, True
        except TimeoutError:
            return collected, False


# ── 1. WS handshake ───────────────────────────────────────────────────────────

async def test_smoke_ws_handshake(ws_server: str) -> None:
    """Connect to the brain, send hello, receive hello.ok within 2 s."""
    async with ws_lib.connect(ws_server) as ws:
        await ws.send(json.dumps({"type": "hello"}))
        raw = await asyncio.wait_for(ws.recv(), timeout=2.0)
    assert json.loads(raw)["type"] == "hello.ok"


# ── 2. Session lifecycle ──────────────────────────────────────────────────────

async def test_smoke_session_lifecycle(ws_server: str, tmp_db_path: str) -> None:
    """hello → session.start → session.started → session.stop → session.stopped.

    Also verifies the session row is committed to SQLite with a non-null ended_at.
    """
    from acis.infrastructure.repositories.sqlite import SQLiteSessionRepository

    async with ws_lib.connect(ws_server) as ws:
        # Handshake
        await ws.send(json.dumps({"type": "hello"}))
        await asyncio.wait_for(ws.recv(), timeout=2.0)

        # Start
        await ws.send(json.dumps({"type": "session.start", "name": "Smoke lifecycle"}))
        started = json.loads(await asyncio.wait_for(ws.recv(), timeout=5.0))
        assert started["type"] == "session.started", f"unexpected: {started}"
        session_id: str = started["session_id"]
        assert session_id

        # Ping round-trip (sanity-check keep-alive)
        await ws.send(json.dumps({"type": "ping"}))
        pong = json.loads(await asyncio.wait_for(ws.recv(), timeout=2.0))
        assert pong["type"] == "pong"

        # Stop
        await ws.send(json.dumps({"type": "session.stop"}))
        stopped = json.loads(await asyncio.wait_for(ws.recv(), timeout=5.0))
        assert stopped["type"] == "session.stopped", f"unexpected: {stopped}"
        assert stopped["session_id"] == session_id

    # SQLite check — ws_server and this test share the same tmp_db_path
    repo = SQLiteSessionRepository(db_path=tmp_db_path)
    session = repo.get_session(session_id)
    assert session is not None, "session row not found in SQLite"
    assert session.ended_at is not None, "ended_at should be set after session.stop"


# ── 3. ASR — model endpoint liveness ─────────────────────────────────────────

async def test_smoke_asr(api_key: str, sine_wav: bytes) -> None:
    """VoxtralASR.transcribe() returns a str without raising.

    The sine wave likely produces an empty transcript — that is acceptable.
    The test confirms the model name is valid and the endpoint is reachable.
    """
    from acis.infrastructure.output_adapters.asr.voxtral import VoxtralASR
    from acis.settings import settings

    asr = VoxtralASR(api_key=api_key, model=settings.ACIS_ASR_MODEL)
    result = await asr.transcribe(sine_wav)
    assert isinstance(result, str), f"expected str, got {type(result)}: {result!r}"


# ── 4. Cue extraction ─────────────────────────────────────────────────────────

async def test_smoke_cue_extraction(api_key: str, tmp_db_path: str, collecting_bus) -> None:
    """ExtractCues produces ≥ 1 concept cue from a transcript containing 'Twilio AMD'."""
    from acis.application.session_context import SessionContext
    from acis.application.use_cases.extract_cues import ExtractCues
    from acis.application.use_cases.start_session import StartSession
    from acis.domain.entities import Utterance
    from acis.infrastructure.output_adapters.llm.cue_extractor import MistralCueExtractor
    from acis.infrastructure.repositories.sqlite import SQLiteSessionRepository
    from acis.settings import settings

    repo = SQLiteSessionRepository(db_path=tmp_db_path)
    extractor = MistralCueExtractor(api_key=api_key, model=settings.ACIS_CUE_MODEL)
    start_uc = StartSession(repo=repo, bus=collecting_bus)
    extract_uc = ExtractCues(extractor=extractor, repo=repo, bus=collecting_bus)

    session = await start_uc.execute(name="Cue smoke test")
    sctx = SessionContext(session=session)

    # Fill the accumulator with a transcript known to trigger a Concept cue.
    # Voxtral is bypassed here — we inject text directly.
    utterances = [
        "We're using Twilio AMD in our outbound dialer.",
        "AMD stands for Answering Machine Detection — it tells us if a human or voicemail picked up.",
        "Without AMD we'd waste agent time on voicemail boxes.",
    ]
    for text in utterances:
        sctx.accumulator.push(Utterance(text=text, t_start=0.0, t_end=3.0))

    await extract_uc.execute(sctx)

    cue_events = collecting_bus.of_type("cue.new")
    assert len(cue_events) >= 1, "Expected ≥1 cue.new, got nothing. Check model output."

    concept_events = [e for e in cue_events if e["cue_type"] == "concept"]
    assert len(concept_events) >= 1, (
        f"Expected ≥1 concept cue, got cue types: {[e['cue_type'] for e in cue_events]}"
    )


# ── 5. Session summary ────────────────────────────────────────────────────────

async def test_smoke_summary(api_key: str) -> None:
    """MistralSummarizer returns a complete AISummary from a canned short transcript."""
    from acis.domain.entities import Session, Utterance
    from acis.infrastructure.output_adapters.llm.summarizer import MistralSummarizer
    from acis.settings import settings

    summarizer = MistralSummarizer(api_key=api_key, model=settings.ACIS_SUMMARY_MODEL)
    session = Session(name="Smoke summary")
    utterances = [
        Utterance(
            text="We need to delay the release to next Thursday — QA found a critical auth bug.",
            t_start=0.0, t_end=5.0,
        ),
        Utterance(text="Dino will fix the authentication issue by Wednesday morning.", t_start=5.0, t_end=10.0),
        Utterance(text="Ali will update the changelog and notify stakeholders.", t_start=10.0, t_end=15.0),
        Utterance(
            text="We agreed to add monitoring dashboards for the new payment service before go-live.",
            t_start=15.0, t_end=20.0,
        ),
    ]

    summary = await summarizer.summarize(session, utterances)

    assert summary.prose, "prose should be non-empty"
    assert summary.title, "title should be non-empty"
    assert summary.title not in {"Untitled session", "Smoke summary"}, (
        f"Expected a generated title, got: {summary.title!r}"
    )
    assert len(summary.action_items) >= 1, (
        f"Expected ≥1 action item (Dino / Ali tasks), got: {summary.action_items}"
    )
    assert len(summary.keypoints) >= 1, f"Expected ≥1 keypoint, got: {summary.keypoints}"


# ── 6. Full session over WebSocket ────────────────────────────────────────────

async def test_smoke_full_session(ws_server: str, sine_wav: bytes) -> None:
    """Full pipeline: handshake → start → 3 audio chunks → stop → session.stopped.

    Uses a sine wave WAV (likely produces no transcript) to verify the pipeline
    runs without exceptions.  session.stopped is asserted; summary.ready is not
    required (no utterances → summariser skips gracefully).
    """
    b64_chunk = base64.b64encode(sine_wav).decode()
    chunk_json = json.dumps({
        "type": "audio.chunk",
        "data_b64": b64_chunk,
        "sample_rate": 16000,
    })

    async with ws_lib.connect(ws_server, max_size=10 * 1024 * 1024) as ws:
        # 1. Handshake
        await ws.send(json.dumps({"type": "hello"}))
        msg = json.loads(await asyncio.wait_for(ws.recv(), timeout=2.0))
        assert msg["type"] == "hello.ok"

        # 2. Start session
        await ws.send(json.dumps({"type": "session.start", "name": "Full smoke"}))
        msg = json.loads(await asyncio.wait_for(ws.recv(), timeout=5.0))
        assert msg["type"] == "session.started"
        session_id = msg["session_id"]

        # 3. Send 3 audio chunks without waiting between them.
        #    The server processes them sequentially (~2s each for Voxtral).
        for _ in range(3):
            await ws.send(chunk_json)

        # 4. Stop session (queued behind the 3 chunks on the server side)
        await ws.send(json.dumps({"type": "session.stop"}))

        # 5. Drain until session.stopped arrives.
        #    Timeout: 3 chunks × ~3s Voxtral + 10s buffer = 20s.
        collected, found = await _drain_until(ws, "session.stopped", timeout=45.0)

    event_types = [m.get("type") for m in collected]
    assert found, f"session.stopped not received within timeout; got: {event_types}"

    stopped_events = [m for m in collected if m.get("type") == "session.stopped"]
    assert stopped_events[0]["session_id"] == session_id
