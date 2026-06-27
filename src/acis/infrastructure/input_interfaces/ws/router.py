"""Message router — one typed handler per inbound message type.

``dispatch()`` looks up the handler by the parsed model's type and yields
outbound messages for the transport layer to send.  Handlers are thin: they
adapt transport concerns (per-connection session state) and delegate real work
to the application use cases.
"""

from __future__ import annotations

import base64
import sys
from collections.abc import AsyncIterator
from dataclasses import dataclass

from pydantic import BaseModel

from .... import protocol as p
from ....application.session_context import SessionContext
from ....application.use_cases.extract_cues import ExtractCues
from ....application.use_cases.process_chunk import ProcessChunk
from ....application.use_cases.start_session import StartSession
from ....application.use_cases.stop_session import StopSession
from ....infrastructure.repositories.sqlite import SQLiteSessionRepository


@dataclass
class Services:
    """Everything the handlers need, wired once at startup (see settings/injection)."""

    start: StartSession
    stop: StopSession
    process: ProcessChunk
    extract: ExtractCues
    repo: SQLiteSessionRepository


@dataclass
class ConnCtx:
    """Per-connection mutable state: which session (if any) is active."""

    current: SessionContext | None = None


# ── Handlers ─────────────────────────────────────────────────────────────────


async def _hello(ctx: ConnCtx, svc: Services, msg: p.Hello) -> AsyncIterator[BaseModel]:
    yield p.HelloOk()


async def _session_start(ctx: ConnCtx, svc: Services, msg: p.SessionStart) -> AsyncIterator[BaseModel]:
    if ctx.current is not None:
        yield p.Error(message="a session is already active — send session.stop first")
        return
    session = await svc.start.execute(name=msg.name)
    ctx.current = SessionContext(session=session)


async def _session_stop(ctx: ConnCtx, svc: Services, msg: p.SessionStop) -> AsyncIterator[BaseModel]:
    if ctx.current is None:
        yield p.Error(message="no active session")
        return
    await svc.stop.execute(ctx.current.session)
    ctx.current = None


async def _audio_chunk(ctx: ConnCtx, svc: Services, msg: p.AudioChunk) -> AsyncIterator[BaseModel]:
    if ctx.current is None:
        yield p.Error(message="no active session — send session.start first")
        return
    try:
        wav_bytes = base64.b64decode(msg.data_b64)
    except Exception:
        yield p.Error(message="audio.chunk: invalid base64")
        return
    should_extract = await svc.process.execute(ctx.current, wav_bytes)
    if should_extract:
        await svc.extract.execute(ctx.current)


async def _ping(ctx: ConnCtx, svc: Services, msg: p.Ping) -> AsyncIterator[BaseModel]:
    yield p.Pong()


HANDLERS = {
    p.Hello: _hello,
    p.SessionStart: _session_start,
    p.SessionStop: _session_stop,
    p.AudioChunk: _audio_chunk,
    p.Ping: _ping,
}


async def dispatch(ctx: ConnCtx, svc: Services, msg: BaseModel) -> AsyncIterator[BaseModel]:
    handler = HANDLERS.get(type(msg))
    if handler is None:
        print(f"[ws] unhandled message type: {type(msg).__name__}", file=sys.stderr)
        return
    async for out in handler(ctx, svc, msg):
        yield out
