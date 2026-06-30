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
}
