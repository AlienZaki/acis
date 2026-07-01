package ai.acis.ui

import android.content.Intent
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.automirrored.filled.Article
import androidx.compose.material.icons.filled.*
import androidx.compose.material.icons.outlined.Lightbulb
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.AnnotatedString
import androidx.compose.ui.text.SpanStyle
import androidx.compose.ui.text.buildAnnotatedString
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.withStyle
import androidx.compose.ui.unit.dp
import ai.acis.AcisViewModel
import ai.acis.Cue
import ai.acis.data.SessionRecord
import ai.acis.data.TranscriptSegment
import java.text.SimpleDateFormat
import java.util.*

private data class DetailCueSec(val type: String, val label: String, val icon: ImageVector)

private val CUE_SECTIONS = listOf(
    DetailCueSec("concept",    "Concepts",    Icons.AutoMirrored.Filled.Article),
    DetailCueSec("answer",     "Answers",     Icons.Default.QuestionAnswer),
    DetailCueSec("suggestion", "Suggestions", Icons.Outlined.Lightbulb),
    DetailCueSec("bio",        "Bios",        Icons.Default.Person),
)

private fun cueTypeIcon(type: String): ImageVector = when (type) {
    "concept"    -> Icons.AutoMirrored.Filled.Article
    "answer"     -> Icons.Default.QuestionAnswer
    "suggestion" -> Icons.Outlined.Lightbulb
    "bio"        -> Icons.Default.Person
    else         -> Icons.Default.Info
}

private data class ParsedActionItem(val assignee: String?, val text: String)

private fun String.parseActionItem(): ParsedActionItem {
    val match = Regex("""^\[([^\]]+)]\s*(.+)""").find(trim())
    return if (match != null) ParsedActionItem(match.groupValues[1], match.groupValues[2])
    else ParsedActionItem(null, trim())
}

private fun formatDurationMs(ms: Long): String {
    val totalSec = ms / 1000
    val h = totalSec / 3600
    val m = (totalSec % 3600) / 60
    val s = totalSec % 60
    return if (h > 0) "%d:%02d:%02d".format(h, m, s) else "%d:%02d".format(m, s)
}

private fun formatSegmentTime(tStart: Float): String {
    val totalSec = tStart.toInt()
    val h = totalSec / 3600
    val m = (totalSec % 3600) / 60
    val s = totalSec % 60
    return if (h > 0) "%d:%02d:%02d".format(h, m, s) else "%02d:%02d".format(m, s)
}

@OptIn(ExperimentalMaterial3Api::class, ExperimentalLayoutApi::class)
@Composable
fun SessionDetailScreen(
    vm: AcisViewModel,
    sessionId: String,
    onBack: () -> Unit,
) {
    val ui by vm.ui.collectAsStateWithLifecycle()
    val record = ui.history.find { it.sessionId == sessionId } ?: return

    val dateStr = remember(record.endedAt) {
        SimpleDateFormat("HH:mm · yyyy/MM/dd", Locale.getDefault()).format(Date(record.endedAt))
    }

    var selectedTab by remember { mutableIntStateOf(0) }
    var cueModal by remember { mutableStateOf<Cue?>(null) }

    // Cue detail modal
    cueModal?.let { cue ->
        AlertDialog(
            onDismissRequest = { cueModal = null },
            icon = { Icon(cueTypeIcon(cue.cueType), contentDescription = null) },
            title = { Text(cue.title) },
            text = { Text(cue.body) },
            confirmButton = {
                TextButton(onClick = { cueModal = null }) { Text("Dismiss") }
            },
        )
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Column {
                        Text(record.summaryTitle.ifBlank { record.name }, style = MaterialTheme.typography.titleMedium)
                        Text(
                            buildString {
                                append(dateStr)
                                if (record.durationMs > 0) append(" · ${formatDurationMs(record.durationMs)}")
                            },
                            style = MaterialTheme.typography.labelSmall,
                            color = MaterialTheme.colorScheme.outline,
                        )
                    }
                },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back")
                    }
                },
            )
        }
    ) { padding ->
        Column(modifier = Modifier.fillMaxSize().padding(padding)) {
            TabRow(selectedTabIndex = selectedTab) {
                Tab(
                    selected = selectedTab == 0,
                    onClick = { selectedTab = 0 },
                    text = { Text("AI summary") },
                )
                Tab(
                    selected = selectedTab == 1,
                    onClick = { selectedTab = 1 },
                    text = { Text("Transcriptions") },
                )
            }

            when (selectedTab) {
                0 -> AiSummaryTab(record, onCueClick = { cueModal = it })
                1 -> TranscriptionsTab(record.segments)
            }
        }
    }
}

