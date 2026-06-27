"""ExtractCues — rolling transcript → 4 parallel Mistral calls → Cue events."""

from __future__ import annotations

import sys
from dataclasses import dataclass

from ... import protocol as p
from ...application.session_context import SessionContext
from ...domain.ports import AudioEventBus, CueExtractorPort, SessionRepository


@dataclass
class ExtractCues:
    extractor: CueExtractorPort
    repo: SessionRepository
    bus: AudioEventBus

    async def execute(self, sctx: SessionContext) -> None:
        if sctx.accumulator.is_empty:
            return

        cues = await self.extractor.extract(sctx.accumulator.text, sctx.session.id)

        for cue in cues:
            if sctx.deduplicator.is_duplicate(cue.title):
                continue
            sctx.deduplicator.mark_seen(cue.title)
            self.repo.save_cue(cue)
            await self.bus.broadcast(
                p.CueNew(
                    session_id=sctx.session.id,
                    cue_id=cue.id,
                    cue_type=cue.cue_type,
                    title=cue.title,
                    body=cue.body,
                ).model_dump()
            )
            print(f"[cue:{cue.cue_type}] {cue.title}", file=sys.stderr, flush=True)
