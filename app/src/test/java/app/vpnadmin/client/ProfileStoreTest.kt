package app.vpnadmin.client

import java.io.File
import java.nio.file.Files
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertTrue
import org.junit.Test

class ProfileStoreTest {
    @Test
    fun oldProfilesLoadWithSplitTunnelingDisabled() {
        val directory = Files.createTempDirectory("profile-store-old").toFile()
        try {
            File(directory, "servers.json").writeText(
                """{"active":"server-1","servers":[{"id":"server-1","title":"Office","endpoint":"vpn.example.com:51820","address":"10.0.0.2","dns":"1.1.1.1","protocol":"WireGuard","conf":"[Interface]\\nPrivateKey = private\\n[Peer]\\nPublicKey = public\\n"}]}""",
            )

            val library = ProfileStore(directory).load()

            assertEquals("server-1", library.activeId)
            assertEquals(AppRouteMode.AllTraffic, library.servers.single().splitTunnel.mode)
            assertTrue(library.servers.single().splitTunnel.packages.isEmpty())
        } finally {
            directory.deleteRecursively()
        }
    }

    @Test
    fun splitSettingsSurviveProfileWriteAndReload() {
        val directory = Files.createTempDirectory("profile-store-split").toFile()
        try {
            val store = ProfileStore(directory)
            val profile = store.add(sampleKey()).servers.single()
            val expected = SplitTunnelSettings(
                mode = AppRouteMode.SelectedBypassVpn,
                packages = setOf("com.example.browser", "com.example.mail"),
                bypassDomains = setOf("example.com", "xn--e1afmkfd.xn--p1ai"),
            )

            store.setSplitTunnel(profile.id, expected)

            assertEquals(expected, store.load().servers.single().splitTunnel)
            assertFalse(File(directory, "servers.json.tmp").exists())
        } finally {
            directory.deleteRecursively()
        }
    }

    @Test
    fun pendingFirstWriteIsRecoveredWhenMainFileIsMissing() {
        val directory = Files.createTempDirectory("profile-store-pending").toFile()
        try {
            val store = ProfileStore(directory)
            val expected = store.add(sampleKey()).servers.single()
            val mainFile = File(directory, "servers.json")
            val pendingFile = File(directory, "servers.json.tmp")
            mainFile.copyTo(pendingFile)
            mainFile.delete()

            val recovered = store.load()

            assertEquals(expected.id, recovered.activeId)
            assertEquals(expected.key, recovered.servers.single().key)
            assertFalse(pendingFile.exists())
        } finally {
            directory.deleteRecursively()
        }
    }

    @Test
    fun corruptProfilesArePreservedAndWritesBlocked() {
        val directory = Files.createTempDirectory("profile-store-corrupt").toFile()
        try {
            val original = File(directory, "servers.json")
            original.writeText("{not-json")
            val store = ProfileStore(directory)

            val library = store.load()
            val result = runCatching { store.add(sampleKey()) }

            assertNotNull(library.warning)
            assertTrue(result.isFailure)
            assertEquals("{not-json", original.readText())
            assertTrue(directory.listFiles().orEmpty().any { it.name == "servers.json.corrupt" })
        } finally {
            directory.deleteRecursively()
        }
    }

    private fun sampleKey() = ImportedKey(
        title = "Office",
        conf = "[Interface]\nPrivateKey = private\n[Peer]\nPublicKey = public\n",
        endpoint = "vpn.example.com:51820",
        address = "10.0.0.2",
        dns = "1.1.1.1",
        protocol = "WireGuard",
    )
}