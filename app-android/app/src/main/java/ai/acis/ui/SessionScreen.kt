package ai.acis.ui

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import ai.acis.AcisViewModel
import ai.acis.Cue

@Composable
fun SessionScreen(vm: AcisViewModel) {
    val ui by vm.ui.collectAsStateWithLifecycle()

    Scaffold { padding ->
        Column(modifier = Modifier.fillMaxSize().padding(padding)) {

            // Status strip
            Surface(color = MaterialTheme.colorScheme.surfaceVariant) {
                Row(
                    modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 10.dp),
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    Badge(
                        containerColor = if (ui.connected) MaterialTheme.colorScheme.tertiary
                        else MaterialTheme.colorScheme.error
                    )
                    Spacer(Modifier.width(8.dp))
                    Text(ui.status, style = MaterialTheme.typography.labelMedium)
                    if (ui.listening) {
                        Spacer(Modifier.weight(1f))
                        Text("● REC", color = MaterialTheme.colorScheme.error,
                            style = MaterialTheme.typography.labelSmall)
                    }
                }
            }

            // Scrollable content
            LazyColumn(modifier = Modifier.weight(1f).padding(horizontal = 16.dp, vertical = 8.dp)) {

                if (ui.transcript.isNotBlank()) {
                    item {
                        SectionLabel("TRANSCRIPT")
                        Text(
                            ui.transcript,
                            style = MaterialTheme.typography.bodySmall.copy(fontFamily = FontFamily.Monospace),
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                        )
                        Spacer(Modifier.height(16.dp))
                    }
                }

                if (ui.cues.isNotEmpty()) {
                    item { SectionLabel("AI CUES (${ui.cues.size})") }
                    items(ui.cues, key = { it.cueId }) { cue ->
                        CueCard(cue)
                        Spacer(Modifier.height(8.dp))
                    }
                }

                if (ui.summaryProse.isNotBlank()) {
                    item {
                        Spacer(Modifier.height(8.dp))
                        SectionLabel("SESSION SUMMARY")
                        Text(ui.summaryTitle, style = MaterialTheme.typography.titleMedium)
                        Spacer(Modifier.height(4.dp))
                        Text(ui.summaryProse, style = MaterialTheme.typography.bodyMedium)
                        if (ui.summaryActionItems.isNotEmpty()) {
                            Spacer(Modifier.height(8.dp))
                            Text("Action items", style = MaterialTheme.typography.labelSmall)
                            ui.summaryActionItems.forEach { item ->
                                Text("• $item", style = MaterialTheme.typography.bodySmall)
                            }
                        }
                    }
                }

                item { Spacer(Modifier.height(16.dp)) }
            }

            // Bottom controls
            Surface(shadowElevation = 8.dp) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Text("Speak cues via glasses", modifier = Modifier.weight(1f),
                            style = MaterialTheme.typography.bodyMedium)
                        Switch(checked = ui.speakCues, onCheckedChange = vm::setSpeakCues)
                    }
                    Spacer(Modifier.height(12.dp))
                    Button(
                        onClick = { if (ui.listening) vm.stopSession() else vm.startSession() },
                        enabled = ui.connected || ui.listening,
                        modifier = Modifier.fillMaxWidth().height(52.dp),
                        colors = ButtonDefaults.buttonColors(
                            containerColor = if (ui.listening) MaterialTheme.colorScheme.error
                            else MaterialTheme.colorScheme.primary,
                        ),
                    ) {
                        Text(
                            if (ui.listening) "Stop Session" else "Start Session",
                            style = MaterialTheme.typography.titleSmall,
                        )
                    }
                }
            }
        }
    }
}

@Composable
private fun SectionLabel(text: String) {
    Text(
        text,
        style = MaterialTheme.typography.labelSmall,
        color = MaterialTheme.colorScheme.outline,
        modifier = Modifier.padding(bottom = 4.dp),
    )
}

@Composable
private fun CueCard(cue: Cue) {
    val icon = when (cue.cueType) {
        "concept"    -> "💡"
        "answer"     -> "❓"
        "suggestion" -> "✨"
        "bio"        -> "👤"
        else         -> "•"
    }
    Card(modifier = Modifier.fillMaxWidth()) {
        Column(modifier = Modifier.padding(12.dp)) {
            Text(
                "$icon ${cue.title}",
                style = MaterialTheme.typography.titleSmall,
            )
            Spacer(Modifier.height(4.dp))
            Text(
                cue.body,
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
        }
    }
}
