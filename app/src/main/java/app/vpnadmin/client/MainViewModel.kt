package app.vpnadmin.client

import android.app.Application
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.graphics.drawable.Drawable
import android.os.Build
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.isActive
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import org.amnezia.awg.backend.BackendException
import org.amnezia.awg.backend.Tunnel
import org.amnezia.awg.config.BadConfigException
import java.io.InputStream
import java.util.concurrent.CancellationException

enum class Phase {
    Idle,
    Connecting,
    Connected,
}

enum class Screen {
    Home,
    Servers,
    Import,
    Scan,
    Settings,
    SplitTunnel,
    Update,
    Backup,
}

enum class UpdatePhase {
    Idle,
    Checking,
    Downloading,
}

data class InstalledApp(
    val packageName: String,
    val label: String,
    val icon: Drawable? = null,
)

data class UiState(
    val servers: List<StoredServer> = emptyList(),
    val installedApps: List<InstalledApp> = emptyList(),
    val installedAppsLoaded: Boolean = false,
    val activeId: String? = null,
    val screen: Screen = Screen.Home,
    val draft: String = "",
    val phase: Phase = Phase.Idle,
    val error: String? = null,
    val rxBytes: Long = 0,
    val txBytes: Long = 0,
    val handshake: String = "—",
    val connectedSince: Long? = null,
    val now: Long = System.currentTimeMillis(),
    val updatePhase: UpdatePhase = UpdatePhase.Idle,
    val updateMessage: String? = null,
    val updateAvailable: RemoteRelease? = null,
    val currentVersionReleasedAt: Long = 0L,
    val lastUpdateCheckAt: Long = 0L,
    val appUpdatedAt: Long = 0L,
    val pendingInstallApk: String? = null,
    val notice: String? = null,
    val claimingTrial: Boolean = false,
) {
    val active: StoredServer?
        get() = servers.firstOrNull { it.id == activeId }
}

class MainViewModel(app: Application) : AndroidViewModel(app) {
    private val store = ProfileStore(app)
    private val tunnels = (app as VpnApp).tunnels
    private val state: MutableStateFlow<UiState>
    val ui: StateFlow<UiState>

    init {
        val library = store.load()
        val running = tunnels.isUp()
        val since = if (running) storedSince() else null
        if (!running) rememberSince(null)
        state = MutableStateFlow(
            UiState(
                servers = library.servers,
                activeId = library.activeId,
                error = library.warning,
                phase = if (running) Phase.Connected else Phase.Idle,
                connectedSince = since,
                currentVersionReleasedAt = AppUpdater.currentVersionReleasedAt(app),
                lastUpdateCheckAt = AppUpdater.lastCheckAt(app),
                appUpdatedAt = AppUpdater.installedAt(app),
            ),
        )
        ui = state
        viewModelScope.launch {
            val apps = withContext(Dispatchers.IO) { loadInstalledApps(app) }
            state.value = state.value.copy(installedApps = apps, installedAppsLoaded = true)
        }
        checkForUpdate(manual = false)
        refreshPeerExpiry()
        tunnels.listener = { tunnelState ->
            if (tunnelState == Tunnel.State.DOWN) {
                if (state.value.phase != Phase.Connecting) rememberSince(null)
                state.value = state.value.copy(
                    phase = if (state.value.phase == Phase.Connecting) Phase.Connecting else Phase.Idle,
                    rxBytes = 0,
                    txBytes = 0,
                    handshake = "—",
                    connectedSince = if (state.value.phase == Phase.Connecting) state.value.connectedSince else null,
                )
            }
        }
        viewModelScope.launch {
            var tick = 0
            while (isActive) {
                delay(1_000)
                tick += 1
                if (state.value.phase != Phase.Connected) continue
                var next = state.value.copy(now = System.currentTimeMillis())
                if (tick % 2 == 0) {
                    val snapshot = withContext(Dispatchers.IO) {
                        runCatching { tunnels.snapshot() }.getOrNull()
                    }
                    if (snapshot != null) {
                        next = next.copy(
                            rxBytes = snapshot.rxBytes,
                            txBytes = snapshot.txBytes,
                            handshake = formatHandshake(snapshot.handshakeEpochMillis),
                        )
                    }
                }
                if (state.value.phase == Phase.Connected) {
                    state.value = next
                }
            }
        }
    }

