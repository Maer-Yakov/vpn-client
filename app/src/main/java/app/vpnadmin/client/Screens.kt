package app.vpnadmin.client

import androidx.compose.animation.core.LinearEasing
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.tween
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.imePadding
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.selection.selectable
import androidx.compose.foundation.selection.toggleable
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Checkbox
import androidx.compose.material3.IconButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.OutlinedTextFieldDefaults
import androidx.compose.material3.RadioButton
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.alpha
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.drawBehind
import androidx.compose.ui.geometry.CornerRadius
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.ColorFilter
import androidx.compose.ui.graphics.PathEffect
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalClipboardManager
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardCapitalization
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.viewinterop.AndroidView
import android.widget.ImageView

@Composable
fun HomeScreen(
    ui: UiState,
    onConnect: () -> Unit,
    onDisconnect: () -> Unit,
    onServers: () -> Unit,
    onSettings: () -> Unit,
    onAdd: () -> Unit,
    onSupport: () -> Unit,
    onOpenUpdate: () -> Unit = {},
) {
    val active = ui.active
    val connected = ui.phase == Phase.Connected
    val splitEnabled = active?.splitTunnel?.let { settings ->
        settings.bypassDomains.isNotEmpty() ||
            (settings.mode != AppRouteMode.AllTraffic && settings.packages.any(SplitTunnelSettings::isValidPackageName))
    } == true
    Scaffold(containerColor = PanelColors.bg) { padding ->
        Box(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding),
        ) {
            Image(
                painter = painterResource(R.drawable.ic_logo),
                contentDescription = null,
                contentScale = ContentScale.Fit,
                modifier = Modifier
                    .align(Alignment.Center)
                    .size(340.dp)
                    .alpha(0.1f),
            )
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(horizontal = 20.dp)
                    .padding(top = 12.dp),
            ) {
                TopBar(
                    title = "Mvpn",
                    action = "Настройки",
                    onAction = onSettings,
                    iconAction = true,
                    splitTunnelEnabled = splitEnabled,
                )
                Column(
                    modifier = Modifier
                        .weight(1f)
                        .fillMaxWidth(),
                    horizontalAlignment = Alignment.CenterHorizontally,
                    verticalArrangement = Arrangement.Center,
                ) {
                    ConnectControl(
                        phase = ui.phase,
                        enabled = active != null,
                        onClick = {
                            when {
                                ui.phase == Phase.Connected -> onDisconnect()
                                ui.phase == Phase.Idle && active != null -> onConnect()
                            }
                        },
                    )
                    Spacer(Modifier.height(18.dp))
                    if (active != null) {
                        Text(
                            active.key.title,
                            color = PanelColors.text,
                            fontWeight = FontWeight.SemiBold,
                            fontSize = 18.sp,
                            maxLines = 1,
                            overflow = TextOverflow.Ellipsis,
                            modifier = Modifier.clickable(onClick = onServers),
                        )
                        Text(
                            active.key.protocol,
                            color = PanelColors.accent,
                            fontSize = 13.sp,
                            modifier = Modifier.padding(top = 4.dp),
                        )
                    }
                    val connectedStatus = if (ui.phase == Phase.Connected) {
                        SubscriptionExpiry.connectedStatus(active?.key?.expiresAtMillis, ui.now)
                    } else {
                        null
                    }
                    Text(
                        text = when (ui.phase) {
                            Phase.Idle -> if (active == null) "Нет сервера" else "Отключено"
                            Phase.Connecting -> "Подключение"
                            Phase.Connected -> connectedStatus?.title ?: "Подключено"
                        },
                        color = when {
                            ui.phase == Phase.Connected && connectedStatus?.warning == true -> PanelColors.danger
                            connected -> PanelColors.online
                            else -> PanelColors.muted
                        },
                        fontSize = 16.sp,
                        fontWeight = FontWeight.Medium,
                        textAlign = TextAlign.Center,
                        modifier = Modifier.padding(top = 8.dp),
                    )
                    if (ui.phase == Phase.Connected && connectedStatus?.warning == true && connectedStatus.date != null) {
                        Text(
                            connectedStatus.date,
                            color = PanelColors.danger,
                            fontSize = 16.sp,
                            fontWeight = FontWeight.Medium,
                            modifier = Modifier.padding(top = 6.dp),
                        )
                    }
                    if (connected) {
                        Text(
                            elapsedLabel(ui.connectedSince, ui.now),
                            color = PanelColors.accent,
                            fontSize = 16.sp,
                            modifier = Modifier.padding(top = 6.dp),
                        )
                        Row(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(top = 22.dp),
                            horizontalArrangement = Arrangement.spacedBy(10.dp),
                        ) {
                            StatCard("Получено", formatBytes(ui.rxBytes), Modifier.weight(1f))
                            StatCard("Отправлено", formatBytes(ui.txBytes), Modifier.weight(1f))
                        }
                        Text(
                            "Рукопожатие ${ui.handshake}",
                            color = PanelColors.muted,
                            fontSize = 13.sp,
                            modifier = Modifier.padding(top = 10.dp),
                        )
                    } else if (active == null) {
                        TextButton(onClick = onAdd, modifier = Modifier.padding(top = 8.dp)) {
                            Text("Добавить сервер", color = PanelColors.accent)
                        }
                    }
                }
                ui.updateAvailable?.let { release ->
                    PanelCard(onClick = onOpenUpdate) {
                        Text("Доступно обновление ${release.versionName}", color = PanelColors.accent, fontWeight = FontWeight.SemiBold)
                        Text("Нажмите, чтобы открыть раздел «Обновление»", color = PanelColors.muted, fontSize = 13.sp)
                    }
                }
                ui.error?.let {
                    Text(it, color = PanelColors.danger, fontSize = 13.sp, modifier = Modifier.padding(top = 10.dp))
                }
                BottomDock(
                    selected = DockTab.Home,
                    onHome = {},
                    onServers = onServers,
                    onChat = onSupport,
                )
            }
        }
    }
}

