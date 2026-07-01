package ai.acis.data

import android.content.Context
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json

private const val PREFS = "acis_history"
private const val KEY = "sessions"
private const val MAX = 50

class HistoryStore(context: Context) {

    private val prefs = context.getSharedPreferences(PREFS, Context.MODE_PRIVATE)

    fun load(): List<SessionRecord> = try {
        val raw = prefs.getString(KEY, null) ?: return emptyList()
        Json.decodeFromString<List<SessionRecord>>(raw)
    } catch (_: Exception) {
        emptyList()
    }

    fun save(record: SessionRecord) {
        val list = (listOf(record) + load()).take(MAX)
        prefs.edit().putString(KEY, Json.encodeToString(list)).apply()
    }

    /** Remove the sessions whose ids are in [ids]; keeps the rest in order. */
    fun delete(ids: Set<String>) {
        val list = load().filterNot { it.sessionId in ids }
        prefs.edit().putString(KEY, Json.encodeToString(list)).apply()
    }

    fun clear() = prefs.edit().remove(KEY).apply()
}
