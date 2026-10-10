package app.vpnadmin.client

import org.json.JSONObject
import java.net.URLDecoder
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
        if (uri == null && text.contains("vless://", ignoreCase = true)) {
            val link = Regex("""(?i)vless://\S+""").find(text)?.value
                ?: throw IllegalArgumentException("Ключ не распознан")
            return parseVless(link)
        }
        if (uri == null && text.contains("ss://", ignoreCase = true)) {
            val link = Regex("""(?i)ss://\S+""").find(text)?.value
                ?: throw IllegalArgumentException("Ключ не распознан")
            return parseShadowsocks(link)
        }
        if (uri == null && looksLikeOpenVpn(text)) {
            return parseOpenVpn(text)
        }
        val decoded = if (uri != null) decodeVpnUri(uri) else null
        if (decoded != null && !decoded.wireGuard) {
            return protocolKey(decoded)
        }
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
        val protocol: String,
        val wireGuard: Boolean,
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
        var bestProtocol = ""
        var bestWireGuard = false
        for (index in 0 until containers.length()) {
            val container = containers.optJSONObject(index) ?: continue
            val keys = container.keys()
            while (keys.hasNext()) {
                val key = keys.next()
                val block = container.optJSONObject(key) ?: continue
                val conf = block.optString("last_config")
                if (conf.isBlank()) continue
                val matched = when (key) {
                    "awg", "amneziawg" -> Triple(0, "AmneziaWG", true)
                    "wireguard" -> Triple(1, "WireGuard", true)
                    "xray" -> Triple(2, "XRay", false)
                    "ikev2" -> Triple(3, "IKEv2", false)
                    "openvpn" -> Triple(4, "OpenVPN", false)
                    "cloak" -> Triple(5, "OpenVPN Cloak", false)
                    "shadowsocks", "ss" -> Triple(6, "Shadowsocks", false)
                    else -> null
                } ?: continue
                if (matched.first < bestRank) {
                    bestRank = matched.first
                    bestProtocol = matched.second
                    bestWireGuard = matched.third
                    bestConf = conf
                }
            }
        }
        if (bestConf.isBlank()) {
            throw IllegalArgumentException("Этот ключ не поддерживается")
        }
        if (bestWireGuard && !bestConf.contains("[Interface]", ignoreCase = true)) {
            throw IllegalArgumentException("Ключ не распознан")
        }
        return DecodedVpn(
            title,
            bestConf,
            expiresAt ?: expiresAtFromConf(bestConf),
            panelUrl,
            bestProtocol,
            bestWireGuard,
        )
    }

    private fun protocolKey(decoded: DecodedVpn): ImportedKey {
        val stored = if (decoded.conf.endsWith("\n")) decoded.conf else decoded.conf + "\n"
        return ImportedKey(
            title = decoded.title.ifBlank { decoded.protocol },
            conf = stored,
            endpoint = endpointOf(decoded.protocol, stored),
            address = "—",
            dns = "—",
            protocol = decoded.protocol,
            expiresAtMillis = decoded.expiresAtMillis,
            panelUrl = decoded.panelUrl,
        )
    }

    private fun endpointOf(protocol: String, conf: String): String {
        return when (protocol) {
            "OpenVPN", "OpenVPN Cloak" -> openVpnEndpoint(conf)
            "Shadowsocks" -> shadowsocksEndpoint(conf)
            "XRay" -> xrayEndpoint(conf)
            "IKEv2" -> ikev2Endpoint(conf)
            else -> "—"
        }
    }

    private fun openVpnEndpoint(conf: String): String {
        val remote = Regex("""(?m)^\s*remote\s+(\S+)\s+(\d+)""").find(conf) ?: return "—"
        return "${remote.groupValues[1]}:${remote.groupValues[2]}"
    }

    private fun shadowsocksEndpoint(conf: String): String {
        val json = runCatching { JSONObject(conf) }.getOrNull()
        if (json != null) {
            val host = json.optString("server").trim()
            val port = json.optInt("server_port")
            if (host.isNotBlank() && port > 0) return "$host:$port"
        }
        return hostPortAfterAt(decodeShadowsocks(conf.substringAfter("://").substringBefore("#")))
    }

    private fun xrayEndpoint(conf: String): String {
        if (conf.contains("vless://", ignoreCase = true)) return parseVless(conf.trim()).endpoint
        val root = runCatching { JSONObject(conf) }.getOrNull() ?: return "—"
        val vnext = root.optJSONArray("outbounds")
            ?.optJSONObject(0)
            ?.optJSONObject("settings")
            ?.optJSONArray("vnext")
            ?.optJSONObject(0)
            ?: return "—"
        val host = vnext.optString("address").trim()
        val port = vnext.optInt("port")
        if (host.isBlank() || port <= 0) return "—"
        return "$host:$port"
    }

    private fun ikev2Endpoint(conf: String): String {
        val json = runCatching { JSONObject(conf) }.getOrNull()
        val host = json?.optString("hostName")?.trim().orEmpty().ifBlank {
            conf.lineSequence()
                .map { it.trim().removePrefix("#").trim() }
                .firstOrNull { it.startsWith("Server:", ignoreCase = true) }
                ?.substringAfter(":")
                ?.trim()
                .orEmpty()
        }
        return host.ifBlank { "—" }
    }

    private fun parseShadowsocks(uri: String): ImportedKey {
        val body = uri.substringAfter("://")
        val title = decodeFragment(body.substringAfter("#", "")).ifBlank { "Shadowsocks" }
        val userinfo = decodeShadowsocks(body.substringBefore("#"))
        val endpoint = hostPortAfterAt(userinfo)
        if (endpoint == "—") throw IllegalArgumentException("Ключ не распознан")
        val stored = if (uri.endsWith("\n")) uri else "$uri\n"
        return ImportedKey(
            title = title,
            conf = stored,
            endpoint = endpoint,
            address = "—",
            dns = "—",
            protocol = "Shadowsocks",
        )
    }

    private fun parseOpenVpn(text: String): ImportedKey {
        val protocol = if (text.contains("Cloak", ignoreCase = true)) "OpenVPN Cloak" else "OpenVPN"
        val stored = text.trim().replace("\r\n", "\n").let { if (it.endsWith("\n")) it else "$it\n" }
        return ImportedKey(
            title = titleFromConf(stored).takeUnless { it == "VPN" } ?: protocol,
            conf = stored,
            endpoint = openVpnEndpoint(stored),
            address = "—",
            dns = "—",
            protocol = protocol,
        )
    }

    private fun decodeFragment(encoded: String): String {
        return runCatching { URLDecoder.decode(encoded, Charsets.UTF_8.name()) }.getOrDefault(encoded).trim()
    }

    private fun decodeShadowsocks(token: String): String {
        val encoded = token.substringBefore("@").ifBlank { token }
        val padded = encoded + "=".repeat((4 - encoded.length % 4) % 4)
        val bytes = runCatching { Base64.getUrlDecoder().decode(padded) }.getOrNull()
            ?: runCatching { Base64.getDecoder().decode(padded) }.getOrNull()
            ?: return token
        return runCatching { String(bytes, Charsets.UTF_8) }.getOrDefault(token)
    }

    private fun hostPortAfterAt(value: String): String {
        val hostPort = value.substringAfterLast("@", "").substringBefore("?").trim()
        val host = hostPort.substringBefore(":").trim()
        val port = hostPort.substringAfter(":", "").trim()
        if (host.isBlank() || port.isBlank()) return "—"
        return "$host:$port"
    }

    private fun parseVless(uri: String): ImportedKey {
        val body = uri.substringAfter("://")
        val main = body.substringBefore("#")
        val hostPort = main.substringAfterLast("@", "").substringBefore("?")
        val host = hostPort.substringBefore(":").trim()
        val port = hostPort.substringAfter(":", "").trim()
        if (host.isBlank() || port.isBlank() || !main.contains("@")) {
            throw IllegalArgumentException("Ключ не распознан")
        }
        val stored = if (uri.endsWith("\n")) uri else "$uri\n"
        return ImportedKey(
            title = decodeFragment(body.substringAfter("#", "")).ifBlank { "XRay" },
            conf = stored,
            endpoint = "$host:$port",
            address = "—",
            dns = "—",
            protocol = "XRay",
        )
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

internal fun looksLikeOpenVpn(text: String): Boolean {
    val hasRemote = Regex("""(?m)^\s*remote\s+\S+""").containsMatchIn(text)
    return hasRemote && (text.contains("dev tun", ignoreCase = true) || text.contains("<ca>", ignoreCase = true))
}
