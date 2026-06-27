package ai.acis.brain

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.Json
import kotlinx.serialization.json.JsonElement

val AcisJson = Json { ignoreUnknownKeys = true; encodeDefaults = true }

// ── Outbound (app → brain) ────────────────────────────────────────────────

@Serializable
data class Hello(val type: String = "hello")

@Serializable
data class SessionStart(
    val type: String = "session.start",
    val name: String? = null,
)

@Serializable
data class SessionStop(val type: String = "session.stop")

@Serializable
data class AudioChunk(
    val type: String = "audio.chunk",
    @SerialName("data_b64") val dataB64: String,
    @SerialName("sample_rate") val sampleRate: Int = 16000,
)

@Serializable
data class Ping(val type: String = "ping")

// ── Inbound (brain → app) ─────────────────────────────────────────────────

@Serializable
data class Inbound(
    val type: String = "",
    @SerialName("session_id") val sessionId: String? = null,
    val name: String? = null,
    @SerialName("started_at") val startedAt: String? = null,
    val text: String? = null,
    @SerialName("t_start") val tStart: Float? = null,
    @SerialName("t_end") val tEnd: Float? = null,
    @SerialName("cue_id") val cueId: String? = null,
    @SerialName("cue_type") val cueType: String? = null,
    val title: String? = null,
    val body: String? = null,
    val prose: String? = null,
    val keypoints: List<Map<String, JsonElement>>? = null,
    @SerialName("action_items") val actionItems: List<String>? = null,
    val message: String? = null,
)
