"""A binary holodeque implementation."""

from typing import Iterable, Optional, override

from src.base_holodeque import BaseHolodeque, Matrix


class binarydeque(BaseHolodeque[int, int]):
    """A holodeque that only accepts 0 and 1.

    Attributes:
        _matrix: A square matrix representing the state of the holodeque.
        _shape: The dimension of the base matrix (its width and height).
        _size: The current number of elements in the holodeque.
        _maxlen: The maximum allowed size of the holodeque; None if unbounded.
        _alphabet: The set of unique elements that the holodeque can contain.
        _kwargs: A dictionary for additional optional parameters.
    """

    @override
    def __init__(self, iterable: Iterable[int] = (), maxlen: Optional[int] = None, **kwargs) -> None:
        """Initializes a holodeque with the provided iterable.

        Args:
            iterable: An Iterable of elements to populate the holodeque.
            maxlen: Optional maximum size of the holodeque; if not None, restricts
                    the number of elements.
            _kwargs: A dictionary for additional optional parameters.
        """
        super().__init__(maxlen=maxlen, **kwargs)
        self._matrix: Matrix[int] = self.identity(2)
        self._shape: int = 2
        self._alphabet: frozenset[int] = frozenset([0, 1])
        self.extendright(iterable)

    @override
    def _get_axis(self, element: int) -> int:
        if element != 0 and element != 1:
            raise ValueError(f"Invalid value {
                             element}. This holodeque accepts only 0 and 1.")
        return element

    @override
    def _get_element(self, axis: int) -> int:
        return axis

    @override
    def reverse(self) -> None:
        self._matrix[0][0], self._matrix[1][1] = self._matrix[1][1], self._matrix[0][0]

    def negate(self) -> None:
        """Flips all the bits stored in the holodeque.

        Implemented by flipping the base matrix along each diagonal.
        """
        self._matrix[0][0], self._matrix[1][1] = self._matrix[1][1], self._matrix[0][0]
        self._matrix[0][1], self._matrix[1][0] = self._matrix[1][0], self._matrix[0][1]


if __name__ == "__main__":

    # example usage
    q = binarydeque()
    t = binarydeque()
    ext = [0, 0, 0, 0, 1, 1, 0]
    q.extendright(ext)
    t.extendleft(ext)
    assert list(q) == list(reversed(t))
    assert list(t) == list(reversed(q))
