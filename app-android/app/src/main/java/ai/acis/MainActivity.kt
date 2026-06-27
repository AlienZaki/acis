package ai.acis

import android.Manifest
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.result.contract.ActivityResultContracts
import androidx.activity.viewModels
import ai.acis.ui.AcisTheme
import ai.acis.ui.SessionScreen

class MainActivity : ComponentActivity() {

    private val vm: AcisViewModel by viewModels()

    private val requestMic = registerForActivityResult(ActivityResultContracts.RequestPermission()) { granted ->
        if (granted) vm.connect()
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        requestMic.launch(Manifest.permission.RECORD_AUDIO)
        setContent {
            AcisTheme {
                SessionScreen(vm = vm)
            }
        }
    }
}
