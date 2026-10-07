package app.vpnadmin.client

import android.app.Application

class VpnApp : Application() {
    val tunnels: TunnelController by lazy { TunnelController(this) }
}
