"""ExtractCues — rolling transcript → 4 parallel Mistral calls → Cue events."""

from __future__ import annotations

import sys
from dataclasses import dataclass

from ... import protocol as p
from ...application.session_context import SessionContext
from ...domain.entities import Cue
from ...domain.ports import AudioEventBus, CueExtractorPort, EmbedderPort, SessionRepository


@dataclass
class ExtractCues:
    extractor: CueExtractorPort
    embedder: EmbedderPort
    repo: SessionRepository
    bus: AudioEventBus

    async def execute(self, sctx: SessionContext) -> None:
        if sctx.accumulator.is_empty:
            return

        cues = await self.extractor.extract(sctx.accumulator.text, sctx.session.id)

        # Stage 1 — exact-title dedup (cheap, no API call).
        fresh: list[Cue] = []
        for cue in cues:
            if sctx.deduplicator.is_duplicate(cue.title):
                continue
            sctx.deduplicator.mark_seen(cue.title)
            fresh.append(cue)
        if not fresh:
            return

        # Stage 2 — semantic dedup against cues already accepted this session.
        # Falls back to exact-only if embedding fails, so dedup never blocks cues.
        vectors: list[list[float]] = []
        try:
            vectors = await self.embedder.embed([c.title for c in fresh])
        except Exception as exc:
            print(f"[dedup] embed failed, skipping semantic dedup: {exc}", file=sys.stderr, flush=True)
        use_semantic = len(vectors) == len(fresh)

        for i, cue in enumerate(fresh):
            if use_semantic:
                vector = vectors[i]
                if sctx.semantic.is_duplicate(cue.cue_type, vector):
                    continue
                sctx.semantic.add(cue.cue_type, vector)
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
