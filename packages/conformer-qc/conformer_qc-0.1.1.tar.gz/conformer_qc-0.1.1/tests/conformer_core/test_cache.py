#
# Copyright 2018-2024 Fragment Contributors
# SPDX-License-Identifier: Apache-2.0
#
from unittest import TestCase

from conformer_core.caching import Cachable, cached_property


class CacheTest(Cachable):
    _call_counter: int

    def __init__(self) -> None:
        self._call_counter = 0

    @cached_property
    def call_counter(self):
        self._call_counter += 1
        return self._call_counter


class CacheTestCases(TestCase):
    def test_cache(self):
        self.assertTupleEqual(CacheTest._CACHE_VARS, ("call_counter",))

        ct = CacheTest()

        self.assertEqual(ct.call_counter, 1)
        self.assertEqual(ct.call_counter, 1)

        del ct.call_counter

        self.assertEqual(ct.call_counter, 2)
        self.assertEqual(ct.call_counter, 2)

        ct._reset_cache()
        self.assertEqual(ct.call_counter, 3)
