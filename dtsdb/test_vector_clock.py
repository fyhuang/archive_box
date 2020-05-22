import unittest

from .vector_clock import *

class VectorClockTests(unittest.TestCase):
    def test_compare_equal(self) -> None:
        c1 = VectorClock()
        c2 = VectorClock()
        self.assertEqual("equal", c1.compare(c2))
        self.assertEqual("equal", c2.compare(c1))

        c1.increment(1)
        c2.increment(1)
        self.assertEqual("equal", c1.compare(c2))

        c1.increment(1)
        self.assertNotEqual("equal", c1.compare(c2))

    def test_compare_before_after(self) -> None:
        c1 = VectorClock({1: 1})
        c2 = VectorClock()

        self.assertEqual("before", c2.compare(c1))
        self.assertEqual("after", c1.compare(c2))

    def test_compare_concurrent(self) -> None:
        c1 = VectorClock({1: 1})
        c2 = VectorClock({3: 1})

        self.assertEqual("concurrent", c1.compare(c2))
        self.assertEqual("concurrent", c2.compare(c1))

    def test_packed(self) -> None:
        c1 = VectorClock()
        c1.increment(5)
        c1.increment(8)

        packed = c1.to_packed()
        c2 = VectorClock.from_packed(packed)
        self.assertEqual("equal", c1.compare(c2))

    def test_merge_from(self) -> None:
        c1 = VectorClock({1: 1, 2: 3})
        c2 = VectorClock({1: 3, 2: 2})

        c1.merge_from(c2)
        self.assertEqual(VectorClock({1: 3, 2: 3}), c1)
