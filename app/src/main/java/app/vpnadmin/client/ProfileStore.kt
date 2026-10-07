package app.vpnadmin.client

import android.content.Context
import org.json.JSONArray
import org.json.JSONObject
import java.io.File
import java.util.UUID

data class StoredServer(
    val id: String,
    val key: ImportedKey,
)

data class ServerLibrary(
    val servers: List<StoredServer>,
    val activeId: String?,
)

class ProfileStore(context: Context) {
    private val file = File(context.filesDir, "servers.json")
    private val legacyConf = File(context.filesDir, "profile.conf")
    private val legacyTitle = File(context.filesDir, "profile.title")

    fun load(): ServerLibrary {
        migrateLegacy()
        if (!file.isFile) return ServerLibrary(emptyList(), null)
        return try {
            read(JSONObject(file.readText()))
        } catch (_: Exception) {
            ServerLibrary(emptyList(), null)
        }
    }

    fun add(key: ImportedKey): ServerLibrary {
        val current = load()
        val server = StoredServer(UUID.randomUUID().toString(), key)
        val servers = current.servers + server
        return write(servers, server.id)
    }

    fun setActive(id: String): ServerLibrary {
        val current = load()
        if (current.servers.none { it.id == id }) return current
        return write(current.servers, id)
    }

    fun delete(id: String): ServerLibrary {
        val current = load()
        val servers = current.servers.filterNot { it.id == id }
        val active = if (current.activeId == id) servers.firstOrNull()?.id else current.activeId
        return write(servers, active)
    }

    private fun migrateLegacy() {
        if (file.isFile || !legacyConf.isFile) return
        val parsed = try {
            KeyImport.parse(legacyConf.readText())
        } catch (_: IllegalArgumentException) {
            null
        }
        val title = legacyTitle.takeIf { it.isFile }?.readText()?.trim().orEmpty()
        if (parsed == null) return
        val key = if (title.isBlank()) parsed else parsed.copy(title = title)
        write(listOf(StoredServer(UUID.randomUUID().toString(), key)), null)
        legacyConf.delete()
        legacyTitle.delete()
    }

    private fun write(servers: List<StoredServer>, activeId: String?): ServerLibrary {
        val chosen = activeId?.takeIf { id -> servers.any { it.id == id } } ?: servers.firstOrNull()?.id
        val array = JSONArray()
        servers.forEach { server ->
            array.put(
                JSONObject()
                    .put("id", server.id)
                    .put("title", server.key.title)
                    .put("endpoint", server.key.endpoint)
                    .put("address", server.key.address)
                    .put("dns", server.key.dns)
                    .put("protocol", server.key.protocol)
                    .put("conf", server.key.conf),
            )
        }
        file.writeText(JSONObject().put("active", chosen ?: JSONObject.NULL).put("servers", array).toString())
        return ServerLibrary(servers, chosen)
    }

    private fun read(json: JSONObject): ServerLibrary {
        val array = json.optJSONArray("servers") ?: JSONArray()
        val servers = buildList {
            for (index in 0 until array.length()) {
                val item = array.optJSONObject(index) ?: continue
                val conf = item.optString("conf")
                if (conf.isBlank()) continue
                add(
                    StoredServer(
                        id = item.optString("id").ifBlank { UUID.randomUUID().toString() },
                        key = ImportedKey(
                            title = item.optString("title").ifBlank { "VPN" },
                            conf = conf,
                            endpoint = item.optString("endpoint"),
                            address = item.optString("address"),
                            dns = item.optString("dns").ifBlank { "—" },
                            protocol = item.optString("protocol").ifBlank { "AmneziaWG" },
                        ),
                    ),
                )
            }
        }
        val active = json.optString("active").takeIf { id -> servers.any { it.id == id } }
            ?: servers.firstOrNull()?.id
        return ServerLibrary(servers, active)
    }
}
