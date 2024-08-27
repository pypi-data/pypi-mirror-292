#
# Copyright 2018-2024 Fragment Contributors
# SPDX-License-Identifier: Apache-2.0
#
import inspect
import re
from functools import wraps
from io import TextIOBase, TextIOWrapper
from itertools import compress
from typing import (
    Any,
    AnyStr,
    Callable,
    ClassVar,
    Iterable,
    List,
    Optional,
    Set,
    Tuple,
    Type,
)

from conformer_core.properties.core import MASTER_PROP_LIST, PropertySet


class DataSource:
    """
    DataSource classes control property extraction.

    Each data source has multiple extractors. This allows multiple functions to
    extract from the same data stream. i.e. This allow Fragment to only open
    a output file once for parsing.
    """

    # Tupe of data supported
    TYPES: ClassVar[Tuple[Type, ...]] = tuple()

    extractors: List["Extractor"]

    def __init__(self, extractors: Iterable["Extractor"]) -> None:
        self.extractors = [e for e in extractors if e.DATA_SOURCE == self.__class__]

    def extract(self, ctx: Any, all_sources: Iterable[Any], props: PropertySet):
        # Run the extraction process on a set of data sources
        sources = self.select_sources(all_sources)
        self.enable_extractors()

        # Do the extraction giving each extractor access to the source
        for s in sources:
            for e in self.extractors:
                self.call_extractor(props, ctx, e, s)

    def enable_extractors(self):
        """Cleanup method for data extraction"""
        for e in self.extractors:
            e.enabled = True

    def select_sources(self, sources: Iterable[Any]) -> List[Any]:
        """Filter out data sources that are not in TYPES"""
        return [s for s in sources if isinstance(s, self.TYPES)]

    def call_extractor(
        self, props: PropertySet, ctx: Any, extractor: "Extractor", *args, **kwargs
    ):
        """
        Calls an extractor and passes through arguments.

        Updates props with the return value and disables the extractor. If the
        return value is None, the property is not disable and continues
        being called
        """
        if not extractor.enabled:
            return

        val = extractor(ctx, *args, **kwargs)
        if val is None:
            return

        props[extractor.property_name] = val


class ContextDataSource(DataSource):
    """Run an data extractor only on the datacontext"""

    def extract(self, ctx: Any, _: Iterable[Any], props: PropertySet):
        self.enable_extractors()
        for e in self.extractors:
            self.call_extractor(props, ctx, e)


class StringDataSource(DataSource):
    """For data extraction on strings"""

    TYPES = (AnyStr,)


class StreamDataSource(DataSource):
    """For data extractor on IOStreams.

    Each extractor is given a fresh copy of the IOStream.
    This does not work for network trafic because those cannot be rewound
    """

    def extract(self, ctx: Any, all_sources: Iterable[Any], props: PropertySet):
        sources: List[TextIOWrapper] = self.select_sources(all_sources)
        self.enable_extractors()

        # Do the extraction giving each extractor access to the source
        for s in sources:
            for e in self.extractors:
                s.seek(0)  # May break if past non-rewindable IO
                self.call_extractor(props, ctx, e, s)


class SharedStreamDataSource(StreamDataSource):
    """Allows single-pass extraction on IOStreams

    Each extractor is fed a line and an IOStream. Extractors are given the
    opportunity to bind to the IOStream and return a value. If an extractor
    returns a value, the stream keeps its new position. If the IOStream
    returns None, the stream is rewound to it's previous location and passed
    to the next extractor.

    # This does not
    """

    TYPES = (TextIOBase,)

    def extract(self, ctx: Any, all_sources: Iterable[Any], props: PropertySet):
        sources: TextIOWrapper = self.select_sources(all_sources)
        self.enable_extractors()

        # Do the extraction giving each extractor access to the source
        for s in sources:
            self.extract_stream(ctx, s, props)

    def extract_stream(self, ctx: Any, io_handle: TextIOBase, props: PropertySet):
        """Gets file-base properties"""

        extractors = [e for e in self.extractors if e.enabled]

        while True:  # We have to manually iterate through the file
            # Stop reading the file once we have no more extractors
            # file handlers
            if not extractors:
                break

            line = io_handle.readline()
            start_pos = io_handle.tell()

            # END OF FILE
            if len(line) == 0:
                break

            keep = [True for _ in extractors]
            for i, ext in enumerate(extractors):
                val = self.call_extractor(props, ctx, ext, line, io_handle)

                # Reqind to the next
                io_handle.seek(start_pos)

                # Save for another iteration
                if val is None:
                    continue
                keep[i] = False

            extractors = list(compress(extractors, keep))


