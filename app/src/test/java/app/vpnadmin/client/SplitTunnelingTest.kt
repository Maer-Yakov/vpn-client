package app.vpnadmin.client

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class SplitTunnelingTest {
    private val configuration = """
        [Interface]
        PrivateKey = private
        Address = 10.0.0.2/32
        IncludedApplications = old.vpn.app

        [Peer]
        PublicKey = public
        Endpoint = vpn.example.com:51820
        ExcludedApplications = peer.comment.must.remain
    """.trimIndent()

    @Test
    fun selectedPackagesCanBeRestrictedToVpn() {
        val result = SplitTunnelSettings(
            mode = AppRouteMode.SelectedThroughVpn,
            packages = setOf("com.example.mail", "com.example.browser"),
        ).applyTo(configuration)

        assertTrue(result.contains("IncludedApplications = com.example.browser, com.example.mail"))
        assertFalse(result.contains("IncludedApplications = old.vpn.app"))
        assertTrue(result.contains("ExcludedApplications = peer.comment.must.remain"))
        assertFalse(result.contains("ExcludedApplications = com.example"))
    }

    @Test
    fun selectedPackagesCanBypassVpn() {
        val result = SplitTunnelSettings(
            mode = AppRouteMode.SelectedBypassVpn,
            packages = setOf("com.example.mail"),
        ).applyTo(configuration)

        assertTrue(result.contains("ExcludedApplications = com.example.mail"))
        assertFalse(result.contains("IncludedApplications = old.vpn.app"))
    }

    @Test
    fun allTrafficModeLeavesConfigurationUntouched() {
        assertEquals(configuration, SplitTunnelSettings().applyTo(configuration))
    }

    @Test(expected = IllegalArgumentException::class)
    fun splitModeRequiresAtLeastOneValidPackage() {
        SplitTunnelSettings(
            mode = AppRouteMode.SelectedBypassVpn,
            packages = setOf("not a package"),
        ).applyTo(configuration)
    }
}