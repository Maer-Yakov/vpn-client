package app.vpnadmin.client

import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class SiteDomainTest {
    @Test
    fun acceptsUrlAndKeepsOnlyNormalizedHost() {
        assertEquals("example.com", SiteDomain.normalize(" HTTPS://Example.COM:443/path?q=1 "))
        assertEquals("example.com", SiteDomain.normalize("example.com/section"))
    }

    @Test
    fun convertsInternationalDomainToAscii() {
        assertEquals("xn--e1afmkfd.xn--p1ai", SiteDomain.normalize("пример.рф"))
    }

    @Test
    fun rejectsIpAddressesAndUnsupportedSchemes() {
        val ip = runCatching { SiteDomain.normalize("https://192.168.1.10") }.exceptionOrNull()
        val scheme = runCatching { SiteDomain.normalize("ftp://example.com") }.exceptionOrNull()

        assertTrue(ip is IllegalArgumentException)
        assertTrue(scheme is IllegalArgumentException)
    }
}