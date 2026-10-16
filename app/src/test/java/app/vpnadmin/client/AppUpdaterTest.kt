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

    private fun asset(id: Long, name: String) = AppUpdater.ApkAsset(id, name, 1000)

    private val splitAssets = listOf(
        asset(1, "Mvpn-1.8.3-arm64-v8a.apk"),
        asset(2, "Mvpn-1.8.3-armeabi-v7a.apk"),
        asset(3, "Mvpn-1.8.3-x86.apk"),
        asset(4, "Mvpn-1.8.3-x86_64.apk"),
    )

    @Test
    fun picksApkForDeviceAbi() {
        assertEquals(1L, AppUpdater.pickApk(splitAssets, listOf("arm64-v8a", "armeabi-v7a", "armeabi"))?.id)
        assertEquals(2L, AppUpdater.pickApk(splitAssets, listOf("armeabi-v7a", "armeabi"))?.id)
        assertEquals(4L, AppUpdater.pickApk(splitAssets, listOf("x86_64", "x86"))?.id)
    }

    @Test
    fun x86IsNotConfusedWithX8664() {
        assertEquals(3L, AppUpdater.pickApk(splitAssets, listOf("x86"))?.id)
    }

    @Test
    fun noMatchingAbiMeansNoUpdate() {
        assertEquals(null, AppUpdater.pickApk(splitAssets.take(1), listOf("x86_64")))
    }

    @Test
    fun legacySingleApkWithoutAbiStillWorks() {
        val legacy = listOf(asset(9, "Mvpn-1.8.1.apk"), asset(10, "notes.txt"))
        assertEquals(9L, AppUpdater.pickApk(legacy, listOf("arm64-v8a"))?.id)
    }

    @Test
    fun parseReleaseUsesAbiAndIgnoresOtherFiles() {
        val body = """
            {"tag_name":"v1.8.3","published_at":"2026-10-17T00:00:00Z","assets":[
              {"id":11,"name":"Mvpn-1.8.3-arm64-v8a.apk","size":100},
              {"id":12,"name":"Mvpn-1.8.3-armeabi-v7a.apk","size":90},
              {"id":13,"name":"changelog.txt","size":1}
            ]}
        """.trimIndent()
        val release = AppUpdater.parseRelease(body, listOf("armeabi-v7a"))
        assertEquals(12L, release?.assetId)
        assertEquals("1.8.3", release?.versionName)
    }

    @Test
    fun parseVersionPartsStripsPrefix() {
        assertEquals(listOf(1, 4, 0), AppUpdater.parseVersionParts("v1.4.0"))
        assertEquals(listOf(1, 3), AppUpdater.parseVersionParts("1.3"))
    }
}
