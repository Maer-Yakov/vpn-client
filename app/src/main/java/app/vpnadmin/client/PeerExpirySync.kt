package app.vpnadmin.client

import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URL
import java.net.URLEncoder

/**
 * Подтягивает «дату отключения пира» (expires_at) из VPN-Admin по адресу клиента.
 */
object PeerExpirySync {
    private const val CONNECT_TIMEOUT_MS = 8_000
    private const val READ_TIMEOUT_MS = 8_000

    data class Result(
        val found: Boolean,
        val expiresAtMillis: Long?,
    )

    fun fetch(key: ImportedKey): Result? {
        val address = key.address.trim()
        if (address.isEmpty() || address == "—") return null
        for (base in panelBases(key)) {
            val result = runCatching { request(base, address) }.getOrNull()
            if (result != null) return result
        }
        return null
    }

    fun panelBases(key: ImportedKey): List<String> {
        val bases = linkedSetOf<String>()
        key.panelUrl?.trim()?.trimEnd('/')?.takeIf { it.isNotEmpty() }?.let(bases::add)
        val host = key.endpoint.substringBefore("%").substringBefore(":").trim()
        if (host.isNotEmpty() && host !in setOf("vpn.example.com", "127.0.0.1", "localhost")) {
            bases.add("https://$host")
            bases.add("http://$host")
            bases.add("http://$host:8000")
            bases.add("http://$host:8080")
            bases.add("https://$host:8443")
        }
        return bases.toList()
    }

    private fun request(base: String, address: String): Result {
        val encoded = URLEncoder.encode(address, Charsets.UTF_8.name())
        val url = URL("$base/api/public/peer-expiry?address=$encoded")
        val connection = (url.openConnection() as HttpURLConnection).apply {
            connectTimeout = CONNECT_TIMEOUT_MS
            readTimeout = READ_TIMEOUT_MS
            requestMethod = "GET"
            setRequestProperty("Accept", "application/json")
            setRequestProperty("User-Agent", "Mvpn-Android")
            instanceFollowRedirects = true
        }
        try {
            val code = connection.responseCode
            val body = (if (code in 200..299) connection.inputStream else connection.errorStream)
                ?.bufferedReader()
                ?.use { it.readText() }
                .orEmpty()
            if (code == 404) return Result(found = false, expiresAtMillis = null)
            if (code !in 200..299) {
                throw IllegalStateException("HTTP $code")
            }
            val json = JSONObject(body)
            if (json.isNull("expires_at")) {
                return Result(found = true, expiresAtMillis = null)
            }
            val raw = json.optString("expires_at")
            val millis = SubscriptionExpiry.parseIsoToMillis(raw)
                ?: throw IllegalStateException("Bad expires_at")
            return Result(found = true, expiresAtMillis = millis)
        } finally {
            connection.disconnect()
        }
    }
}
