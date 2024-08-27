"""
itertools.chain with sorted result

This module provides a single function, `sorted_chain`, which takes any
number of iterables and returns a single iterable that yields the elements
from the input iterables in sorted order.

The function is designed to be used with other functions from the
`itertools` module, such as `groupby` or `sorted`.
"""

from __future__ import annotations

import heapq
from functools import total_ordering
from typing import TYPE_CHECKING, Any, Callable

if TYPE_CHECKING:
    from collections.abc import Iterable


class IterableIsNotSorted(ValueError):
    """
    Raised if the elements from the input iterables are not in sorted order.

    The exception is raised when `sorted_chain` detects that the elements
    from the input iterables are not in sorted order. This can happen if the
    input iterables are not sorted, or if the input iterables are not sorted
    in the same order as the `key` function suggests.
    """


@total_ordering
class _HeapEntry:
    """
    A class representing an item in the heap. The heap is sorted by the
    `key` attribute, and then by the `index` attribute.
    """

    __slots__ = ("value", "index", "iterable", "key", "reverse")

    def __init__(
        self,
        value: Any,
        index: int,
        iterable: Iterable[Any],
        key: Any,
        reverse: bool,  # noqa: FBT001
    ):
        """
        Initialize a `HeapEntry` object.

        :param value: The value to be stored in the heap entry.
        :param index: The index of the iterable that the value comes from.
        :param iterable: The iterable that the value comes from.
        :param key: The value to be used for sorting.
        """
        self.value = value
        self.index = index
        self.iterable = iterable
        self.key = key
        self.reverse = reverse

    def __lt__(self, other: _HeapEntry) -> bool:
        """
        Compare two heap entries.

        The comparison is first done by the `value` attribute, and then by
        the `index` attribute.
        """
        if self.key < other.key:
            return not self.reverse
        if self.key > other.key:
            return self.reverse
        return self.index < other.index

    def __eq__(self, other: _HeapEntry) -> bool:
        """
        Check if two heap entries are equal.

        The comparison is done by the `key` and `index` attributes.
        """
        return self.key == other.key and self.index == other.index

    def __hash__(self) -> int:
        """
        Return a hash of the heap entry.

        The hash is computed from the `key` and `index` attributes.
        """
        return hash((self.key, self.index))


def sorted_chain(
    *iterables: Iterable[Any],
    key: Callable[[Any], Any] | None = None,
    reverse: bool = False,  # noqa: ARG001, RUF100
) -> Iterable[Any]:
    """Yield the elements from the endless iterables in sorted order.

    :param iterables: The iterables to be sorted.
    :param key: A function of one argument that is used to extract a
        comparison key from each element in the iterable. The default
        value is None, which means that the elements themselves will be
        used as the comparison key.
    :param reverse: A boolean value indicating whether the elements should
        be sorted in reverse order. The default value is False which implies
        that the lowest value is returned first.
    :return: An iterable of the elements from the input iterables in sorted
        order.

    :raises TypeError: If the input iterables do not contain comparable
        elements.
    :raises ValueError: If the input iterables are not in sorted order.
    """
    key = key or (lambda x: x)
    heap: list[_HeapEntry] = []
    for i, it in enumerate(map(iter, iterables)):
        for first_element in it:
            heapq.heappush(
                heap, _HeapEntry(first_element, i, it, key(first_element), reverse)
            )
            break

    while heap:
        element = heapq.heappop(heap)
        yield element.value
        for next_element in element.iterable:
            next_heap_element = _HeapEntry(
                next_element,
                element.index,
                element.iterable,
                key(next_element),
                reverse,
            )
            if next_heap_element < element:
                raise IterableIsNotSorted(
                    f"The values of iterable {element.index} are not in "
                    "sorted order."
                )
            heapq.heappush(
                heap,
                next_heap_element,
            )
            break


__all__ = ["sorted_chain", "IterableIsNotSorted"]
