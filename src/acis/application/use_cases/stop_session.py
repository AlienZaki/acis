"""StopSession — mark session ended and kick off async summary generation."""

from __future__ import annotations

import asyncio
import sys
from dataclasses import dataclass
from datetime import UTC, datetime

from ... import protocol as p
from ...domain.entities import Session
from ...domain.ports import AudioEventBus, SessionRepository, SummarizerPort


@dataclass
class StopSession:
    repo: SessionRepository
    summarizer: SummarizerPort
    bus: AudioEventBus

    async def execute(self, session: Session) -> None:
        session.ended_at = datetime.now(UTC)
        self.repo.save_session(session)
        await self.bus.broadcast(p.SessionStopped(session_id=session.id).model_dump())
        print(f"[session] stopped {session.id}", file=sys.stderr, flush=True)
        # Summarisation runs in the background so the client is not blocked.
        asyncio.create_task(self._summarize(session))

    async def _summarize(self, session: Session) -> None:
        utterances = self.repo.get_utterances(session.id)
        if not utterances:
            return
        try:
            summary = await self.summarizer.summarize(session, utterances)
            self.repo.save_summary(summary)
            await self.bus.broadcast(
                p.SummaryReady(
                    session_id=session.id,
                    title=summary.title,
                    prose=summary.prose,
                    keypoints=summary.keypoints,
                    action_items=summary.action_items,
                ).model_dump()
            )
            print(f"[summary] ready — {summary.title}", file=sys.stderr, flush=True)
        except Exception as exc:
            print(f"[summary] failed: {exc}", file=sys.stderr, flush=True)
            await self.bus.broadcast(p.Error(message=f"Summary generation failed: {exc}").model_dump())
