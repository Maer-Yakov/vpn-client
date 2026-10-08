/*
 * Copyright © 2017-2023 WireGuard LLC. All Rights Reserved.
 * SPDX-License-Identifier: Apache-2.0
 */

package org.amnezia.awg.config;

import java.net.InetAddress;
import java.net.UnknownHostException;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Collections;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Set;

/** Builds a bounded route set with IP prefixes removed for Android versions without excludeRoute. */
public final class RouteExclusions {
    public static final int MAX_LEGACY_ROUTES = 180;

    private RouteExclusions() { }

    public static List<InetNetwork> subtract(
            final Collection<InetNetwork> routes,
            final Collection<InetNetwork> exclusions) {
        final Set<InetNetwork> result = new LinkedHashSet<>();
        for (final InetNetwork route : routes) {
            List<InetNetwork> remaining = Collections.singletonList(route);
            for (final InetNetwork exclusion : exclusions) {
                final List<InetNetwork> next = new ArrayList<>();
                for (final InetNetwork candidate : remaining)
                    next.addAll(subtractOne(candidate, exclusion));
                remaining = next;
                if (result.size() + remaining.size() > MAX_LEGACY_ROUTES)
                    throw new IllegalArgumentException("Слишком много IP-маршрутов для обхода сайтов на этой версии Android");
            }
            result.addAll(remaining);
            if (result.size() > MAX_LEGACY_ROUTES)
                throw new IllegalArgumentException("Слишком много IP-маршрутов для обхода сайтов на этой версии Android");
        }
        return new ArrayList<>(result);
    }

    private static List<InetNetwork> subtractOne(final InetNetwork route, final InetNetwork exclusion) {
        final byte[] routeBytes = route.getAddress().getAddress();
        final byte[] excludedBytes = exclusion.getAddress().getAddress();
        if (routeBytes.length != excludedBytes.length || !contains(routeBytes, route.getMask(), excludedBytes))
            return Collections.singletonList(route);

        if (exclusion.getMask() <= route.getMask())
            return Collections.emptyList();

        final int excludedPrefix = Math.min(exclusion.getMask(), excludedBytes.length * 8);
        final List<InetNetwork> siblings = new ArrayList<>();
        for (int bit = route.getMask(); bit < excludedPrefix; bit++) {
            final byte[] sibling = excludedBytes.clone();
            setBit(sibling, bit, !getBit(excludedBytes, bit));
            for (int trailing = bit + 1; trailing < sibling.length * 8; trailing++)
                setBit(sibling, trailing, false);
            try {
                final InetAddress address = InetAddress.getByAddress(sibling);
                siblings.add(InetNetwork.parse(address.getHostAddress() + "/" + (bit + 1)));
            } catch (final UnknownHostException | ParseException e) {
                throw new IllegalArgumentException("Не удалось построить IP-маршрут", e);
            }
        }
        return siblings;
    }

    private static boolean contains(final byte[] network, final int prefix, final byte[] address) {
        if (network.length != address.length)
            return false;
        final int fullBytes = prefix / 8;
        for (int index = 0; index < fullBytes; index++)
            if (network[index] != address[index])
                return false;
        final int remainingBits = prefix % 8;
        if (remainingBits == 0)
            return true;
        final int mask = 0xff << (8 - remainingBits);
        return (network[fullBytes] & mask) == (address[fullBytes] & mask);
    }

    private static boolean getBit(final byte[] address, final int bit) {
        return (address[bit / 8] & (1 << (7 - bit % 8))) != 0;
    }

    private static void setBit(final byte[] address, final int bit, final boolean enabled) {
        final int index = bit / 8;
        final int mask = 1 << (7 - bit % 8);
        if (enabled)
            address[index] = (byte) (address[index] | mask);
        else
            address[index] = (byte) (address[index] & ~mask);
    }
}