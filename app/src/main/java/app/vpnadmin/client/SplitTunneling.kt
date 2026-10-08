package app.vpnadmin.client

enum class AppRouteMode {
    AllTraffic,
    SelectedThroughVpn,
    SelectedBypassVpn,
}

data class SplitTunnelSettings(
    val mode: AppRouteMode = AppRouteMode.AllTraffic,
    val packages: Set<String> = emptySet(),
    val bypassDomains: Set<String> = emptySet(),
) {
    val isEnabled: Boolean
        get() = mode != AppRouteMode.AllTraffic || bypassDomains.isNotEmpty()

    fun applyTo(configuration: String): String {
        if (mode == AppRouteMode.AllTraffic) return configuration

        val selectedPackages = packages
            .filter(::isValidPackageName)
            .sorted()
        require(selectedPackages.isNotEmpty()) { "Выберите хотя бы одно приложение" }

        var inInterface = false
        val preservedLines = configuration.lineSequence().filterNot { rawLine ->
            val line = rawLine.substringBefore('#').trim()
            if (line.startsWith("[")) {
                inInterface = line.equals("[Interface]", ignoreCase = true)
                false
            } else if (inInterface) {
                val separator = line.indexOf('=')
                if (separator <= 0) {
                    false
                } else {
                    val name = line.substring(0, separator).trim()
                    name.equals("IncludedApplications", ignoreCase = true) ||
                        name.equals("ExcludedApplications", ignoreCase = true)
                }
            } else {
                false
            }
        }.joinToString("\n").trimEnd()

        val directive = when (mode) {
            AppRouteMode.AllTraffic -> return configuration
            AppRouteMode.SelectedThroughVpn -> "IncludedApplications"
            AppRouteMode.SelectedBypassVpn -> "ExcludedApplications"
        }
        return "$preservedLines\n\n[Interface]\n$directive = ${selectedPackages.joinToString(", ")}\n"
    }

    companion object {
        private val packageNamePattern = Regex("[A-Za-z0-9_]+(\\.[A-Za-z0-9_]+)+")

        fun isValidPackageName(value: String): Boolean = packageNamePattern.matches(value)
    }
}