    fun show(screen: Screen) {
        state.value = state.value.copy(
            screen = screen,
            error = null,
            notice = null,
            draft = if (screen == Screen.Import) "" else state.value.draft,
        )
    }

    fun updateDraft(value: String) {
        state.value = state.value.copy(draft = value, error = null, notice = null)
    }

    fun refreshConnection() {
        if (state.value.phase == Phase.Connecting) return
        val running = tunnels.isUp()
        if (running && state.value.phase != Phase.Connected) {
            val since = storedSince()
            state.value = state.value.copy(
                phase = Phase.Connected,
                connectedSince = since,
                now = System.currentTimeMillis(),
                error = null,
            )
            refreshPeerExpiry()
        } else if (!running && state.value.phase == Phase.Connected) {
            rememberSince(null)
            state.value = state.value.copy(
                phase = Phase.Idle,
                rxBytes = 0,
                txBytes = 0,
                handshake = "—",
                connectedSince = null,
            )
        } else if (running && state.value.phase == Phase.Connected) {
            refreshPeerExpiry()
        }
    }

    fun report(message: String) {
        state.value = state.value.copy(error = message, notice = null)
    }

    fun setActiveExpiresInDays(days: Int) {
        val active = state.value.active ?: return
        val millis = System.currentTimeMillis() + days.coerceAtLeast(0) * 86_400_000L
        val library = store.setExpiresAt(active.id, millis)
        state.value = state.value.copy(
            servers = library.servers,
            activeId = library.activeId,
            notice = "Тестовый срок подписки: ${SubscriptionExpiry.formatDate(millis)}",
            error = null,
        )
    }

    fun refreshPeerExpiry() {
        val active = state.value.active ?: return
        viewModelScope.launch {
            val remote = withContext(Dispatchers.IO) {
                runCatching { PeerExpirySync.fetch(active.key) }.getOrNull()
            } ?: return@launch
            if (!remote.found) return@launch
            if (remote.expiresAtMillis == active.key.expiresAtMillis) return@launch
            val library = store.setExpiresAt(active.id, remote.expiresAtMillis)
            state.value = state.value.copy(
                servers = library.servers,
                activeId = library.activeId,
            )
        }
    }

    fun exportBackupText(): String? {
        if (state.value.servers.isEmpty()) {
            report("Нет серверов для сохранения")
            return null
        }
        return try {
            store.exportBackup()
        } catch (error: Exception) {
            report(error.message?.takeIf { it.isNotBlank() } ?: "Не удалось сохранить конфигурацию")
            null
        }
    }

    fun onBackupSaved() {
        state.value = state.value.copy(
            error = null,
            notice = "Конфигурация сохранена на телефон",
        )
    }

    fun importBackupText(raw: String) {
        viewModelScope.launch {
            if (state.value.phase != Phase.Idle) {
                try {
                    withContext(Dispatchers.IO) { tunnels.disconnect() }
                } catch (error: CancellationException) {
                    throw error
                } catch (error: Exception) {
                    state.value = state.value.copy(error = userMessage(error), notice = null)
                    return@launch
                }
                rememberSince(null)
            }
            try {
                val library = withContext(Dispatchers.Default) { store.importBackup(raw) }
                state.value = state.value.copy(
                    servers = library.servers,
                    activeId = library.activeId,
                    phase = Phase.Idle,
                    error = null,
                    notice = "Конфигурация загружена (${library.servers.size})",
                    rxBytes = 0,
                    txBytes = 0,
                    handshake = "—",
                    connectedSince = null,
                    screen = Screen.Backup,
                )
            } catch (error: IllegalArgumentException) {
                state.value = state.value.copy(error = error.message, notice = null)
            } catch (error: CancellationException) {
                throw error
            } catch (_: Exception) {
                state.value = state.value.copy(error = "Не удалось загрузить конфигурацию", notice = null)
            }
        }
    }

    fun importBackupStream(stream: InputStream) {
        viewModelScope.launch {
            try {
                val text = withContext(Dispatchers.IO) {
                    val bytes = stream.use { it.readAtMost(MAX_BACKUP_BYTES) }
                    if (bytes.size > MAX_BACKUP_BYTES) {
                        throw IllegalArgumentException("Файл слишком большой")
                    }
                    bytes.toString(Charsets.UTF_8)
                }
                importBackupText(text)
            } catch (error: IllegalArgumentException) {
                state.value = state.value.copy(error = error.message, notice = null)
            } catch (error: CancellationException) {
                throw error
            } catch (_: Exception) {
                state.value = state.value.copy(error = "Не удалось прочитать файл", notice = null)
            }
        }
    }

