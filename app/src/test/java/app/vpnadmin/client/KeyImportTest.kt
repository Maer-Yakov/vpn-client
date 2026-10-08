package app.vpnadmin.client

import org.json.JSONObject
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test
import java.util.Base64
import java.util.zip.Deflater

class KeyImportTest {
    @Test
    fun rejectsOversizedSharedPayload() {
        val error = runCatching { KeyImport.parse("x".repeat(512 * 1024 + 1)) }.exceptionOrNull()

        assertTrue(error is IllegalArgumentException)
        assertTrue(error?.message.orEmpty().contains("слишком большой"))
    }

    @Test
    fun decodesPanelVpnUri() {
        val conf = """
            # Дом
            [Interface]
            PrivateKey = AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=
            Address = 10.8.1.2/32
            DNS = 1.1.1.1
            Jc = 4

            [Peer]
            PublicKey = BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB=
            PresharedKey = CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC=
            Endpoint = 203.0.113.10:51820
            AllowedIPs = 0.0.0.0/0, ::/0
            PersistentKeepalive = 25
        """.trimIndent()
        val json = JSONObject()
            .put("description", "Дом (NL)")
            .put("expiresAt", "2026-12-31T15:30:00Z")
            .put(
                "containers",
                org.json.JSONArray().put(
                    JSONObject().put(
                        "amneziawg",
                        JSONObject().put("last_config", conf),
                    ),
                ),
            )
        val message = "VPN-ключ для Иван (AmneziaWG)\nIP 10.8.1.2\n\n${panelVpnUri(json.toString())}"
        val imported = KeyImport.parse(message)
        assertEquals("Дом (NL)", imported.title)
        assertEquals("203.0.113.10:51820", imported.endpoint)
        assertEquals("10.8.1.2", imported.address)
        assertEquals("AmneziaWG", imported.protocol)
        assertEquals("1.1.1.1", imported.dns)
        assertTrue(imported.conf.contains("Jc = 4"))
        assertTrue(imported.conf.contains("PrivateKey = AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA="))
        assertEquals(SubscriptionExpiry.parseIsoToMillis("2026-12-31T15:30:00Z"), imported.expiresAtMillis)
    }

    @Test
    fun readsExpiresAtFromConfComment() {
        val imported = KeyImport.parse(
            """
            # Офис
            # ExpiresAt = 2026-10-10T12:00:00Z
            [Interface]
            PrivateKey = AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=
            Address = 10.8.1.3/32

            [Peer]
            PublicKey = BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB=
            Endpoint = 203.0.113.10:51820
            AllowedIPs = 0.0.0.0/0
            """.trimIndent(),
        )
        assertEquals(SubscriptionExpiry.parseIsoToMillis("2026-10-10T12:00:00Z"), imported.expiresAtMillis)
    }

    @Test
    fun parsesPlainConf() {
        val imported = KeyImport.parse(
            """
            # Офис
            [Interface]
            PrivateKey = AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=
            Address = 10.8.1.3/32

            [Peer]
            PublicKey = BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB=
            Endpoint = vpn.example.com:51820
            AllowedIPs = 0.0.0.0/0
            """.trimIndent(),
        )
        assertEquals("Офис", imported.title)
        assertEquals("vpn.example.com:51820", imported.endpoint)
        assertEquals("WireGuard", imported.protocol)
    }

    @Test
    fun rejectsOtherProtocols() {
        val json = JSONObject()
            .put("description", "XRay")
            .put(
                "containers",
                org.json.JSONArray().put(
                    JSONObject().put(
                        "xray",
                        JSONObject().put("last_config", "not wireguard"),
                    ),
                ),
            )
        val error = runCatching { KeyImport.parse(panelVpnUri(json.toString())) }.exceptionOrNull()
        assertTrue(error is IllegalArgumentException)
        assertTrue(error?.message.orEmpty().contains("не поддерживается"))
    }

    private fun panelVpnUri(json: String): String {
        val raw = json.toByteArray(Charsets.UTF_8)
        val deflater = Deflater()
        deflater.setInput(raw)
        deflater.finish()
        val compressed = ByteArray(raw.size + 64)
        val written = deflater.deflate(compressed)
        deflater.end()
        val payload = ByteArray(4 + written)
        payload[0] = (raw.size ushr 24).toByte()
        payload[1] = (raw.size ushr 16).toByte()
        payload[2] = (raw.size ushr 8).toByte()
        payload[3] = raw.size.toByte()
        System.arraycopy(compressed, 0, payload, 4, written)
        return "vpn://" + Base64.getUrlEncoder().withoutPadding().encodeToString(payload)
    }

    @Test
    fun recognizesQrPayload() {
        assertTrue(looksLikeVpnKey("prefix vpn://abc"))
        assertTrue(looksLikeVpnKey("[Interface]\nPrivateKey = a\n[Peer]\n"))
        assertFalse(looksLikeVpnKey("https://example.com"))
    }
}
