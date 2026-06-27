"""WebSocket transport — the brain's front door.

Connection lifecycle:
  hello → session.start → [audio.chunk]* → session.stop → summary.ready (async)

The ``WebSocketEventBus`` is a lightweight broadcast ring: all connected clients
receive every outbound event so a laptop and a phone can both observe the same
session simultaneously.

Run:
    uv run acis-serve
    # or
    uv run python -m acis serve
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from dataclasses import dataclass, field

from pydantic import BaseModel

from .... import protocol
from ....settings.injection import build_services
from .router import ConnCtx, Services, dispatch

# ── Event bus ────────────────────────────────────────────────────────────────


@dataclass
class WebSocketEventBus:
    """Thread-safe broadcast bus backed by a set of live WebSocket connections."""

    _clients: set = field(default_factory=set, init=False, repr=False)

    def add(self, ws) -> None:
        self._clients.add(ws)

    def remove(self, ws) -> None:
        self._clients.discard(ws)

    async def broadcast(self, event: dict) -> None:
        if not self._clients:
            return
        raw = json.dumps(event)
        await asyncio.gather(*(c.send(raw) for c in list(self._clients)), return_exceptions=True)


# ── Connection handler ────────────────────────────────────────────────────────


async def handle_connection(ws, *, services: Services, bus: WebSocketEventBus) -> None:
    bus.add(ws)
    ctx = ConnCtx()

    try:
        async for raw in ws:
            msg = protocol.parse_inbound(raw)
            if msg is None:
                continue
            async for out in dispatch(ctx, services, msg):
                if isinstance(out, BaseModel):
                    await ws.send(json.dumps(out.model_dump()))
    finally:
        bus.remove(ws)
        # If the client disconnects mid-session, stop gracefully.
        if ctx.current is not None:
            try:
                await services.stop.execute(ctx.current.session)
            except Exception as exc:
                print(f"[ws] disconnect cleanup failed: {exc}", file=sys.stderr)


# ── Server entrypoint ─────────────────────────────────────────────────────────


async def serve(host: str, port: int, *, services: Services, bus: WebSocketEventBus) -> None:
    import websockets

    async def handler(ws):
        await handle_connection(ws, services=services, bus=bus)

    async with websockets.serve(handler, host, port):
        print(f"acis serve → ws://{host}:{port}", flush=True)
        await asyncio.Future()  # run forever


def main() -> None:
    ap = argparse.ArgumentParser(prog="acis-serve", description="ACIS WebSocket brain")
    ap.add_argument("--host", default=None)
    ap.add_argument("--port", type=int, default=None)
    args = ap.parse_args()

    from ....settings import settings

    host = args.host or settings.ACIS_SERVE_HOST
    port = args.port or settings.ACIS_SERVE_PORT

    bus = WebSocketEventBus()
    services = build_services(bus=bus)
    asyncio.run(serve(host, port, services=services, bus=bus))


if __name__ == "__main__":
    main()
