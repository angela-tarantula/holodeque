"""A numpy holodeque implementation."""

from collections.abc import Hashable
from typing import Callable, Self, override

import numpy as np

from src.base_holodeque import BaseHolodeque, Matrix
from src.holodeque import holodeque


class numpydeque[T: Hashable](holodeque[T]):
    """A numpy holodeque implementation."""

    @staticmethod
    def identity(n: int) -> Matrix[int]:
        return np.eye(n, dtype=np.int64)

    @override
    def clear(self) -> None:
        if self._size:
            temp: Matrix[int] = self.identity(self._shape)
            for i in range(self._shape):
                for j in range(self._shape):
                    self._matrix[i][j] = temp[i][j]
            self._size = 0

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
    @BaseHolodeque.compatible
    def concatleft(self, other: Self) -> None:
        if self._maxlen is not None and self._size + other._size > self._maxlen:
            raise ValueError(
                "incompatible holodeque because it would exceed maximum length")
        if self is other:
            other = self.copy()
        convert: Callable[[int], int] = lambda x: other._get_axis(
            self._get_element(x))
        temp: Matrix[int] = np.array(
            [other._matrix[convert(i)] for i in range(self._shape)])
        self._matrix = np.matmul(temp, self._matrix)  # type: ignore
        self._size += other.size

    @override
    @BaseHolodeque.compatible
    def concatright(self, other: Self) -> None:
        if self._maxlen is not None and self._size + other._size > self._maxlen:
            raise ValueError(
                "incompatible holodeque because it would exceed maximum length")
        if self is other:
            other = self.copy()
        convert: Callable[[int], int] = lambda x: other._get_axis(
            self._get_element(x))
        temp: Matrix[int] = np.array(
            [other._matrix[convert(i)] for i in range(self._shape)])
        self._matrix = np.matmul(self._matrix, temp)  # type: ignore
        self._size += other.size


if __name__ == "__main__":

    # example usage
    q = numpydeque(alphabet={0, 1, 2, 3})
    t = holodeque(alphabet={0, 1, 2, 3})
    ext = [0, 1, 2, 2, 3, 0, 3, 2, 3, 2, 2, 1]
    q.extendright(ext)
    t.extendleft(ext)
    assert list(q) == list(reversed(t))
    assert list(t) == list(reversed(q))
