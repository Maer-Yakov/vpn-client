package app.vpnadmin.client

import androidx.compose.animation.core.LinearEasing
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.tween
import androidx.compose.foundation.Canvas
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
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.OutlinedTextFieldDefaults
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.platform.LocalClipboardManager
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardCapitalization
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp

@Composable
fun HomeScreen(
    ui: UiState,
    onConnect: () -> Unit,
    onDisconnect: () -> Unit,
    onServers: () -> Unit,
    onSettings: () -> Unit,
    onAdd: () -> Unit,
) {
    val active = ui.active
    val connected = ui.phase == Phase.Connected
    Scaffold(containerColor = PanelColors.bg) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .padding(horizontal = 20.dp, vertical = 12.dp),
        ) {
            TopBar(title = "VPN", action = "Настройки", onAction = onSettings)
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
                Spacer(Modifier.height(22.dp))
                Text(
                    text = when (ui.phase) {
                        Phase.Idle -> if (active == null) "Нет сервера" else "Отключено"
                        Phase.Connecting -> "Подключение"
                        Phase.Connected -> "Подключено"
                    },
                    color = if (connected) PanelColors.online else PanelColors.text,
                    fontSize = 22.sp,
                    fontWeight = FontWeight.SemiBold,
                )
                if (connected) {
                    Text(
                        elapsedLabel(ui.connectedSince, ui.now),
                        color = PanelColors.accent,
                        fontSize = 16.sp,
                        modifier = Modifier.padding(top = 6.dp),
                    )
                }
                if (connected) {
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
                }
            }
            if (active == null) {
                PanelCard(onClick = onAdd) {
                    Text("Добавить сервер", color = PanelColors.text, fontWeight = FontWeight.SemiBold)
                    Text(
                        "Вставьте ключ vpn:// из панели",
                        color = PanelColors.muted,
                        fontSize = 13.sp,
                    )
                }
            } else {
                PanelCard(onClick = onServers) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Column(modifier = Modifier.weight(1f)) {
                            Text(
                                active.key.title,
                                color = PanelColors.text,
                                fontWeight = FontWeight.SemiBold,
                                maxLines = 1,
                                overflow = TextOverflow.Ellipsis,
                            )
                            Text(
                                "${active.key.protocol} · ${active.key.endpoint}",
                                color = PanelColors.muted,
                                fontSize = 13.sp,
                                maxLines = 1,
                                overflow = TextOverflow.Ellipsis,
                            )
                        }
                        Text("›", color = PanelColors.muted, fontSize = 22.sp)
                    }
                }
            }
            ui.error?.let {
                Text(it, color = PanelColors.danger, fontSize = 13.sp, modifier = Modifier.padding(top = 10.dp))
            }
        }
    }
}

@Composable
fun ServersScreen(
    ui: UiState,
    onBack: () -> Unit,
    onAdd: () -> Unit,
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
                    Text("Список пуст. Добавьте ключ из панели.", color = PanelColors.muted)
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
                        Text(server.key.protocol, color = PanelColors.accent, fontSize = 13.sp)
                        Text(server.key.endpoint, color = PanelColors.muted, fontSize = 13.sp)
                        TextButton(onClick = { onDelete(server.id) }) {
                            Text("Удалить", color = PanelColors.danger)
                        }
                    }
                }
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
            Text(
                "Вставьте сообщение из панели со ссылкой vpn:// или текст файла .conf.",
                color = PanelColors.muted,
                fontSize = 14.sp,
            )
            OutlinedTextField(
                value = ui.draft,
                onValueChange = onDraft,
                modifier = Modifier.fillMaxWidth(),
                minLines = 6,
                placeholder = { Text("vpn://…") },
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
fun SettingsScreen(ui: UiState, version: String, onBack: () -> Unit) {
    val key = ui.active?.key
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
            if (key == null) {
                Text("Сервер не выбран.", color = PanelColors.muted)
            } else {
                SettingRow("Сервер", key.title)
                SettingRow("Протокол", key.protocol)
                SettingRow("Адрес сервера", key.endpoint)
                SettingRow("Адрес в сети", key.address)
                SettingRow("DNS", key.dns)
            }
            SettingRow("Версия", version)
            Text(
                "Клиент подключается к вашему серверу ключом из панели. Установщик контейнеров и чужие протоколы здесь не используются.",
                color = PanelColors.muted,
                fontSize = 13.sp,
                modifier = Modifier.padding(top = 8.dp),
            )
        }
    }
}

@Composable
private fun TopBar(title: String, action: String, onAction: () -> Unit) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(bottom = 8.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Box(
            modifier = Modifier
                .size(10.dp)
                .clip(CircleShape)
                .background(PanelColors.accent),
        )
        Spacer(Modifier.width(10.dp))
        Text(title, color = PanelColors.text, fontSize = 22.sp, fontWeight = FontWeight.SemiBold, modifier = Modifier.weight(1f))
        TextButton(onClick = onAction) {
            Text(action, color = PanelColors.accent)
        }
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
private fun GhostButton(label: String, onClick: () -> Unit) {
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
