package app.vpnadmin.client

import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale
import java.util.TimeZone
import kotlin.math.ceil

object SubscriptionExpiry {
    const val WARNING_DAYS = 2

    fun daysRemaining(expiresAtMillis: Long?, nowMillis: Long = System.currentTimeMillis()): Int? {
        if (expiresAtMillis == null || expiresAtMillis <= 0L) return null
        val seconds = (expiresAtMillis - nowMillis) / 1000.0
        if (seconds <= 0) return -1
        return ceil(seconds / 86400.0).toInt().coerceAtLeast(1)
    }

    fun shouldWarn(expiresAtMillis: Long?, nowMillis: Long = System.currentTimeMillis()): Boolean {
        val remaining = daysRemaining(expiresAtMillis, nowMillis) ?: return false
        return remaining in 0..WARNING_DAYS || remaining == -1
    }

    fun formatDate(expiresAtMillis: Long): String {
        val formatter = SimpleDateFormat("dd.MM.yyyy", Locale("ru"))
        formatter.timeZone = TimeZone.getDefault()
        return formatter.format(Date(expiresAtMillis))
    }

    fun connectedStatus(expiresAtMillis: Long?, nowMillis: Long = System.currentTimeMillis()): ConnectedStatus {
        if (!shouldWarn(expiresAtMillis, nowMillis) || expiresAtMillis == null) {
            return ConnectedStatus("Подключено", null, warning = false)
        }
        val remaining = daysRemaining(expiresAtMillis, nowMillis)
        val title = if (remaining != null && remaining < 0) "Подписка истекла" else "Истекает подписка"
        return ConnectedStatus(title, formatDate(expiresAtMillis), warning = true)
    }

    fun parseIsoToMillis(raw: String?): Long? {
        val value = raw?.trim().orEmpty()
        if (value.isEmpty()) return null
        val patterns = listOf(
            "yyyy-MM-dd'T'HH:mm:ssX",
            "yyyy-MM-dd'T'HH:mm:ss.SSSX",
            "yyyy-MM-dd'T'HH:mm:ss'Z'",
            "yyyy-MM-dd'T'HH:mm:ss",
            "yyyy-MM-dd HH:mm:ss",
            "yyyy-MM-dd",
        )
        for (pattern in patterns) {
            try {
                val formatter = SimpleDateFormat(pattern, Locale.US)
                if (pattern.contains("X") || pattern.contains("'Z'")) {
                    formatter.timeZone = TimeZone.getTimeZone("UTC")
                }
                val parsed = formatter.parse(value) ?: continue
                return parsed.time
            } catch (_: Exception) {
                continue
            }
        }
        value.toLongOrNull()?.takeIf { it > 1_000_000_000_000L }?.let { return it }
        value.toLongOrNull()?.takeIf { it > 1_000_000_000L }?.let { return it * 1000L }
        return null
    }

    data class ConnectedStatus(
        val title: String,
        val date: String?,
        val warning: Boolean,
    )
}
