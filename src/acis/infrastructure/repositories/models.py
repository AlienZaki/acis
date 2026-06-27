"""SQLModel ORM models — table definitions only, no business logic."""

from __future__ import annotations

from datetime import datetime

from sqlmodel import Field, SQLModel


class SessionORM(SQLModel, table=True):
    __tablename__ = "sessions"

    id: str = Field(primary_key=True)
    name: str = ""
    started_at: datetime
    ended_at: datetime | None = None
    summary_json: str | None = None  # AISummary serialised as a JSON blob


class UtteranceORM(SQLModel, table=True):
    __tablename__ = "utterances"

    id: int | None = Field(default=None, primary_key=True)
    session_id: str = Field(foreign_key="sessions.id", index=True)
    text: str
    t_start: float
    t_end: float


class CueORM(SQLModel, table=True):
    __tablename__ = "cues"

    id: str = Field(primary_key=True)
    session_id: str = Field(foreign_key="sessions.id", index=True)
    cue_type: str
    title: str
    body: str
    spoken_through_glasses: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)


class PrepNoteORM(SQLModel, table=True):
    __tablename__ = "prep_notes"

    id: str = Field(primary_key=True)
    title: str = ""
    body: str = ""
    active: bool = True
