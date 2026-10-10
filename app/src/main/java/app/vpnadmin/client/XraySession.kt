package app.vpnadmin.client

import android.content.Context
import android.content.Intent
import androidx.core.content.ContextCompat
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.TimeoutCancellationException
import kotlinx.coroutines.delay
import kotlinx.coroutines.withTimeout
import java.io.File
import java.util.UUID

/**
 * Запуск Xray в отдельном процессе службы. Состояние туннеля читается из файла,
 * потому что процесс службы не делит память с экраном.
 */
object XraySession {
    const val ACTION_STOP = "app.vpnadmin.client.XRAY_STOP"
    const val EXTRA_REQUEST = "request"
    const val EXTRA_CONFIG = "config"
    const val EXTRA_MODE = "mode"
    const val EXTRA_PACKAGES = "packages"

    private const val STATE_FILE = "xray-tunnel.state"
    private const val RESULT_FILE = "xray-result.txt"
    private const val FRESH_MS = 8_000L

    fun isRunning(context: Context): Boolean {
        val lines = readState(context) ?: return false
        if (lines.getOrNull(0)?.trim() != "1") return false
        val stamp = lines.getOrNull(3)?.trim()?.toLongOrNull() ?: return false
        return System.currentTimeMillis() - stamp < FRESH_MS
    }

    fun snapshot(context: Context): TrafficSnapshot {
        val lines = readState(context) ?: return TrafficSnapshot(0, 0, 0)
        return TrafficSnapshot(
            rxBytes = lines.getOrNull(1)?.trim()?.toLongOrNull() ?: 0L,
            txBytes = lines.getOrNull(2)?.trim()?.toLongOrNull() ?: 0L,
            handshakeEpochMillis = lines.getOrNull(4)?.trim()?.toLongOrNull() ?: 0L,
        )
    }

    suspend fun connect(context: Context, configJson: String, split: SplitTunnelSettings) {
        val request = UUID.randomUUID().toString()
        File(context.filesDir, RESULT_FILE).delete()
        val intent = Intent(context, XrayVpnService::class.java)
            .putExtra(EXTRA_REQUEST, request)
            .putExtra(EXTRA_CONFIG, configJson)
            .putExtra(EXTRA_MODE, split.mode.name)
            .putStringArrayListExtra(EXTRA_PACKAGES, ArrayList(split.packages))
        try {
            withTimeout(25_000) {
                ContextCompat.startForegroundService(context, intent)
                while (true) {
                    val result = readResult(context, request)
                    if (result != null) {
                        if (!result.first) {
                            throw IllegalStateException(result.second.ifBlank { "Не удалось подключиться" })
                        }
                        return@withTimeout
                    }
                    delay(200)
                }
            }
        } catch (error: TimeoutCancellationException) {
            stop(context)
            throw IllegalStateException("Не удалось запустить подключение")
        } catch (error: CancellationException) {
            stop(context)
            throw error
        }
    }

    fun stop(context: Context) {
        val intent = Intent(context, XrayVpnService::class.java).setAction(ACTION_STOP)
        runCatching { context.startService(intent) }
            .onFailure { runCatching { ContextCompat.startForegroundService(context, intent) } }
    }

    internal fun writeResult(context: Context, request: String, ok: Boolean, error: String?) {
        val file = File(context.filesDir, RESULT_FILE)
        val tmp = File(context.filesDir, "$RESULT_FILE.tmp")
        tmp.writeText("$request\n${if (ok) 1 else 0}\n${error.orEmpty().lineSequence().firstOrNull().orEmpty()}\n")
        if (!tmp.renameTo(file)) {
            file.writeText(tmp.readText())
            tmp.delete()
        }
    }

    private fun readResult(context: Context, request: String): Pair<Boolean, String>? {
        val lines = runCatching { File(context.filesDir, RESULT_FILE).readLines() }.getOrNull() ?: return null
        if (lines.getOrNull(0)?.trim() != request) return null
        return (lines.getOrNull(1)?.trim() == "1") to lines.getOrNull(2).orEmpty()
    }

    private fun readState(context: Context): List<String>? {
        val file = File(context.filesDir, STATE_FILE)
        if (!file.isFile) return null
        return runCatching { file.readLines() }.getOrNull()
    }
}
