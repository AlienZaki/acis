"""Ports — the interfaces the application core depends on (hexagonal boundary).

Every port is a strategy seam: concrete adapters in
``infrastructure/output_adapters`` are interchangeable behind these Protocols,
selected at startup by the factories in ``settings/injection.py``.
"""

from __future__ import annotations

from typing import Protocol

from .entities import AISummary, Cue, PrepNote, Session, Utterance


class ASRPort(Protocol):
    """Transcribe a WAV buffer to text."""

    async def transcribe(self, wav_bytes: bytes) -> str: ...


class CueExtractorPort(Protocol):
    """Run 4 parallel LLM calls against rolling transcript; return extracted cues."""

    async def extract(self, transcript: str, session_id: str) -> list[Cue]: ...


class SummarizerPort(Protocol):
    """Generate an end-of-session AI summary from the full utterance list."""

    async def summarize(self, session: Session, utterances: list[Utterance]) -> AISummary: ...


class AudioEventBus(Protocol):
    """Broadcast a JSON-serialisable event dict to all connected clients."""

    async def broadcast(self, event: dict) -> None: ...


class SessionRepository(Protocol):
    def save_session(self, session: Session) -> None: ...
    def get_session(self, session_id: str) -> Session | None: ...
    def list_sessions(self) -> list[Session]: ...
    def save_utterance(self, utterance: Utterance, session_id: str) -> None: ...
    def get_utterances(self, session_id: str) -> list[Utterance]: ...
    def save_cue(self, cue: Cue) -> None: ...
    def get_cues(self, session_id: str) -> list[Cue]: ...
    def save_summary(self, summary: AISummary) -> None: ...
    def get_summary(self, session_id: str) -> AISummary | None: ...


class PrepNoteRepository(Protocol):
    def save(self, note: PrepNote) -> None: ...
    def list_active(self) -> list[PrepNote]: ...
    def delete(self, note_id: str) -> None: ...
