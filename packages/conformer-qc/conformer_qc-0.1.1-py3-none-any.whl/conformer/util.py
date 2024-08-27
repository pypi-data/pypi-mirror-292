#
# Copyright 2018-2024 Fragment Contributors
# SPDX-License-Identifier: Apache-2.0
#
from functools import partial, wraps
from typing import Any, Callable, TypeVar

from lru import LRU

from conformer.systems import System

T = TypeVar("T")
V = TypeVar("V")


def supersystem_cache(
    fn_max_size: Callable[[T], V] = None, max_size=100
) -> Callable[[T], V]:
    # Called without a valid function. :o
    if isinstance(fn_max_size, int) or fn_max_size is None:
        return partial(supersystem_cache, max_size=max_size)

    return wraps(fn_max_size)(
        SuperSystemCacheWrapper(fn_max_size, max_size=max_size),
    )


def derive_noop(supersystem: System, v: Any, sys: System) -> Any:
    """Do nothing to transform these values"""
    return v


class SuperSystemCacheWrapper:
    fn: Callable
    _derive_fn: Callable | None
    cache: LRU

    def __init__(self, fn: Callable, max_size: int) -> None:
        self.fn = fn
        self.cache = LRU(max_size)
        self._derive_fn = derive_noop

    def __contains__(self, k: Any) -> bool:
        return id(k) in self.cache

    def get(self, sys: System) -> None:
        return self.cache[id(sys)]

    def update(self, sys: System, return_val: Any) -> None:
        self.cache[id(sys)] = return_val

    def __call__(self, sys: System, *args: Any, **kwds: Any) -> Any:
        # Act as a simple cache
        if sys in self:
            return self.get(sys)

        # Check if supersystem exists
        ss = sys.supersystem
        if ss is None or not ss.is_canonized:
            # Add to the simple cache
            sys_value = self.fn(sys, *args, **kwds)
            self.update(sys, sys_value)
            return sys_value

        if ss in self:
            ss_value = self.get(ss)
        else:
            ss_value = self.fn(ss, *args, **kwds)
            # TODO: Take arguments into account?
            self.update(ss, ss_value)

        return self._derive_fn(ss, ss_value, sys, *args, **kwds)

    def no_cache(self, sys: System, *args, **kwargs) -> Any:
        return self.fn(sys, *args, **kwargs)

    def derive(self, fn: Callable) -> Callable:
        self._derive_fn = fn
        return fn
