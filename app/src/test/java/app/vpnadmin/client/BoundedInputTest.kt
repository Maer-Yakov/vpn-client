package app.vpnadmin.client

import java.io.ByteArrayInputStream
import org.junit.Assert.assertArrayEquals
import org.junit.Test

class BoundedInputTest {
    @Test
    fun readsAtMostLimitPlusOneBytes() {
        val input = ByteArrayInputStream(byteArrayOf(1, 2, 3, 4, 5))

        assertArrayEquals(byteArrayOf(1, 2, 3), input.readAtMost(2))
    }

    @Test
    fun readsSmallStreamCompletely() {
        val expected = byteArrayOf(1, 2, 3)

        assertArrayEquals(expected, ByteArrayInputStream(expected).readAtMost(3))
    }
}