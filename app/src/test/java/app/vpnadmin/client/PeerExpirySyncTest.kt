package app.vpnadmin.client

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test

class PeerExpirySyncTest {
    @Test
    fun enabledClientKeepsAccess() {
        val result = PeerExpirySync.parse(
            200,
            """{"address":"10.8.1.2","expires_at":"2026-12-31T15:30:00Z","enabled":true,"active":true}""",
        )!!
        assertTrue(result.found)
        assertTrue(result.enabled)
        assertFalse(result.accessDenied)
        assertEquals(SubscriptionExpiry.parseIsoToMillis("2026-12-31T15:30:00Z"), result.expiresAtMillis)
    }

    @Test
    fun disabledClientDeniesAccess() {
        val result = PeerExpirySync.parse(
            200,
            """{"address":"10.8.1.2","expires_at":null,"enabled":false,"active":false}""",
        )!!
        assertFalse(result.enabled)
        assertFalse(result.revoked)
        assertTrue(result.accessDenied)
    }

    @Test
    fun expiredClientDeniesAccess() {
        val result = PeerExpirySync.parse(
            200,
            """{"address":"10.8.1.2","expires_at":"2020-01-01T00:00:00Z","enabled":true,"active":false}""",
        )!!
        assertTrue(result.accessDenied)
    }

    @Test
    fun oldPanelWithoutEnabledFieldIsTreatedAsEnabled() {
        val result = PeerExpirySync.parse(200, """{"address":"10.8.1.2","expires_at":null}""")!!
        assertTrue(result.enabled)
        assertFalse(result.accessDenied)
    }

    @Test
    fun panelNotFoundMeansRevoked() {
        val result = PeerExpirySync.parse(404, """{"detail":"Peer not found","revoked":true}""")!!
        assertTrue(result.revoked)
        assertTrue(result.accessDenied)
    }

    @Test
    fun foreignNotFoundIsIgnored() {
        assertNull(PeerExpirySync.parse(404, "<html>404 Not Found</html>"))
        assertNull(PeerExpirySync.parse(404, """{"detail":"Not Found"}"""))
    }

    @Test
    fun serverErrorIsNotAnAnswer() {
        val error = runCatching { PeerExpirySync.parse(502, "") }.exceptionOrNull()
        assertTrue(error is IllegalStateException)
    }
}
