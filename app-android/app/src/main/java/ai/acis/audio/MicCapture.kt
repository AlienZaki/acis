package ai.acis.audio

import android.annotation.SuppressLint
import android.media.AudioFormat
import android.media.AudioRecord
import android.media.MediaRecorder
import android.util.Base64
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.launch
import java.io.ByteArrayOutputStream
import java.io.DataOutputStream
import java.nio.ByteBuffer
import java.nio.ByteOrder

/**
 * Captures 3-second WAV chunks from the phone mic using VOICE_COMMUNICATION
 * source so the OS applies AEC/NR — important when glasses speakers are active.
 * Each chunk is delivered as a base64-encoded WAV string (16-bit PCM, 16 kHz mono).
 */
class MicCapture(private val onChunk: (base64Wav: String) -> Unit) {

    private val SAMPLE_RATE = 16_000
    private val CHUNK_SAMPLES = SAMPLE_RATE * 3  // 3 seconds
    private val BUFFER_SIZE = maxOf(
        AudioRecord.getMinBufferSize(SAMPLE_RATE, AudioFormat.CHANNEL_IN_MONO, AudioFormat.ENCODING_PCM_16BIT),
        CHUNK_SAMPLES * 2,
    )

    private var job: Job? = null
    private var recorder: AudioRecord? = null

    @SuppressLint("MissingPermission")
    fun start() {
        job = CoroutineScope(Dispatchers.IO).launch {
            val rec = AudioRecord(
                MediaRecorder.AudioSource.VOICE_COMMUNICATION,
                SAMPLE_RATE,
                AudioFormat.CHANNEL_IN_MONO,
                AudioFormat.ENCODING_PCM_16BIT,
                BUFFER_SIZE,
            ).also { recorder = it; it.startRecording() }

            val pcm = ShortArray(CHUNK_SAMPLES)
            while (job?.isActive == true) {
                var offset = 0
                while (offset < CHUNK_SAMPLES && job?.isActive == true) {
                    val n = rec.read(pcm, offset, CHUNK_SAMPLES - offset)
                    if (n > 0) offset += n
                }
                if (offset == CHUNK_SAMPLES) {
                    onChunk(encodeWavBase64(pcm))
                }
            }
        }
    }

    fun stop() {
        job?.cancel()
        job = null
        recorder?.stop()
        recorder?.release()
        recorder = null
    }

    private fun encodeWavBase64(pcm: ShortArray): String {
        val numBytes = pcm.size * 2
        val out = ByteArrayOutputStream(44 + numBytes)
        DataOutputStream(out).apply {
            write("RIFF".toByteArray())
            writeIntLE(36 + numBytes)
            write("WAVE".toByteArray())
            write("fmt ".toByteArray())
            writeIntLE(16)
            writeShortLE(1)           // PCM
            writeShortLE(1)           // mono
            writeIntLE(SAMPLE_RATE)
            writeIntLE(SAMPLE_RATE * 2)
            writeShortLE(2)           // block align
            writeShortLE(16)          // bits per sample
            write("data".toByteArray())
            writeIntLE(numBytes)
            val buf = ByteBuffer.allocate(numBytes).order(ByteOrder.LITTLE_ENDIAN)
            for (s in pcm) buf.putShort(s)
            write(buf.array())
        }
        return Base64.encodeToString(out.toByteArray(), Base64.NO_WRAP)
    }

    private fun DataOutputStream.writeIntLE(v: Int) =
        write(ByteBuffer.allocate(4).order(ByteOrder.LITTLE_ENDIAN).putInt(v).array())

    private fun DataOutputStream.writeShortLE(v: Int) =
        write(ByteBuffer.allocate(2).order(ByteOrder.LITTLE_ENDIAN).putShort(v.toShort()).array())
}