@Composable
fun ServersScreen(
    ui: UiState,
    onBack: () -> Unit,
    onAdd: () -> Unit,
    onTrial: () -> Unit,
    onSupport: () -> Unit,
    onSelect: (String) -> Unit,
    onDelete: (String) -> Unit,
) {
    Scaffold(containerColor = PanelColors.bg) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .padding(horizontal = 20.dp, vertical = 12.dp),
        ) {
            TopBar(title = "Серверы", action = "Назад", onAction = onBack)
            Column(
                modifier = Modifier
                    .weight(1f)
                    .verticalScroll(rememberScrollState()),
                verticalArrangement = Arrangement.spacedBy(10.dp),
            ) {
                if (ui.servers.isEmpty()) {
                    Text("Список пуст", color = PanelColors.muted)
                } else {
                    Text("Мои", color = PanelColors.muted, fontSize = 12.sp)
                }
                ui.servers.forEach { server ->
                    val selected = server.id == ui.activeId
                    Column(
                        modifier = Modifier
                            .fillMaxWidth()
                            .clip(RoundedCornerShape(12.dp))
                            .background(PanelColors.panel)
                            .border(
                                1.dp,
                                if (selected) PanelColors.accent else PanelColors.line,
                                RoundedCornerShape(12.dp),
                            )
                            .clickable { onSelect(server.id) }
                            .padding(14.dp),
                        verticalArrangement = Arrangement.spacedBy(4.dp),
                    ) {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Text(
                                server.key.title,
                                color = PanelColors.text,
                                fontWeight = FontWeight.SemiBold,
                                modifier = Modifier.weight(1f),
                                maxLines = 1,
                                overflow = TextOverflow.Ellipsis,
                            )
                            if (selected) {
                                Text("выбран", color = PanelColors.accent, fontSize = 12.sp)
                            }
                        }
                        Text(
                            "${server.key.protocol} · ${server.key.endpoint}",
                            color = PanelColors.muted,
                            fontSize = 13.sp,
                            maxLines = 1,
                            overflow = TextOverflow.Ellipsis,
                        )
                        TextButton(onClick = { onDelete(server.id) }) {
                            Text("Удалить", color = PanelColors.danger)
                        }
                    }
                }
                Text("Пробный", color = PanelColors.muted, fontSize = 12.sp)
                TrialRow(claiming = ui.claimingTrial, onClick = onTrial)
            }
            Button(
                onClick = onAdd,
                modifier = Modifier.fillMaxWidth(),
                colors = ButtonDefaults.buttonColors(
                    containerColor = PanelColors.accent,
                    contentColor = PanelColors.accentInk,
                ),
            ) {
                Text("Добавить сервер", fontWeight = FontWeight.SemiBold)
            }
            ui.error?.let {
                Text(it, color = PanelColors.danger, fontSize = 13.sp, modifier = Modifier.padding(top = 8.dp))
            }
            BottomDock(
                selected = DockTab.Servers,
                onHome = onBack,
                onServers = {},
                onChat = onSupport,
            )
        }
    }
}

