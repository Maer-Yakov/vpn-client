package app.vpnadmin.client

import android.content.Intent
import android.net.VpnService
import android.os.Bundle
import android.provider.Settings
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.activity.result.contract.ActivityResultContracts
import androidx.activity.viewModels
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

class MainActivity : ComponentActivity() {
    private val model: MainViewModel by viewModels()
    private var pendingBackupText: String? = null
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
    private val createBackup = registerForActivityResult(ActivityResultContracts.CreateDocument("application/json")) { uri ->
        val text = pendingBackupText
        pendingBackupText = null
        if (uri == null || text == null) return@registerForActivityResult
        try {
            contentResolver.openOutputStream(uri)?.use { output ->
                output.write(text.toByteArray(Charsets.UTF_8))
            } ?: run {
                model.report("Не удалось сохранить файл")
                return@registerForActivityResult
            }
            model.onBackupSaved()
        } catch (_: Exception) {
            model.report("Не удалось сохранить файл")
        }
    }
    private val openBackup = registerForActivityResult(ActivityResultContracts.OpenDocument()) { uri ->
        if (uri == null) return@registerForActivityResult
        try {
            val stream = contentResolver.openInputStream(uri)
            if (stream == null) {
                model.report("Не удалось открыть файл")
            } else {
                model.importBackupStream(stream)
            }
        } catch (_: Exception) {
            model.report("Не удалось открыть файл")
        }
    }
    private val installPermission = registerForActivityResult(ActivityResultContracts.StartActivityForResult()) {
        model.resumePendingInstall()
        launchPendingInstall()
    }

    override fun onResume() {
        super.onResume()
        model.refreshConnection()
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        model.installRequester = { launchPendingInstall() }
        if (intent.getBooleanExtra(EXTRA_TEST_SUBSCRIPTION_WARNING, false)) {
            model.setActiveExpiresInDays(1)
        }
        consumeIntent(intent)
        setContent {
            VpnTheme {
                var showStartup by remember { mutableStateOf(savedInstanceState == null) }
                val ui by model.ui.collectAsStateWithLifecycle()
                Box(modifier = Modifier.fillMaxSize()) {
                    when (ui.screen) {
                        Screen.Home -> HomeScreen(
                            ui = ui,
                            onConnect = ::requestConnect,
                            onDisconnect = model::disconnect,
                            onServers = { model.show(Screen.Servers) },
                            onSettings = { model.show(Screen.Settings) },
                            onAdd = { model.show(Screen.Import) },
                            onTrial = model::claimTrial,
                            onSupport = ::openSupport,
                            onOpenUpdate = { model.show(Screen.Update) },
                        )
                        Screen.Servers -> ServersScreen(
                            ui = ui,
                            onBack = { model.show(Screen.Home) },
                            onAdd = { model.show(Screen.Import) },
                            onTrial = model::claimTrial,
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
                            onUpdate = { model.show(Screen.Update) },
                            onBackup = { model.show(Screen.Backup) },
                        )
                        Screen.SplitTunnel -> SplitTunnelScreen(
                            ui = ui,
                            onBack = { model.show(Screen.Settings) },
                            onSplitMode = model::setSplitMode,
                            onToggleSplitApp = model::toggleSplitApp,
                            onAddBypassDomain = model::addBypassDomain,
                            onRemoveBypassDomain = model::removeBypassDomain,
                        )
                        Screen.Update -> UpdateScreen(
                            ui = ui,
                            version = BuildConfig.VERSION_NAME,
                            onBack = { model.show(Screen.Settings) },
                            onCheck = { model.checkForUpdate(manual = true) },
                        )
                        Screen.Backup -> BackupScreen(
                            ui = ui,
                            onBack = { model.show(Screen.Settings) },
                            onSave = ::saveBackup,
                            onLoad = {
                                openBackup.launch(arrayOf("application/json", "text/plain", "*/*"))
                            },
                        )
                    }
                    if (showStartup) {
                        MvpnStartupAnimation(onFinished = { showStartup = false })
                    }
                }
            }
        }
    }

    override fun onDestroy() {
        if (model.installRequester != null) {
            model.installRequester = null
        }
        super.onDestroy()
    }

    override fun onNewIntent(intent: Intent) {
        super.onNewIntent(intent)
        setIntent(intent)
        consumeIntent(intent)
    }

    private fun launchPendingInstall() {
        val intent = model.consumeInstallRequest() ?: return
        if (intent.action == Settings.ACTION_MANAGE_UNKNOWN_APP_SOURCES) {
            installPermission.launch(intent)
        } else {
            startActivity(intent)
        }
    }

    private fun saveBackup() {
        val text = model.exportBackupText() ?: return
        pendingBackupText = text
        val stamp = SimpleDateFormat("yyyyMMdd-HHmm", Locale.US).format(Date())
        createBackup.launch("mvpn-backup-$stamp.json")
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
        const val EXTRA_TEST_SUBSCRIPTION_WARNING = "test_subscription_warning"
    }
}
