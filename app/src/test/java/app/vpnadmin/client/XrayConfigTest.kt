package app.vpnadmin.client

import org.json.JSONObject
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class XrayConfigTest {
    @Test
    fun buildsTunConfigFromVlessLink() {
        val json = JSONObject(
            XrayConfig.build(
                "vless://11111111-2222-3333-4444-555555555555@85.137.164.156:443" +
                    "?encryption=none&flow=xtls-rprx-vision&security=reality" +
                    "&sni=www.microsoft.com&fp=chrome&pbk=PUBLIC_KEY&sid=abcd" +
                    "&type=tcp&spx=%2F#QR",
                setOf("example.com"),
            ),
        )
        val inbound = json.getJSONArray("inbounds").getJSONObject(0)
        assertEquals("socks", inbound.getString("protocol"))
        assertEquals("127.0.0.1", inbound.getString("listen"))
        assertEquals(XrayConfig.SOCKS_PORT, inbound.getInt("port"))
        val outbound = json.getJSONArray("outbounds").getJSONObject(0)
        assertEquals("vless", outbound.getString("protocol"))
        val settings = outbound.getJSONObject("settings")
        assertEquals("11111111-2222-3333-4444-555555555555", settings.getString("id"))
        assertEquals("xtls-rprx-vision", settings.getString("flow"))
        assertEquals("85.137.164.156", settings.getString("address"))
        assertEquals(443, settings.getInt("port"))
        val stream = outbound.getJSONObject("streamSettings")
        assertEquals("raw", stream.getString("network"))
        val reality = stream.getJSONObject("realitySettings")
        assertEquals("PUBLIC_KEY", reality.getString("publicKey"))
        assertEquals("PUBLIC_KEY", reality.getString("password"))
        assertEquals("www.microsoft.com", reality.getString("serverName"))
        assertEquals("abcd", reality.getString("shortId"))
        assertEquals("/", reality.getString("spiderX"))
        val rules = json.getJSONObject("routing").getJSONArray("rules")
        val dnsRule = (0 until rules.length()).map { rules.getJSONObject(it) }
            .first { it.optString("port") == "53" }
        assertEquals("dns-out", dnsRule.getString("outboundTag"))
        assertEquals("https://1.1.1.1/dns-query", json.getJSONObject("dns").getJSONArray("servers").getString(0))
        val domainRule = (0 until rules.length()).map { rules.getJSONObject(it) }
            .first { it.optJSONArray("domain") != null }
        assertEquals("direct", domainRule.getString("outboundTag"))
        assertEquals("domain:example.com", domainRule.getJSONArray("domain").getString(0))
        assertTrue(XrayConfig.tunnelConfig("/data/hev.log").contains("port: ${XrayConfig.SOCKS_PORT}"))
    }

    @Test
    fun buildsTunConfigFromPanelJson() {
        val stored = """
            {"outbounds":[{"protocol":"vless","settings":{"vnext":[{"address":"vpn.example.com","port":443,"users":[{"id":"aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee","encryption":"none","flow":"xtls-rprx-vision"}]}]},"streamSettings":{"network":"tcp","security":"reality","realitySettings":{"serverName":"www.microsoft.com","fingerprint":"chrome","publicKey":"SERVER_KEY","shortId":"aa","spiderX":"/"}}}]}
        """.trim()
        val json = JSONObject(XrayConfig.build(stored))
        val settings = json.getJSONArray("outbounds").getJSONObject(0).getJSONObject("settings")
        assertEquals("vpn.example.com", settings.getString("address"))
        assertEquals(443, settings.getInt("port"))
        assertEquals("aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee", settings.getString("id"))
        assertEquals("socks", json.getJSONArray("inbounds").getJSONObject(0).getString("protocol"))
        assertEquals("dns", json.getJSONArray("outbounds").getJSONObject(1).getString("protocol"))
        assertTrue(json.getJSONObject("routing").getJSONArray("rules").length() >= 3)
    }

    @Test
    fun buildsTunConfigFromFlattenedPanelJson() {
        val stored = """
            {"outbounds":[{"protocol":"vless","settings":{"address":"85.137.164.156","port":443,"id":"aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee","encryption":"none","flow":"xtls-rprx-vision"},"streamSettings":{"network":"raw","security":"reality","realitySettings":{"serverName":"www.googletagmanager.com","fingerprint":"chrome","password":"SERVER_KEY","shortId":"aa","spiderX":"/"}}}]}
        """.trim()
        val json = JSONObject(XrayConfig.build(stored))
        val settings = json.getJSONArray("outbounds").getJSONObject(0).getJSONObject("settings")
        assertEquals("85.137.164.156", settings.getString("address"))
        assertEquals("aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee", settings.getString("id"))
        val reality = json.getJSONArray("outbounds").getJSONObject(0)
            .getJSONObject("streamSettings")
            .getJSONObject("realitySettings")
        assertEquals("SERVER_KEY", reality.getString("publicKey"))
        assertEquals("SERVER_KEY", reality.getString("password"))
    }

    @Test
    fun rejectsRealityWithoutPublicKey() {
        val error = runCatching {
            XrayConfig.build("vless://11111111-2222-3333-4444-555555555555@10.0.0.1:443?security=reality&sni=www.microsoft.com")
        }.exceptionOrNull()
        assertTrue(error is IllegalArgumentException)
    }
}
