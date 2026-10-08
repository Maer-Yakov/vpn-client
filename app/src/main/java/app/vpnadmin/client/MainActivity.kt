package app.vpnadmin.client

import android.content.Intent
import android.net.VpnService
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.activity.result.contract.ActivityResultContracts
import androidx.activity.viewModels
import androidx.compose.runtime.getValue
import androidx.lifecycle.compose.collectAsStateWithLifecycle

class MainActivity : ComponentActivity() {
    private val model: MainViewModel by viewModels()
    private val vpnPermission = registerForActivityResult(ActivityResultContracts.StartActivityForResult()) {
        if (it.resultCode == RESULT_OK) {
            model.connect()
        } else {
            model.report("Подключение отменено: нет разрешения VPN")
        }
    }
    private val openKey = registerForActivityResult(ActivityResultContracts.OpenDocument()) { uri ->
        if (uri == null) return@registerForActivityResult
        try {
            val stream = contentResolver.openInputStream(uri)
            if (stream == null) {
                model.report("Не удалось открыть файл")
            } else {
                model.importStream(stream)
            }
        } catch (_: Exception) {
            model.report("Не удалось открыть файл")
        }
    }

    override fun onResume() {
        super.onResume()
        model.refreshConnection()
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        consumeIntent(intent)
        setContent {
            VpnTheme {
                val ui by model.ui.collectAsStateWithLifecycle()
                when (ui.screen) {
                    Screen.Home -> HomeScreen(
                        ui = ui,
                        onConnect = ::requestConnect,
                        onDisconnect = model::disconnect,
                        onServers = { model.show(Screen.Servers) },
                        onSettings = { model.show(Screen.Settings) },
                        onAdd = { model.show(Screen.Import) },
                        onSupport = ::openSupport,
                    )
                    Screen.Servers -> ServersScreen(
                        ui = ui,
                        onBack = { model.show(Screen.Home) },
                        onAdd = { model.show(Screen.Import) },
                        onSelect = model::select,
                        onDelete = model::delete,
                    )
                    Screen.Import -> ImportScreen(
                        ui = ui,
                        onBack = { model.show(if (ui.servers.isEmpty()) Screen.Home else Screen.Servers) },
                        onDraft = model::updateDraft,
                        onPaste = model::updateDraft,
                        onEmptyClipboard = { model.report("Буфер обмена пуст") },
                        onOpenFile = { openKey.launch(arrayOf("text/plain", "application/octet-stream", "*/*")) },
                        onScan = { model.show(Screen.Scan) },
                        onSave = { model.importText(ui.draft) },
                    )
                    Screen.Scan -> QrScanScreen(
                        onBack = { model.show(Screen.Import) },
                        onResult = model::importText,
                    )
                    Screen.Settings -> SettingsScreen(
                        ui = ui,
                        version = BuildConfig.VERSION_NAME,
                        onBack = { model.show(Screen.Home) },
                        onSupport = ::openSupport,
                        onSplitTunnel = { model.show(Screen.SplitTunnel) },
                    )
                    Screen.SplitTunnel -> SplitTunnelScreen(
                        ui = ui,
                        onBack = { model.show(Screen.Settings) },
                        onSplitMode = model::setSplitMode,
                        onToggleSplitApp = model::toggleSplitApp,
                        onAddBypassDomain = model::addBypassDomain,
                        onRemoveBypassDomain = model::removeBypassDomain,
                    )
                }
            }
        }
    }

    override fun onNewIntent(intent: Intent) {
        super.onNewIntent(intent)
        setIntent(intent)
        consumeIntent(intent)
    }

    private fun openSupport() {
        if (!SupportChat.open(this)) {
            model.report("Не удалось открыть чат поддержки")
        }
    }

    private fun requestConnect() {
        val prepare = VpnService.prepare(this)
        if (prepare != null) {
            vpnPermission.launch(prepare)
        } else {
            model.connect()
        }
    }

    private fun consumeIntent(intent: Intent?) {
        if (intent == null || intent.getBooleanExtra(EXTRA_CONSUMED, false)) return
        val payload = when (intent.action) {
            Intent.ACTION_SEND -> intent.getStringExtra(Intent.EXTRA_TEXT)
            Intent.ACTION_VIEW -> intent.dataString
            else -> null
        }
        if (payload.isNullOrBlank()) return
        intent.putExtra(EXTRA_CONSUMED, true)
        model.importText(payload)
    }

    private companion object {
        const val EXTRA_CONSUMED = "app.vpnadmin.client.consumed"
    }
}