    fun claimTrial() {
        if (state.value.claimingTrial) return
        viewModelScope.launch {
            state.value = state.value.copy(claimingTrial = true, error = null, notice = null)
            val deviceId = TrialClient.androidId(getApplication())
            if (deviceId.isBlank()) {
                state.value = state.value.copy(claimingTrial = false, error = "Не удалось определить устройство")
                return@launch
            }
            try {
                val raw = withContext(Dispatchers.IO) { TrialClient.claim(deviceId) }
                val key = withContext(Dispatchers.Default) { KeyImport.parse(raw) }
                if (state.value.phase != Phase.Idle) {
                    try {
                        withContext(Dispatchers.IO) { tunnels.disconnect() }
                    } catch (error: CancellationException) {
                        throw error
                    } catch (error: Exception) {
                        state.value = state.value.copy(claimingTrial = false, error = userMessage(error))
                        return@launch
                    }
                }
                val library = store.add(key)
                rememberSince(null)
                state.value = state.value.copy(
                    servers = library.servers,
                    activeId = library.activeId,
                    screen = Screen.Home,
                    draft = "",
                    phase = Phase.Idle,
                    error = null,
                    notice = "Тестовый сервер на 1 день, скорость 1 Мбит/с",
                    rxBytes = 0,
                    txBytes = 0,
                    handshake = "—",
                    connectedSince = null,
                    claimingTrial = false,
                )
            } catch (error: CancellationException) {
                state.value = state.value.copy(claimingTrial = false)
                throw error
            } catch (error: Exception) {
                state.value = state.value.copy(
                    claimingTrial = false,
                    notice = null,
                    error = error.message?.takeIf { it.isNotBlank() } ?: "Не удалось получить тестовый сервер",
                )
            }
        }
    }

    fun importText(raw: String) {
        viewModelScope.launch {
            try {
                val key = withContext(Dispatchers.Default) { KeyImport.parse(raw) }
                if (state.value.phase != Phase.Idle) {
                    try {
                        withContext(Dispatchers.IO) { tunnels.disconnect() }
                    } catch (error: CancellationException) {
                        throw error
                    } catch (error: Exception) {
                        state.value = state.value.copy(error = userMessage(error))
                        return@launch
                    }
                }
                val library = store.add(key)
                rememberSince(null)
                state.value = state.value.copy(
                    servers = library.servers,
                    activeId = library.activeId,
                    screen = Screen.Home,
                    draft = "",
                    phase = Phase.Idle,
                    error = null,
                    rxBytes = 0,
                    txBytes = 0,
                    handshake = "—",
                    connectedSince = null,
                )
            } catch (error: IllegalArgumentException) {
                state.value = state.value.copy(screen = Screen.Import, draft = raw, error = error.message)
            } catch (error: CancellationException) {
                throw error
            } catch (_: Exception) {
                state.value = state.value.copy(screen = Screen.Import, draft = raw, error = "Не удалось сохранить профиль")
            }
        }
    }

    fun importStream(stream: InputStream) {
        viewModelScope.launch {
            try {
                val text = withContext(Dispatchers.IO) {
                    val bytes = stream.use { it.readAtMost(MAX_KEY_BYTES) }
                    if (bytes.size > MAX_KEY_BYTES) {
                        throw IllegalArgumentException("Файл слишком большой")
                    }
                    bytes.toString(Charsets.UTF_8)
                }
                importText(text)
            } catch (error: IllegalArgumentException) {
                state.value = state.value.copy(screen = Screen.Import, error = error.message)
            } catch (error: CancellationException) {
                throw error
            } catch (_: Exception) {
                state.value = state.value.copy(screen = Screen.Import, error = "Не удалось прочитать файл")
            }
        }
    }

    fun select(id: String) {
        viewModelScope.launch {
            if (state.value.phase != Phase.Idle && state.value.activeId != id) {
                try {
                    withContext(Dispatchers.IO) { tunnels.disconnect() }
                } catch (error: CancellationException) {
                    throw error
                } catch (error: Exception) {
                    state.value = state.value.copy(error = userMessage(error))
                    return@launch
                }
                rememberSince(null)
                state.value = state.value.copy(
                    phase = Phase.Idle,
                    rxBytes = 0,
                    txBytes = 0,
                    handshake = "—",
                    connectedSince = null,
                )
            }
            val library = store.setActive(id)
            state.value = state.value.copy(
                servers = library.servers,
                activeId = library.activeId,
                screen = Screen.Home,
                error = null,
            )
        }
    }

