"""InjectText — feed a pre-transcribed line directly into the session pipeline.

Skips ASR entirely: used by fixture replay and tests so the STT is stubbed out.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass

from ... import protocol as p
from ...application.session_context import SessionContext
from ...domain.entities import Utterance
from ...domain.ports import AudioEventBus, SessionRepository

_CHUNK_SECS = 3.0


@dataclass
class InjectText:
    repo: SessionRepository
    bus: AudioEventBus

    async def execute(self, sctx: SessionContext, text: str) -> bool:
        """Store utterance and broadcast transcript.delta; returns True when cue extraction should run."""
        if not text:
            return False

        t_start = sctx.clock
        t_end = t_start + _CHUNK_SECS
        sctx.clock = t_end

        utt = Utterance(text=text, t_start=t_start, t_end=t_end)
        self.repo.save_utterance(utt, sctx.session.id)

        await self.bus.broadcast(
            p.TranscriptDelta(
                session_id=sctx.session.id,
                text=text,
                t_start=t_start,
                t_end=t_end,
            ).model_dump()
        )
        print(f"[inject] {text}", file=sys.stderr, flush=True)

        return sctx.accumulator.push(utt)
