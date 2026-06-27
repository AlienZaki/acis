"""Per-session mutable state, owned by the connection handler."""

from __future__ import annotations

from dataclasses import dataclass, field

from ..domain.entities import Session
from ..domain.services import CueDeduplicator, TranscriptAccumulator
from ..settings import settings


@dataclass
class SessionContext:
    session: Session
    accumulator: TranscriptAccumulator = field(
        default_factory=lambda: TranscriptAccumulator(extract_threshold_words=settings.ACIS_CUE_THRESHOLD_WORDS)
    )
    deduplicator: CueDeduplicator = field(default_factory=CueDeduplicator)
    clock: float = 0.0  # elapsed seconds since session start
