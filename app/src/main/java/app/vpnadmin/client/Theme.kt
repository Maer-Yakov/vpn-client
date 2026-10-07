package app.vpnadmin.client

import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color

object PanelColors {
    val bg = Color(0xFF0E1218)
    val panel = Color(0xFF161C25)
    val line = Color(0xFF2A3442)
    val text = Color(0xFFE8EEF6)
    val muted = Color(0xFF8B98A8)
    val accent = Color(0xFF3DD6C6)
    val accentInk = Color(0xFF06221E)
    val online = Color(0xFF3ECF8E)
    val danger = Color(0xFFE85D75)
    val inset = Color(0xFF10161E)
}

@Composable
fun VpnTheme(content: @Composable () -> Unit) {
    MaterialTheme(
        colorScheme = darkColorScheme(
            primary = PanelColors.accent,
            onPrimary = PanelColors.accentInk,
            background = PanelColors.bg,
            surface = PanelColors.panel,
            onBackground = PanelColors.text,
            onSurface = PanelColors.text,
            error = PanelColors.danger,
            outline = PanelColors.line,
        ),
        content = content,
    )
}
