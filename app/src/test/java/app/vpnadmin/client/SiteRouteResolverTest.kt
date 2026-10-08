package app.vpnadmin.client

import java.net.InetAddress
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class SiteRouteResolverTest {
    @Test
    fun resolvesIpv4AndIpv6AsHostRoutes() {
        val routes = SiteRouteResolver.resolve(setOf("example.com")) {
            arrayOf(InetAddress.getByName("203.0.113.10"), InetAddress.getByName("2001:db8::10"))
        }

        assertEquals(2, routes.size)
        assertTrue(routes.any { it.toString() == "203.0.113.10/32" })
        assertTrue(routes.any { it.toString().endsWith("/128") })
    }

    @Test
    fun reportsDnsFailureBeforeConnecting() {
        val result = runCatching {
            SiteRouteResolver.resolve(setOf("example.com")) { throw java.net.UnknownHostException() }
        }

        assertTrue(result.exceptionOrNull() is IllegalArgumentException)
        assertTrue(result.exceptionOrNull()?.message.orEmpty().contains("example.com"))
    }
}