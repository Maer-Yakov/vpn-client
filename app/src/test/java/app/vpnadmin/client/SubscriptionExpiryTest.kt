package app.vpnadmin.client

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test

class SubscriptionExpiryTest {
    @Test
    fun noDateMeansNoWarning() {
        assertNull(SubscriptionExpiry.daysRemaining(null))
        assertFalse(SubscriptionExpiry.shouldWarn(null))
        assertEquals("Подключено", SubscriptionExpiry.connectedStatus(null).title)
    }

    @Test
    fun warnsWhenTwoDaysOrLessRemain() {
        val now = 1_700_000_000_000L
        val inOneDay = now + 86_400_000L
        val inThreeDays = now + 3 * 86_400_000L
        assertTrue(SubscriptionExpiry.shouldWarn(inOneDay, now))
        assertFalse(SubscriptionExpiry.shouldWarn(inThreeDays, now))
        val status = SubscriptionExpiry.connectedStatus(inOneDay, now)
        assertTrue(status.warning)
        assertEquals("Истекает подписка", status.title)
        assertEquals(SubscriptionExpiry.formatDate(inOneDay), status.date)
    }

    @Test
    fun expiredShowsExpiredLabel() {
        val now = 1_700_000_000_000L
        val past = now - 60_000L
        val status = SubscriptionExpiry.connectedStatus(past, now)
        assertTrue(status.warning)
        assertEquals("Подписка истекла", status.title)
    }

    @Test
    fun parsesIsoDates() {
        val millis = SubscriptionExpiry.parseIsoToMillis("2026-12-31T18:30:00+03:00")
        assertTrue(millis != null && millis > 0L)
        assertEquals(millis, SubscriptionExpiry.parseIsoToMillis("2026-12-31T15:30:00Z"))
    }
}
