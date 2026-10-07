package app.vpnadmin.client

import android.content.ActivityNotFoundException
import android.content.Context
import android.content.Intent
import android.net.Uri

object SupportChat {
    const val URL = "https://t.me/Maer_VPN_bot"

    fun open(context: Context): Boolean {
        val intent = Intent(Intent.ACTION_VIEW, Uri.parse(URL))
        return try {
            context.startActivity(intent)
            true
        } catch (_: ActivityNotFoundException) {
            false
        }
    }
}
