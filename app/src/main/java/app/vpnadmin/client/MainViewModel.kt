package app.vpnadmin.client

import android.app.Application
import android.content.Context
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

enum class Phase {
    Idle,
    Connecting,
    Connected,
}

enum class Screen {
    Home,
    Servers,
    Import,
    Settings,
}

data class UiState(
    val servers: List<StoredServer> = emptyList(),
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
                phase = if (running) Phase.Connected else Phase.Idle,
                connectedSince = since,
            ),
        )
        ui = state
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
        state.value = state.value.copy(screen = screen, error = null, draft = if (screen == Screen.Import) "" else state.value.draft)
    }

    fun updateDraft(value: String) {
        state.value = state.value.copy(draft = value, error = null)
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
        } else if (!running && state.value.phase == Phase.Connected) {
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

    fun report(message: String) {
        state.value = state.value.copy(error = message)
    }

    fun importText(raw: String) {
        viewModelScope.launch {
            try {
                val key = withContext(Dispatchers.Default) { KeyImport.parse(raw) }
                if (state.value.phase != Phase.Idle) {
                    withContext(Dispatchers.IO) { runCatching { tunnels.disconnect() } }
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
                state.value = state.value.copy(screen = Screen.Import, error = error.message)
            }
        }
    }

    fun importStream(stream: InputStream) {
        viewModelScope.launch {
            try {
                val text = withContext(Dispatchers.IO) {
                    val bytes = stream.use { it.readNBytes(MAX_KEY_BYTES + 1) }
                    if (bytes.size > MAX_KEY_BYTES) {
                        throw IllegalArgumentException("Файл слишком большой")
                    }
                    bytes.toString(Charsets.UTF_8)
                }
                importText(text)
            } catch (error: IllegalArgumentException) {
                state.value = state.value.copy(screen = Screen.Import, error = error.message)
            }
        }
    }

    fun select(id: String) {
        viewModelScope.launch {
            if (state.value.phase != Phase.Idle && state.value.activeId != id) {
                withContext(Dispatchers.IO) { runCatching { tunnels.disconnect() } }
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

    fun delete(id: String) {
        if (state.value.phase != Phase.Idle && state.value.activeId == id) {
            report("Сначала отключите VPN")
            return
        }
        val library = store.delete(id)
        state.value = state.value.copy(servers = library.servers, activeId = library.activeId, error = null)
    }

    fun connect() {
        val profile = state.value.active ?: return
        if (state.value.phase != Phase.Idle) return
        viewModelScope.launch {
            state.value = state.value.copy(phase = Phase.Connecting, error = null, screen = Screen.Home)
            try {
                withContext(Dispatchers.IO) { tunnels.connect(profile.key.conf) }
                val started = System.currentTimeMillis()
                rememberSince(started)
                state.value = state.value.copy(phase = Phase.Connected, error = null, connectedSince = started, now = started)
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
            } catch (error: Exception) {
                state.value = state.value.copy(error = userMessage(error))
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
                BackendException.Reason.UNABLE_TO_START_VPN -> "Служба VPN не запустилась. Откройте приложение и попробуйте снова"
                BackendException.Reason.TUN_CREATION_ERROR -> "Система не создала VPN-интерфейс"
                BackendException.Reason.GO_ACTIVATION_ERROR_CODE -> "Туннель не запустился. Проверьте ключ из панели"
                else -> "Не удалось подключиться"
            }
        }
        if (error is BadConfigException) {
            return "Конфигурация не подошла для AmneziaWG"
        }
        return error.message?.takeIf { it.isNotBlank() } ?: "Не удалось подключиться"
    }

    private companion object {
        const val MAX_KEY_BYTES = 256 * 1024
        const val PREFS = "vpn_session"
        const val KEY_SINCE = "connected_since"
    }
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
