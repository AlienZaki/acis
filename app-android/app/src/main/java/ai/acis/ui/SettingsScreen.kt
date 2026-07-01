package ai.acis.ui

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.text.KeyboardActions
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Check
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import ai.acis.AcisViewModel

private val LANGUAGES = listOf(
    "auto"       to "Auto-detected",
    "en"         to "English",
    "ar"         to "Arabic",
    "zh"         to "Chinese (Simplified)",
    "de"         to "German",
    "fr"         to "French",
    "ja"         to "Japanese",
    "ko"         to "Korean",
    "pt"         to "Portuguese",
    "es"         to "Spanish",
)

private val CUE_DURATIONS = listOf(
    "auto" to "Auto-adjusted",
    "3"    to "3 seconds",
    "5"    to "5 seconds",
    "8"    to "8 seconds",
)

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SettingsScreen(vm: AcisViewModel, outerPadding: PaddingValues = PaddingValues()) {
    val ui by vm.ui.collectAsStateWithLifecycle()
    var urlDraft by remember(ui.brainUrl) { mutableStateOf(ui.brainUrl) }
    var showLangMenu by remember { mutableStateOf(false) }
    var showDurationMenu by remember { mutableStateOf(false) }
    val selectedLang = ui.spokenLanguage
    val selectedLangLabel = LANGUAGES.firstOrNull { it.first == selectedLang }?.second ?: "Auto-detected"
    val selectedDurationLabel = CUE_DURATIONS.firstOrNull { it.first == ui.cueDuration }?.second ?: "Auto-adjusted"

    Scaffold(topBar = { TopAppBar(title = { Text("Settings") }) }) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .padding(bottom = outerPadding.calculateBottomPadding())
                .verticalScroll(rememberScrollState())
                .padding(horizontal = 16.dp, vertical = 24.dp),
            verticalArrangement = Arrangement.spacedBy(24.dp),
        ) {
            // Brain URL
            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Text("Brain server URL", style = MaterialTheme.typography.titleSmall)
                OutlinedTextField(
                    value = urlDraft,
                    onValueChange = { urlDraft = it },
                    placeholder = { Text("ws://192.168.1.x:8765") },
                    singleLine = true,
                    modifier = Modifier.fillMaxWidth(),
                    keyboardOptions = KeyboardOptions(imeAction = ImeAction.Done),
                    keyboardActions = KeyboardActions(onDone = {
                        vm.setBrainUrl(urlDraft)
                        vm.reconnectWithNewUrl()
                    }),
                )
                Text(
                    "Enter the WebSocket address of the ACIS brain running on your laptop.",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.outline,
                )
                Button(
                    onClick = {
                        vm.setBrainUrl(urlDraft)
                        vm.reconnectWithNewUrl()
                    },
                    enabled = urlDraft != ui.brainUrl || !ui.connected,
                ) {
                    Text("Save & reconnect")
                }
            }

            HorizontalDivider()

            // Voice input
            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                SettingsSectionLabel("Voice input")
                Surface(
                    shape = MaterialTheme.shapes.medium,
                    color = MaterialTheme.colorScheme.surfaceVariant,
                    modifier = Modifier.fillMaxWidth(),
                ) {
                    Column {
                        VoiceInputRow("Glasses", "glasses", ui.voiceInput) { vm.setVoiceInput("glasses") }
                        HorizontalDivider()
                        VoiceInputRow("Phone", "phone", ui.voiceInput) { vm.setVoiceInput("phone") }
                    }
                }
            }

            // Glasses interface
            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                SettingsSectionLabel("Glasses interface")
                Surface(
                    shape = MaterialTheme.shapes.medium,
                    color = MaterialTheme.colorScheme.surfaceVariant,
                    modifier = Modifier.fillMaxWidth(),
                ) {
                    Column {
                        SettingsToggleRow("AI cues", ui.glassesAiCues) { vm.setGlassesAiCues(it) }
                        HorizontalDivider()
                        SettingsToggleRow("Live transcription", ui.glassesLiveTranscription) {
                            vm.setGlassesLiveTranscription(it)
                        }
                    }
                }
                Text(
                    "These will only affect the glasses interface during a session. " +
                        "The app will still transcribe and create a live AI summary.",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.outline,
                )
            }

            // Auto pop-up + Cue duration
            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Surface(
                    shape = MaterialTheme.shapes.medium,
                    color = MaterialTheme.colorScheme.surfaceVariant,
                    modifier = Modifier.fillMaxWidth(),
                ) {
                    Column {
                        SettingsToggleRow("Auto pop-up", ui.autoPopup) { vm.setAutoPopup(it) }
                        HorizontalDivider()
                        ExposedDropdownMenuBox(
                            expanded = showDurationMenu,
                            onExpandedChange = { showDurationMenu = it },
                        ) {
                            Row(
                                modifier = Modifier
                                    .menuAnchor(MenuAnchorType.PrimaryNotEditable)
                                    .fillMaxWidth()
                                    .padding(horizontal = 16.dp, vertical = 14.dp),
                                horizontalArrangement = Arrangement.SpaceBetween,
                                verticalAlignment = Alignment.CenterVertically,
                            ) {
                                Text("Cue duration", style = MaterialTheme.typography.bodyLarge)
                                Row(verticalAlignment = Alignment.CenterVertically) {
                                    Text(
                                        selectedDurationLabel,
                                        style = MaterialTheme.typography.bodyMedium,
                                        color = MaterialTheme.colorScheme.outline,
                                    )
                                    ExposedDropdownMenuDefaults.TrailingIcon(expanded = showDurationMenu)
                                }
                            }
                            ExposedDropdownMenu(
                                expanded = showDurationMenu,
                                onDismissRequest = { showDurationMenu = false },
                            ) {
                                CUE_DURATIONS.forEach { (value, label) ->
                                    DropdownMenuItem(
                                        text = { Text(label) },
                                        onClick = {
                                            vm.setCueDuration(value)
                                            showDurationMenu = false
                                        },
                                        trailingIcon = {
                                            if (value == ui.cueDuration) {
                                                Text("✓", color = MaterialTheme.colorScheme.primary)
                                            }
                                        },
                                    )
                                }
                            }
                        }
                    }
                }
                Text(
                    "When a new cue is detected it will expand automatically on the glasses display.",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.outline,
                )
            }

            HorizontalDivider()

            // Spoken language
            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Text("Spoken language", style = MaterialTheme.typography.titleSmall)
                Text(
                    "Helps the transcription model focus on the right language.",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.outline,
                )
                ExposedDropdownMenuBox(
                    expanded = showLangMenu,
                    onExpandedChange = { showLangMenu = it },
                ) {
                    OutlinedTextField(
                        value = selectedLangLabel,
                        onValueChange = {},
                        readOnly = true,
                        modifier = Modifier.menuAnchor(MenuAnchorType.PrimaryNotEditable).fillMaxWidth(),
                        trailingIcon = { ExposedDropdownMenuDefaults.TrailingIcon(expanded = showLangMenu) },
                    )
                    ExposedDropdownMenu(
                        expanded = showLangMenu,
                        onDismissRequest = { showLangMenu = false },
                    ) {
                        LANGUAGES.forEach { (code, label) ->
                            DropdownMenuItem(
                                text = { Text(label) },
                                onClick = {
                                    vm.setSpokenLanguage(code)
                                    showLangMenu = false
                                },
                                trailingIcon = {
                                    if (code == selectedLang) {
                                        Text("✓", color = MaterialTheme.colorScheme.primary)
                                    }
                                },
                            )
                        }
                    }
                }
            }
        }
    }
}

@Composable
private fun SettingsSectionLabel(text: String) {
    Text(
        text,
        style = MaterialTheme.typography.titleSmall,
        color = MaterialTheme.colorScheme.onSurface,
    )
}

@Composable
private fun SettingsToggleRow(label: String, checked: Boolean, onChange: (Boolean) -> Unit) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(start = 16.dp, end = 16.dp, top = 8.dp, bottom = 8.dp),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Text(label, style = MaterialTheme.typography.bodyLarge)
        Switch(checked = checked, onCheckedChange = onChange)
    }
}

@Composable
private fun VoiceInputRow(label: String, value: String, selected: String, onSelect: () -> Unit) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .clickable(onClick = onSelect)
            .padding(horizontal = 16.dp, vertical = 16.dp),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Text(label, style = MaterialTheme.typography.bodyLarge)
        if (value == selected) {
            Icon(
                Icons.Default.Check,
                contentDescription = "Selected",
                tint = MaterialTheme.colorScheme.primary,
            )
        }
    }
}
