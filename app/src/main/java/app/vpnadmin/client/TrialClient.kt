package app.vpnadmin.client

import android.content.Context
import android.provider.Settings
import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URL

object TrialClient {
    const val PANEL_URL = "http://85.137.164.156:8080"
    private const val CONNECT_TIMEOUT_MS = 15_000
    private const val READ_TIMEOUT_MS = 20_000

    fun androidId(context: Context): String {
        return Settings.Secure.getString(context.contentResolver, Settings.Secure.ANDROID_ID).orEmpty().trim()
    }

    fun claim(deviceId: String): String {
        val connection = (URL("$PANEL_URL/api/public/trial").openConnection() as HttpURLConnection).apply {
            requestMethod = "POST"
            connectTimeout = CONNECT_TIMEOUT_MS
            readTimeout = READ_TIMEOUT_MS
            doOutput = true
            setRequestProperty("Accept", "application/json")
            setRequestProperty("Content-Type", "application/json")
            setRequestProperty("User-Agent", "Mvpn-Android")
        }
        try {
            val payload = JSONObject().put("device_id", deviceId).toString()
            connection.outputStream.use { it.write(payload.toByteArray()) }
            val code = connection.responseCode
            val body = (if (code in 200..299) connection.inputStream else connection.errorStream)
                ?.bufferedReader()
                ?.use { it.readText() }
                .orEmpty()
            if (code !in 200..299) {
                throw IllegalStateException(messageOf(body, code))
            }
            val config = JSONObject(body).optString("config")
            if (!config.startsWith("vpn://")) {
                throw IllegalStateException("Сервер не прислал ключ")
            }
            return config
        } finally {
            connection.disconnect()
        }
    }

    private fun messageOf(body: String, code: Int): String {
        val detail = runCatching { JSONObject(body).optString("detail") }.getOrNull().orEmpty()
        if (detail.isNotBlank()) return detail
        return if (code == 409) {
            "Тестовый сервер можно получить только один раз"
        } else {
            "Не удалось получить тестовый сервер"
        }
    }
}