@OptIn(ExperimentalLayoutApi::class)
@Composable
private fun AiSummaryTab(record: SessionRecord, onCueClick: (Cue) -> Unit) {
    val context = LocalContext.current

    LazyColumn(
        modifier = Modifier.fillMaxSize(),
        contentPadding = PaddingValues(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp),
    ) {
        // Prose summary
        if (record.summaryProse.isNotBlank()) {
            item {
                Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                    DetailSectionLabel("Conversation summary")
                    Text(record.summaryProse, style = MaterialTheme.typography.bodyMedium)
                }
            }
        }

        // Action items
        if (record.actionItems.isNotEmpty()) {
            item {
                val parsed = remember(record.actionItems) { record.actionItems.map { it.parseActionItem() } }
                Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        DetailSectionLabel("Action items", modifier = Modifier.weight(1f))
                        IconButton(
                            onClick = {
                                val text = record.actionItems.joinToString("\n") { "• $it" }
                                context.startActivity(
                                    Intent.createChooser(
                                        Intent(Intent.ACTION_SEND).apply {
                                            type = "text/plain"
                                            putExtra(Intent.EXTRA_TEXT, text)
                                        },
                                        "Share action items",
                                    )
                                )
                            }
                        ) {
                            Icon(Icons.Default.Share, contentDescription = "Share action items")
                        }
                    }
                    parsed.forEach { item ->
                        ActionItemRow(item)
                    }
                }
            }
        }

        // AI cues grouped by type
        if (record.cues.isNotEmpty()) {
            item {
                DetailSectionLabel("AI cues")
            }
            CUE_SECTIONS.forEach { sec ->
                val cuesOfType = record.cues.filter { it.cueType == sec.type }
                if (cuesOfType.isNotEmpty()) {
                    item(key = "section_${sec.type}") {
                        CueSection(sec = sec, cues = cuesOfType, onCueClick = onCueClick)
                    }
                }
            }
        }

        item { Spacer(Modifier.height(8.dp)) }
    }
}

@Composable
private fun TranscriptionsTab(segments: List<TranscriptSegment>) {
    if (segments.isEmpty()) {
        Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
            Text("No transcript available.", color = MaterialTheme.colorScheme.outline)
        }
        return
    }

    LazyColumn(
        modifier = Modifier.fillMaxSize(),
        contentPadding = PaddingValues(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        items(segments) { segment ->
            Column(verticalArrangement = Arrangement.spacedBy(2.dp)) {
                Text(
                    formatSegmentTime(segment.tStart),
                    style = MaterialTheme.typography.labelSmall,
                    color = MaterialTheme.colorScheme.outline,
                    fontFamily = FontFamily.Monospace,
                )
                Text(segment.text, style = MaterialTheme.typography.bodyMedium)
            }
        }
        item { Spacer(Modifier.height(8.dp)) }
    }
}

@OptIn(ExperimentalLayoutApi::class)
@Composable
private fun CueSection(sec: DetailCueSec, cues: List<Cue>, onCueClick: (Cue) -> Unit) {
    var showAll by remember { mutableStateOf(false) }
    val hasMore = cues.size > CUE_PREVIEW_LIMIT
    val visible = if (showAll || !hasMore) cues else cues.take(CUE_PREVIEW_LIMIT)

    Column {
        Row(
            modifier = Modifier.fillMaxWidth().padding(vertical = 8.dp),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Icon(
                sec.icon,
                contentDescription = sec.label,
                modifier = Modifier.size(18.dp),
                tint = MaterialTheme.colorScheme.primary,
            )
            Spacer(Modifier.width(8.dp))
            Text(sec.label, style = MaterialTheme.typography.titleSmall, modifier = Modifier.weight(1f))
            Text(
                "${cues.size}",
                style = MaterialTheme.typography.labelSmall,
                color = MaterialTheme.colorScheme.outline,
            )
        }

        FlowRow(
            horizontalArrangement = Arrangement.spacedBy(8.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp),
            modifier = Modifier.padding(bottom = 8.dp),
        ) {
            visible.forEach { cue ->
                InputChip(
                    selected = false,
                    onClick = { onCueClick(cue) },
                    label = { Text(cue.title, style = MaterialTheme.typography.labelMedium) },
                )
            }
            if (hasMore) {
                SeeAllChip(
                    showAll = showAll,
                    moreCount = cues.size - CUE_PREVIEW_LIMIT,
                    onClick = { showAll = !showAll },
                )
            }
        }
    }
}

@Composable
private fun ActionItemRow(item: ParsedActionItem) {
    var checked by remember { mutableStateOf(false) }
    Row(
        modifier = Modifier.fillMaxWidth(),
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
            buildAssigneeString(item),
            style = if (checked)
                MaterialTheme.typography.bodyMedium.copy(
                    color = MaterialTheme.colorScheme.outline,
                    textDecoration = androidx.compose.ui.text.style.TextDecoration.LineThrough,
                )
            else
                MaterialTheme.typography.bodyMedium,
            modifier = Modifier.padding(top = 2.dp),
        )
    }
}

@Composable
private fun buildAssigneeString(item: ParsedActionItem): AnnotatedString =
    if (item.assignee != null) {
        buildAnnotatedString {
            withStyle(SpanStyle(fontWeight = FontWeight.SemiBold)) {
                append("[${item.assignee}] ")
            }
            append(item.text)
        }
    } else {
        AnnotatedString(item.text)
    }

@Composable
private fun DetailSectionLabel(text: String, modifier: Modifier = Modifier) {
    Text(
        text,
        style = MaterialTheme.typography.labelSmall,
        color = MaterialTheme.colorScheme.outline,
        modifier = modifier,
    )
}

