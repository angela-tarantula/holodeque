"""A fixed-alphabet holodeque in pure Python."""

from collections.abc import Hashable, Callable, Iterable, Set
from typing import Self, Optional, override

from src.base_holodeque import Matrix
from src.alphabetized_holodeque import AlphabeticHolodeque


class holodeque[T: Hashable](AlphabeticHolodeque[int, T]):
    """A holodeque with a predefined alphabet (acceptable input).   

    Attributes:
        _matrix: A square matrix representing the state of the holodeque.
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
    def _identity(self, n: int) -> Matrix[int]:
        if n < 1:
            raise ValueError("n must be positive.")
        return [[int(i == j) for j in range(n)] for i in range(n)]
    
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
                    other._matrix[convert(row)][convert(x)] * self._matrix[x][col]
                    for x in range(self._shape)
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
                    self._matrix[row][x] * other._matrix[convert(x)][convert(col)]
                    for x in range(self._shape)
                )
                for col in range(self._shape)
            ]
            # replace row with new_row
            for col in range(self._shape):
                self._matrix[row][col] = new_row[col]
        self._size += other.size
    
    @override
    def clear(self) -> None:
        if self._size:
            for i in range(self._shape):
                for j in range(self._shape):
                    if i == j:
                        self._matrix[i][j] = 1
                    else:
                        self._matrix[i][j] = 0
            self._size = 0


if __name__ == "__main__":

    # example usage
    q = holodeque(alphabet={0, 1, 2, 3})
    t = holodeque(alphabet={0, 1, 2, 3})
    ext = [0, 1, 2, 2, 3, 0, 3, 2, 3, 2, 2, 1]
    q.extendright(ext)
    t.extendleft(ext)
    assert list(q) == list(reversed(t))
    assert list(t) == list(reversed(q))
