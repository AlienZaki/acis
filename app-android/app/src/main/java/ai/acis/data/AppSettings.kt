package ai.acis.data

import android.content.Context
import ai.acis.BuildConfig

private const val PREFS = "acis_settings"

class AppSettings(context: Context) {

    private val prefs = context.getSharedPreferences(PREFS, Context.MODE_PRIVATE)

    var brainUrl: String
        get() = prefs.getString("brain_url", BuildConfig.BRAIN_URL) ?: BuildConfig.BRAIN_URL
        set(v) = prefs.edit().putString("brain_url", v).apply()

    var spokenLanguage: String
        get() = prefs.getString("spoken_language", "auto") ?: "auto"
        set(v) = prefs.edit().putString("spoken_language", v).apply()

    /** Render the live session as the in-lens HUD simulation. */
    var lensPreview: Boolean
        get() = prefs.getBoolean("lens_preview", false)
        set(v) = prefs.edit().putBoolean("lens_preview", v).apply()

    // ── Glasses interface (in-lens HUD behaviour) ──

    /** Audio source: "glasses" or "phone". */
    var voiceInput: String
        get() = prefs.getString("voice_input", "glasses") ?: "glasses"
        set(v) = prefs.edit().putString("voice_input", v).apply()

    /** Show AI cues in the lens HUD. */
    var glassesAiCues: Boolean
        get() = prefs.getBoolean("glasses_ai_cues", true)
        set(v) = prefs.edit().putBoolean("glasses_ai_cues", v).apply()

    /** Show live transcription captions in the lens HUD. */
    var glassesLiveTranscription: Boolean
        get() = prefs.getBoolean("glasses_live_transcription", true)
        set(v) = prefs.edit().putBoolean("glasses_live_transcription", v).apply()

    /** Auto-expand a new cue to its full card (vs a compact title-only pill). */
    var autoPopup: Boolean
        get() = prefs.getBoolean("auto_popup", true)
        set(v) = prefs.edit().putBoolean("auto_popup", v).apply()

    /** How long a cue stays on the lens: "auto", or a fixed "3"/"5"/"8" seconds. */
    var cueDuration: String
        get() = prefs.getString("cue_duration", "auto") ?: "auto"
        set(v) = prefs.edit().putString("cue_duration", v).apply()
}
