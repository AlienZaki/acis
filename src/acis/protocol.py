"""Typed WebSocket protocol — Pydantic models for every message on the wire.

Two families:
- **Inbound**  — what clients send the brain (discriminated on ``type``).
- **Outbound** — what the brain pushes back.

``parse_inbound(raw)`` validates one client frame into a typed model, returning
None for anything malformed / unknown so the server can skip it safely.

``gen-types`` (``scripts/gen_ts_protocol.py``) emits matching TypeScript from
this module so the React Native app shares the exact contract.
"""

from __future__ import annotations

import json
from typing import Annotated, Literal

from pydantic import BaseModel, Field, ValidationError

# ─────────────────────────── Inbound (client → brain) ────────────────────────


class Hello(BaseModel):
    type: Literal["hello"]


class SessionStart(BaseModel):
    type: Literal["session.start"]
    name: str | None = None  # user-supplied session name; brain generates one if absent


class SessionStop(BaseModel):
    type: Literal["session.stop"]


class AudioChunk(BaseModel):
    """3-second WAV chunk from the phone mic, base64-encoded.

    Sample rate must match ``ACIS_AUDIO_SAMPLE_RATE`` (default 16 kHz mono).
    The brain decodes, transcribes via Voxtral, and accumulates the text.
    """

    type: Literal["audio.chunk"]
    data_b64: str
    sample_rate: int = 16000


class Ping(BaseModel):
    type: Literal["ping"]


Inbound = Annotated[
    Hello | SessionStart | SessionStop | AudioChunk | Ping,
    Field(discriminator="type"),
]


class _InboundEnvelope(BaseModel):
    msg: Inbound


def parse_inbound(raw: str | bytes | dict) -> BaseModel | None:
    """Validate one client frame into a typed model, or None if malformed / unknown."""
    try:
        data = raw if isinstance(raw, dict) else json.loads(raw)
        return _InboundEnvelope(msg=data).msg  # ty: ignore[invalid-argument-type]
    except (ValidationError, TypeError, ValueError):
        return None


# ─────────────────────────── Outbound (brain → clients) ──────────────────────

CueTypeLiteral = Literal["concept", "answer", "suggestion", "bio"]


class HelloOk(BaseModel):
    type: Literal["hello.ok"] = "hello.ok"


class SessionStarted(BaseModel):
    type: Literal["session.started"] = "session.started"
    session_id: str
    name: str
    started_at: str  # ISO 8601


class SessionStopped(BaseModel):
    type: Literal["session.stopped"] = "session.stopped"
    session_id: str


class TranscriptDelta(BaseModel):
    """A recognised speech segment, broadcast immediately after Voxtral returns."""

    type: Literal["transcript.delta"] = "transcript.delta"
    session_id: str
    text: str
    t_start: float  # seconds since session start
    t_end: float


class CueNew(BaseModel):
    """A freshly extracted cue — the app speaks it through the glasses."""

    type: Literal["cue.new"] = "cue.new"
    session_id: str
    cue_id: str
    cue_type: CueTypeLiteral
    title: str
    body: str


class SummaryReady(BaseModel):
    """Post-session AI summary — fires after Mistral Large finishes."""

    type: Literal["summary.ready"] = "summary.ready"
    session_id: str
    title: str
    prose: str
    keypoints: list[dict]  # [{heading: str, bullets: [str]}]
    action_items: list[str]


class Error(BaseModel):
    type: Literal["error"] = "error"
    message: str


class Pong(BaseModel):
    type: Literal["pong"] = "pong"
