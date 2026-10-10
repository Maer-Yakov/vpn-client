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
    fun decodesOfficialAwgBlock() {
        val conf = """
            [Interface]
            PrivateKey = AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=
            Address = 10.8.1.4/32
            Jc = 4

            [Peer]
            PublicKey = BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB=
            Endpoint = 203.0.113.10:39743
            AllowedIPs = 0.0.0.0/0
        """.trimIndent()
        val json = JSONObject()
            .put("description", "Polar")
            .put(
                "containers",
                org.json.JSONArray().put(
                    JSONObject().put("awg", JSONObject().put("last_config", conf)),
                ),
            )
        val imported = KeyImport.parse(panelVpnUri(json.toString()))
        assertEquals("Polar", imported.title)
        assertEquals("AmneziaWG", imported.protocol)
        assertEquals("203.0.113.10:39743", imported.endpoint)
    }

    @Test
    fun rejectsUnknownProtocol() {
        val json = JSONObject()
            .put("description", "XRay")
            .put(
                "containers",
                org.json.JSONArray().put(
                    JSONObject().put(
                        "mystery",
                        JSONObject().put("last_config", "not wireguard"),
                    ),
                ),
            )
        val error = runCatching { KeyImport.parse(panelVpnUri(json.toString())) }.exceptionOrNull()
        assertTrue(error is IllegalArgumentException)
        assertTrue(error?.message.orEmpty().contains("не поддерживается"))
    }

    @Test
    fun acceptsEveryPanelQr() {
        val openvpn = """
            # Дом
            client
            dev tun
            proto udp
            remote vpn.example.com 1194
            <ca>
            PLACEHOLDER
            </ca>
        """.trimIndent()
        val ovpn = KeyImport.parse(openvpn)
        assertEquals("OpenVPN", ovpn.protocol)
        assertEquals("vpn.example.com:1194", ovpn.endpoint)
        assertEquals("Дом", ovpn.title)

        val cloak = KeyImport.parse(panelVpnUri(vpnJson("cloak", openvpn.replace("Дом", "OpenVPN over Cloak for Дом"))))
        assertEquals("OpenVPN Cloak", cloak.protocol)
        assertEquals("vpn.example.com:1194", cloak.endpoint)

        val shadowsocks = KeyImport.parse(
            "ss://" + Base64.getEncoder().encodeToString(
                "chacha20-ietf-poly1305:secret@vpn.example.com:8388".toByteArray(),
            ) + "#%D0%A1%D0%B5%D1%82%D1%8C",
        )
        assertEquals("Shadowsocks", shadowsocks.protocol)
        assertEquals("vpn.example.com:8388", shadowsocks.endpoint)
        assertEquals("Сеть", shadowsocks.title)

        val xray = KeyImport.parse(
            panelVpnUri(
                vpnJson(
                    "xray",
                    """{"outbounds":[{"settings":{"vnext":[{"address":"85.137.164.156","port":443}]}}]}""",
                ),
            ),
        )
        assertEquals("XRay", xray.protocol)
        assertEquals("85.137.164.156:443", xray.endpoint)

        val ike = KeyImport.parse(
            panelVpnUri(vpnJson("ikev2", """{"hostName":"85.137.164.156","userName":"client","cert":"Y2VydA==","password":""}""")),
        )
        assertEquals("IKEv2", ike.protocol)
        assertEquals("85.137.164.156", ike.endpoint)
    }

    @Test
    fun parsesXrayVlessLink() {
        val imported = KeyImport.parse(
            "vless://11111111-2222-3333-4444-555555555555@85.137.164.156:443?encryption=none&security=reality&type=tcp#XRay%20Nord",
        )
        assertEquals("XRay Nord", imported.title)
        assertEquals("XRay", imported.protocol)
        assertEquals("85.137.164.156:443", imported.endpoint)
        assertTrue(imported.conf.startsWith("vless://"))
    }

    private fun vpnJson(key: String, lastConfig: String): String {
        return JSONObject()
            .put("description", "Клиент")
            .put(
                "containers",
                org.json.JSONArray().put(JSONObject().put(key, JSONObject().put("last_config", lastConfig))),
            )
            .toString()
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
        assertTrue(looksLikeVpnKey("vless://11111111-2222-3333-4444-555555555555@host:443#name"))
        assertTrue(looksLikeVpnKey("ss://YWJj@host:1"))
        assertTrue(looksLikeVpnKey("client\ndev tun\nremote vpn.example.com 1194\n<ca>\n"))
        assertFalse(looksLikeVpnKey("https://example.com"))
    }
}
