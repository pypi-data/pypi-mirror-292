#
# Copyright 2018-2024 Fragment Contributors
# SPDX-License-Identifier: Apache-2.0
#
import unittest
from typing import Tuple

from conformer_core.accessors import (
    Accessor,
    FilterCompositeAccessor,
    ModCompositeAccessor,
)


class AddString(Accessor[str, str]):
    def __init__(self, to_append: str) -> None:
        super().__init__()
        self.to_append = to_append

    def churn(self) -> None:
        while not self.in_queue.empty():
            (s,) = self.in_queue.get()
            self.out_queue.put(
                (
                    (s + self.to_append,)  # Repackage keyword args
                )
            )
            self.in_queue.task_done()


class IsFactor(Accessor[int, Tuple[int, bool]]):
    def __init__(self, val: int) -> None:
        super().__init__()
        self.val = val

    def churn(self) -> None:
        while not self.in_queue.empty():
            ar = self.in_queue.get()
            self.out_queue.put((ar, ar[0] % self.val == 0))
            self.in_queue.task_done()


class AccessorTestCases(unittest.TestCase):
    def test_mods(self):
        B = AddString("B")
        C = AddString("C")
        accessor = ModCompositeAccessor([B, C])

        self.assertEqual(accessor("A")[0], "ABC")
        self.assertEqual(B.num_completed, 1)
        self.assertEqual(C.num_completed, 1)

    def test_filters(self):
        two = IsFactor(2)
        three = IsFactor(3)
        accessor = FilterCompositeAccessor([two, three])

        self.assertEqual(((2,), False), accessor(2))
        self.assertEqual(two.num_completed, 1)
        self.assertEqual(three.num_completed, 1)

        self.assertEqual(((3,), False), accessor(3))
        self.assertEqual(two.num_completed, 2)
        self.assertEqual(three.num_completed, 1)

        self.assertEqual(((6,), True), accessor(6))
        self.assertEqual(two.num_completed, 3)
        self.assertEqual(three.num_completed, 2)