    fun setSplitMode(mode: AppRouteMode) {
        val current = state.value
        val active = current.active ?: return
        if (current.phase != Phase.Idle) {
            report("Отключите VPN, чтобы изменить раздельное туннелирование")
            return
        }
        saveSplitSettings(active.id, active.splitTunnel.copy(mode = mode))
    }

    fun toggleSplitApp(packageName: String, selected: Boolean) {
        if (!SplitTunnelSettings.isValidPackageName(packageName)) return
        val current = state.value
        val active = current.active ?: return
        if (current.phase != Phase.Idle) {
            report("Отключите VPN, чтобы изменить список приложений")
            return
        }
        val packages = active.splitTunnel.packages.toMutableSet()
        if (selected) packages.add(packageName) else packages.remove(packageName)
        saveSplitSettings(active.id, active.splitTunnel.copy(packages = packages))
    }

    fun addBypassDomain(input: String): Boolean {
        val current = state.value
        val active = current.active ?: run {
            report("Сначала выберите сервер")
            return false
        }
        if (current.phase != Phase.Idle) {
            report("Отключите VPN, чтобы изменить список сайтов")
            return false
        }
        val domain = try {
            SiteDomain.normalize(input)
        } catch (error: IllegalArgumentException) {
            report(error.message ?: "Некорректный домен сайта")
            return false
        }
        if (domain in active.splitTunnel.bypassDomains) {
            report("Этот сайт уже добавлен")
            return false
        }
        saveSplitSettings(active.id, active.splitTunnel.copy(bypassDomains = active.splitTunnel.bypassDomains + domain))
        return true
    }

    fun removeBypassDomain(domain: String) {
        val current = state.value
        val active = current.active ?: return
        if (current.phase != Phase.Idle) {
            report("Отключите VPN, чтобы изменить список сайтов")
            return
        }
        saveSplitSettings(active.id, active.splitTunnel.copy(bypassDomains = active.splitTunnel.bypassDomains - domain))
    }

    fun delete(id: String) {
        if (state.value.phase != Phase.Idle && state.value.activeId == id) {
            report("Сначала отключите VPN")
            return
        }
        val library = store.delete(id)
        state.value = state.value.copy(servers = library.servers, activeId = library.activeId, error = null)
    }

    fun connect() {
        val current = state.value
        val profile = current.active ?: return
        if (state.value.phase != Phase.Idle) return
        if (profile.splitTunnel.mode != AppRouteMode.AllTraffic &&
            profile.splitTunnel.packages.none(SplitTunnelSettings::isValidPackageName)
        ) {
            state.value = state.value.copy(
                screen = Screen.Settings,
                error = "Выберите хотя бы одно приложение для раздельного туннелирования",
            )
            return
        }
        if (current.installedAppsLoaded) {
            val installedPackages = current.installedApps.mapTo(mutableSetOf(), InstalledApp::packageName)
            if (profile.splitTunnel.packages.any { it !in installedPackages }) {
                state.value = state.value.copy(
                    screen = Screen.Settings,
                    error = "В списке есть удалённые приложения. Снимите их выбор и повторите подключение",
                )
                return
            }
        }
        viewModelScope.launch {
            state.value = state.value.copy(phase = Phase.Connecting, error = null, screen = Screen.Home)
            try {
                withContext(Dispatchers.IO) { tunnels.connect(profile.key.conf, profile.splitTunnel) }
                val started = System.currentTimeMillis()
                rememberSince(started)
                state.value = state.value.copy(phase = Phase.Connected, error = null, connectedSince = started, now = started)
                refreshPeerExpiry()
            } catch (error: Exception) {
                rememberSince(null)
                state.value = state.value.copy(phase = Phase.Idle, error = userMessage(error), connectedSince = null)
            }
        }
    }

