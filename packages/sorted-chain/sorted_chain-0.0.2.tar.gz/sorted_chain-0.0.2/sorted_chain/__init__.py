# sorted_chain
# Copyright (C) 2024 Nicco Kunzmann
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
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