class Extractor:
    DATA_SOURCE: ClassVar[DataSource] = ContextDataSource

    property_name: str
    fn: Callable

    def __init__(self, prop_name=None) -> None:
        self.property_name = prop_name
        self.enabled = True
        self.fn = None

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        if not self.enabled:
            return

        ret = self.fn(*args, **kwargs)

        if ret is None:
            return

        self.enabled = False  # Disable and stop searching
        return ret

    def bind(self, fn: Callable) -> "Extractor":
        if self.property_name is None:
            if fn.__name__.startswith("prop_"):
                self.property_name = fn.__name__[5:]
            else:
                self.property_name = fn.__name__
        self.fn = fn
        return wraps(fn)(self)


class ExclusiveStreamExtractor(Extractor):
    DATA_SOURCE = StreamDataSource


class StreamExtractor(Extractor):
    DATA_SOURCE = SharedStreamDataSource


class StringExtractor(Extractor):
    DATA_SOURCE = StringDataSource


class REExtractor(StreamExtractor):
    def __init__(self, patterns: List[str] = None, prop_name=None) -> None:
        super().__init__(prop_name=prop_name)
        patterns = patterns or []
        self.patterns = [re.compile(p) for p in patterns]

    def __call__(self, ctx: Any, line: str, io_handle: TextIOBase) -> Any:
        if not self.enabled:
            return

        m = None
        for pattern in self.patterns:
            m = pattern.search(line)
            if m is not None:
                break

        # No matches? No fn call
        if m is None:
            return

        return super().__call__(ctx, m, io_handle)


EXTRACTOR_MAPPING = {
    "ctx": Extractor,
    "context": Extractor,
    "default": Extractor,
    "file": StreamExtractor,
    "stream": StreamExtractor,
    "re_file": REExtractor,
    "regex": REExtractor,  # Aliase for re_file
    "file_exclusive": ExclusiveStreamExtractor,
}


class calc_property:
    """
    Convenience decorator for binding to class methods
    """

    extractor_bundle: Tuple[Extractor, Any, Any]

    def __init__(self, extractor=None, source=None, *args, **kwargs) -> None:
        if extractor is None:
            if source:
                extractor = EXTRACTOR_MAPPING[source]
            else:
                extractor = Extractor  # Default. Only gets context

        self.extractor_bundle = (
            extractor,
            args,
            kwargs,
        )

    def __call__(self, fn: Callable) -> Any:
        # Annotate the method for reconstruction at init
        setattr(fn, "__extractor", self.extractor_bundle)
        return fn


class PropertyExtractorMixin:
    _supported_properties: Set[str]
    _data_providers: Set[DataSource]
    _property_extractors: List[Extractor]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        # TODO: I feel like this could be done in the __init_sublcass__ method
        extractor_fns = [
            e
            for e in inspect.getmembers(
                self,
                predicate=(
                    lambda x: inspect.isroutine(x) and hasattr(x, "__extractor")
                ),
            )
        ]

        for name, fn in extractor_fns:
            CLS, args, kwargs = getattr(fn, "__extractor")
            setattr(self, name, CLS(*args, **kwargs).bind(fn))
        self._collect_property_extractors()

    def available_properties(self) -> set:
        if not hasattr(self, "_supported_properties"):
            self._collect_property_extractors()
        return self._supported_properties

    def get_properties(
        self, ctx: Any, sources: Iterable[Any], properties: Optional[PropertySet] = None
    ) -> PropertySet:
        if properties is None:
            properties = PropertySet({})

        # Load/create cache of extractors
        self.available_properties()

        # Allow each provider to have a go at all sources
        for provider in self._data_providers:
            provider.extract(ctx, sources, properties)

        return properties

    def _collect_property_extractors(self):
        """
        Inspects self and retrieves the property extraction functions
        """
        prop_extractors: List[Extractor] = []
        for _, extractor in inspect.getmembers(
            self, predicate=lambda x: isinstance(x, Extractor)
        ):
            prop_extractors.append(extractor)
        supported_properties = [n.property_name for n in prop_extractors]

        # Make sure we don't have duplicates
        if len(supported_properties) != len(set(supported_properties)):
            raise ValueError("There were duplicates in the property extractors")

        # Make sure we are sticking to the MASTER_PROP_LIST
        for n in supported_properties:
            if n not in MASTER_PROP_LIST and n not in ["warnings", "error"]:
                raise ValueError(f"{n} is not a supported property")

        _provider_set = {e.DATA_SOURCE for e in prop_extractors}
        self._data_providers = [S(prop_extractors) for S in _provider_set]
        self._property_extractors = prop_extractors
        self._supported_properties = set(supported_properties)
