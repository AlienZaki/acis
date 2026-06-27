"""ProcessChunk — WAV bytes → Voxtral ASR → accumulator → maybe trigger cue extraction."""

from __future__ import annotations

import sys
from dataclasses import dataclass

from ... import protocol as p
from ...application.session_context import SessionContext
from ...domain.entities import Utterance
from ...domain.ports import ASRPort, AudioEventBus, SessionRepository

_CHUNK_SECS = 3.0  # matches ACIS_AUDIO_CHUNK_SECS default; kept here for t_end math


@dataclass
class ProcessChunk:
    asr: ASRPort
    repo: SessionRepository
    bus: AudioEventBus

    async def execute(self, sctx: SessionContext, wav_bytes: bytes) -> bool:
        """Transcribe one audio chunk and accumulate the result.

        Returns True when the extraction threshold is crossed so the caller can
        fire ``ExtractCues`` without polling a flag.
        """
        text = await self.asr.transcribe(wav_bytes)
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
        print(f"[asr] {text}", file=sys.stderr, flush=True)

        return sctx.accumulator.push(utt)
