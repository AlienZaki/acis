package ai.acis.ui

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.core.tween
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.MenuBook
import androidx.compose.material.icons.filled.Person
import androidx.compose.material.icons.filled.QuestionMark
import androidx.compose.material.icons.outlined.Lightbulb
import androidx.compose.material3.Icon
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import ai.acis.Cue
import ai.acis.UiState
import kotlinx.coroutines.delay

// Monochrome-green HUD, approximating a single-colour smart-glasses lens display.
private val LensGreen = Color(0xFF3BFF4A)
/** Seconds a cue stays on the lens, from the "Cue duration" setting. */
private fun cueSeconds(cue: Cue, setting: String): Int = when (setting) {
    "3" -> 3
    "5" -> 5
    "8" -> 8
    else -> (3 + cue.body.split(" ").size / 10).coerceIn(3, 8) // "auto" — scale with body length
}

/**
 * Simulates how the live session would render in the glasses' in-lens HUD:
 * a black field with a faint dot-matrix grid, a live caption, and AI cues that
 * surface in a bordered card — icon + title + "Close in Ns" countdown — then
 * fade away. Ephemeral, rather than the app's persistent chip list.
 *
 * Respects the glasses-interface settings: AI cues / live transcription toggles,
 * auto pop-up (full card vs compact), and cue duration.
 */
@Composable
fun LensSimulationView(ui: UiState, modifier: Modifier = Modifier) {
    // Surface the newest cue, count it down, then let it fade out.
    var activeCue by remember { mutableStateOf<Cue?>(null) }
    var remainingSec by remember { mutableIntStateOf(0) }
    val latestCueId = ui.cues.lastOrNull()?.cueId
    LaunchedEffect(latestCueId, ui.glassesAiCues, ui.cueDuration) {
        if (latestCueId != null && ui.glassesAiCues) {
            val cue = ui.cues.last()
            activeCue = cue
            var t = cueSeconds(cue, ui.cueDuration)
            remainingSec = t
            while (t > 0) {
                delay(1000)
                t--
                remainingSec = t
            }
            activeCue = null
        } else {
            activeCue = null
        }
    }

    val sessionActive = ui.listening || ui.sessionId != null
    val caption = when {
        !ui.glassesLiveTranscription -> ""
        else -> ui.segments.takeLast(2).joinToString(" ") { it.text }.ifBlank {
            if (sessionActive) "Listening…" else "Start a session to preview the lens."
        }
    }

    Box(modifier = modifier.fillMaxSize().background(Color.Black)) {
        DotGrid()

        Column(modifier = Modifier.fillMaxSize().padding(20.dp)) {
            Spacer(Modifier.height(24.dp))

            // Ephemeral cue card — fades in on arrival, fades out at end of countdown.
            AnimatedVisibility(
                visible = activeCue != null,
                enter = fadeIn(tween(200)),
                exit = fadeOut(tween(500)),
            ) {
                activeCue?.let { cue -> LensCueCard(cue, remainingSec, expanded = ui.autoPopup) }
            }

            Spacer(Modifier.weight(1f))

            // Live caption — left-aligned, larger, like real glasses captions.
            if (caption.isNotEmpty()) {
                Text(
                    caption,
                    color = LensGreen,
                    fontFamily = FontFamily.Monospace,
                    fontSize = 17.sp,
                    lineHeight = 24.sp,
                    fontWeight = FontWeight.Medium,
                    modifier = Modifier.fillMaxWidth(),
                )
            }

            Spacer(Modifier.weight(0.9f))
        }
    }
}

/** Faint green dot-matrix, evoking the reference HUD's grid field. */
@Composable
private fun DotGrid() {
    Canvas(Modifier.fillMaxSize()) {
        val step = 16.dp.toPx()
        val r = 1.1.dp.toPx()
        val dot = LensGreen.copy(alpha = 0.10f)
        var y = step
        while (y < size.height) {
            var x = step
            while (x < size.width) {
                drawCircle(dot, r, Offset(x, y))
                x += step
            }
            y += step
        }
    }
}

@Composable
private fun LensCueCard(cue: Cue, remainingSec: Int, expanded: Boolean) {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .border(1.5.dp, LensGreen, RoundedCornerShape(10.dp))
            .padding(horizontal = 14.dp, vertical = 12.dp),
    ) {
        // Header: icon + title (left), "Close in Ns" countdown (right).
        Row(verticalAlignment = Alignment.CenterVertically) {
            Icon(
                cueIcon(cue.cueType),
                contentDescription = null,
                tint = LensGreen,
                modifier = Modifier.size(20.dp),
            )
            Spacer(Modifier.width(10.dp))
            Text(
                cue.title,
                color = LensGreen,
                fontFamily = FontFamily.Monospace,
                fontSize = 17.sp,
                fontWeight = FontWeight.SemiBold,
                modifier = Modifier.weight(1f),
                maxLines = 2,
                overflow = TextOverflow.Ellipsis,
            )
            Spacer(Modifier.width(8.dp))
            Text(
                "Close in ${remainingSec}s",
                color = LensGreen,
                fontFamily = FontFamily.Monospace,
                fontSize = 14.sp,
            )
        }

        if (expanded && cue.body.isNotBlank()) {
            Spacer(Modifier.height(8.dp))
            Text(
                cue.body,
                color = LensGreen,
                fontFamily = FontFamily.Monospace,
                fontSize = 15.sp,
                lineHeight = 22.sp,
                modifier = Modifier.padding(start = 30.dp),
            )
        }
    }
}

private fun cueIcon(type: String): ImageVector = when (type) {
    "concept"    -> Icons.AutoMirrored.Filled.MenuBook
    "answer"     -> Icons.Default.QuestionMark
    "suggestion" -> Icons.Outlined.Lightbulb
    "bio"        -> Icons.Default.Person
    else         -> Icons.Default.QuestionMark
}
