package app.vpnadmin.client

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.animation.core.Animatable
import androidx.compose.animation.core.FastOutSlowInEasing
import androidx.compose.animation.core.tween
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.alpha
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch

@Composable
internal fun MvpnStartupAnimation(onFinished: () -> Unit) {
    var visible by remember { mutableStateOf(true) }
    val progress = remember { List(4) { Animatable(0f) } }
    val letters = listOf("M", "v", "p", "n")
    val starts = listOf(-132f to 0f, 0f to -110f, 0f to 110f, 132f to 0f)

    LaunchedEffect(Unit) {
        progress.forEachIndexed { index, animation ->
            launch {
                delay(index * 115L)
                animation.animateTo(1f, tween(650, easing = FastOutSlowInEasing))
            }
        }
        delay(1050)
        visible = false
        delay(280)
        onFinished()
    }

    AnimatedVisibility(
        visible = visible,
        enter = fadeIn(tween(160)),
        exit = fadeOut(tween(280)),
    ) {
        Box(
            modifier = Modifier
                .fillMaxSize()
                .background(PanelColors.bg),
            contentAlignment = Alignment.Center,
        ) {
            Image(
                painter = painterResource(R.drawable.ic_logo),
                contentDescription = null,
                modifier = Modifier
                    .size(236.dp)
                    .clip(RoundedCornerShape(44.dp))
                    .alpha(0.3f),
            )
            Row(verticalAlignment = Alignment.CenterVertically) {
                letters.forEachIndexed { index, letter ->
                    Text(
                        text = letter,
                        color = if (index % 2 == 0) PanelColors.text else PanelColors.accent,
                        fontSize = 48.sp,
                        fontWeight = FontWeight.Bold,
                        modifier = Modifier.graphicsLayer {
                            val amount = progress[index].value
                            translationX = starts[index].first * (1f - amount) * density
                            translationY = starts[index].second * (1f - amount) * density
                            alpha = amount
                        },
                    )
                }
            }
        }
    }
}