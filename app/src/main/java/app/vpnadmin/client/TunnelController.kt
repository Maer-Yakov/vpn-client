package app.vpnadmin.client

import android.app.Application
import org.amnezia.awg.backend.GoBackend
import org.amnezia.awg.backend.Tunnel
import org.amnezia.awg.config.Config
import java.io.ByteArrayInputStream

class TunnelController(app: Application) {
    private val backend = GoBackend(app)
    private val tunnel = object : Tunnel {
        override fun getName(): String = "vpn"

        override fun onStateChange(newState: Tunnel.State) {
            listener?.invoke(newState)
        }
    }

    @Volatile
    private var config: Config? = null

    @Volatile
    var listener: ((Tunnel.State) -> Unit)? = null

    fun connect(conf: String, splitTunnel: SplitTunnelSettings = SplitTunnelSettings()) {
        val routedConf = splitTunnel.applyTo(conf)
        val parsed = Config.parse(ByteArrayInputStream(routedConf.toByteArray(Charsets.UTF_8)))
        val exclusions = SiteRouteResolver.resolve(splitTunnel.bypassDomains)
        backend.setRouteExclusions(exclusions)
        try {
            backend.setState(tunnel, Tunnel.State.UP, parsed)
            config = parsed
        } finally {
            backend.setRouteExclusions(emptySet())
        }
    }

    fun disconnect() {
        try {
            backend.setState(tunnel, Tunnel.State.DOWN, null)
        } finally {
            backend.setRouteExclusions(emptySet())
            config = null
        }
    }

    fun isUp(): Boolean = backend.getState(tunnel) == Tunnel.State.UP

    fun snapshot(): TrafficSnapshot {
        val current = config ?: return TrafficSnapshot(0, 0, 0)
        val stats = backend.getStatistics(tunnel)
        val peer = current.peers.firstOrNull()?.let { stats.peer(it.publicKey) }
        return TrafficSnapshot(
            rxBytes = stats.totalRx(),
            txBytes = stats.totalTx(),
            handshakeEpochMillis = peer?.latestHandshakeEpochMillis ?: 0L,
        )
    }
}

data class TrafficSnapshot(
    val rxBytes: Long,
    val txBytes: Long,
    val handshakeEpochMillis: Long,
)
