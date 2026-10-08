package app.vpnadmin.client

import java.net.IDN
import java.net.URI
import java.util.Locale

object SiteDomain {
    private val labelPattern = Regex("[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?")

    fun normalize(input: String): String {
        val value = input.trim()
        require(value.isNotEmpty()) { "Введите домен сайта" }

        val uri = runCatching {
            if (value.contains("://")) URI(value) else URI("https://$value")
        }.getOrElse { throw IllegalArgumentException("Укажите домен, например example.com") }
        require(uri.scheme.equals("https", ignoreCase = true) || uri.scheme.equals("http", ignoreCase = true)) {
            "Для сайта разрешены только http:// и https://"
        }
        require(uri.rawUserInfo == null) { "Вместо ссылки укажите только домен сайта" }

        val rawHost = uri.host ?: uri.rawAuthority?.substringBefore(':')
            ?: throw IllegalArgumentException("Не удалось определить домен")
        val host = try {
            IDN.toASCII(rawHost.trimEnd('.'), IDN.USE_STD3_ASCII_RULES).lowercase(Locale.ROOT)
        } catch (_: IllegalArgumentException) {
            throw IllegalArgumentException("Некорректный домен сайта")
        }
        require(host.length in 1..253 && host.contains('.')) { "Укажите полное доменное имя" }
        require(host.split('.').all(labelPattern::matches)) { "Некорректный домен сайта" }
        require(!isIpv4Literal(host)) { "Укажите домен, а не IP-адрес" }
        return host
    }

    private fun isIpv4Literal(host: String): Boolean =
        host.split('.').let { labels ->
            labels.size == 4 && labels.all { label -> label.toIntOrNull()?.let { it in 0..255 } == true }
        }
}