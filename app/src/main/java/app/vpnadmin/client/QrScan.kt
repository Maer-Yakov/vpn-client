package app.vpnadmin.client

import android.Manifest
import android.content.pm.PackageManager
import android.util.Size
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.camera.core.CameraSelector
import androidx.camera.core.ExperimentalGetImage
import androidx.camera.core.ImageAnalysis
import androidx.camera.core.Preview
import androidx.camera.core.resolutionselector.ResolutionSelector
import androidx.camera.core.resolutionselector.ResolutionStrategy
import androidx.camera.lifecycle.ProcessCameraProvider
import androidx.camera.view.PreviewView
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.viewinterop.AndroidView
import androidx.core.content.ContextCompat
import androidx.lifecycle.compose.LocalLifecycleOwner
import com.google.mlkit.vision.barcode.BarcodeScanning
import com.google.mlkit.vision.common.InputImage
import java.util.concurrent.Executors
import java.util.concurrent.atomic.AtomicBoolean

@Composable
fun QrScanScreen(onBack: () -> Unit, onResult: (String) -> Unit) {
    val context = LocalContext.current
    var granted by remember {
        mutableStateOf(
            ContextCompat.checkSelfPermission(context, Manifest.permission.CAMERA) == PackageManager.PERMISSION_GRANTED,
        )
    }
    var cameraError by remember { mutableStateOf<String?>(null) }
    val permission = rememberLauncherForActivityResult(ActivityResultContracts.RequestPermission()) {
        granted = it
    }
    LaunchedEffect(Unit) {
        if (!granted) permission.launch(Manifest.permission.CAMERA)
    }
    Scaffold(containerColor = PanelColors.bg) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .padding(horizontal = 20.dp, vertical = 12.dp),
        ) {
            TopBar(title = "QR-код", action = "Назад", onAction = onBack)
            when {
                !granted -> {
                    Text(
                        "Чтобы считать ключ, разрешите приложению камеру.",
                        color = PanelColors.muted,
                        fontSize = 14.sp,
                    )
                    GhostButton("Разрешить камеру") { permission.launch(Manifest.permission.CAMERA) }
                }
                cameraError != null -> {
                    Text(cameraError.orEmpty(), color = PanelColors.danger, fontSize = 14.sp)
                }
                else -> {
                    Text(
                        "Наведите камеру на QR-код.",
                        color = PanelColors.muted,
                        fontSize = 14.sp,
                    )
                    Box(
                        modifier = Modifier
                            .fillMaxWidth()
                            .weight(1f)
                            .padding(top = 16.dp),
                        contentAlignment = Alignment.Center,
                    ) {
                        CameraPreview(
                            onResult = onResult,
                            onError = { cameraError = "Камера недоступна" },
                        )
                        Box(
                            modifier = Modifier
                                .size(240.dp)
                                .border(2.dp, PanelColors.accent, RoundedCornerShape(16.dp)),
                        )
                    }
                }
            }
        }
    }
}

@Composable
@androidx.annotation.OptIn(markerClass = [ExperimentalGetImage::class])
private fun CameraPreview(onResult: (String) -> Unit, onError: () -> Unit) {
    val context = LocalContext.current
    val lifecycleOwner = LocalLifecycleOwner.current
    val previewView = remember {
        PreviewView(context).apply {
            scaleType = PreviewView.ScaleType.FILL_CENTER
        }
    }
    val handled = remember { AtomicBoolean(false) }
    DisposableEffect(lifecycleOwner) {
        val executor = Executors.newSingleThreadExecutor()
        val mainExecutor = ContextCompat.getMainExecutor(context)
        val scanner = BarcodeScanning.getClient()
        val cameraProviderFuture = ProcessCameraProvider.getInstance(context)
        cameraProviderFuture.addListener({
            val provider = try {
                cameraProviderFuture.get()
            } catch (_: Exception) {
                onError()
                return@addListener
            }
            val resolution = ResolutionSelector.Builder()
                .setResolutionStrategy(
                    ResolutionStrategy(
                        Size(1920, 1080),
                        ResolutionStrategy.FALLBACK_RULE_CLOSEST_HIGHER_THEN_LOWER,
                    ),
                )
                .build()
            val preview = Preview.Builder().build().also {
                it.surfaceProvider = previewView.surfaceProvider
            }
            val analysis = ImageAnalysis.Builder()
                .setResolutionSelector(resolution)
                .setBackpressureStrategy(ImageAnalysis.STRATEGY_KEEP_ONLY_LATEST)
                .build()
            analysis.setAnalyzer(executor) { image ->
                val media = image.image
                if (media == null || handled.get()) {
                    image.close()
                    return@setAnalyzer
                }
                val input = InputImage.fromMediaImage(media, image.imageInfo.rotationDegrees)
                scanner.process(input)
                    .addOnSuccessListener(mainExecutor) { codes ->
                        val raw = codes.mapNotNull { it.rawValue }.firstOrNull(::looksLikeVpnKey)
                        if (raw != null && handled.compareAndSet(false, true)) {
                            onResult(raw)
                        }
                    }
                    .addOnCompleteListener(executor) { image.close() }
            }
            try {
                provider.unbindAll()
                provider.bindToLifecycle(
                    lifecycleOwner,
                    CameraSelector.DEFAULT_BACK_CAMERA,
                    preview,
                    analysis,
                )
            } catch (_: Exception) {
                onError()
            }
        }, mainExecutor)
        onDispose {
            handled.set(true)
            scanner.close()
            if (cameraProviderFuture.isDone) {
                runCatching { cameraProviderFuture.get().unbindAll() }
            }
            executor.shutdown()
        }
    }
    AndroidView(factory = { previewView }, modifier = Modifier.fillMaxSize())
}

internal fun looksLikeVpnKey(text: String): Boolean {
    val value = text.trim()
    return value.contains("vpn://") ||
        (value.contains("[Interface]", ignoreCase = true) && value.contains("[Peer]", ignoreCase = true))
}
