package app.vpnadmin.client

import org.amnezia.awg.config.InetNetwork
import java.net.InetAddress
import java.net.UnknownHostException

object SiteRouteResolver {
    const val MAX_SITES = 64
    const val MAX_RESOLVED_ADDRESSES = 128

    fun resolve(
        domains: Set<String>,
        lookup: (String) -> Array<InetAddress> = InetAddress::getAllByName,
    ): Set<InetNetwork> {
        require(domains.size <= MAX_SITES) { "Можно добавить не более $MAX_SITES сайтов" }
        val routes = linkedSetOf<InetNetwork>()
        domains.forEach { value ->
            val domain = SiteDomain.normalize(value)
            val addresses = try {
                lookup(domain)
            } catch (_: UnknownHostException) {
                throw IllegalArgumentException("Не удалось определить IP сайта $domain")
            } catch (_: SecurityException) {
                throw IllegalArgumentException("Не удалось определить IP сайта $domain")
            }
            require(addresses.isNotEmpty()) { "Не удалось определить IP сайта $domain" }
            addresses.forEach { address ->
                val numericAddress = InetAddress.getByAddress(address.address)
                val prefix = numericAddress.address.size * 8
                routes += InetNetwork.parse("${numericAddress.hostAddress}/$prefix")
                require(routes.size <= MAX_RESOLVED_ADDRESSES) {
                    "Список сайтов разрешается в слишком много IP-адресов"
                }
            }
        }
        return routes
    }
}