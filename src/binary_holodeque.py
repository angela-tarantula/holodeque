"""A binary holodeque implementation."""

from typing import Optional, Iterable, override
from src.abstract_holodeque import HolodequeBase, Matrix


class binarydeque(HolodequeBase[int]):
    """A holodeque that only accepts 0 and 1.

    Attributes:
        _matrix: A square matrix representing the state of the binary_holodeque.
        _shape: The dimension of the base matrix (its width and height).
        _size: The current number of elements in the binary_holodeque.
        _maxlen: The maximum allowed size of the holodeque; None if unbounded.
    """

    @override
    def __init__(self, iterable: Iterable[int] = (), maxlen: Optional[int] = None) -> None:
        """Initializes a binary_holodeque with the provided iterable.

        Args:
            iterable: An Iterable of elements to populate the binary_holodeque.
            maxlen: Optional maximum size of the holodeque; if not None, restricts
                    the number of elements.
        """
        super().__init__(iterable=iterable, maxlen=maxlen)

    @override
    def _initialize_matrix(self) -> Matrix[int]:
        """Initializes the base matrix for the binary_holodeque.

        Returns:
            A 2x2 Matrix to represent the initial state of the binary_holodeque.
        """
        return self.identity(2)

    @override
    def _handle_overflow(self, from_left: bool = True) -> None:
        """Handles overflow when the binary_holodeque reaches its maximum size.

        Pops an element from the side opposite the push.

        Args:
            from_left: A bool indicating the origin of the push.
        """
        if from_left:
            self.popright()
        else:
            self.popleft()

    @override
    def _get_axis(self, element: int) -> int:
        if not isinstance(element, int):
            raise TypeError(f"Expected an integer, but got {type(element).__name__}.")
        if element not in {0, 1}:
            raise ValueError(f"Invalid value {element}. The binary_holodeque accepts only 0 and 1.")
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
