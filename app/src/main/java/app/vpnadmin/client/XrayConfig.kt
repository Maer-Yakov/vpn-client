package app.vpnadmin.client

import org.json.JSONArray
import org.json.JSONObject
import java.net.URLDecoder

/**
 * Собирает JSON ядра Xray из сохранённого ключа панели: ссылки vless:// или
 * клиентского JSON с исходящим VLESS. Телефонный трафик пишет hev-socks5-tunnel
 * в локальный SOCKS. DNS уходит в модуль DNS ядра по HTTPS на порт 443:
 * VLESS с flow xtls-rprx-vision не переносит UDP, а порт 53 через сервер обрывается.
 */
object XrayConfig {
    const val TUN_MTU = 1280
    const val TUN_ADDRESS = "10.10.14.2"
    const val TUN_ADDRESS_V6 = "fd00:10:14::2"
    const val SOCKS_PORT = 10808

    fun build(storedConf: String, bypassDomains: Set<String> = emptySet()): String {
        val link = parse(storedConf)
        val user = JSONObject()
            .put("id", link.uuid)
            .put("encryption", link.encryption.ifBlank { "none" })
        if (link.flow.isNotBlank()) user.put("flow", link.flow)

        val stream = JSONObject()
            .put("network", link.network.ifBlank { "tcp" })
            .put("security", link.security)
        if (link.security.equals("reality", ignoreCase = true)) {
            stream.put(
                "realitySettings",
                JSONObject()
                    .put("serverName", link.sni)
                    .put("fingerprint", link.fingerprint.ifBlank { "chrome" })
                    .put("publicKey", link.publicKey)
                    .put("shortId", link.shortId)
                    .put("spiderX", link.spiderX),
            )
        } else if (link.security.equals("tls", ignoreCase = true) && link.sni.isNotBlank()) {
            stream.put("tlsSettings", JSONObject().put("serverName", link.sni))
        }

        val proxy = JSONObject()
            .put("tag", "proxy")
            .put("protocol", "vless")
            .put(
                "settings",
                JSONObject().put(
                    "vnext",
                    JSONArray().put(
                        JSONObject()
                            .put("address", link.host)
                            .put("port", link.port)
                            .put("users", JSONArray().put(user)),
                    ),
                ),
            )
            .put("streamSettings", stream)

        val root = JSONObject()
            .put("log", JSONObject().put("loglevel", "warning"))
            .put("stats", JSONObject())
            .put(
                "policy",
                JSONObject().put(
                    "system",
                    JSONObject()
                        .put("statsOutboundUplink", true)
                        .put("statsOutboundDownlink", true),
                ),
            )
            .put(
                "dns",
                JSONObject()
                    .put("tag", "dns-in")
                    .put("queryStrategy", "UseIPv4")
                    .put(
                        "servers",
                        JSONArray()
                            .put("https://1.1.1.1/dns-query")
                            .put("https://1.0.0.1/dns-query"),
                    ),
            )
            .put(
                "inbounds",
                JSONArray().put(
                    JSONObject()
                        .put("tag", "socks-in")
                        .put("listen", "127.0.0.1")
                        .put("port", SOCKS_PORT)
                        .put("protocol", "socks")
                        .put(
                            "settings",
                            JSONObject()
                                .put("auth", "noauth")
                                .put("udp", true)
                                .put("ip", "127.0.0.1"),
                        )
                        .put(
                            "sniffing",
                            JSONObject()
                                .put("enabled", true)
                                .put("routeOnly", true)
                                .put(
                                    "destOverride",
                                    JSONArray().put("http").put("tls").put("quic"),
                                ),
                        ),
                ),
            )
            .put(
                "outbounds",
                JSONArray()
                    .put(proxy)
                    .put(JSONObject().put("tag", "dns-out").put("protocol", "dns"))
                    .put(JSONObject().put("tag", "direct").put("protocol", "freedom"))
                    .put(JSONObject().put("tag", "block").put("protocol", "blackhole")),
            )
            .put("routing", routing(bypassDomains))
        return root.toString()
    }

    fun tunnelConfig(logFile: String): String = """
        tunnel:
          mtu: $TUN_MTU
          ipv4: $TUN_ADDRESS
          ipv6: '$TUN_ADDRESS_V6'
        socks5:
          address: 127.0.0.1
          port: $SOCKS_PORT
          udp: 'udp'
        misc:
          tcp-read-write-timeout: 300000
          udp-read-write-timeout: 60000
          log-file: '$logFile'
          log-level: info
    """.trimIndent() + "\n"

    private fun routing(bypassDomains: Set<String>): JSONObject {
        val rules = JSONArray()
        rules.put(
            JSONObject()
                .put("type", "field")
                .put("inboundTag", JSONArray().put("socks-in"))
                .put("port", "53")
                .put("outboundTag", "dns-out"),
        )
        rules.put(
            JSONObject()
                .put("type", "field")
                .put("inboundTag", JSONArray().put("dns-in"))
                .put("outboundTag", "proxy"),
        )
        rules.put(
            JSONObject()
                .put("type", "field")
                .put("network", "udp")
                .put("outboundTag", "block"),
        )
        bypassDomains.map { it.trim() }.filter { it.isNotEmpty() }.distinct().forEach { domain ->
            rules.put(
                JSONObject()
                    .put("type", "field")
                    .put("domain", JSONArray().put("domain:$domain"))
                    .put("outboundTag", "direct"),
            )
        }
        return JSONObject()
            .put("domainStrategy", "AsIs")
            .put("rules", rules)
    }