@Composable
fun ImportScreen(
    ui: UiState,
    onBack: () -> Unit,
    onDraft: (String) -> Unit,
    onPaste: (String) -> Unit,
    onEmptyClipboard: () -> Unit,
    onOpenFile: () -> Unit,
    onScan: () -> Unit,
    onSave: () -> Unit,
) {
    val clipboard = LocalClipboardManager.current
    Scaffold(containerColor = PanelColors.bg) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .verticalScroll(rememberScrollState())
                .padding(horizontal = 20.dp, vertical = 12.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            TopBar(title = "Новый сервер", action = "Назад", onAction = onBack)
            GhostButton("Сканировать QR", onScan)
            OutlinedTextField(
                value = ui.draft,
                onValueChange = onDraft,
                modifier = Modifier.fillMaxWidth(),
                minLines = 6,
                placeholder = { Text("Вставьте ключ") },
                colors = fieldColors(),
                keyboardOptions = KeyboardOptions(capitalization = KeyboardCapitalization.None),
            )
            GhostButton("Вставить из буфера") {
                val text = clipboard.getText()?.text.orEmpty()
                if (text.isBlank()) onEmptyClipboard() else onPaste(text)
            }
            GhostButton("Открыть файл", onOpenFile)
            Button(
                onClick = onSave,
                enabled = ui.draft.isNotBlank(),
                modifier = Modifier.fillMaxWidth(),
                colors = ButtonDefaults.buttonColors(
                    containerColor = PanelColors.accent,
                    contentColor = PanelColors.accentInk,
                ),
            ) {
                Text("Сохранить", fontWeight = FontWeight.SemiBold)
            }
            ui.error?.let { Text(it, color = PanelColors.danger) }
        }
    }
}

@Composable
fun SettingsScreen(
    ui: UiState,
    version: String,
    onBack: () -> Unit,
    onSupport: () -> Unit,
    onSplitTunnel: () -> Unit,
    onUpdate: () -> Unit,
    onBackup: () -> Unit,
    onAbout: () -> Unit,
) {
    Scaffold(containerColor = PanelColors.bg) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .verticalScroll(rememberScrollState())
                .padding(horizontal = 20.dp, vertical = 12.dp),
            verticalArrangement = Arrangement.spacedBy(10.dp),
        ) {
            TopBar(title = "Настройки", action = "Назад", onAction = onBack)
            MenuCard(
                icon = R.drawable.ic_split,
                title = "Раздельное туннелирование",
                subtitle = "Маршрутизация выбранных приложений",
                onClick = onSplitTunnel,
            )
            MenuCard(
                icon = R.drawable.ic_menu_update,
                title = "Обновление",
                subtitle = if (ui.updateAvailable != null) {
                    "Доступна ${ui.updateAvailable.versionName}"
                } else {
                    "Проверка и установка новой версии"
                },
                subtitleColor = if (ui.updateAvailable != null) PanelColors.accent else PanelColors.muted,
                onClick = onUpdate,
            )
            MenuCard(
                icon = R.drawable.ic_menu_config,
                title = "Конфигурация",
                subtitle = "Резервное копирование",
                onClick = onBackup,
            )
            MenuCard(
                icon = R.drawable.ic_menu_info,
                title = "О программе",
                subtitle = "Mvpn $version",
                onClick = onAbout,
            )
            ui.notice?.let { Text(it, color = PanelColors.accent, fontSize = 13.sp) }
            ui.error?.let { Text(it, color = PanelColors.danger, fontSize = 13.sp) }
            SupportLink(onSupport)
        }
    }
}

