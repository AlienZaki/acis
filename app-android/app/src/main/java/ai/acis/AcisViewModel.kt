package ai.acis

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import ai.acis.audio.MicCapture
import ai.acis.brain.AcisBrainClient
import ai.acis.data.AppSettings
import ai.acis.data.HistoryStore
import ai.acis.data.SessionRecord
import ai.acis.data.TranscriptSegment
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.update
import kotlinx.serialization.Serializable

@Serializable
data class Cue(
    val cueId: String,
    val cueType: String,
    val title: String,
    val body: String,
)

data class UiState(
    val connected: Boolean = false,
    val status: String = "disconnected",
    val sessionId: String? = null,
    val sessionName: String = "",
    val listening: Boolean = false,
    val transcript: String = "",
    val segments: List<TranscriptSegment> = emptyList(),
    val cues: List<Cue> = emptyList(),
    val summaryTitle: String = "",
    val summaryProse: String = "",
    val summaryActionItems: List<String> = emptyList(),
    val brainUrl: String = BuildConfig.BRAIN_URL,
    val spokenLanguage: String = "auto",
    val history: List<SessionRecord> = emptyList(),
)

class AcisViewModel(app: Application) : AndroidViewModel(app) {

    private val settings = AppSettings(app)
    private val historyStore = HistoryStore(app)

    private val _ui = MutableStateFlow(
        UiState(
            brainUrl = settings.brainUrl,
            spokenLanguage = settings.spokenLanguage,
            history = historyStore.load(),
        )
    )
    val ui: StateFlow<UiState> = _ui

    private var client: AcisBrainClient? = null
    private var mic: MicCapture? = null
    private var sessionStartedAt: Long = 0L

    fun connect() {
        client?.disconnect()
        client = AcisBrainClient(_ui.value.brainUrl).also { c ->
            c.listener = brainListener
            c.connect()
        }
        _ui.update { it.copy(status = "connecting…") }
    }

    fun startSession(name: String = "") {
        val sessionName = name.ifBlank { "Session" }
        sessionStartedAt = System.currentTimeMillis()
        client?.startSession(sessionName)
        mic = MicCapture { b64 -> client?.sendAudioChunk(b64) }.also { it.start() }
        _ui.update {
            it.copy(
                listening = true,
                sessionName = sessionName,
                transcript = "",
                segments = emptyList(),
                cues = emptyList(),
                summaryTitle = "",
                summaryProse = "",
                summaryActionItems = emptyList(),
            )
        }
    }

    fun stopSession() {
        mic?.stop(); mic = null
        client?.stopSession()
        _ui.update { it.copy(listening = false) }
    }

    fun setBrainUrl(url: String) {
        settings.brainUrl = url
        _ui.update { it.copy(brainUrl = url) }
    }

    fun setSpokenLanguage(code: String) {
        settings.spokenLanguage = code
        _ui.update { it.copy(spokenLanguage = code) }
    }

    fun reconnectWithNewUrl() {
        if (client != null) connect()
    }

    fun clearHistory() {
        historyStore.clear()
        _ui.update { it.copy(history = emptyList()) }
    }

    override fun onCleared() {
        mic?.stop()
        client?.disconnect()
    }

    private val brainListener = object : AcisBrainClient.Listener {
        override fun onConnected(ok: Boolean, status: String) =
            _ui.update { it.copy(connected = ok, status = status) }

        override fun onSessionStarted(sessionId: String, name: String) {
            // Stamp the start time here so sessions started externally (e.g. the
            // fixture-replay tool) also get a correct duration — not now-minus-zero.
            sessionStartedAt = System.currentTimeMillis()
            _ui.update {
                it.copy(
                    sessionId = sessionId,
                    sessionName = name,
                    transcript = "",
                    segments = emptyList(),
                    cues = emptyList(),
                    summaryTitle = "",
                    summaryProse = "",
                    summaryActionItems = emptyList(),
                )
            }
        }

        override fun onTranscriptDelta(sessionId: String, text: String, tStart: Float) {
            val segment = TranscriptSegment(tStart, text)
            _ui.update {
                it.copy(
                    transcript = it.transcript + if (it.transcript.isEmpty()) text else " $text",
                    segments = it.segments + segment,
                )
            }
        }

        override fun onCueNew(sessionId: String, cueId: String, cueType: String, title: String, body: String) {
            val cue = Cue(cueId, cueType, title, body)
            _ui.update { it.copy(cues = it.cues + cue) }
        }

        override fun onSummaryReady(sessionId: String, title: String, prose: String, actionItems: List<String>) {
            val now = System.currentTimeMillis()
            _ui.update { it.copy(summaryTitle = title, summaryProse = prose, summaryActionItems = actionItems) }
            val record = SessionRecord(
                sessionId = sessionId,
                name = _ui.value.sessionName,
                startedAt = sessionStartedAt,
                endedAt = now,
                durationMs = now - sessionStartedAt,
                summaryTitle = title,
                summaryProse = prose,
                actionItems = actionItems,
                cues = _ui.value.cues,
                segments = _ui.value.segments,
            )
            historyStore.save(record)
            _ui.update { it.copy(history = historyStore.load()) }
        }

        override fun onError(message: String) =
            _ui.update { it.copy(status = "error: $message") }
    }
}
