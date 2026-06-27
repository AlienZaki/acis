"""StartSession — create a new session, persist it, and broadcast session.started."""

from __future__ import annotations

import sys
from dataclasses import dataclass

from ... import protocol as p
from ...domain.entities import Session
from ...domain.ports import AudioEventBus, SessionRepository


@dataclass
class StartSession:
    repo: SessionRepository
    bus: AudioEventBus

    async def execute(self, name: str | None = None) -> Session:
        session = Session(name=name or "Untitled session")
        self.repo.save_session(session)
        await self.bus.broadcast(
            p.SessionStarted(
                session_id=session.id,
                name=session.name,
                started_at=session.started_at.isoformat(),
            ).model_dump()
        )
        print(f"[session] started {session.id} — {session.name}", file=sys.stderr, flush=True)
        return session
