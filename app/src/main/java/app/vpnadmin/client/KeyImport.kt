package app.vpnadmin.client

import org.json.JSONObject
import java.util.Base64
import java.util.zip.Inflater

data class ImportedKey(
    val title: String,
    val conf: String,
    val endpoint: String,
    val address: String,
    val dns: String,
    val protocol: String,
    val expiresAtMillis: Long? = null,
    val panelUrl: String? = null,
)

object KeyImport {
    private val vpnUri = Regex("""vpn://[A-Za-z0-9_\-=]+""")
    private val OBFUSCATION = listOf("Jc", "Jmin", "Jmax", "S1", "S2", "H1", "I1")

    fun parse(raw: String): ImportedKey {
        if (raw.length > MAX_IMPORT_CHARS) {
            throw IllegalArgumentException("Ключ слишком большой")
        }
        val text = raw.trim().removePrefix("\uFEFF")
        if (text.isEmpty()) {
            throw IllegalArgumentException("Вставьте ключ")
        }
        val uri = vpnUri.find(text)?.value
        val decoded = if (uri != null) decodeVpnUri(uri) else null
        val conf = (decoded?.conf ?: text).trim().replace("\r\n", "\n")
        if (!conf.contains("[Interface]", ignoreCase = true) || !conf.contains("[Peer]", ignoreCase = true)) {
            throw IllegalArgumentException("Ключ не распознан")
        }
        requireField(conf, "PrivateKey")
        requireField(conf, "Address")
        requireField(conf, "PublicKey")
        requireField(conf, "Endpoint")
        val title = decoded?.title?.takeIf { it.isNotBlank() } ?: titleFromConf(conf)
        val stored = if (conf.endsWith("\n")) conf else "$conf\n"
        val expiresAt = decoded?.expiresAtMillis ?: expiresAtFromConf(stored)
        return ImportedKey(
            title = title,
            conf = stored,
            endpoint = field(stored, "Endpoint"),
            address = field(stored, "Address").substringBefore("/").substringBefore(",").trim(),
            dns = field(stored, "DNS").ifBlank { "—" },
            protocol = if (OBFUSCATION.any { field(stored, it).isNotBlank() }) "AmneziaWG" else "WireGuard",
            expiresAtMillis = expiresAt,
            panelUrl = decoded?.panelUrl,
        )
    }

    private data class DecodedVpn(
        val title: String,
        val conf: String,
        val expiresAtMillis: Long?,
        val panelUrl: String?,
    )

    private fun decodeVpnUri(uri: String): DecodedVpn {
        var payload = uri.removePrefix("vpn://")
        val remainder = payload.length % 4
        if (remainder != 0) {
            payload += "=".repeat(4 - remainder)
        }
        val bytes = try {
            Base64.getUrlDecoder().decode(payload)
        } catch (_: IllegalArgumentException) {
            throw IllegalArgumentException("Ключ повреждён")
        }
        if (bytes.size < 5) {
            throw IllegalArgumentException("Ключ повреждён")
        }
        val rawLen = ((bytes[0].toInt() and 0xff) shl 24) or
            ((bytes[1].toInt() and 0xff) shl 16) or
            ((bytes[2].toInt() and 0xff) shl 8) or
            (bytes[3].toInt() and 0xff)
        if (rawLen !in 1..1_000_000) {
            throw IllegalArgumentException("Ключ повреждён")
        }
        val inflater = Inflater()
        try {
            inflater.setInput(bytes, 4, bytes.size - 4)
            val out = ByteArray(rawLen)
            var offset = 0
            while (!inflater.finished() && offset < out.size) {
                val count = inflater.inflate(out, offset, out.size - offset)
                if (count == 0) break
                offset += count
            }
            if (offset != rawLen) {
                throw IllegalArgumentException("Ключ повреждён")
            }
            val json = String(out, Charsets.UTF_8)
            return extractConf(json)
        } catch (error: IllegalArgumentException) {
            throw error
        } catch (_: Exception) {
            throw IllegalArgumentException("Ключ повреждён")
        } finally {
            inflater.end()
        }
    }

    private fun extractConf(json: String): DecodedVpn {
        val root = try {
            JSONObject(json)
        } catch (_: Exception) {
            throw IllegalArgumentException("Ключ повреждён")
        }
        val title = root.optString("description").trim().ifBlank { root.optString("name").trim() }
        val expiresAt = SubscriptionExpiry.parseIsoToMillis(
            root.optString("expiresAt").ifBlank { root.optString("expires_at") },
        )
        val panelUrl = root.optString("panelUrl").ifBlank { root.optString("panel_url") }
            .trim()
            .trimEnd('/')
            .ifBlank { null }
        val containers = root.optJSONArray("containers")
            ?: throw IllegalArgumentException("Ключ не распознан")
        var bestRank = Int.MAX_VALUE
        var bestConf = ""
        for (index in 0 until containers.length()) {
            val container = containers.optJSONObject(index) ?: continue
            val keys = container.keys()
            while (keys.hasNext()) {
                val key = keys.next()
                val block = container.optJSONObject(key) ?: continue
                val conf = block.optString("last_config")
                if (!conf.contains("[Interface]", ignoreCase = true)) continue
                val rank = when (key) {
                    "amneziawg" -> 0
                    "wireguard" -> 1
                    else -> 5
                }
                if (rank < bestRank) {
                    bestRank = rank
                    bestConf = conf
                }
            }
        }
        if (bestConf.isBlank() || bestRank > 1) {
            throw IllegalArgumentException("Этот ключ не поддерживается")
        }
        return DecodedVpn(title, bestConf, expiresAt ?: expiresAtFromConf(bestConf), panelUrl)
    }

    private fun expiresAtFromConf(conf: String): Long? {
        for (raw in conf.lineSequence()) {
            val line = raw.trim()
            if (line.isEmpty()) continue
            val body = when {
                line.startsWith("#") -> line.removePrefix("#").trim()
                else -> line
            }
            val eq = body.indexOf('=')
            if (eq <= 0) continue
            val name = body.substring(0, eq).trim()
            if (!name.equals("ExpiresAt", ignoreCase = true)) continue
            return SubscriptionExpiry.parseIsoToMillis(body.substring(eq + 1).trim())
        }
        return null
    }

    private fun requireField(conf: String, name: String) {
        if (field(conf, name).isBlank()) {
            throw IllegalArgumentException("В ключе не хватает данных")
        }
    }

    private fun titleFromConf(conf: String): String {
        val comment = conf.lineSequence()
            .map { it.trim() }
            .firstOrNull { it.startsWith("#") && it.length > 1 }
        return comment?.removePrefix("#")?.trim()?.ifBlank { null } ?: "VPN"
    }

    private fun field(conf: String, name: String): String {
        val wanted = name.lowercase()
        for (raw in conf.lineSequence()) {
            val line = raw.trim()
            if (line.isEmpty() || line.startsWith("#") || line.startsWith("[")) continue
            val eq = line.indexOf('=')
            if (eq <= 0) continue
            if (line.substring(0, eq).trim().lowercase() == wanted) {
                return line.substring(eq + 1).trim()
            }
        }
        return ""
    }

    private const val MAX_IMPORT_CHARS = 512 * 1024
}
