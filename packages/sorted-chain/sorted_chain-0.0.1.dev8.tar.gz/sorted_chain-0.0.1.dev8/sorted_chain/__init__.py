"""
itertools.chain with sorted result

This module provides a single function, `sorted_chain`, which takes any
number of iterables and returns a single iterable that yields the elements
from the input iterables in sorted order.

The function is designed to be used with other functions from the
`itertools` module, such as `groupby` or `sorted`.
"""

from .sorted_chain import IterableIsNotSorted, sorted_chain
from .version import __version__, __version_tuple__, version, version_tuple

__all__ = [
    "sorted_chain",
    "__version__",
    "version",
    "__version_tuple__",
    "version_tuple",
    "IterableIsNotSorted",
]
