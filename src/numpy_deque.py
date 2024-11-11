"""A fixed-alphabet holodeque using numpy."""

from collections.abc import Hashable, Set, Iterable
from typing import Callable, Optional, Self, override

import numpy as np

from src.base_holodeque import Matrix
from src.alphabetized_holodeque import AlphabeticHolodeque


class numpydeque[T: Hashable](AlphabeticHolodeque[np.int64, T]):
    """A holodeque with a predefined alphabet.   

    Attributes:
        _matrix: A square numpy matrix representing the state of the holodeque.
        _shape: The dimension of the base matrix (its width and height).
        _size: The current number of elements in the holodeque.
        _maxlen: The maximum allowed size of the holodeque; None if unbounded.
        _alphabet: The set of unique elements that the holodeque can contain.
        _element_tuple: An tuple of acceptable input for the holodeque.
        _element_map: A hashmap that maps each containable element to an index in _element_tuple.
    """

    @override
    def __init__(self, iterable: Iterable[T] = (), *, alphabet: Set[T], maxlen: Optional[int] = None) -> None:
        super().__init__(iterable, alphabet=alphabet, maxlen=maxlen)

    @override
    def _identity(self, n: int) -> Matrix[np.int64]:
        return np.eye(n, dtype=np.int64)

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
        if self._maxlen is not None and self._size + other._size > self._maxlen:
            raise ValueError(
                "incompatible holodeque because it would exceed maximum length")
        if self._alphabet != other._alphabet:
            raise ValueError(
                "incompatible holodeque because they have different alphabets")
        if self._element_tuple != other._element_tuple:
            # prepare for matrix multiplication
            self._remap(other._element_tuple, other._element_map)
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
        if self._maxlen is not None and self._size + other._size > self._maxlen:
            raise ValueError(
                "incompatible holodeque because it would exceed maximum length")
        if self._alphabet != other._alphabet:
            raise ValueError(
                "incompatible holodeque because they have different alphabets")
        if self._element_tuple != other._element_tuple:
            # prepare for matrix multiplication
            self._remap(other._element_tuple, other._element_map)
        if self is other:
            other = self.copy()
        convert: Callable[[int], int] = lambda x: other._get_axis(
            self._get_element(x))
        temp: Matrix[np.int64] = np.array(
            [other._matrix[convert(i)] for i in range(self._shape)])
        self._matrix = np.matmul(self._matrix, temp)  # type: ignore
        self._size += other.size
    
    def _remap(self, other_element_tuple: tuple[T, ...], other_element_map: dict[T, int]) -> None:
        """Remaps this holodeque's element tuple to match another holodeque's element tuple.
        
        Swaps the rows and columns for each cycle detected.
        
        Args:
            other_element_tuple: The element tuple of the other holodeque.
            other_element_map: The element map of the other holodeque.
        """
        index_mapping = [other_element_map[element] for element in self._element_tuple]
        visited = [False] * self._shape
        for i in range(self._shape):
            if visited[i] or index_mapping[i] == i:
                continue
            cycle = []
            j = i
            while not visited[j]:
                visited[j] = True
                cycle.append(j)
                j = index_mapping[j]
            for k in range(1, len(cycle)):
                idx1 = cycle[0]
                idx2 = cycle[k]
                for col in range(self._shape):
                    self._matrix[idx1][col], self._matrix[idx2][col] = self._matrix[idx2][col], self._matrix[idx1][col]
                for row in range(self._shape):
                    self._matrix[row][idx1], self._matrix[row][idx2] = self._matrix[row][idx2], self._matrix[row][idx1]
        self._element_tuple = other_element_tuple
        self._element_map = other_element_map

    @override
    def clear(self) -> None:
        if self._size:
            temp: Matrix[np.int64] = self._identity(self._shape)
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
