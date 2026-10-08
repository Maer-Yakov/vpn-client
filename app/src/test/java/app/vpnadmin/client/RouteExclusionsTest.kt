package app.vpnadmin.client

import java.net.InetAddress
import org.amnezia.awg.config.InetNetwork
import org.amnezia.awg.config.RouteExclusions
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class RouteExclusionsTest {
    @Test
    fun removesExcludedIpv4HostFromDefaultRoute() {
        val excluded = InetNetwork.parse("203.0.113.10/32")
        val routes = RouteExclusions.subtract(listOf(InetNetwork.parse("0.0.0.0/0")), listOf(excluded))

        assertFalse(routes.any { contains(it, excluded.address) })
        assertTrue(routes.size <= RouteExclusions.MAX_LEGACY_ROUTES)
    }

    @Test
    fun removesExcludedIpv6HostFromDefaultRoute() {
        val excluded = InetNetwork.parse("2001:db8::10/128")
        val routes = RouteExclusions.subtract(listOf(InetNetwork.parse("::/0")), listOf(excluded))

        assertFalse(routes.any { contains(it, excluded.address) })
        assertTrue(routes.size <= RouteExclusions.MAX_LEGACY_ROUTES)
    }

    @Test(expected = IllegalArgumentException::class)
    fun rejectsExclusionSetThatWouldExceedLegacyRouteLimit() {
        val addresses = (0..2).map { index ->
            val address = listOf("::1", "8000::1", "4000::1")[index]
            InetNetwork.parse("$address/128")
        }
        RouteExclusions.subtract(listOf(InetNetwork.parse("::/0")), addresses)
    }

    private fun contains(network: InetNetwork, address: InetAddress): Boolean {
        val networkBytes = network.address.address
        val addressBytes = address.address
        if (networkBytes.size != addressBytes.size) return false
        val prefix = network.mask
        for (bit in 0 until prefix) {
            val mask = 1 shl (7 - bit % 8)
            if ((networkBytes[bit / 8].toInt() and mask) != (addressBytes[bit / 8].toInt() and mask)) {
                return false
            }
        }
        return true
    }
}