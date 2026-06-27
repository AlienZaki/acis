"""ACIS command-line interface.

Commands
--------
acis start [--name NAME]     Capture from local mic, stream to Voxtral, print cues.
acis serve [--host H --port P]  Start the WebSocket server (app mode).
acis sessions                List stored sessions.
acis show <session_id>       Print a session's transcript, cues, and summary.

In ``start`` mode the laptop mic feeds Voxtral in 3-second chunks.  All events
are printed to stdout — no phone required.  Press Ctrl-C to stop and trigger the
end-of-session AI summary.
"""

from __future__ import annotations

import argparse
import asyncio
import io
import sys
import wave

# ── Audio helpers ──────────────────────────────────────────────────────────────


def _to_wav_bytes(audio, sample_rate: int) -> bytes:
    """Convert float32 mono numpy array to WAV bytes (16-bit PCM)."""
    import numpy as np

    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        pcm = (audio * 32767).clip(-32767, 32767).astype(np.int16)
        wf.writeframes(pcm.tobytes())
    return buf.getvalue()


def _record_chunk(sample_rate: int, chunk_secs: float) -> bytes:
    """Blocking: record one chunk from the default mic and return WAV bytes."""
    import sounddevice as sd

    chunk_samples = int(sample_rate * chunk_secs)
    audio = sd.rec(chunk_samples, samplerate=sample_rate, channels=1, dtype="float32")
    sd.wait()
    return _to_wav_bytes(audio, sample_rate)


# ── ConsoleBus — prints events to stdout instead of broadcasting over WS ──────


class ConsoleBus:
    async def broadcast(self, event: dict) -> None:
        t = event.get("type", "")
        if t == "session.started":
            print(f"\n[session started] id={event['session_id']}  name={event['name']}", flush=True)
        elif t == "transcript.delta":
            print(f"  {event['text']}", flush=True)
        elif t == "cue.new":
            cue_type = event["cue_type"].upper()
            print(f"\n  ▶ [{cue_type}] {event['title']}\n    {event['body']}\n", flush=True)
        elif t == "session.stopped":
            print("\n[session stopped] Generating summary…", flush=True)
        elif t == "summary.ready":
            _print_summary(event)
        elif t == "error":
            print(f"[error] {event['message']}", file=sys.stderr, flush=True)


def _print_summary(event: dict) -> None:
    print(f"\n{'=' * 60}")
    print(f"  {event['title']}")
    print(f"{'=' * 60}")
    print(f"\n{event['prose']}\n")
    for kp in event.get("keypoints", []):
        print(f"  {kp.get('heading', '')}")
        for b in kp.get("bullets", []):
            print(f"    • {b}")
    if event.get("action_items"):
        print("\n  Action items:")
        for item in event["action_items"]:
            print(f"    ☐ {item}")
    print()


# ── Commands ──────────────────────────────────────────────────────────────────


async def _cmd_start(name: str | None) -> None:
    from .application.session_context import SessionContext
    from .settings import settings
    from .settings.injection import build_services

    bus = ConsoleBus()
    svc = build_services(bus=bus)  # type: ignore[arg-type]

    session = await svc.start.execute(name=name)
    sctx = SessionContext(session=session)

    print("Listening on mic — press Ctrl-C to stop.\n", flush=True)

    try:
        while True:
            wav_bytes = await asyncio.to_thread(
                _record_chunk,
                settings.ACIS_AUDIO_SAMPLE_RATE,
                settings.ACIS_AUDIO_CHUNK_SECS,
            )
            should_extract = await svc.process.execute(sctx, wav_bytes)
            if should_extract:
                await svc.extract.execute(sctx)
    except KeyboardInterrupt:
        pass

    await svc.stop.execute(sctx.session)
    # Allow the background summary task to complete.
    await asyncio.sleep(1)
    await asyncio.gather(*asyncio.all_tasks() - {asyncio.current_task()}, return_exceptions=True)


def _cmd_sessions() -> None:
    from .settings.injection import build_repository

    repo = build_repository()
    sessions = repo.list_sessions()
    if not sessions:
        print("No sessions stored.")
        return
    for s in sessions:
        ended = s.ended_at.strftime("%H:%M") if s.ended_at else "ongoing"
        print(f"  {s.id[:8]}…  {s.started_at.strftime('%Y-%m-%d %H:%M')} → {ended}  {s.name}")


def _cmd_show(session_id: str) -> None:
    from .settings.injection import build_repository

    repo = build_repository()
    session = repo.get_session(session_id)
    if session is None:
        # Try prefix match
        for s in repo.list_sessions():
            if s.id.startswith(session_id):
                session = s
                session_id = s.id
                break
    if session is None:
        print(f"Session {session_id!r} not found.")
        return

    print(f"\n{'=' * 60}")
    print(f"  {session.name}")
    print(f"  {session.started_at.strftime('%Y-%m-%d %H:%M')}")
    print(f"{'=' * 60}\n")

    utterances = repo.get_utterances(session_id)
    if utterances:
        print("TRANSCRIPT\n")
        for u in utterances:
            print(f"  [{u.t_start:.0f}s]  {u.text}")

    cues = repo.get_cues(session_id)
    if cues:
        print("\nCUES\n")
        for c in cues:
            print(f"  [{c.cue_type.upper()}] {c.title}")
            print(f"    {c.body}\n")

    summary = repo.get_summary(session_id)
    if summary:
        _print_summary(
            {
                "title": summary.title,
                "prose": summary.prose,
                "keypoints": summary.keypoints,
                "action_items": summary.action_items,
            }
        )


def _cmd_serve(host: str | None, port: int | None) -> None:
    import sys

    from .infrastructure.input_interfaces.ws.app import main as serve_main

    if host:
        sys.argv = ["acis-serve", "--host", host]
    if port:
        sys.argv = [*sys.argv, "--port", str(port)]
    serve_main()


# ── Entrypoint ────────────────────────────────────────────────────────────────


def main() -> None:
    ap = argparse.ArgumentParser(prog="acis", description="Ambient Conversation Intelligence System")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_start = sub.add_parser("start", help="Start a session (local mic capture)")
    p_start.add_argument("--name", default=None, help="Session name")

    sub.add_parser("sessions", help="List stored sessions")

    p_show = sub.add_parser("show", help="Show a stored session (prefix of session_id is fine)")
    p_show.add_argument("session_id")

    p_serve = sub.add_parser("serve", help="Start the WebSocket server (app mode)")
    p_serve.add_argument("--host", default=None)
    p_serve.add_argument("--port", type=int, default=None)

    args = ap.parse_args()

    if args.cmd == "start":
        asyncio.run(_cmd_start(args.name))
    elif args.cmd == "sessions":
        _cmd_sessions()
    elif args.cmd == "show":
        _cmd_show(args.session_id)
    elif args.cmd == "serve":
        _cmd_serve(getattr(args, "host", None), getattr(args, "port", None))


if __name__ == "__main__":
    main()
