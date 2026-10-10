package app.vpnadmin.client

import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Build
import android.provider.Settings
import androidx.core.content.FileProvider
import org.json.JSONObject
import java.io.File
import java.io.FileOutputStream
import java.net.HttpURLConnection
import java.net.URL
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale
import java.util.TimeZone

data class RemoteRelease(
    val tag: String,
    val versionName: String,
    val publishedAtMillis: Long,
    val assetId: Long,
    val assetName: String,
    val assetSize: Long,
)

data class UpdateCheckResult(
    val release: RemoteRelease?,
    val updateAvailable: Boolean,
    val message: String,
)

object AppUpdater {
    private const val PREFS = "app_updates"
    private const val KEY_LAST_CHECK = "last_check_at"
    private const val KEY_CURRENT_RELEASE_AT = "current_release_at"
    private const val CONNECT_TIMEOUT_MS = 15_000
    private const val READ_TIMEOUT_MS = 60_000
    private const val MAX_APK_BYTES = 250L * 1024L * 1024L

    fun lastCheckAt(context: Context): Long =
        context.getSharedPreferences(PREFS, Context.MODE_PRIVATE).getLong(KEY_LAST_CHECK, 0L)

    fun currentVersionReleasedAt(context: Context): Long =
        context.getSharedPreferences(PREFS, Context.MODE_PRIVATE).getLong(KEY_CURRENT_RELEASE_AT, 0L)

