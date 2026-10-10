package app.vpnadmin.client

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.Intent
import android.content.pm.PackageManager
import android.content.pm.ServiceInfo
import android.net.VpnService
import android.os.Build
import android.os.ParcelFileDescriptor
import android.util.Log
import libv2ray.CoreCallbackHandler
import libv2ray.CoreController
import libv2ray.Libv2ray
import java.io.File

/**
 * Туннель Xray. Служба в отдельном процессе, чтобы ядро Xray не делило
 * загрузчик Go с AmneziaWG. Своё приложение исключено из VPN: исходящие
 * сокеты ядра идут мимо туннеля и не замыкаются в петлю.
 */
class XrayVpnService : VpnService() {
    private val lock = Any()
    private val callback = object : CoreCallbackHandler {
        override fun onEmitStatus(code: Long, message: String?): Long {
            if (!message.isNullOrBlank()) Log.i(TAG, message)
            return 0
        }
        override fun shutdown(): Long = 0
        override fun startup(): Long = 0
    }

    private var generation = 0
    private var pendingRequest: String? = null
    private var tun: ParcelFileDescriptor? = null
    private var core: CoreController? = null
    private var hevOn = false
    private var statsThread: Thread? = null
    private var rxBytes = 0L
    private var txBytes = 0L

    @Volatile
    private var handshakeAt = 0L

