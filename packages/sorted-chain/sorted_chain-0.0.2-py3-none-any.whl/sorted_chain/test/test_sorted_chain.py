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
"""Test cases for the `sorted_chain` module."""

import pytest

from sorted_chain import IterableIsNotSorted, sorted_chain


def test_sorted_chain_integers():
    """Test that sorted_chain works for integers."""
    iterable1 = [1, 3, 5]
    iterable2 = [2, 4, 6]
    assert list(sorted_chain(iterable1, iterable2)) == [1, 2, 3, 4, 5, 6]


def test_sorted_chain_with_key():
    """Test that sorted_chain works with a key function."""
    iterable1 = ["hello333", "world4444"]
    iterable2 = ["foo1", "bar22"]
    assert list(sorted_chain(iterable1, iterable2, key=len)) == [
        "foo1",
        "bar22",
        "hello333",
        "world4444",
    ]


def test_sorted_chain_reverse():
    """Test that sorted_chain works with reverse."""
    iterable1 = reversed([1, 3, 5])
    iterable2 = reversed([2, 4, 6])
    assert list(sorted_chain(iterable1, iterable2, reverse=True)) == [6, 5, 4, 3, 2, 1]


def test_sorted_chain_five_iterators():
    """Test that sorted_chain works with 5 iterators."""
    iterable1 = [1, 3, 5]
    iterable2 = [2, 4, 6]
    iterable3 = [0, 7, 10]
    iterable4 = [8, 9]
    iterable5 = [11]
    assert list(
        sorted_chain(iterable1, iterable2, iterable3, iterable4, iterable5)
    ) == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]


def endless_ints(start=0):
    """A generator that yields endless integers starting from `start`."""
    n = start
    while True:
        yield n
        n += 1


def test_sorted_chain_with_endless_iterators():
    """Test that sorted_chain works with endless iterators."""
    iterable1 = endless_ints(1)
    iterable2 = endless_ints(2)
    iterable3 = endless_ints(3)
    iterable4 = endless_ints(4)
    iterable5 = endless_ints(5)
    it_result = sorted_chain(iterable1, iterable2, iterable3, iterable4, iterable5)
    expected_result = [1, 2, 2, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5, 5]
    for result, expected in zip(it_result, expected_result):
        assert result == expected


class A:
    """A class with a single value a."""

    def __init__(self, a):
        """Initialize an instance of A with value `a`."""
        self.a = a

    def __eq__(self, other):
        """Return True if two A objects are equal."""
        if not isinstance(other, A):
            return NotImplemented
        return self.a == other.a


def test_sorted_chain_with_objects():
    """Test that sorted_chain works with objects from class A."""
    iterable1 = [A(1), A(3), A(5)]
    iterable2 = [A(2), A(4), A(6)]
    iterable3 = [A(0), A(7), A(10)]
    iterable4 = [A(8), A(9)]
    iterable5 = [A(11)]
    assert list(
        sorted_chain(
            iterable1, iterable2, iterable3, iterable4, iterable5, key=lambda x: x.a
        )
    ) == [A(0), A(1), A(2), A(3), A(4), A(5), A(6), A(7), A(8), A(9), A(10), A(11)]


def test_sorted_chain_with_objects_uncomparable():
    """TypeError when input elements are not comparable."""
    iterable1 = [A(1), A(3), A(5)]
    iterable2 = [A(2), A(4), A(6)]
    with pytest.raises(TypeError):
        list(sorted_chain(iterable1, iterable2))


def test_sorted_chain_with_objects_wrong_order():
    """ValueError when input elements are not in order."""
    iterable1 = [3, 1, 5]
    iterable2 = [2, 4, 6]
    with pytest.raises(IterableIsNotSorted):
        list(sorted_chain(iterable1, iterable2))
    with pytest.raises(IterableIsNotSorted):
        list(sorted_chain(iterable1, iterable2, reverse=True))