    fun disconnect() {
        if (state.value.phase == Phase.Idle) return
        viewModelScope.launch {
            try {
                withContext(Dispatchers.IO) { tunnels.disconnect() }
            } catch (error: CancellationException) {
                throw error
            } catch (error: Exception) {
                state.value = state.value.copy(error = userMessage(error))
                return@launch
            }
            rememberSince(null)
            state.value = state.value.copy(
                phase = Phase.Idle,
                rxBytes = 0,
                txBytes = 0,
                handshake = "—",
                connectedSince = null,
            )
        }
    }

    fun checkForUpdate(manual: Boolean) {
        if (state.value.updatePhase != UpdatePhase.Idle) return
        viewModelScope.launch {
            state.value = state.value.copy(
                updatePhase = UpdatePhase.Checking,
                updateMessage = if (manual) "Проверка обновлений…" else state.value.updateMessage,
                error = if (manual && state.value.screen == Screen.Update) null else state.value.error,
            )
            val result = try {
                withContext(Dispatchers.IO) {
                    AppUpdater.checkLatest(getApplication())
                }
            } catch (error: CancellationException) {
                throw error
            } catch (_: Exception) {
                UpdateCheckResult(null, false, "Не удалось проверить обновления")
            }
            val releaseAt = when {
                result.release != null && !result.updateAvailable -> result.release.publishedAtMillis
                else -> state.value.currentVersionReleasedAt
            }
            if (releaseAt > 0L) {
                AppUpdater.rememberCurrentReleaseAt(getApplication(), releaseAt)
            }
            state.value = state.value.copy(
                updatePhase = UpdatePhase.Idle,
                updateAvailable = result.release.takeIf { result.updateAvailable },
                updateMessage = result.message,
                currentVersionReleasedAt = if (releaseAt > 0L) releaseAt else state.value.currentVersionReleasedAt,
                lastUpdateCheckAt = AppUpdater.lastCheckAt(getApplication()),
            )
            if (manual && result.updateAvailable && result.release != null) {
                downloadAndInstallUpdate()
            }
        }
    }

    fun downloadAndInstallUpdate() {
        val release = state.value.updateAvailable ?: return
        if (state.value.updatePhase != UpdatePhase.Idle) return
        viewModelScope.launch {
            state.value = state.value.copy(
                updatePhase = UpdatePhase.Downloading,
                updateMessage = "Скачивание ${release.versionName}…",
                error = null,
            )
            try {
                val apk = withContext(Dispatchers.IO) {
                    AppUpdater.downloadApk(getApplication(), release)
                }
                state.value = state.value.copy(
                    updatePhase = UpdatePhase.Idle,
                    updateMessage = "Установка ${release.versionName}…",
                    pendingInstallApk = apk.absolutePath,
                )
                requestInstall(apk.absolutePath)
            } catch (error: CancellationException) {
                throw error
            } catch (error: Exception) {
                state.value = state.value.copy(
                    updatePhase = UpdatePhase.Idle,
                    updateMessage = error.message?.takeIf { it.isNotBlank() } ?: "Не удалось скачать обновление",
                    pendingInstallApk = null,
                )
            }
        }
    }

    fun resumePendingInstall() {
        val path = state.value.pendingInstallApk ?: return
        pendingInstallPath = path
    }

    fun consumeInstallRequest(): Intent? {
        val path = pendingInstallPath ?: return null
        pendingInstallPath = null
        val file = java.io.File(path)
        if (!file.isFile) {
            state.value = state.value.copy(
                updateMessage = "Файл обновления не найден",
                pendingInstallApk = null,
            )
            return null
        }
        val app = getApplication<Application>()
        if (!AppUpdater.canInstallPackages(app)) {
            pendingInstallPath = path
            return AppUpdater.installPermissionSettingsIntent(app)
        }
        return AppUpdater.installIntent(app, file)
    }

    private var pendingInstallPath: String? = null

    private fun requestInstall(path: String) {
        pendingInstallPath = path
        state.value = state.value.copy(pendingInstallApk = path)
        installRequester?.invoke()
    }

    var installRequester: (() -> Unit)? = null

    private fun storedSince(): Long {
        val saved = getApplication<Application>()
            .getSharedPreferences(PREFS, Context.MODE_PRIVATE)
            .getLong(KEY_SINCE, 0L)
        return if (saved > 0L) saved else System.currentTimeMillis()
    }

    private fun rememberSince(value: Long?) {
        val editor = getApplication<Application>()
            .getSharedPreferences(PREFS, Context.MODE_PRIVATE)
            .edit()
        if (value == null) editor.remove(KEY_SINCE) else editor.putLong(KEY_SINCE, value)
        editor.apply()
    }

