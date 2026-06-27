"""Core domain entities — pure data, no I/O."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Literal
from uuid import uuid4

CueType = Literal["concept", "answer", "suggestion", "bio"]


@dataclass(frozen=True)
class Utterance:
    text: str
    t_start: float  # seconds since session start
    t_end: float


@dataclass
class Session:
    id: str = field(default_factory=lambda: str(uuid4()))
    name: str = "Untitled session"
    started_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    ended_at: datetime | None = None


@dataclass(frozen=True)
class Cue:
    id: str
    cue_type: CueType
    title: str
    body: str
    session_id: str
    spoken_through_glasses: bool = False


@dataclass
class AISummary:
    session_id: str
    title: str
    prose: str
    keypoints: list[dict]  # [{heading: str, bullets: [str]}]
    action_items: list[str]


@dataclass
class PrepNote:
    id: str = field(default_factory=lambda: str(uuid4()))
    title: str = ""
    body: str = ""
    active: bool = True