@Composable
fun BackupScreen(
    ui: UiState,
    onBack: () -> Unit,
    onSave: () -> Unit,
    onLoad: () -> Unit,
) {
    Scaffold(containerColor = PanelColors.bg) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .verticalScroll(rememberScrollState())
                .padding(horizontal = 20.dp, vertical = 12.dp),
            verticalArrangement = Arrangement.spacedBy(10.dp),
        ) {
            TopBar(title = "Конфигурация", action = "Назад", onAction = onBack)
            Text(
                "Сохраняются серверы, режимы раздельного туннелирования, списки приложений и сайтов. В файле есть ключи VPN — храните его только у себя.",
                color = PanelColors.muted,
                fontSize = 13.sp,
            )
            SettingRow(
                "Последнее копирование",
                if (ui.lastBackupAt > 0L) AppUpdater.formatDate(ui.lastBackupAt) else "ещё не было",
            )
            Button(
                onClick = onSave,
                enabled = ui.servers.isNotEmpty(),
                modifier = Modifier.fillMaxWidth(),
                colors = ButtonDefaults.buttonColors(
                    containerColor = PanelColors.accent,
                    contentColor = PanelColors.accentInk,
                    disabledContainerColor = PanelColors.line,
                    disabledContentColor = PanelColors.muted,
                ),
            ) {
                Text("Сохранить на телефон")
            }
            GhostButton("Загрузить с телефона", onLoad)
            ui.notice?.let { Text(it, color = PanelColors.accent, fontSize = 13.sp) }
            ui.error?.let { Text(it, color = PanelColors.danger, fontSize = 13.sp) }
        }
    }
}

@Composable
fun UpdateScreen(
    ui: UiState,
    version: String,
    onBack: () -> Unit,
    onCheck: () -> Unit,
) {
    val busy = ui.updatePhase != UpdatePhase.Idle
    val buttonLabel = when (ui.updatePhase) {
        UpdatePhase.Checking -> "Проверка…"
        UpdatePhase.Downloading -> "Скачивание…"
        UpdatePhase.Idle -> "Проверить обновление"
    }
    Scaffold(containerColor = PanelColors.bg) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .verticalScroll(rememberScrollState())
                .padding(horizontal = 20.dp, vertical = 12.dp),
            verticalArrangement = Arrangement.spacedBy(10.dp),
        ) {
            TopBar(title = "Обновление", action = "Назад", onAction = onBack)
            SettingRow("Текущая версия", version)
            SettingRow(
                "Дата текущей версии",
                AppUpdater.formatDate(
                    ui.currentVersionReleasedAt.takeIf { it > 0L } ?: ui.appUpdatedAt,
                ),
            )
            SettingRow("Дата последнего обновления", AppUpdater.formatDate(ui.appUpdatedAt))
            SettingRow("Последняя проверка", AppUpdater.formatDate(ui.lastUpdateCheckAt))
            ui.updateAvailable?.let { release ->
                SettingRow(
                    "Доступна версия",
                    "${release.versionName} · ${AppUpdater.formatDate(release.publishedAtMillis)}",
                )
            }
            ui.updateMessage?.let { message ->
                Text(
                    message,
                    color = if (ui.updateAvailable != null) PanelColors.accent else PanelColors.muted,
                    fontSize = 13.sp,
                )
            }
            Button(
                onClick = onCheck,
                enabled = !busy,
                modifier = Modifier.fillMaxWidth(),
                colors = ButtonDefaults.buttonColors(
                    containerColor = PanelColors.accent,
                    contentColor = PanelColors.accentInk,
                    disabledContainerColor = PanelColors.line,
                    disabledContentColor = PanelColors.muted,
                ),
            ) {
                Text(buttonLabel)
            }
        }
    }
}

