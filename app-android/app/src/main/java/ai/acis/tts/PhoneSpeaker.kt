package ai.acis.tts

import android.content.Context
import android.speech.tts.TextToSpeech
import android.speech.tts.UtteranceProgressListener
import java.util.Locale
import java.util.concurrent.LinkedBlockingQueue

class PhoneSpeaker(context: Context) {

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
            queue.poll()
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
        tts?.speak(text, TextToSpeech.QUEUE_ADD, null, "acis-cue")
    }

    private val utteranceListener = object : UtteranceProgressListener() {
        override fun onStart(utteranceId: String?) {}
        override fun onDone(utteranceId: String?) = drainQueue()
        @Deprecated("Deprecated in API 21")
        override fun onError(utteranceId: String?) = drainQueue()
        override fun onError(utteranceId: String?, errorCode: Int) = drainQueue()
    }
}
