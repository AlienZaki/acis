package ai.acis

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import ai.acis.audio.MicCapture
import ai.acis.brain.AcisBrainClient
import ai.acis.tts.GlassesSpeaker
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.update

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
    val listening: Boolean = false,
    val transcript: String = "",
    val cues: List<Cue> = emptyList(),
    val summaryTitle: String = "",
    val summaryProse: String = "",
    val summaryActionItems: List<String> = emptyList(),
    val speakCues: Boolean = true,
    val brainUrl: String = BuildConfig.BRAIN_URL,
)

class AcisViewModel(app: Application) : AndroidViewModel(app) {

    private val _ui = MutableStateFlow(UiState())
    val ui: StateFlow<UiState> = _ui

    private var client: AcisBrainClient? = null
    private var mic: MicCapture? = null
    private val speaker = GlassesSpeaker(app)

    fun connect() {
        client?.disconnect()
        client = AcisBrainClient(_ui.value.brainUrl).also { c ->
            c.listener = brainListener
            c.connect()
        }
        _ui.update { it.copy(status = "connecting…") }
    }

    fun startSession(name: String? = null) {
        client?.startSession(name)
        mic = MicCapture { b64 -> client?.sendAudioChunk(b64) }.also { it.start() }
        _ui.update { it.copy(listening = true, transcript = "", cues = emptyList(), summaryProse = "") }
    }

    fun stopSession() {
        mic?.stop(); mic = null
        client?.stopSession()
        _ui.update { it.copy(listening = false) }
    }

    fun setSpeakCues(v: Boolean) = _ui.update { it.copy(speakCues = v) }
    fun setBrainUrl(url: String) = _ui.update { it.copy(brainUrl = url) }

    override fun onCleared() {
        mic?.stop()
        client?.disconnect()
        speaker.shutdown()
    }

    private val brainListener = object : AcisBrainClient.Listener {
        override fun onConnected(ok: Boolean, status: String) =
            _ui.update { it.copy(connected = ok, status = status) }

        override fun onSessionStarted(sessionId: String, name: String) =
            _ui.update { it.copy(sessionId = sessionId) }

        override fun onTranscriptDelta(sessionId: String, text: String, tStart: Float) =
            _ui.update { it.copy(transcript = it.transcript + if (it.transcript.isEmpty()) text else " $text") }

        override fun onCueNew(sessionId: String, cueId: String, cueType: String, title: String, body: String) {
            val cue = Cue(cueId, cueType, title, body)
            _ui.update { it.copy(cues = it.cues + cue) }
            if (_ui.value.speakCues) {
                val label = cueType.replaceFirstChar { it.uppercaseChar() }
                val snippet = body.split(Regex("(?<=[.!?])\\s+")).firstOrNull() ?: body
                speaker.speak("$label: $title. $snippet")
            }
        }

        override fun onSummaryReady(sessionId: String, title: String, prose: String, actionItems: List<String>) =
            _ui.update { it.copy(summaryTitle = title, summaryProse = prose, summaryActionItems = actionItems) }

        override fun onError(message: String) =
            _ui.update { it.copy(status = "error: $message") }
    }
}
