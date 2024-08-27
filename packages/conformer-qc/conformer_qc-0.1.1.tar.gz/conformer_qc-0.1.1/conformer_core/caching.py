#
# Copyright 2018-2024 Fragment Contributors
# SPDX-License-Identifier: Apache-2.0
#
from dataclasses import field
from functools import cached_property as _cached_property
from inspect import getmembers
from typing import Any, Tuple


class cached_property(_cached_property):
    def __delete__(self, instance: Any) -> None:
        try:
            del instance.__dict__[self.attrname]
        except AttributeError:
            msg = (
                f"No '__dict__' attribute on {type(instance).__name__!r} "
                f"instance to cache {self.attrname!r} property."
            )
            raise TypeError(msg) from None
        except KeyError:
            pass


class Cachable:
    _CACHE_VARS: Tuple[str, ...] = field(default=tuple(), init=False)

    def _reset_cache(self):
        """
        Removes all cached values so they can be recalculated

        TODO: add a `keep` variable
        """
        for k in self._CACHE_VARS:
            delattr(self, k)

    def __init_subclass__(cls) -> None:
        cache_vars = []
        for name, val in getmembers(cls, lambda k: isinstance(k, cached_property)):
            cache_vars.append(name)

        cls._CACHE_VARS = tuple(cache_vars)