@Composable
fun SplitTunnelScreen(
    ui: UiState,
    onBack: () -> Unit,
    onSplitMode: (AppRouteMode) -> Unit,
    onToggleSplitApp: (String, Boolean) -> Unit,
    onAddBypassDomain: (String) -> Boolean,
    onRemoveBypassDomain: (String) -> Unit,
) {
    var appFilter by remember { mutableStateOf("") }
    var siteDraft by remember { mutableStateOf("") }
    var expanded by remember { mutableStateOf(false) }
    val active = ui.active
    val splitSettings = active?.splitTunnel ?: SplitTunnelSettings()
    val canEditSplit = ui.phase == Phase.Idle && active != null
    val missingApps = if (ui.installedAppsLoaded) {
        splitSettings.packages
            .filterNot { packageName -> ui.installedApps.any { it.packageName == packageName } }
            .map { packageName -> InstalledApp(packageName, "Не установлено") }
    } else {
        emptyList()
    }
    val visibleApps = (ui.installedApps + missingApps).filter { app ->
        app.label.contains(appFilter, ignoreCase = true) ||
            app.packageName.contains(appFilter, ignoreCase = true)
    }
    Scaffold(containerColor = PanelColors.bg) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .imePadding()
                .verticalScroll(rememberScrollState())
                .padding(horizontal = 20.dp, vertical = 12.dp),
            verticalArrangement = Arrangement.spacedBy(10.dp),
        ) {
            TopBar(title = "Раздельное туннелирование", action = "Назад", onAction = onBack)
            Text(
                "Для сервера: ${active?.key?.title ?: "не выбран"}",
                color = PanelColors.muted,
                fontSize = 13.sp,
            )
            Text(
                "Режим приложений действует только для этого сервера. Добавленные ниже сайты всегда идут в обход VPN.",
                color = PanelColors.muted,
                fontSize = 13.sp,
            )
            if (!canEditSplit) {
                Text("Отключите VPN и выберите сервер для изменения настроек.", color = PanelColors.muted, fontSize = 13.sp)
            }
            AppRouteMode.entries.forEach { mode ->
                val title = when (mode) {
                    AppRouteMode.AllTraffic -> "Весь трафик через VPN"
                    AppRouteMode.SelectedThroughVpn -> "Только выбранные приложения через VPN"
                    AppRouteMode.SelectedBypassVpn -> "Выбранные приложения в обход VPN"
                }
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clip(RoundedCornerShape(10.dp))
                        .selectable(
                            selected = splitSettings.mode == mode,
                            enabled = canEditSplit,
                            role = Role.RadioButton,
                            onClick = { onSplitMode(mode) },
                        )
                        .padding(horizontal = 8.dp, vertical = 2.dp),
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    RadioButton(selected = splitSettings.mode == mode, onClick = null, enabled = canEditSplit)
                    Text(title, color = PanelColors.text, fontSize = 14.sp, modifier = Modifier.padding(start = 8.dp))
                }
            }
            if (splitSettings.mode != AppRouteMode.AllTraffic) {
                if (ui.installedApps.isEmpty()) {
                    val message = if (ui.installedAppsLoaded) {
                        "Приложения с ярлыками не найдены"
                    } else {
                        "Список приложений загружается…"
                    }
                    Text(message, color = PanelColors.muted, fontSize = 13.sp)
                }
                Box(modifier = Modifier.fillMaxWidth()) {
                    OutlinedTextField(
                        value = if (splitSettings.packages.isEmpty()) {
                            "Выберите приложения"
                        } else {
                            "Выбрано: ${splitSettings.packages.size}"
                        },
                        onValueChange = {},
                        readOnly = true,
                        enabled = canEditSplit,
                        label = { Text("Приложения") },
                        trailingIcon = {
                            Text(if (expanded) "▲" else "▼", color = PanelColors.muted)
                        },
                        modifier = Modifier.fillMaxWidth(),
                        colors = fieldColors(),
                    )
                    Box(
                        modifier = Modifier
                            .matchParentSize()
                            .clickable(enabled = canEditSplit) { expanded = !expanded },
                    )
                }
                if (expanded) {
                    OutlinedTextField(
                        value = appFilter,
                        onValueChange = { appFilter = it },
                        modifier = Modifier.fillMaxWidth(),
                        singleLine = true,
                        enabled = canEditSplit,
                        placeholder = { Text("Поиск приложения") },
                        colors = fieldColors(),
                        keyboardOptions = KeyboardOptions(capitalization = KeyboardCapitalization.None),
                    )
                    Column(
                        modifier = Modifier
                            .fillMaxWidth()
                            .heightIn(max = 320.dp)
                            .clip(RoundedCornerShape(10.dp))
                            .background(PanelColors.panel)
                            .border(1.dp, PanelColors.line, RoundedCornerShape(10.dp))
                            .verticalScroll(rememberScrollState()),
                    ) {
                        if (visibleApps.isEmpty()) {
                            Text(
                                "Ничего не найдено",
                                color = PanelColors.muted,
                                fontSize = 13.sp,
                                modifier = Modifier.padding(horizontal = 12.dp, vertical = 10.dp),
                            )
                        }
                        visibleApps.forEach { app ->
                            Row(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .clickable(enabled = canEditSplit) {
                                        onToggleSplitApp(
                                            app.packageName,
                                            app.packageName !in splitSettings.packages,
                                        )
                                    }
                                    .padding(horizontal = 8.dp, vertical = 4.dp),
                                verticalAlignment = Alignment.CenterVertically,
                            ) {
                                InstalledAppIcon(app)
                                Column(
                                    modifier = Modifier
                                        .weight(1f)
                                        .padding(horizontal = 12.dp),
                                ) {
                                    Text(app.label, color = PanelColors.text)
                                    Text(app.packageName, color = PanelColors.muted, fontSize = 11.sp)
                                }
                                Checkbox(
                                    checked = app.packageName in splitSettings.packages,
                                    onCheckedChange = null,
                                    enabled = canEditSplit,
                                )
                            }
                        }
                    }
                }
                Text("Выбрано: ${splitSettings.packages.size}", color = PanelColors.muted, fontSize = 13.sp)
            }
            Text("Сайты в обход VPN", color = PanelColors.text, fontWeight = FontWeight.SemiBold)
            Text(
                "Введите домен или URL. IP-адреса определяются при подключении; сайты с общим CDN-IP тоже могут идти в обход.",
                color = PanelColors.muted,
                fontSize = 13.sp,
            )
            Row(verticalAlignment = Alignment.CenterVertically) {
                OutlinedTextField(
                    value = siteDraft,
                    onValueChange = { siteDraft = it },
                    modifier = Modifier.weight(1f),
                    singleLine = true,
                    enabled = canEditSplit,
                    label = { Text("Домен сайта") },
                    placeholder = { Text("example.com") },
                    colors = fieldColors(),
                    keyboardOptions = KeyboardOptions(capitalization = KeyboardCapitalization.None),
                )
                TextButton(
                    enabled = canEditSplit && siteDraft.isNotBlank(),
                    onClick = {
                        if (onAddBypassDomain(siteDraft)) siteDraft = ""
                    },
                ) {
                    Text("Добавить", color = PanelColors.accent)
                }
            }
            splitSettings.bypassDomains.sorted().forEach { domain ->
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clip(RoundedCornerShape(8.dp))
                        .background(PanelColors.panel)
                        .border(1.dp, PanelColors.line, RoundedCornerShape(8.dp))
                        .padding(start = 12.dp, end = 4.dp),
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    Text(domain, color = PanelColors.text, modifier = Modifier.weight(1f))
                    TextButton(enabled = canEditSplit, onClick = { onRemoveBypassDomain(domain) }) {
                        Text("Удалить", color = PanelColors.danger)
                    }
                }
            }
            ui.error?.let { Text(it, color = PanelColors.danger, fontSize = 13.sp) }
        }
    }
}

