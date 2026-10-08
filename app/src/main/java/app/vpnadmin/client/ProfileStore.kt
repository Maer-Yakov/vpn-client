package app.vpnadmin.client

import android.content.Context
import org.json.JSONArray
import org.json.JSONObject
import java.io.File
import java.io.FileOutputStream
import java.nio.file.AtomicMoveNotSupportedException
import java.nio.file.Files
import java.nio.file.StandardCopyOption
import java.util.UUID

data class StoredServer(
    val id: String,
    val key: ImportedKey,
    val splitTunnel: SplitTunnelSettings = SplitTunnelSettings(),
)

data class ServerLibrary(
    val servers: List<StoredServer>,
    val activeId: String?,
    val warning: String? = null,
)

class ProfileStore internal constructor(private val filesDir: File) {
    constructor(context: Context) : this(context.filesDir)

    private val file = File(filesDir, "servers.json")
    private val temporaryFile = File(filesDir, "servers.json.tmp")
    private val legacyConf = File(filesDir, "profile.conf")
    private val legacyTitle = File(filesDir, "profile.title")

    fun load(): ServerLibrary {
        migrateLegacy()
        val recoveryWarning = recoverPendingWrite()
        if (recoveryWarning != null) return ServerLibrary(emptyList(), null, recoveryWarning)
        if (!file.isFile) return ServerLibrary(emptyList(), null)
        return try {
            read(JSONObject(file.readText()))
        } catch (_: Exception) {
            val backup = File(filesDir, "servers.json.corrupt")
            val preserved = runCatching { file.copyTo(backup, overwrite = false) }.isSuccess
            val warning = if (preserved) {
                "Файл профилей повреждён. Копия сохранена: ${backup.name}"
            } else {
                "Файл профилей повреждён и не может быть прочитан"
            }
            ServerLibrary(emptyList(), null, warning)
        }
    }

    fun add(key: ImportedKey): ServerLibrary {
        val current = load()
        requireWritable(current)
        val server = StoredServer(UUID.randomUUID().toString(), key)
        val servers = current.servers + server
        return write(servers, server.id)
    }

    fun setActive(id: String): ServerLibrary {
        val current = load()
        requireWritable(current)
        if (current.servers.none { it.id == id }) return current
        return write(current.servers, id)
    }

    fun setSplitTunnel(id: String, settings: SplitTunnelSettings): ServerLibrary {
        val current = load()
        requireWritable(current)
        if (current.servers.none { it.id == id }) return current
        val servers = current.servers.map { server ->
            if (server.id == id) server.copy(splitTunnel = settings) else server
        }
        return write(servers, current.activeId)
    }

    fun delete(id: String): ServerLibrary {
        val current = load()
        requireWritable(current)
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
                    .put("conf", server.key.conf)
                    .put("splitMode", server.splitTunnel.mode.name)
                    .put("splitPackages", JSONArray(server.splitTunnel.packages.sorted()))
                    .put("bypassDomains", JSONArray(server.splitTunnel.bypassDomains.sorted())),
            )
        }
        val contents = JSONObject().put("active", chosen ?: JSONObject.NULL).put("servers", array).toString()
        filesDir.mkdirs()
        try {
            FileOutputStream(temporaryFile).use { output ->
                output.write(contents.toByteArray(Charsets.UTF_8))
                output.fd.sync()
            }
            moveIntoPlace(temporaryFile, file)
        } finally {
            temporaryFile.delete()
        }
        return ServerLibrary(servers, chosen)
    }

    private fun recoverPendingWrite(): String? {
        if (!temporaryFile.isFile) return null
        if (file.isFile) {
            temporaryFile.delete()
            return null
        }
        return try {
            moveIntoPlace(temporaryFile, file)
            null
        } catch (_: Exception) {
            "Не удалось восстановить временный файл профилей"
        }
    }

    private fun moveIntoPlace(source: File, destination: File) {
        try {
            Files.move(
                source.toPath(),
                destination.toPath(),
                StandardCopyOption.ATOMIC_MOVE,
                StandardCopyOption.REPLACE_EXISTING,
            )
        } catch (_: AtomicMoveNotSupportedException) {
            Files.move(source.toPath(), destination.toPath(), StandardCopyOption.REPLACE_EXISTING)
        }
    }

    private fun requireWritable(library: ServerLibrary) {
        check(library.warning == null) { library.warning.orEmpty() }
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
                        splitTunnel = readSplitTunnel(item),
                    ),
                )
            }
        }
        val active = json.optString("active").takeIf { id -> servers.any { it.id == id } }
            ?: servers.firstOrNull()?.id
        return ServerLibrary(servers, active)
    }

    private fun readSplitTunnel(item: JSONObject): SplitTunnelSettings {
        val mode = runCatching { AppRouteMode.valueOf(item.optString("splitMode")) }
            .getOrDefault(AppRouteMode.AllTraffic)
        val packages = item.optJSONArray("splitPackages")?.let { array ->
            buildSet {
                for (index in 0 until array.length()) {
                    val packageName = array.optString(index)
                    if (SplitTunnelSettings.isValidPackageName(packageName)) add(packageName)
                }
            }
        }.orEmpty()
        val domains = item.optJSONArray("bypassDomains")?.let { array ->
            buildSet {
                for (index in 0 until array.length()) {
                    runCatching { SiteDomain.normalize(array.optString(index)) }
                        .getOrNull()
                        ?.let(::add)
                }
            }
        }.orEmpty()
        return SplitTunnelSettings(mode, packages, domains)
    }
}