    private fun parse(storedConf: String): VlessLink {
        val trimmed = storedConf.trim()
        val vless = trimmed.lineSequence()
            .map { it.trim() }
            .firstOrNull { it.startsWith("vless://", ignoreCase = true) }
        if (vless != null) return parseVless(vless)
        if (trimmed.startsWith("{")) return parseJson(trimmed)
        throw IllegalArgumentException("Ключ XRay не распознан")
    }

    private fun parseVless(uri: String): VlessLink {
        val body = uri.substringAfter("://").substringBefore("#")
        val main = body.substringBefore("?")
        val user = decode(main.substringBefore("@"))
        val hostPort = main.substringAfter("@", "")
        if (!main.contains("@") || user.isBlank() || hostPort.isBlank()) {
            throw IllegalArgumentException("Ключ XRay не распознан")
        }
        val (host, port) = splitHostPort(hostPort)
        val params = parseQuery(body.substringAfter("?", ""))
        val security = params["security"].orEmpty().ifBlank { "reality" }
        return validated(
            VlessLink(
                uuid = user,
                host = host,
                port = port,
                encryption = params["encryption"].orEmpty().ifBlank { "none" },
                flow = params["flow"].orEmpty(),
                network = params["type"].orEmpty().ifBlank { "tcp" },
                security = security,
                sni = params["sni"].orEmpty(),
                fingerprint = params["fp"].orEmpty().ifBlank { "chrome" },
                publicKey = params["pbk"].orEmpty(),
                shortId = params["sid"].orEmpty(),
                spiderX = params["spx"] ?: "/",
            ),
        )
    }

    private fun parseJson(text: String): VlessLink {
        val root = JSONObject(text)
        val outbounds = root.optJSONArray("outbounds")
            ?: throw IllegalArgumentException("Ключ XRay не распознан")
        var outbound: JSONObject? = null
        for (index in 0 until outbounds.length()) {
            val item = outbounds.optJSONObject(index) ?: continue
            if (item.optString("protocol").equals("vless", ignoreCase = true)) {
                outbound = item
                break
            }
        }
        val vless = outbound ?: throw IllegalArgumentException("Ключ XRay не распознан")
        val vnext = vless.optJSONObject("settings")
            ?.optJSONArray("vnext")
            ?.optJSONObject(0)
            ?: throw IllegalArgumentException("Ключ XRay не распознан")
        val user = vnext.optJSONArray("users")?.optJSONObject(0)
        val stream = vless.optJSONObject("streamSettings")
        val reality = stream?.optJSONObject("realitySettings")
        val security = stream?.optString("security").orEmpty().ifBlank { "reality" }
        return validated(
            VlessLink(
                uuid = user?.optString("id").orEmpty(),
                host = vnext.optString("address").trim(),
                port = vnext.optInt("port"),
                encryption = user?.optString("encryption").orEmpty().ifBlank { "none" },
                flow = user?.optString("flow").orEmpty(),
                network = stream?.optString("network").orEmpty().ifBlank { "tcp" },
                security = security,
                sni = reality?.optString("serverName").orEmpty().ifBlank {
                    stream?.optJSONObject("tlsSettings")?.optString("serverName").orEmpty()
                },
                fingerprint = reality?.optString("fingerprint").orEmpty().ifBlank { "chrome" },
                publicKey = reality?.optString("publicKey").orEmpty(),
                shortId = reality?.optString("shortId").orEmpty(),
                spiderX = reality?.optString("spiderX") ?: "/",
            ),
        )
    }

    private fun validated(link: VlessLink): VlessLink {
        if (link.uuid.isBlank() || link.host.isBlank() || link.port !in 1..65535) {
            throw IllegalArgumentException("Ключ XRay не распознан")
        }
        if (link.security.equals("reality", ignoreCase = true)) {
            if (link.publicKey.isBlank() || link.sni.isBlank()) {
                throw IllegalArgumentException("В ключе XRay не хватает параметров Reality")
            }
        }
        return link
    }

    private fun splitHostPort(value: String): Pair<String, Int> {
        val trimmed = decode(value.trim())
        val host: String
        val portText: String
        if (trimmed.startsWith("[")) {
            val end = trimmed.indexOf(']')
            if (end <= 1) throw IllegalArgumentException("Ключ XRay не распознан")
            host = trimmed.substring(1, end)
            portText = trimmed.substring(end + 1).removePrefix(":")
        } else {
            val colon = trimmed.lastIndexOf(':')
            if (colon <= 0) throw IllegalArgumentException("Ключ XRay не распознан")
            host = trimmed.substring(0, colon)
            portText = trimmed.substring(colon + 1)
        }
        val port = portText.toIntOrNull() ?: throw IllegalArgumentException("Ключ XRay не распознан")
        return host to port
    }

    private fun parseQuery(query: String): Map<String, String> {
        if (query.isBlank()) return emptyMap()
        return query.split('&').mapNotNull { part ->
            if (part.isBlank()) return@mapNotNull null
            decode(part.substringBefore("=")) to decode(part.substringAfter("=", ""))
        }.toMap()
    }

    private fun decode(value: String): String =
        runCatching { URLDecoder.decode(value, Charsets.UTF_8.name()) }.getOrDefault(value)

    private data class VlessLink(
        val uuid: String,
        val host: String,
        val port: Int,
        val encryption: String,
        val flow: String,
        val network: String,
        val security: String,
        val sni: String,
        val fingerprint: String,
        val publicKey: String,
        val shortId: String,
        val spiderX: String,
    )
}