@Composable
private fun InstalledAppIcon(app: InstalledApp) {
    AndroidView(
        factory = { context -> ImageView(context).apply { contentDescription = app.label } },
        update = { imageView -> imageView.setImageDrawable(app.icon) },
        modifier = Modifier.size(32.dp),
    )
}

@Composable
fun AboutScreen(version: String, onBack: () -> Unit) {
    Scaffold(containerColor = PanelColors.bg) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .padding(horizontal = 20.dp, vertical = 12.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
        ) {
            TopBar(title = "О программе", action = "Назад", onAction = onBack)
            Spacer(Modifier.height(28.dp))
            Image(
                painter = painterResource(R.drawable.ic_logo),
                contentDescription = "Логотип Mvpn",
                modifier = Modifier
                    .size(120.dp)
                    .clip(RoundedCornerShape(28.dp)),
            )
            Spacer(Modifier.height(16.dp))
            Text("Mvpn", color = PanelColors.text, fontSize = 28.sp, fontWeight = FontWeight.Bold)
            Text("Версия $version", color = PanelColors.muted, modifier = Modifier.padding(top = 6.dp))
            Text(
                "Клиент для подключения к серверам VPN. Ключ можно вставить вручную или считать с QR-кода.",
                color = PanelColors.muted,
                fontSize = 14.sp,
                textAlign = TextAlign.Center,
                modifier = Modifier.padding(top = 18.dp),
            )
        }
    }
}

@Composable
internal fun TopBar(
    title: String,
    action: String,
    onAction: () -> Unit,
    iconAction: Boolean = false,
    splitTunnelEnabled: Boolean = false,
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(bottom = 8.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Image(
            painter = painterResource(R.drawable.ic_logo),
            contentDescription = null,
            modifier = Modifier
                .size(36.dp)
                .clip(RoundedCornerShape(8.dp)),
        )
        Spacer(Modifier.width(10.dp))
        Text(title, color = PanelColors.text, fontSize = 22.sp, fontWeight = FontWeight.SemiBold, modifier = Modifier.weight(1f))
        if (splitTunnelEnabled) {
            Image(
                painter = painterResource(R.drawable.ic_split),
                contentDescription = "Раздельное туннелирование включено",
                colorFilter = ColorFilter.tint(PanelColors.accent),
                modifier = Modifier
                    .padding(end = 4.dp)
                    .size(22.dp),
            )
        }
        if (iconAction) {
            IconButton(
                onClick = onAction,
                modifier = Modifier.semantics { contentDescription = action },
            ) {
                Image(
                    painter = painterResource(R.drawable.ic_settings),
                    contentDescription = null,
                    modifier = Modifier.size(24.dp),
                )
            }
        } else {
            TextButton(onClick = onAction) {
                Text(action, color = PanelColors.accent)
            }
        }
    }
}

