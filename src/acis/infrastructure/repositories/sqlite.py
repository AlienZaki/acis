"""SQLite persistence via SQLModel.

``SQLiteSessionRepository`` implements both ``SessionRepository`` and
``PrepNoteRepository`` ports behind a single engine.
"""

from __future__ import annotations

import json
from pathlib import Path

from sqlmodel import Session as DBSession, SQLModel, create_engine, select

from ...domain.entities import AISummary, Cue, PrepNote, Session, Utterance
from .models import CueORM, PrepNoteORM, SessionORM, UtteranceORM


class SQLiteSessionRepository:
    def __init__(self, db_path: str | Path = "~/.acis/acis.db") -> None:
        path = Path(db_path).expanduser()
        path.parent.mkdir(parents=True, exist_ok=True)
        self._engine = create_engine(f"sqlite:///{path}", echo=False)
        SQLModel.metadata.create_all(self._engine)

    # ── Sessions ──

    def save_session(self, session: Session) -> None:
        with DBSession(self._engine) as db:
            orm = db.get(SessionORM, session.id)
            if orm is None:
                db.add(SessionORM(
                    id=session.id, name=session.name, started_at=session.started_at, ended_at=session.ended_at
                ))
            else:
                orm.name = session.name
                orm.ended_at = session.ended_at
            db.commit()

    def get_session(self, session_id: str) -> Session | None:
        with DBSession(self._engine) as db:
            orm = db.get(SessionORM, session_id)
            if orm is None:
                return None
            return Session(id=orm.id, name=orm.name, started_at=orm.started_at, ended_at=orm.ended_at)

    def list_sessions(self) -> list[Session]:
        with DBSession(self._engine) as db:
            rows = db.exec(select(SessionORM).order_by(SessionORM.started_at.desc())).all()  # ty: ignore[arg-type]
            return [Session(id=r.id, name=r.name, started_at=r.started_at, ended_at=r.ended_at) for r in rows]

    # ── Utterances ──

    def save_utterance(self, utterance: Utterance, session_id: str) -> None:
        with DBSession(self._engine) as db:
            db.add(UtteranceORM(
                session_id=session_id, text=utterance.text, t_start=utterance.t_start, t_end=utterance.t_end
            ))
            db.commit()

    def get_utterances(self, session_id: str) -> list[Utterance]:
        with DBSession(self._engine) as db:
            rows = db.exec(
                select(UtteranceORM)
                .where(UtteranceORM.session_id == session_id)
                .order_by(UtteranceORM.t_start)
            ).all()
            return [Utterance(text=r.text, t_start=r.t_start, t_end=r.t_end) for r in rows]

    # ── Cues ──

    def save_cue(self, cue: Cue) -> None:
        with DBSession(self._engine) as db:
            db.add(
                CueORM(
                    id=cue.id,
                    session_id=cue.session_id,
                    cue_type=cue.cue_type,
                    title=cue.title,
                    body=cue.body,
                    spoken_through_glasses=cue.spoken_through_glasses,
                )
            )
            db.commit()

    def get_cues(self, session_id: str) -> list[Cue]:
        with DBSession(self._engine) as db:
            rows = db.exec(select(CueORM).where(CueORM.session_id == session_id)).all()
            return [
                Cue(  # ty: ignore[arg-type]
                    id=r.id, cue_type=r.cue_type, title=r.title, body=r.body,
                    session_id=r.session_id, spoken_through_glasses=r.spoken_through_glasses,
                )
                for r in rows
            ]

    # ── Summaries (stored inside SessionORM.summary_json) ──

    def save_summary(self, summary: AISummary) -> None:
        with DBSession(self._engine) as db:
            orm = db.get(SessionORM, summary.session_id)
            if orm is not None:
                orm.summary_json = json.dumps(
                    {
                        "title": summary.title,
                        "prose": summary.prose,
                        "keypoints": summary.keypoints,
                        "action_items": summary.action_items,
                    }
                )
                db.commit()

    def get_summary(self, session_id: str) -> AISummary | None:
        with DBSession(self._engine) as db:
            orm = db.get(SessionORM, session_id)
            if orm is None or orm.summary_json is None:
                return None
            data = json.loads(orm.summary_json)
            return AISummary(session_id=session_id, **data)

    # ── Prep notes ──

    def save(self, note: PrepNote) -> None:
        with DBSession(self._engine) as db:
            orm = db.get(PrepNoteORM, note.id)
            if orm is None:
                db.add(PrepNoteORM(id=note.id, title=note.title, body=note.body, active=note.active))
            else:
                orm.title = note.title
                orm.body = note.body
                orm.active = note.active
            db.commit()

    def list_active(self) -> list[PrepNote]:
        with DBSession(self._engine) as db:
            rows = db.exec(select(PrepNoteORM).where(PrepNoteORM.active == True)).all()  # noqa: E712
            return [PrepNote(id=r.id, title=r.title, body=r.body, active=r.active) for r in rows]

    def delete(self, note_id: str) -> None:
        with DBSession(self._engine) as db:
            orm = db.get(PrepNoteORM, note_id)
            if orm is not None:
                db.delete(orm)
                db.commit()