    fun installedAt(context: Context): Long {
        return try {
            val info = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
                context.packageManager.getPackageInfo(
                    context.packageName,
                    PackageManager.PackageInfoFlags.of(0),
                )
            } else {
                @Suppress("DEPRECATION")
                context.packageManager.getPackageInfo(context.packageName, 0)
            }
            info.lastUpdateTime
        } catch (_: Exception) {
            0L
        }
    }

    fun rememberLastCheck(context: Context, at: Long = System.currentTimeMillis()) {
        context.getSharedPreferences(PREFS, Context.MODE_PRIVATE)
            .edit()
            .putLong(KEY_LAST_CHECK, at)
            .apply()
    }

    fun rememberCurrentReleaseAt(context: Context, at: Long) {
        if (at <= 0L) return
        context.getSharedPreferences(PREFS, Context.MODE_PRIVATE)
            .edit()
            .putLong(KEY_CURRENT_RELEASE_AT, at)
            .apply()
    }

    fun checkLatest(context: Context, localVersionName: String = BuildConfig.VERSION_NAME): UpdateCheckResult {
        val token = BuildConfig.GITHUB_UPDATE_TOKEN.trim()
        if (token.isEmpty()) {
            return UpdateCheckResult(null, false, "Не задан токен доступа к GitHub")
        }
        val connection = openApi(
            url = "https://api.github.com/repos/${BuildConfig.GITHUB_REPO}/releases/latest",
            accept = "application/vnd.github+json",
            token = token,
        )
        try {
            val code = connection.responseCode
            val body = (if (code in 200..299) connection.inputStream else connection.errorStream)
                ?.bufferedReader()
                ?.use { it.readText() }
                .orEmpty()
            if (code !in 200..299) {
                return UpdateCheckResult(null, false, githubErrorMessage(code, body))
            }
            val release = parseRelease(body)
                ?: return UpdateCheckResult(null, false, "В релизе нет APK")
            if (release.versionName == localVersionName || !isNewerVersion(release.versionName, localVersionName)) {
                rememberCurrentReleaseAt(context, release.publishedAtMillis)
                return UpdateCheckResult(release, false, "Установлена актуальная версия")
            }
            return UpdateCheckResult(release, true, "Доступна версия ${release.versionName}")
        } finally {
            connection.disconnect()
            rememberLastCheck(context)
        }
    }

    fun downloadApk(context: Context, release: RemoteRelease): File {
        val token = BuildConfig.GITHUB_UPDATE_TOKEN.trim()
        require(token.isNotEmpty()) { "Не задан токен доступа к GitHub" }
        require(release.assetSize in 1..MAX_APK_BYTES) { "Некорректный размер APK" }

        val dir = File(context.cacheDir, "updates").apply { mkdirs() }
        dir.listFiles()?.forEach { it.delete() }
        val target = File(dir, release.assetName.ifBlank { "update.apk" })

        val connection = openApi(
            url = "https://api.github.com/repos/${BuildConfig.GITHUB_REPO}/releases/assets/${release.assetId}",
            accept = "application/octet-stream",
            token = token,
        )
        try {
            val code = connection.responseCode
            if (code !in 200..299) {
                val body = connection.errorStream?.bufferedReader()?.use { it.readText() }.orEmpty()
                throw IllegalStateException(githubErrorMessage(code, body))
            }
            val length = connection.contentLengthLong
            if (length > MAX_APK_BYTES) {
                throw IllegalStateException("Файл обновления слишком большой")
            }
            connection.inputStream.use { input ->
                FileOutputStream(target).use { output ->
                    val buffer = ByteArray(64 * 1024)
                    var total = 0L
                    while (true) {
                        val read = input.read(buffer)
                        if (read < 0) break
                        total += read
                        if (total > MAX_APK_BYTES) {
                            throw IllegalStateException("Файл обновления слишком большой")
                        }
                        output.write(buffer, 0, read)
                    }
                }
            }
            if (!target.isFile || target.length() <= 0L) {
                throw IllegalStateException("Не удалось скачать обновление")
            }
            return target
        } finally {
            connection.disconnect()
        }
    }

    fun apkUri(context: Context, file: File): Uri =
        FileProvider.getUriForFile(context, "${context.packageName}.update", file)

    fun installIntent(context: Context, file: File): Intent {
        val uri = apkUri(context, file)
        return Intent(Intent.ACTION_VIEW).apply {
            setDataAndType(uri, "application/vnd.android.package-archive")
            addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
            addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        }
    }

    fun canInstallPackages(context: Context): Boolean {
        return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            context.packageManager.canRequestPackageInstalls()
        } else {
            true
        }
    }

    fun installPermissionSettingsIntent(context: Context): Intent =
        Intent(
            Settings.ACTION_MANAGE_UNKNOWN_APP_SOURCES,
            Uri.parse("package:${context.packageName}"),
        )

    fun formatDate(millis: Long): String {
        if (millis <= 0L) return "—"
        val formatter = SimpleDateFormat("dd.MM.yyyy HH:mm", Locale("ru"))
        formatter.timeZone = TimeZone.getDefault()
        return formatter.format(Date(millis))
    }

    internal fun isNewerVersion(remote: String, local: String): Boolean {
        val left = parseVersionParts(remote)
        val right = parseVersionParts(local)
        val size = maxOf(left.size, right.size)
        for (index in 0 until size) {
            val a = left.getOrElse(index) { 0 }
            val b = right.getOrElse(index) { 0 }
            if (a != b) return a > b
        }
        return false
    }

    internal fun parseVersionParts(raw: String): List<Int> {
        val cleaned = raw.trim().removePrefix("v").removePrefix("V")
        val core = cleaned.takeWhile { it.isDigit() || it == '.' }
        if (core.isBlank()) return listOf(0)
        return core.split('.').map { part -> part.toIntOrNull()?.coerceAtLeast(0) ?: 0 }
    }

    private fun parseRelease(body: String): RemoteRelease? {
        val json = JSONObject(body)
        val tag = json.optString("tag_name").trim()
        if (tag.isEmpty()) return null
        val versionName = tag.removePrefix("v").removePrefix("V")
        val publishedAt = parseIsoTime(json.optString("published_at"))
        val assets = json.optJSONArray("assets") ?: return null
        for (index in 0 until assets.length()) {
            val asset = assets.optJSONObject(index) ?: continue
            val name = asset.optString("name")
            if (!name.endsWith(".apk", ignoreCase = true)) continue
            val id = asset.optLong("id")
            val size = asset.optLong("size")
            if (id <= 0L) continue
            return RemoteRelease(
                tag = tag,
                versionName = versionName,
                publishedAtMillis = publishedAt,
                assetId = id,
                assetName = name,
                assetSize = size,
            )
        }
        return null
    }

    private fun parseIsoTime(value: String): Long {
        if (value.isBlank()) return 0L
        return try {
            val formatter = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss'Z'", Locale.US)
            formatter.timeZone = TimeZone.getTimeZone("UTC")
            formatter.parse(value)?.time ?: 0L
        } catch (_: Exception) {
            0L
        }
    }

    private fun openApi(url: String, accept: String, token: String): HttpURLConnection {
        val connection = (URL(url).openConnection() as HttpURLConnection).apply {
            instanceFollowRedirects = true
            connectTimeout = CONNECT_TIMEOUT_MS
            readTimeout = READ_TIMEOUT_MS
            requestMethod = "GET"
            setRequestProperty("Accept", accept)
            setRequestProperty("User-Agent", "Mvpn-Android")
            setRequestProperty("X-GitHub-Api-Version", "2022-11-28")
            setRequestProperty("Authorization", "Bearer $token")
        }
        return connection
    }

    private fun githubErrorMessage(code: Int, body: String): String {
        return when (code) {
            401, 403 -> "Нет доступа к репозиторию обновлений"
            404 -> "Релизы не найдены"
            else -> "Ошибка проверки обновлений ($code)"
        }.also { _ -> body }
    }
}