private enum class DockTab { Home, Servers }

@Composable
private fun BottomDock(
    selected: DockTab,
    onHome: () -> Unit,
    onServers: () -> Unit,
    onChat: () -> Unit,
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(top = 8.dp, bottom = 6.dp),
        horizontalArrangement = Arrangement.SpaceEvenly,
        verticalAlignment = Alignment.CenterVertically,
    ) {
        DockIcon(R.drawable.ic_nav_home, "Главная", selected == DockTab.Home, onHome)
        DockIcon(R.drawable.ic_nav_servers, "Серверы", selected == DockTab.Servers, onServers)
        DockIcon(R.drawable.ic_nav_chat, "Чат поддержки", false, onChat)
    }
}

@Composable
private fun DockIcon(icon: Int, label: String, selected: Boolean, onClick: () -> Unit) {
    IconButton(
        onClick = onClick,
        modifier = Modifier.semantics { contentDescription = label },
    ) {
        Image(
            painter = painterResource(icon),
            contentDescription = null,
            colorFilter = ColorFilter.tint(if (selected) PanelColors.accent else PanelColors.muted),
            modifier = Modifier.size(26.dp),
        )
    }
}

@Composable
private fun TrialRow(claiming: Boolean, onClick: () -> Unit) {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(12.dp))
            .background(PanelColors.panel)
            .drawBehind {
                val stroke = 1.dp.toPx()
                drawRoundRect(
                    color = PanelColors.line,
                    style = Stroke(
                        width = stroke,
                        pathEffect = PathEffect.dashPathEffect(floatArrayOf(14f, 10f)),
                    ),
                    cornerRadius = CornerRadius(12.dp.toPx(), 12.dp.toPx()),
                )
            }
            .clickable(enabled = !claiming, onClick = onClick)
            .padding(14.dp),
        verticalArrangement = Arrangement.spacedBy(4.dp),
    ) {
        Text("Тестовый сервер", color = PanelColors.text, fontWeight = FontWeight.SemiBold)
        Text(
            if (claiming) "Получаем ключ…" else "1 день, скорость 1 Мбит/с",
            color = PanelColors.muted,
            fontSize = 13.sp,
        )
    }
}

@Composable
private fun ConnectControl(phase: Phase, enabled: Boolean, onClick: () -> Unit) {
    val spin = rememberInfiniteTransition(label = "connect")
    val angle by spin.animateFloat(
        initialValue = 0f,
        targetValue = 360f,
        animationSpec = infiniteRepeatable(tween(1100, easing = LinearEasing), RepeatMode.Restart),
        label = "angle",
    )
    val ring = when (phase) {
        Phase.Connected -> PanelColors.online
        Phase.Connecting -> PanelColors.accent
        Phase.Idle -> PanelColors.line
    }
    Box(
        modifier = Modifier
            .size(196.dp)
            .clip(CircleShape)
            .clickable(enabled = enabled && phase != Phase.Connecting, onClick = onClick),
        contentAlignment = Alignment.Center,
    ) {
        Canvas(Modifier.fillMaxSize()) {
            val stroke = 4.dp.toPx()
            val inset = stroke / 2
            drawCircle(color = PanelColors.panel, radius = size.minDimension / 2 - stroke)
            drawCircle(color = ring, radius = size.minDimension / 2 - inset, style = Stroke(stroke))
            if (phase == Phase.Connecting) {
                drawArc(
                    color = PanelColors.accent,
                    startAngle = angle,
                    sweepAngle = 90f,
                    useCenter = false,
                    style = Stroke(width = stroke, cap = StrokeCap.Round),
                    topLeft = Offset(inset, inset),
                    size = Size(size.width - stroke, size.height - stroke),
                )
            }
        }
        Canvas(Modifier.size(54.dp)) {
            val color = when (phase) {
                Phase.Connected -> PanelColors.online
                Phase.Connecting -> PanelColors.accent
                Phase.Idle -> if (enabled) PanelColors.text else PanelColors.muted
            }
            val stroke = 4.dp.toPx()
            drawArc(
                color = color,
                startAngle = -50f,
                sweepAngle = 280f,
                useCenter = false,
                style = Stroke(stroke, cap = StrokeCap.Round),
            )
            drawLine(
                color = color,
                start = Offset(size.width / 2, size.height * 0.12f),
                end = Offset(size.width / 2, size.height * 0.48f),
                strokeWidth = stroke,
                cap = StrokeCap.Round,
            )
        }
    }
}

