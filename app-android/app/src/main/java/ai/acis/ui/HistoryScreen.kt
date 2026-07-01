package ai.acis.ui

import androidx.compose.foundation.ExperimentalFoundationApi
import androidx.compose.foundation.combinedClickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.KeyboardArrowRight
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.filled.Delete
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import ai.acis.AcisViewModel
import ai.acis.data.SessionRecord
import java.text.SimpleDateFormat
import java.util.*

private fun formatDurationMs(ms: Long): String {
    val totalSec = ms / 1000
    val h = totalSec / 3600
    val m = (totalSec % 3600) / 60
    val s = totalSec % 60
    return if (h > 0) "%d:%02d:%02d".format(h, m, s) else "%d:%02d".format(m, s)
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun HistoryScreen(
    vm: AcisViewModel,
    outerPadding: PaddingValues = PaddingValues(),
    onSessionClick: (String) -> Unit = {},
) {
    val ui by vm.ui.collectAsStateWithLifecycle()
    var selectedIds by remember { mutableStateOf<Set<String>>(emptySet()) }
    var showDeleteDialog by remember { mutableStateOf(false) }
    val selectionMode = selectedIds.isNotEmpty()

    fun toggle(id: String) {
        selectedIds = if (id in selectedIds) selectedIds - id else selectedIds + id
    }

    if (showDeleteDialog) {
        val n = selectedIds.size
        AlertDialog(
            onDismissRequest = { showDeleteDialog = false },
            title = { Text("Delete $n session${if (n == 1) "" else "s"}?") },
            text = { Text("The selected sessions will be permanently deleted from this device.") },
            confirmButton = {
                TextButton(onClick = {
                    vm.deleteSessions(selectedIds)
                    selectedIds = emptySet()
                    showDeleteDialog = false
                }) { Text("Delete", color = MaterialTheme.colorScheme.error) }
            },
            dismissButton = {
                TextButton(onClick = { showDeleteDialog = false }) { Text("Cancel") }
            },
        )
    }

    Scaffold(
        topBar = {
            if (selectionMode) {
                TopAppBar(
                    navigationIcon = {
                        IconButton(onClick = { selectedIds = emptySet() }) {
                            Icon(Icons.Default.Close, contentDescription = "Cancel selection")
                        }
                    },
                    title = { Text("${selectedIds.size} selected") },
                    actions = {
                        TextButton(onClick = { selectedIds = ui.history.map { it.sessionId }.toSet() }) {
                            Text("All")
                        }
                        IconButton(onClick = { showDeleteDialog = true }) {
                            Icon(Icons.Default.Delete, contentDescription = "Delete selected")
                        }
                    },
                )
            } else {
                TopAppBar(title = { Text("History") })
            }
        }
    ) { padding ->
        if (ui.history.isEmpty()) {
            Box(modifier = Modifier.fillMaxSize().padding(padding), contentAlignment = Alignment.Center) {
                Text("No sessions yet.", color = MaterialTheme.colorScheme.outline)
            }
        } else {
            LazyColumn(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(padding)
                    .padding(start = 16.dp, end = 16.dp, bottom = outerPadding.calculateBottomPadding()),
            ) {
                items(ui.history, key = { it.sessionId }) { record ->
                    SessionListRow(
                        record = record,
                        selectionMode = selectionMode,
                        selected = record.sessionId in selectedIds,
                        onClick = {
                            if (selectionMode) toggle(record.sessionId)
                            else onSessionClick(record.sessionId)
                        },
                        onLongClick = { toggle(record.sessionId) },
                    )
                    Spacer(Modifier.height(8.dp))
                }
                item { Spacer(Modifier.height(4.dp)) }
            }
        }
    }
}

@OptIn(ExperimentalFoundationApi::class)
@Composable
private fun SessionListRow(
    record: SessionRecord,
    selectionMode: Boolean,
    selected: Boolean,
    onClick: () -> Unit,
    onLongClick: () -> Unit,
) {
    val dateStr = remember(record.endedAt) {
        SimpleDateFormat("HH:mm · yyyy/MM/dd", Locale.getDefault()).format(Date(record.endedAt))
    }

    Card(
        modifier = Modifier
            .fillMaxWidth()
            .combinedClickable(onClick = onClick, onLongClick = onLongClick),
        colors = if (selected) {
            CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.secondaryContainer)
        } else {
            CardDefaults.cardColors()
        },
    ) {
        Row(
            modifier = Modifier.padding(12.dp),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            if (selectionMode) {
                Checkbox(checked = selected, onCheckedChange = null)
                Spacer(Modifier.width(8.dp))
            }
            Column(modifier = Modifier.weight(1f), verticalArrangement = Arrangement.spacedBy(2.dp)) {
                Text(
                    record.summaryTitle.ifBlank { record.name },
                    style = MaterialTheme.typography.titleSmall,
                )
                Text(
                    buildString {
                        append(dateStr)
                        if (record.durationMs > 0) append(" · ${formatDurationMs(record.durationMs)}")
                    },
                    style = MaterialTheme.typography.labelSmall,
                    color = MaterialTheme.colorScheme.outline,
                )
            }
            if (!selectionMode) {
                Icon(
                    Icons.AutoMirrored.Filled.KeyboardArrowRight,
                    contentDescription = null,
                    modifier = Modifier.size(16.dp),
                    tint = MaterialTheme.colorScheme.outline,
                )
            }
        }
    }
}
