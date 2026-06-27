package ai.acis.tts

import android.content.Context
import android.media.AudioManager
import android.speech.tts.TextToSpeech
import android.speech.tts.UtteranceProgressListener
import java.util.Locale
import java.util.concurrent.LinkedBlockingQueue

/**
 * Queues and speaks cues via Android TTS routed through STREAM_VOICE_CALL so
 * audio follows the Bluetooth SCO/A2DP link to the Ray-Ban open-ear speakers.
 *
 * Queue depth is capped at 3 to avoid a backlog when cues arrive faster than
 * speech speed — the oldest unspoken cue is dropped when the queue is full.
 */
class GlassesSpeaker(context: Context) {

    private val queue = LinkedBlockingQueue<String>(3)
    private var tts: TextToSpeech? = null
    private var ready = false

    init {
        tts = TextToSpeech(context) { status ->
            if (status == TextToSpeech.SUCCESS) {
                tts?.language = Locale.US
                ready = true
                tts?.setOnUtteranceProgressListener(utteranceListener)
                drainQueue()
            }
        }
    }

    fun speak(text: String) {
        if (!queue.offer(text)) {
            queue.poll()  // drop oldest
            queue.offer(text)
        }
        if (ready) drainQueue()
    }

    fun stop() {
        queue.clear()
        tts?.stop()
    }

    fun shutdown() {
        tts?.shutdown()
        tts = null
    }

    private fun drainQueue() {
        val text = queue.poll() ?: return
        val params = android.os.Bundle().apply {
            putInt(TextToSpeech.Engine.KEY_PARAM_STREAM, AudioManager.STREAM_VOICE_CALL)
        }
        tts?.speak(text, TextToSpeech.QUEUE_ADD, params, "acis-cue")
    }

    private val utteranceListener = object : UtteranceProgressListener() {
        override fun onStart(utteranceId: String?) {}
        override fun onDone(utteranceId: String?) = drainQueue()
        @Deprecated("Deprecated in API 21")
        override fun onError(utteranceId: String?) = drainQueue()
        override fun onError(utteranceId: String?, errorCode: Int) = drainQueue()
    }
}