    @Volatile
    private var running = false

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        startInForeground()
        if (intent == null || intent.action == XraySession.ACTION_STOP) {
            stopTunnel()
            stopSelf()
            return START_NOT_STICKY
        }
        threadStart(intent)
        return START_NOT_STICKY
    }

    override fun onRevoke() {
        stopTunnel()
        stopSelf()
    }

    override fun onDestroy() {
        stopTunnel()
        super.onDestroy()
    }

    private fun threadStart(intent: Intent) {
        Thread({ startTunnel(intent) }, "xray-start").start()
    }

    private fun startTunnel(intent: Intent) {
        val request = intent.getStringExtra(XraySession.EXTRA_REQUEST).orEmpty()
        val myGeneration = synchronized(lock) {
            generation += 1
            val previous = pendingRequest
            pendingRequest = request
            stopTunnelLocked()
            if (previous != null && previous != request) {
                publish(previous, false, "Подключение прервано")
            }
            generation
        }
        var opened: ParcelFileDescriptor? = null
        var controller: CoreController? = null
        var hevStarted = false
        try {
            val json = intent.getStringExtra(XraySession.EXTRA_CONFIG)?.takeIf { it.isNotBlank() }
                ?: throw IllegalStateException("Нет конфигурации XRay")
            opened = openTun(intent)
            Libv2ray.initCoreEnv(filesDir.absolutePath, "")
            val startedCore = CoreController(callback)
            controller = startedCore
            startedCore.startLoop(json, 0)
            val tunFd = opened?.fd ?: throw IllegalStateException("Не удалось открыть VPN")
            hevStarted = startHev(tunFd)
            if (!hevStarted) {
                runCatching { hev.htproxy.TProxyService.TProxyStopService() }
                throw IllegalStateException("Не удалось запустить туннель")
            }
            synchronized(lock) {
                if (generation != myGeneration) {
                    runCatching { hev.htproxy.TProxyService.TProxyStopService() }
                    runCatching { controller?.stopLoop() }
                    runCatching { opened?.close() }
                    opened = null
                    return
                }
                tun = opened
                opened = null
                hevOn = true
                hevStarted = false
                core = controller
                controller = null
                running = true
                rxBytes = 0
                txBytes = 0
                handshakeAt = 0
                pendingRequest = null
                writeState(true, 0, 0)
            }
            startStats()
            publish(request, true, null)
        } catch (error: Exception) {
            Log.e(TAG, "xray start failed", error)
            if (hevStarted) runCatching { hev.htproxy.TProxyService.TProxyStopService() }
            runCatching { controller?.stopLoop() }
            runCatching { opened?.close() }
            synchronized(lock) {
                if (generation == myGeneration) {
                    pendingRequest = null
                    stopTunnelLocked()
                }
            }
            publish(request, false, error.message?.takeIf { it.isNotBlank() } ?: "Не удалось подключиться")
            stopSelf()
        } catch (error: LinkageError) {
            Log.e(TAG, "xray library failed", error)
            if (hevStarted) runCatching { hev.htproxy.TProxyService.TProxyStopService() }
            runCatching { controller?.stopLoop() }
            runCatching { opened?.close() }
            synchronized(lock) {
                if (generation == myGeneration) {
                    pendingRequest = null
                    stopTunnelLocked()
                }
            }
            publish(request, false, "Не удалось запустить XRay")
            stopSelf()
        }
    }

    private fun startHev(tunFd: Int): Boolean {
        val logFile = File(filesDir, "hev.log")
        val config = File(filesDir, "hev-socks5-tunnel.yaml")
        config.writeText(XrayConfig.tunnelConfig(logFile.absolutePath))
        val started = hev.htproxy.TProxyService.TProxyStartService(config.absolutePath, tunFd)
        if (!started) return false
        Thread.sleep(300)
        return hev.htproxy.TProxyService.TProxyIsRunning()
    }

    private fun openTun(intent: Intent): ParcelFileDescriptor {
        val builder = Builder()
        builder.setSession("Mvpn")
        builder.setMtu(XrayConfig.TUN_MTU)
        builder.addAddress(XrayConfig.TUN_ADDRESS, 32)
        builder.addRoute("0.0.0.0", 0)
        builder.addAddress(XrayConfig.TUN_ADDRESS_V6, 128)
        builder.addRoute("::", 0)
        builder.addDnsServer("1.1.1.1")
        builder.addDnsServer("8.8.8.8")
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            builder.setMetered(false)
        }
        val mode = runCatching {
            AppRouteMode.valueOf(intent.getStringExtra(XraySession.EXTRA_MODE) ?: AppRouteMode.AllTraffic.name)
        }.getOrDefault(AppRouteMode.AllTraffic)
        val selected = intent.getStringArrayListExtra(XraySession.EXTRA_PACKAGES)?.toSet().orEmpty()
        for (name in disallowedPackages(mode, selected)) {
            try {
                builder.addDisallowedApplication(name)
            } catch (_: PackageManager.NameNotFoundException) {
                // Приложение уже удалено. Остальные исключения сохраняются.
            }
        }
        return builder.establish() ?: throw IllegalStateException("Разрешите создание VPN-подключения")
    }

    private fun disallowedPackages(mode: AppRouteMode, selected: Set<String>): List<String> {
        val own = packageName
        val chosen = selected.filter(SplitTunnelSettings::isValidPackageName).toSet()
        val names = when (mode) {
            AppRouteMode.AllTraffic -> listOf(own)
            AppRouteMode.SelectedBypassVpn -> (chosen + own).distinct()
            AppRouteMode.SelectedThroughVpn -> {
                val installed = launcherPackages()
                if (installed.isEmpty()) {
                    throw IllegalStateException("Не удалось прочитать список приложений")
                }
                (installed.filter { it !in chosen } + own).distinct()
            }
        }
        return names
    }

    @Suppress("DEPRECATION")
    private fun launcherPackages(): Set<String> {
        val launcher = Intent(Intent.ACTION_MAIN).addCategory(Intent.CATEGORY_LAUNCHER)
        val activities = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            packageManager.queryIntentActivities(launcher, PackageManager.ResolveInfoFlags.of(0))
        } else {
            packageManager.queryIntentActivities(launcher, 0)
        }
        return activities.mapNotNull { it.activityInfo?.packageName }.toSet()
    }

    private fun startStats() {
        statsThread?.interrupt()
        statsThread = Thread({
            while (!Thread.currentThread().isInterrupted && running) {
                val controller = core
                if (controller != null) {
                    val line = runCatching { controller.queryAllOutboundTrafficStats() }.getOrDefault("")
                    accumulate(line)
                    writeState(true, rxBytes, txBytes)
                }
                try {
                    Thread.sleep(2_000)
                } catch (_: InterruptedException) {
                    break
                }
            }
        }, "xray-stats")
        statsThread?.start()
        Thread({
            val controller = core ?: return@Thread
            val delayMillis = runCatching {
                controller.measureDelay("https://www.google.com/generate_204")
            }.getOrNull()
            if (running && delayMillis != null && delayMillis >= 0L) {
                handshakeAt = System.currentTimeMillis()
            }
        }, "xray-probe").start()
    }

    private fun accumulate(line: String) {
        line.split(';').forEach { part ->
            val bits = part.split(',')
            if (bits.size != 3) return@forEach
            val value = bits[2].toLongOrNull() ?: return@forEach
            when (bits[1]) {
                "downlink" -> {
                    rxBytes += value
                    if (value > 0) {
                        handshakeAt = System.currentTimeMillis()
                        Log.i(TAG, "downlink $value")
                    }
                }
                "uplink" -> {
                    txBytes += value
                    if (value > 0) Log.i(TAG, "uplink $value")
                }
            }
        }
    }

    private fun stopTunnel() {
        val request = synchronized(lock) {
            generation += 1
            val request = pendingRequest
            pendingRequest = null
            stopTunnelLocked()
            request
        }
        if (request != null) publish(request, false, "Подключение прервано")
    }

    private fun stopTunnelLocked() {
        running = false
        statsThread?.interrupt()
        statsThread = null
        if (hevOn) {
            runCatching { hev.htproxy.TProxyService.TProxyStopService() }
            hevOn = false
        }
        runCatching { core?.stopLoop() }
        core = null
        runCatching { tun?.close() }
        tun = null
        rxBytes = 0
        txBytes = 0
        handshakeAt = 0
        writeState(false, 0, 0)
    }

    private fun writeState(up: Boolean, rx: Long, tx: Long) {
        val file = File(filesDir, "xray-tunnel.state")
        val tmp = File(filesDir, "xray-tunnel.state.tmp")
        tmp.writeText("${if (up) 1 else 0}\n$rx\n$tx\n${System.currentTimeMillis()}\n$handshakeAt\n")
        if (!tmp.renameTo(file)) {
            file.writeText(tmp.readText())
            tmp.delete()
        }
    }

    private fun publish(request: String, ok: Boolean, error: String?) {
        if (request.isBlank()) return
        XraySession.writeResult(this, request, ok, error)
    }

    private fun startInForeground() {
        val manager = getSystemService(NotificationManager::class.java)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(CHANNEL_ID, "VPN", NotificationManager.IMPORTANCE_LOW)
            channel.setShowBadge(false)
            manager.createNotificationChannel(channel)
        }
        val open = PendingIntent.getActivity(
            this,
            0,
            Intent(this, MainActivity::class.java),
            PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT,
        )
        val notification = Notification.Builder(this, CHANNEL_ID)
            .setContentTitle("Mvpn")
            .setContentText("Подключено")
            .setSmallIcon(R.drawable.ic_logo)
            .setContentIntent(open)
            .setOngoing(true)
            .build()
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.UPSIDE_DOWN_CAKE) {
            startForeground(NOTIFICATION_ID, notification, ServiceInfo.FOREGROUND_SERVICE_TYPE_SPECIAL_USE)
        } else {
            startForeground(NOTIFICATION_ID, notification)
        }
    }

    private companion object {
        const val TAG = "MvpnXray"
        const val CHANNEL_ID = "mvpn-vpn"
        const val NOTIFICATION_ID = 42
    }
}
