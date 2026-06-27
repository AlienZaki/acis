/**
 * AcisWebSocket — thin wrapper around the native WebSocket that:
 *  - parses every inbound frame as a typed Outbound message
 *  - serialises every Inbound object to JSON before sending
 *  - provides a simple event-listener API (one handler per message type)
 *  - reconnects automatically with exponential back-off
 */

import type { Inbound, Outbound } from "./protocol";

type OutboundHandler<T extends Outbound = Outbound> = (msg: T) => void;
type Handlers = { [K in Outbound["type"]]?: OutboundHandler<Extract<Outbound, { type: K }>> };

const RECONNECT_BASE_MS = 1_000;
const RECONNECT_MAX_MS = 30_000;

export class AcisWebSocket {
  private _url: string;
  private _ws: WebSocket | null = null;
  private _handlers: Handlers = {};
  private _reconnectDelay = RECONNECT_BASE_MS;
  private _stopped = false;

  constructor(url: string) {
    this._url = url;
  }

  /** Register a handler for one outbound message type. */
  on<K extends Outbound["type"]>(type: K, handler: OutboundHandler<Extract<Outbound, { type: K }>>) {
    (this._handlers as Record<string, OutboundHandler>)[type] = handler as OutboundHandler;
    return this;
  }

  connect(): void {
    if (this._stopped) return;
    this._ws = new WebSocket(this._url);

    this._ws.onopen = () => {
      this._reconnectDelay = RECONNECT_BASE_MS;
      this.send({ type: "hello" });
    };

    this._ws.onmessage = (event) => {
      try {
        const msg: Outbound = JSON.parse(event.data as string);
        const handler = (this._handlers as Record<string, OutboundHandler>)[msg.type];
        if (handler) handler(msg as never);
      } catch {
        // malformed frame — skip
      }
    };

    this._ws.onclose = () => {
      if (!this._stopped) {
        setTimeout(() => {
          this._reconnectDelay = Math.min(this._reconnectDelay * 2, RECONNECT_MAX_MS);
          this.connect();
        }, this._reconnectDelay);
      }
    };
  }

  send(msg: Inbound): void {
    if (this._ws?.readyState === WebSocket.OPEN) {
      this._ws.send(JSON.stringify(msg));
    }
  }

  disconnect(): void {
    this._stopped = true;
    this._ws?.close();
  }

  get isConnected(): boolean {
    return this._ws?.readyState === WebSocket.OPEN;
  }
}
