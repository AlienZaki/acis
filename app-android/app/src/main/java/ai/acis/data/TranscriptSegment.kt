package ai.acis.data

import kotlinx.serialization.Serializable

@Serializable
data class TranscriptSegment(val tStart: Float, val text: String)
