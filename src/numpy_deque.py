"""A numpy implementation of holodeque."""

from collections.abc import Hashable, Set, Iterable
from typing import Callable, Optional, Self, override

import numpy as np

from src.base_holodeque import BaseHolodeque, Matrix


class numpydeque[T: Hashable](BaseHolodeque[np.int64, T]):
    """A holodeque with a predefined alphabet (acceptable input).   

    Attributes:
        _matrix: A square numpy matrix representing the state of the holodeque.
        _shape: The dimension of the base matrix (its width and height).
        _size: The current number of elements in the holodeque.
        _maxlen: The maximum allowed size of the holodeque; None if unbounded.
        _alphabet: The set of unique elements that the holodeque can contain.
        _element_tuple: An tuple of acceptable input for the holodeque.
        _element_map: A hashmap that maps each containable element to an index in _element_tuple.
        _kwargs: A dictionary for additional optional parameters.
    """

    @override
    def __init__(self, iterable: Iterable[T] = (), *, alphabet: Set[T], maxlen: Optional[int] = None, **kwargs) -> None:
        """Initializes a holodeque with the provided iterable.

        Args:
            alphabet: The set of unique elements that the holodeque can contain.
            iterable: An Iterable of elements to populate the holodeque.
            maxlen: Optional maximum size of the holodeque; if not None, restricts
                    the number of elements.
            _kwargs: A dictionary for additional optional parameters.
        """
        super().__init__(maxlen=maxlen, alphabet=frozenset(alphabet), **kwargs)
        if len(alphabet) < 2:
            raise ValueError("alphabet must contain at least 2 elements")
        self._matrix: Matrix[np.int64] = self.__class__.identity(len(alphabet))
        self._shape: int = len(alphabet)
        self._alphabet: frozenset[T] = frozenset(alphabet)
        self._element_tuple: tuple[T, ...] = tuple(alphabet)
        self._element_map: dict[T, int] = {
            letter: i for i, letter in enumerate(self._element_tuple)}
        self.extendright(iterable)

    @staticmethod
    def identity(n: int) -> Matrix[np.int64]:
        """Creates an nxn identity matrix"""
        return np.eye(n, dtype=np.int64)

    @override
    def _get_axis(self, element: T) -> int:
        if element not in self._alphabet:
            raise ValueError(
                f"The holodeque does not accept the element: {element}")
        return self._element_map[element]

    @override
    def _get_element(self, axis: int) -> T:
        return self._element_tuple[axis]

    @override
    def _transform(self, axis: int, left: bool = True, reverse: bool = False) -> None:
        for i in range(self._shape):
            if i == axis:
                continue
            match (left, reverse):
                case (True, True):
                    # Subtract other rows from row of axis
                    self._matrix[axis] -= self._matrix[i]  # type: ignore
                case (True, False):
                    # Add row other rows to row of axis
                    self._matrix[axis] += self._matrix[i]  # type: ignore
                case (False, True):
                    # Subtract column of axis from other columns
                    self._matrix[:, i] -= self._matrix[:, axis]  # type: ignore
                case (False, False):
                    # Add column of axis to other columns
                    self._matrix[:, i] += self._matrix[:, axis]  # type: ignore

    @override
    def concatleft(self, other: Self) -> None:
        if not isinstance(other, type(self)):
            raise TypeError
        if self._alphabet != other._alphabet:
            raise ValueError(
                "incompatible holodeque because they have different alphabets")
        if self._maxlen is not None and self._size + other._size > self._maxlen:
            raise ValueError(
                "incompatible holodeque because it would exceed maximum length")
        if self is other:
            other = self.copy()
        convert: Callable[[int], int] = lambda x: other._get_axis(
            self._get_element(x))
        temp: Matrix[np.int64] = np.array(
            [other._matrix[convert(i)] for i in range(self._shape)])
        self._matrix = np.matmul(temp, self._matrix) # type: ignore
        self._size += other.size

    @override
    def concatright(self, other: Self) -> None:
        if not isinstance(other, type(self)):
            raise TypeError
        if self._alphabet != other._alphabet:
            raise ValueError(
                "incompatible holodeque because they have different alphabets")
        if self._maxlen is not None and self._size + other._size > self._maxlen:
            raise ValueError(
                "incompatible holodeque because it would exceed maximum length")
        if self is other:
            other = self.copy()
        convert: Callable[[int], int] = lambda x: other._get_axis(
            self._get_element(x))
        temp: Matrix[np.int64] = np.array(
            [other._matrix[convert(i)] for i in range(self._shape)])
        self._matrix = np.matmul(self._matrix, temp)  # type: ignore
        self._size += other.size

    @override
    def clear(self) -> None:
        if self._size:
            temp: Matrix[np.int64] = self.identity(self._shape)
            for i in range(self._shape):
                for j in range(self._shape):
                    self._matrix[i][j] = temp[i][j]
            self._size = 0

    @override
    def copy(self: Self) -> Self:
        new_holodeque: Self = self.__class__(
            maxlen=self._maxlen, **self._kwargs)
        new_holodeque._element_tuple = tuple(
            elem for elem in self._element_tuple)
        new_holodeque._element_map = {
            key: val for key, val in self._element_map.items()}
        if self._maxlen != 0:
            new_holodeque.concatright(self)
        return new_holodeque


if __name__ == "__main__":

    # example usage
    q = numpydeque(alphabet={0, 1, 2, 3})
    t = numpydeque(alphabet={0, 1, 2, 3})
    ext = [0, 1, 2, 2, 3, 0, 3, 2, 3, 2, 2, 1]
    q.extendright(ext)
    t.extendleft(ext)
    assert list(q) == list(reversed(t))
    assert list(t) == list(reversed(q))