@Composable
private fun StatCard(label: String, value: String, modifier: Modifier) {
    Column(
        modifier = modifier
            .clip(RoundedCornerShape(12.dp))
            .background(PanelColors.panel)
            .border(1.dp, PanelColors.line, RoundedCornerShape(12.dp))
            .padding(12.dp),
    ) {
        Text(label, color = PanelColors.muted, fontSize = 12.sp)
        Text(value, color = PanelColors.text, fontWeight = FontWeight.SemiBold, fontSize = 16.sp)
    }
}

@Composable
private fun MenuCard(
    icon: Int,
    title: String,
    subtitle: String,
    onClick: () -> Unit,
    subtitleColor: Color = PanelColors.muted,
) {
    PanelCard(onClick = onClick) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            Image(
                painter = painterResource(icon),
                contentDescription = null,
                colorFilter = ColorFilter.tint(PanelColors.accent),
                modifier = Modifier.size(24.dp),
            )
            Spacer(Modifier.width(12.dp))
            Column(modifier = Modifier.weight(1f)) {
                Text(title, color = PanelColors.text, fontWeight = FontWeight.SemiBold)
                Text(subtitle, color = subtitleColor, fontSize = 13.sp)
            }
            Text("›", color = PanelColors.muted, fontSize = 22.sp)
        }
    }
}

@Composable
private fun PanelCard(onClick: () -> Unit, content: @Composable () -> Unit) {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(12.dp))
            .background(PanelColors.panel)
            .border(1.dp, PanelColors.line, RoundedCornerShape(12.dp))
            .clickable(onClick = onClick)
            .padding(14.dp),
        verticalArrangement = Arrangement.spacedBy(4.dp),
        content = { content() },
    )
}

@Composable
private fun SupportLink(onClick: () -> Unit) {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(12.dp))
            .background(PanelColors.panel)
            .border(1.dp, PanelColors.line, RoundedCornerShape(12.dp))
            .clickable(onClick = onClick)
            .padding(14.dp),
    ) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            Image(
                painter = painterResource(R.drawable.ic_nav_chat),
                contentDescription = null,
                colorFilter = ColorFilter.tint(PanelColors.accent),
                modifier = Modifier.size(24.dp),
            )
            Spacer(Modifier.width(12.dp))
            Text(
                "Чат поддержки",
                color = PanelColors.text,
                fontWeight = FontWeight.SemiBold,
                modifier = Modifier.weight(1f),
            )
            Text("›", color = PanelColors.muted, fontSize = 22.sp)
        }
    }
}

@Composable
private fun SettingRow(label: String, value: String) {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(12.dp))
            .background(PanelColors.panel)
            .border(1.dp, PanelColors.line, RoundedCornerShape(12.dp))
            .padding(14.dp),
    ) {
        Text(label, color = PanelColors.muted, fontSize = 12.sp)
        Text(value, color = PanelColors.text, fontWeight = FontWeight.Medium)
    }
}

@Composable
internal fun GhostButton(label: String, onClick: () -> Unit) {
    TextButton(
        onClick = onClick,
        modifier = Modifier
            .fillMaxWidth()
            .border(1.dp, PanelColors.line, RoundedCornerShape(8.dp)),
    ) {
        Text(label, color = PanelColors.text)
    }
}

@Composable
private fun fieldColors() = OutlinedTextFieldDefaults.colors(
    focusedTextColor = PanelColors.text,
    unfocusedTextColor = PanelColors.text,
    focusedBorderColor = PanelColors.accent,
    unfocusedBorderColor = PanelColors.line,
    cursorColor = PanelColors.accent,
    focusedContainerColor = PanelColors.inset,
    unfocusedContainerColor = PanelColors.inset,
    focusedPlaceholderColor = PanelColors.muted,
    unfocusedPlaceholderColor = PanelColors.muted,
)
