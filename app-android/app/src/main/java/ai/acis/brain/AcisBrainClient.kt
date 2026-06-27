package ai.acis.brain

import android.util.Log
import kotlinx.serialization.encodeToString
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.Response
import okhttp3.WebSocket
import okhttp3.WebSocketListener
import java.util.concurrent.TimeUnit

private const val TAG = "AcisBrain"

class AcisBrainClient(private val url: String) {

    interface Listener {
        fun onConnected(ok: Boolean, status: String)
        fun onSessionStarted(sessionId: String, name: String)
        fun onTranscriptDelta(sessionId: String, text: String, tStart: Float)
        fun onCueNew(sessionId: String, cueId: String, cueType: String, title: String, body: String)
        fun onSummaryReady(sessionId: String, title: String, prose: String, actionItems: List<String>)
        fun onError(message: String)
    }

    var listener: Listener? = null

    private val http = OkHttpClient.Builder()
        .connectTimeout(10, TimeUnit.SECONDS)
        .readTimeout(0, TimeUnit.SECONDS)  // keep-alive
        .build()

    private var ws: WebSocket? = null
    private var closed = false

    fun connect() {
        closed = false
        ws = http.newWebSocket(Request.Builder().url(url).build(), socketListener)
    }

    fun disconnect() {
        closed = true
        ws?.close(1000, null)
        ws = null
    }

    fun startSession(name: String? = null) =
        send(AcisJson.encodeToString(SessionStart(name = name)))

    fun stopSession() = send(AcisJson.encodeToString(SessionStop()))

    fun sendAudioChunk(dataB64: String) =
        send(AcisJson.encodeToString(AudioChunk(dataB64 = dataB64)))

    private fun send(json: String) {
        if (ws?.send(json) == false) Log.w(TAG, "send failed — socket not open")
    }

    private val socketListener = object : WebSocketListener() {
        override fun onOpen(socket: WebSocket, response: Response) {
            socket.send(AcisJson.encodeToString(Hello()))
            listener?.onConnected(false, "authenticating…")
        }

        override fun onMessage(socket: WebSocket, text: String) {
            val msg = runCatching { AcisJson.decodeFromString<Inbound>(text) }.getOrElse {
                Log.w(TAG, "parse error: $it")
                return
            }
            when (msg.type) {
                "hello.ok"         -> listener?.onConnected(true, "connected")
                "session.started"  -> listener?.onSessionStarted(msg.sessionId ?: "", msg.name ?: "")
                "transcript.delta" -> listener?.onTranscriptDelta(
                    msg.sessionId ?: "", msg.text ?: "", msg.tStart ?: 0f
                )
                "cue.new"          -> listener?.onCueNew(
                    msg.sessionId ?: "", msg.cueId ?: "",
                    msg.cueType ?: "", msg.title ?: "", msg.body ?: ""
                )
                "summary.ready"    -> listener?.onSummaryReady(
                    msg.sessionId ?: "", msg.title ?: "",
                    msg.prose ?: "", msg.actionItems ?: emptyList()
                )
                "error"            -> listener?.onError(msg.message ?: "unknown error")
            }
        }

        override fun onFailure(socket: WebSocket, t: Throwable, response: Response?) {
            Log.w(TAG, "WS failure: ${t.message}")
            listener?.onConnected(false, "disconnected: ${t.message}")
            if (!closed) reconnectSoon()
        }

        override fun onClosed(socket: WebSocket, code: Int, reason: String) {
            if (!closed) reconnectSoon()
        }
    }

    private fun reconnectSoon() {
        if (closed) return
        Thread {
            Thread.sleep(2000)
            if (!closed) connect()
        }.start()
    }
}
