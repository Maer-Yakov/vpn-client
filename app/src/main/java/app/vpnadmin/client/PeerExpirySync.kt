package app.vpnadmin.client

import android.content.Context
import android.net.ConnectivityManager
import android.net.Network
import android.net.NetworkCapabilities
import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URL
import java.net.URLEncoder

/**
 * Подтягивает «дату отключения пира» (expires_at) из VPN-Admin по адресу клиента,
 * а также признак «клиент выключен или удалён».
 */
object PeerExpirySync {
    private const val CONNECT_TIMEOUT_MS = 8_000
    private const val READ_TIMEOUT_MS = 8_000

    data class Result(
        val found: Boolean,
        val expiresAtMillis: Long?,
        /** false, если администратор выключил клиента или срок истёк. Старая панель поля не шлёт: тогда true. */
        val enabled: Boolean = true,
        /** true, только если сама панель ответила «такого пира нет». Чужой 404 сюда не попадает. */
        val revoked: Boolean = false,
    ) {
        val accessDenied: Boolean get() = revoked || !enabled
    }

    /**
     * Спрашивает панель. [network] — сеть в обход VPN: если пир отключён в панели, туннель превращается
     * в «чёрную дыру», и запрос через него до панели не дойдёт (приложение так и показывало «Подключено»).
     */
    fun fetch(key: ImportedKey, network: Network? = null): Result? {
        val address = key.address.trim()
        if (address.isEmpty() || address == "—") return null
        for (base in panelBases(key)) {
            val result = runCatching { request(base, address, network) }.getOrNull()
            if (result != null) return result
        }
        return null
    }

    /** Физическая сеть (Wi-Fi или мобильная) без VPN; null, если найти не удалось. */
    fun underlyingNetwork(context: Context): Network? {
        val manager = context.getSystemService(Context.CONNECTIVITY_SERVICE) as? ConnectivityManager ?: return null
        return runCatching {
            manager.allNetworks.firstOrNull { network ->
                val caps = manager.getNetworkCapabilities(network) ?: return@firstOrNull false
                caps.hasCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET) &&
                    !caps.hasTransport(NetworkCapabilities.TRANSPORT_VPN)
            }
        }.getOrNull()
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

    private fun request(base: String, address: String, network: Network?): Result? {
        val encoded = URLEncoder.encode(address, Charsets.UTF_8.name())
        val url = URL("$base/api/public/peer-expiry?address=$encoded")
        val opened = network?.openConnection(url) ?: url.openConnection()
        val connection = (opened as HttpURLConnection).apply {
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
            return parse(code, body)
        } finally {
            connection.disconnect()
        }
    }

    /**
     * Разбор ответа панели. null — ответ не от панели (чужой 404, ошибка сервера): пробуем следующий адрес.
     */
    internal fun parse(code: Int, body: String): Result? {
        if (code == 404) {
            val revoked = runCatching { JSONObject(body).optBoolean("revoked", false) }.getOrDefault(false)
            return if (revoked) Result(found = false, expiresAtMillis = null, revoked = true) else null
        }
        if (code !in 200..299) {
            throw IllegalStateException("HTTP $code")
        }
        val json = JSONObject(body)
        // Старая панель не шлёт enabled/active: считаем клиента включённым.
        val enabled = json.optBoolean("enabled", true) && json.optBoolean("active", true)
        if (json.isNull("expires_at")) {
            return Result(found = true, expiresAtMillis = null, enabled = enabled)
        }
        val raw = json.optString("expires_at")
        val millis = SubscriptionExpiry.parseIsoToMillis(raw)
            ?: throw IllegalStateException("Bad expires_at")
        return Result(found = true, expiresAtMillis = millis, enabled = enabled)
    }
}
