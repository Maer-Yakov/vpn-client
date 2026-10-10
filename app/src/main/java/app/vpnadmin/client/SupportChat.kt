package app.vpnadmin.client

import android.content.ActivityNotFoundException
import android.content.ComponentName
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.net.Uri

object SupportChat {
    const val URL = "https://t.me/Maer_VPN_bot"
    private val PACKAGES = listOf(
        "org.telegram.messenger",
        "org.telegram.messenger.web",
        "org.thunderdog.challegram",
    )

    fun open(context: Context): Boolean {
        val app = telegramIntent(context)
        if (app != null && start(context, app)) return true
        return start(context, Intent(Intent.ACTION_VIEW, Uri.parse(URL)))
    }

    private fun telegramIntent(context: Context): Intent? {
        val packageName = installedTelegram(context) ?: return null
        val uri = Uri.parse(URL)
        val probe = Intent(Intent.ACTION_VIEW, uri).setPackage(packageName)
        val match = context.packageManager.resolveActivity(probe, PackageManager.MATCH_DEFAULT_ONLY)
        return Intent(Intent.ACTION_VIEW, uri).apply {
            if (match != null && match.activityInfo?.packageName == packageName) {
                component = ComponentName(packageName, match.activityInfo.name)
            } else {
                setPackage(packageName)
            }
            addFlags(Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP or Intent.FLAG_ACTIVITY_SINGLE_TOP)
        }
    }

    private fun installedTelegram(context: Context): String? {
        val manager = context.packageManager
        return PACKAGES.firstOrNull { packageName ->
            try {
                manager.getPackageInfo(packageName, 0)
                true
            } catch (_: PackageManager.NameNotFoundException) {
                false
            }
        }
    }

    private fun start(context: Context, intent: Intent): Boolean {
        return try {
            context.startActivity(intent)
            true
        } catch (_: ActivityNotFoundException) {
            false
        }
    }
}
