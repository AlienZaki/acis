package ai.acis.data

import ai.acis.Cue
import kotlinx.serialization.Serializable

@Serializable
data class SessionRecord(
    val sessionId: String,
    val name: String,
    val startedAt: Long = 0L,
    val endedAt: Long,
    val durationMs: Long = 0L,
    val summaryTitle: String,
    val summaryProse: String,
    val actionItems: List<String>,
    val cues: List<Cue> = emptyList(),
    val segments: List<TranscriptSegment> = emptyList(),
)
