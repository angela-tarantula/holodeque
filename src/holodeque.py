"""A fixed-alphabet holodeque implementation."""

from collections.abc import Hashable, Set, Callable
from typing import Iterable, Optional, Self, Any, override
from functools import wraps

from src.base_holodeque import BaseHolodeque, Matrix


class holodeque[T: Hashable](BaseHolodeque[int, T]):
    """A holodeque with a predefined alphabet (acceptable input).   

    Attributes:
        _matrix: A square matrix representing the state of the holodeque.
        _shape: The dimension of the base matrix (its width and height).
        _size: The current number of elements in the holodeque.
        _maxlen: The maximum allowed size of the holodeque; None if unbounded.
        _alphabet: The set of unique elements that the holodeque can contain.
        _element_tuple: An tuple of acceptable input for the holodeque.
        _element_map: A hashmap that maps each containable element to an index in _element_tuple.
        _kwargs: A dictionary for additional optional parameters.
    """

    @override
    def __init__(self, iterable: Iterable[T] = (), *, alphabet: Set[T], maxlen: Optional[int] = None) -> None:
        """Initializes a holodeque with the provided iterable.

        Args:
            alphabet: The set of unique elements that the holodeque can contain.
            iterable: An Iterable of elements to populate the holodeque.
            maxlen: Optional maximum size of the holodeque; if not None, restricts
                    the number of elements.
            _kwargs: A dictionary for additional optional parameters.
        """
        super().__init__(maxlen=maxlen, alphabet=frozenset(alphabet))
        if len(alphabet) < 2:
            raise ValueError("alphabet must contain at least 2 elements")
        self._matrix: Matrix[int] = self.__class__.identity(len(alphabet))
        self._shape: int = len(alphabet)
        self._alphabet: frozenset[T] = frozenset(alphabet)
        self._element_tuple: tuple[T, ...] = tuple(alphabet)
        self._element_map: dict[T, int] = {
            letter: i for i, letter in enumerate(self._element_tuple)}
        self.extendright(iterable)
    
    @staticmethod
    def identity(n: int) -> Matrix[int]:
        """Creates an nxn identity matrix"""
        if n < 1:
            raise ValueError("n must be positive.")
        return [[int(i == j) for j in range(n)] for i in range(n)]

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
    def concatleft(self, other: Self) -> None:
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
        for col in range(self._shape):
            # calculate new_col to replace col
            new_col: list[int] = [
                sum(
                    (
                        other._matrix[convert(row)][convert(
                            x)] * self._matrix[x][col]
                        for x in range(1, self._shape)
                    ),
                    start=other._matrix[convert(row)][convert(
                        0)] * self._matrix[0][col]
                )
                for row in range(self._shape)
            ]
            # replace col with new_col
            for row in range(self._shape):
                self._matrix[row][col] = new_col[row]
        self._size += other.size
    
    
    @override
    def concatright(self, other: Self) -> None:
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
        for row in range(self._shape):
            # calculate new_row to replace row
            new_row: list[int] = [
                sum(
                    (
                        self._matrix[row][x] *
                        other._matrix[convert(x)][convert(col)]
                        for x in range(1, self._shape)
                    ),
                    start=self._matrix[row][0] *
                    other._matrix[convert(0)][convert(col)]
                )
                for col in range(self._shape)
            ]
            # replace row with new_row
            for col in range(self._shape):
                self._matrix[row][col] = new_row[col]
        self._size += other.size
    
    


if __name__ == "__main__":

    # example usage
    q = holodeque(alphabet={0, 1, 2, 3})
    t = holodeque(alphabet={0, 1, 2, 3})
    ext = [0, 1, 2, 2, 3, 0, 3, 2, 3, 2, 2, 1]
    q.extendright(ext)
    t.extendleft(ext)
    assert list(q) == list(reversed(t))
    assert list(t) == list(reversed(q))