    private fun saveSplitSettings(id: String, settings: SplitTunnelSettings) {
        val library = store.setSplitTunnel(id, settings)
        state.value = state.value.copy(servers = library.servers, activeId = library.activeId, error = null)
    }

    @Suppress("DEPRECATION")
    private fun loadInstalledApps(application: Application): List<InstalledApp> {
        val launcher = Intent(Intent.ACTION_MAIN).addCategory(Intent.CATEGORY_LAUNCHER)
        val activities = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            application.packageManager.queryIntentActivities(
                launcher,
                PackageManager.ResolveInfoFlags.of(0),
            )
        } else {
            application.packageManager.queryIntentActivities(launcher, 0)
        }
        return activities.mapNotNull { resolveInfo ->
            val packageName = resolveInfo.activityInfo?.packageName ?: return@mapNotNull null
            val label = resolveInfo.loadLabel(application.packageManager)?.toString()
                ?.takeIf { it.isNotBlank() } ?: packageName
            val icon = runCatching { resolveInfo.loadIcon(application.packageManager) }.getOrNull()
            InstalledApp(packageName, label, icon)
        }.distinctBy(InstalledApp::packageName).sortedBy { it.label.lowercase() }
    }

    private fun formatHandshake(epochMillis: Long): String {
        if (epochMillis <= 0L) return "ещё нет"
        val seconds = ((System.currentTimeMillis() - epochMillis) / 1000).coerceAtLeast(0)
        return when {
            seconds < 60 -> "$seconds с назад"
            seconds < 3600 -> "${seconds / 60} мин назад"
            else -> "${seconds / 3600} ч назад"
        }
    }

    private fun userMessage(error: Exception): String {
        if (error is BackendException) {
            return when (error.reason) {
                BackendException.Reason.VPN_NOT_AUTHORIZED -> "Разрешите создание VPN-подключения"
                BackendException.Reason.DNS_RESOLUTION_FAILURE -> "Не удалось найти адрес сервера"
                BackendException.Reason.UNABLE_TO_START_VPN -> "Не удалось запустить подключение"
                BackendException.Reason.TUN_CREATION_ERROR -> "Не удалось создать подключение"
                BackendException.Reason.GO_ACTIVATION_ERROR_CODE -> "Не удалось подключиться. Проверьте ключ"
                else -> "Не удалось подключиться"
            }
        }
        if (error is BadConfigException) {
            return "Ключ не подошёл"
        }
        return error.message?.takeIf { it.isNotBlank() } ?: "Не удалось подключиться"
    }

    private companion object {
        const val MAX_KEY_BYTES = 256 * 1024
        const val MAX_BACKUP_BYTES = 2 * 1024 * 1024
        const val PREFS = "vpn_session"
        const val KEY_SINCE = "connected_since"
    }
}

internal fun InputStream.readAtMost(maxBytes: Int): ByteArray {
    require(maxBytes >= 0)
    val output = java.io.ByteArrayOutputStream(minOf(maxBytes, 8 * 1024))
    val buffer = ByteArray(8 * 1024)
    var total = 0
    while (total <= maxBytes) {
        val count = read(buffer, 0, minOf(buffer.size, maxBytes + 1 - total))
        if (count < 0) break
        if (count == 0) {
            val next = read()
            if (next < 0) break
            output.write(next)
            total += 1
        } else {
            output.write(buffer, 0, count)
            total += count
        }
    }
    return output.toByteArray()
}

fun elapsedLabel(since: Long?, now: Long): String {
    if (since == null) return "00:00:00"
    val total = ((now - since) / 1000).coerceAtLeast(0)
    val hours = total / 3600
    val minutes = (total % 3600) / 60
    val seconds = total % 60
    return "%02d:%02d:%02d".format(hours, minutes, seconds)
}

fun formatBytes(value: Long): String {
    val units = arrayOf("Б", "КБ", "МБ", "ГБ")
    var size = value.toDouble()
    var index = 0
    while (size >= 1024 && index < units.lastIndex) {
        size /= 1024
        index += 1
    }
    return if (index == 0) {
        "$value ${units[index]}"
    } else {
        java.util.Locale.US.let { java.lang.String.format(it, "%.1f %s", size, units[index]) }
    }
}
