#
# Copyright 2018-2024 Fragment Contributors
# SPDX-License-Identifier: Apache-2.0
#
from itertools import islice
from queue import Queue
from typing import (
    Any,
    Generator,
    Generic,
    Iterator,
    List,
    Tuple,
    TypeVar,
)

try:
    from itertools import batched
except ImportError:

    def batched(iterable, n):
        "Batch data into tuples of length n. The last batch may be shorter."
        "NOTE: This was added to itertools in in Python 3.12"
        if n < 1:
            raise ValueError("n must be at least one")
        it = iter(iterable)
        while batch := tuple(islice(it, n)):
            yield batch


InType = TypeVar("InType")
OutType = TypeVar("OutType")


class Accessor(Generic[InType, OutType]):
    num_submitted: int
    num_completed: int

    in_queue: Queue[InType]
    out_queue: Queue[OutType]

    def __init__(self) -> None:
        self.num_submitted = 0
        self.num_completed = 0
        self.in_queue = Queue()
        self.out_queue = Queue()

    def __call__(self, *args: Any) -> Any:
        if self.num_active != 0:
            raise Exception(
                "Cannot use accessor in synchonous mode with pending async jobs."
            )
        self.submit(*args)
        return list(self.as_completed())[0]  # Is there a better way?

    @property
    def num_active(self) -> int:
        return self.num_submitted - self.num_completed

    def submit(self, *args: Any) -> None:
        """Add's work to be handled asynchronously"""
        self.num_submitted += 1
        self.in_queue.put(args)

    def churn(self) -> None:
        ...

    def get_completed(self) -> List[OutType]:
        """Returns completed work"""
        self.churn()
        completed = []
        while not self.out_queue.empty():
            res = self.out_queue.get()
            completed.append(res)
            self.out_queue.task_done()

        self.num_completed += len(completed)
        return completed

    def as_completed(self) -> Generator[OutType, None, None]:
        """Allows work to to be returned as it becomes available"""
        while self.num_active != 0:
            for work in self.get_completed():
                yield work


class CompositeAccessor(Accessor, Generic[InType, OutType]):
    layers: List[Accessor]

    def __init__(self, layers: List[Accessor]) -> None:
        super().__init__()
        self.layers = layers

    def __getitem__(self, key):
        return self.layers[key]

    def __len__(self):
        return len(self.layers)

    def __contains__(self, value: object) -> bool:
        return self.layers.__contains__(value)

    def __iter__(self) -> Iterator:
        return self.layers.__iter__()


class ModCompositeAccessor(CompositeAccessor, Generic[InType]):
    layers: List[Accessor[InType, InType]]

    def churn(self) -> None:
        new_work = []
        while not self.in_queue.empty():
            s = self.in_queue.get()
            new_work.append(s)
            self.in_queue.task_done()

        # Go through layers and propogate
        for layer in self.layers:
            # Add system to the layer
            for ar in new_work:
                layer.submit(*ar)

            # Pass work to next layer
            new_work.clear()
            for s in layer.get_completed():
                new_work.append(s)

        for res in new_work:
            self.out_queue.put(res)


class FilterCompositeAccessor(CompositeAccessor):
    layers: List[Accessor[InType, Tuple[InType, bool]]]

    def churn(self) -> None:
        new_work = []
        while not self.in_queue.empty():
            s = self.in_queue.get()
            new_work.append(s)
            self.in_queue.task_done()

        # Go through layers and propogate
        for layer in self.layers:
            # Add system to the layer
            for ar in new_work:
                layer.submit(*ar)

            new_work.clear()
            for res in layer.get_completed():
                # If status is False, we short-circuit
                if res[1]:
                    new_work.append(res[0])
                else:
                    self.out_queue.put(res)

        for inputs in new_work:
            self.out_queue.put((inputs, True))
