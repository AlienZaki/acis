package ai.acis.ui

import android.content.Intent
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.Article
import androidx.compose.material.icons.filled.*
import androidx.compose.material.icons.outlined.Lightbulb
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import ai.acis.AcisViewModel
import ai.acis.Cue

private data class CueSectionDef(val type: String, val label: String, val icon: ImageVector)

private val LIVE_CUE_SECTIONS = listOf(
    CueSectionDef("concept",    "Concepts",    Icons.AutoMirrored.Filled.Article),
    CueSectionDef("answer",     "Answers",     Icons.Default.QuestionAnswer),
    CueSectionDef("suggestion", "Suggestions", Icons.Outlined.Lightbulb),
    CueSectionDef("bio",        "Bios",        Icons.Default.Person),
)

private fun cueIcon(type: String): ImageVector = when (type) {
    "concept"    -> Icons.AutoMirrored.Filled.Article
    "answer"     -> Icons.Default.QuestionAnswer
    "suggestion" -> Icons.Outlined.Lightbulb
    "bio"        -> Icons.Default.Person
    else         -> Icons.Default.Info
}

@OptIn(ExperimentalMaterial3Api::class, ExperimentalLayoutApi::class)
@Composable
fun SessionScreen(vm: AcisViewModel, outerPadding: PaddingValues = PaddingValues()) {
    val ui by vm.ui.collectAsStateWithLifecycle()
    val context = LocalContext.current
    var cueModal by remember { mutableStateOf<Cue?>(null) }

    cueModal?.let { cue ->
        AlertDialog(
            onDismissRequest = { cueModal = null },
            icon = { Icon(cueIcon(cue.cueType), contentDescription = null) },
            title = { Text(cue.title) },
            text = { Text(cue.body) },
            confirmButton = {
                TextButton(onClick = { cueModal = null }) { Text("Dismiss") }
            },
        )
    }

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
                        Text(
                            "● REC",
                            color = MaterialTheme.colorScheme.error,
                            style = MaterialTheme.typography.labelSmall,
                        )
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

                // Cues grouped by type with chip layout
                if (ui.cues.isNotEmpty()) {
                    item {
                        SectionLabel("AI CUES (${ui.cues.size})")
                        Spacer(Modifier.height(4.dp))
                    }
                    LIVE_CUE_SECTIONS.forEach { sec ->
                        val cuesOfType = ui.cues.filter { it.cueType == sec.type }
                        if (cuesOfType.isNotEmpty()) {
                            item(key = "cueSec_${sec.type}") {
                                LiveCueSection(
                                    sec = sec,
                                    cues = cuesOfType,
                                    onCueClick = { cueModal = it },
                                )
                            }
                        }
                    }
                }

                if (ui.summaryProse.isNotBlank()) {
                    item {
                        Spacer(Modifier.height(8.dp))
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            SectionLabel("SESSION SUMMARY")
                            Spacer(Modifier.weight(1f))
                            IconButton(onClick = {
                                val text = buildString {
                                    appendLine(ui.summaryTitle)
                                    appendLine()
                                    appendLine(ui.summaryProse)
                                    if (ui.summaryActionItems.isNotEmpty()) {
                                        appendLine()
                                        appendLine("Action items:")
                                        ui.summaryActionItems.forEach { appendLine("• $it") }
                                    }
                                }
                                context.startActivity(
                                    Intent.createChooser(
                                        Intent(Intent.ACTION_SEND).apply {
                                            type = "text/plain"
                                            putExtra(Intent.EXTRA_TEXT, text)
                                        },
                                        "Share summary",
                                    )
                                )
                            }) {
                                Icon(Icons.Default.Share, contentDescription = "Share summary")
                            }
                        }
                        Text(ui.summaryTitle, style = MaterialTheme.typography.titleMedium)
                        Spacer(Modifier.height(4.dp))
                        Text(ui.summaryProse, style = MaterialTheme.typography.bodyMedium)
                        if (ui.summaryActionItems.isNotEmpty()) {
                            Spacer(Modifier.height(8.dp))
                            SectionLabel("ACTION ITEMS")
                            ui.summaryActionItems.forEach { item ->
                                SessionActionItem(item)
                            }
                        }
                    }
                }

                item { Spacer(Modifier.height(16.dp)) }
            }

            // Bottom controls
            Surface(shadowElevation = 8.dp) {
                Column(modifier = Modifier.padding(16.dp).padding(bottom = outerPadding.calculateBottomPadding())) {
                    Button(
                        onClick = {
                            if (ui.listening) vm.stopSession()
                            else vm.startSession()
                        },
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

@OptIn(ExperimentalLayoutApi::class)
@Composable
private fun LiveCueSection(sec: CueSectionDef, cues: List<Cue>, onCueClick: (Cue) -> Unit) {
    var expanded by remember { mutableStateOf(true) }

    Column {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .clickable { expanded = !expanded }
                .padding(vertical = 6.dp),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Icon(
                sec.icon,
                contentDescription = sec.label,
                modifier = Modifier.size(16.dp),
                tint = MaterialTheme.colorScheme.primary,
            )
            Spacer(Modifier.width(6.dp))
            Text(
                sec.label,
                style = MaterialTheme.typography.labelMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                modifier = Modifier.weight(1f),
            )
            Text(
                "${cues.size}",
                style = MaterialTheme.typography.labelSmall,
                color = MaterialTheme.colorScheme.outline,
            )
            Spacer(Modifier.width(4.dp))
            Icon(
                if (expanded) Icons.Default.ExpandLess else Icons.Default.ExpandMore,
                contentDescription = if (expanded) "Collapse" else "Expand",
                modifier = Modifier.size(16.dp),
                tint = MaterialTheme.colorScheme.outline,
            )
        }

        if (expanded) {
            FlowRow(
                horizontalArrangement = Arrangement.spacedBy(6.dp),
                verticalArrangement = Arrangement.spacedBy(6.dp),
                modifier = Modifier.padding(bottom = 8.dp),
            ) {
                cues.forEach { cue ->
                    InputChip(
                        selected = false,
                        onClick = { onCueClick(cue) },
                        label = { Text(cue.title, style = MaterialTheme.typography.labelSmall) },
                    )
                }
            }
        }
    }
}

@Composable
fun SectionLabel(text: String) {
    Text(
        text,
        style = MaterialTheme.typography.labelSmall,
        color = MaterialTheme.colorScheme.outline,
        modifier = Modifier.padding(bottom = 4.dp),
    )
}

@Composable
private fun SessionActionItem(text: String) {
    var checked by remember { mutableStateOf(false) }
    Row(
        modifier = Modifier.fillMaxWidth().padding(vertical = 2.dp),
        horizontalArrangement = Arrangement.spacedBy(4.dp),
        verticalAlignment = Alignment.Top,
    ) {
        Checkbox(
            checked = checked,
            onCheckedChange = { checked = it },
            modifier = Modifier.size(20.dp).padding(top = 2.dp),
        )
        Spacer(Modifier.width(4.dp))
        Text(
            text,
            style = if (checked)
                MaterialTheme.typography.bodySmall.copy(
                    color = MaterialTheme.colorScheme.outline,
                    textDecoration = androidx.compose.ui.text.style.TextDecoration.LineThrough,
                )
            else
                MaterialTheme.typography.bodySmall,
            modifier = Modifier.padding(top = 2.dp),
        )
    }
}
