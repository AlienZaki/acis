package ai.acis.ui

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.text.KeyboardActions
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
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

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SettingsScreen(vm: AcisViewModel, outerPadding: PaddingValues = PaddingValues()) {
    val ui by vm.ui.collectAsStateWithLifecycle()
    var urlDraft by remember(ui.brainUrl) { mutableStateOf(ui.brainUrl) }
    var showLangMenu by remember { mutableStateOf(false) }
    val selectedLang = ui.spokenLanguage
    val selectedLangLabel = LANGUAGES.firstOrNull { it.first == selectedLang }?.second ?: "Auto-detected"

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
