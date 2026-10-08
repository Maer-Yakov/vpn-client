package app.vpnadmin.client

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class AppUpdaterTest {
    @Test
    fun newerVersionComparesSemver() {
        assertTrue(AppUpdater.isNewerVersion("1.4.0", "1.3.0"))
        assertTrue(AppUpdater.isNewerVersion("v2.0.0", "1.9.9"))
        assertFalse(AppUpdater.isNewerVersion("1.3.0", "1.3.0"))
        assertFalse(AppUpdater.isNewerVersion("1.2.0", "1.3.0"))
    }

    @Test
    fun parseVersionPartsStripsPrefix() {
        assertEquals(listOf(1, 4, 0), AppUpdater.parseVersionParts("v1.4.0"))
        assertEquals(listOf(1, 3), AppUpdater.parseVersionParts("1.3"))
    }
}
