"""A fixed-alphabet holodeque implementation."""

from typing import Optional, Iterable, override, AbstractSet
from holodeque.src.abstract_holodeque import HolodequeBase, Matrix, MatrixRow


class holodeque[T](HolodequeBase[T]):
    """A holodeque with a predefined alphabet (acceptable input).   

    Attributes:
        _matrix: A square matrix representing the state of the holodeque.
        _shape: The dimension of the base matrix (its width and height).
        _size: The current number of elements in the holodeque.
        _maxlen: The maximum allowed size of the holodeque; None if unbounded.
        _element_tuple: A tuple of acceptable input for the holodeque.
        _element_map: A hashmap that converts each acceptable input to a unique
          index of _matrix.
    """

    @override
    def __init__(self, iterable: Iterable[T] = (), maxlen: Optional[int] = None, alphabet: AbstractSet[T] = set()) -> None:
        """Initializes a holodeque with the provided iterable.

        Args:
            iterable: An Iterable of elements to populate the holodeque.
            maxlen: Optional maximum size of the holodeque; if not None, restricts
                    the number of elements.
            alphabet: A set of acceptable input for the holodeque.
        """
        self._element_tuple: tuple[T, ...] = tuple(alphabet)
        self._element_map: dict[T, int] = {
            letter: i for i, letter in enumerate(self._element_tuple)}
        super().__init__(iterable=iterable, maxlen=maxlen, alphabet=frozenset(alphabet))

    @property
    def alphabet(self) -> Iterable[T]:
        """The set of input the holodeque accepts."""
        return self._element_map.keys()

    @override
    def _initialize_matrix(self) -> Matrix[int]:
        """Initializes the base matrix for the holodeque.

        Returns:
            An nxn Matrix representing the initial state of the holodeque,
              where n is the number of acceptable input.
        """
        return self.identity(len(self._element_tuple))

    @override
    def _handle_overflow(self, from_left: bool = True) -> None:
        """Handles overflow when the holodeque reaches its maximum size.

        Pops an element from the side opposite the push.

        Args:
            from_left: A bool indicating the origin of the push.
        """
        if from_left:
            self.popright()
        else:
            self.popleft()


    @override
    def _get_axis(self, element: T) -> int:
        if element not in self._element_map:
            raise ValueError(f"The holodeque does not accept the element: {element}")
        return self._element_map[element]

    @override
    def _get_element(self, axis: int) -> T:
        return self._element_tuple[axis]


if __name__ == "__main__":

    # example usage
    q = holodeque(alphabet={0, 1, 2, 3})
    t = holodeque(alphabet={0, 1, 2, 3})
    ext = [0, 1, 2, 2, 3, 0, 3, 2, 3, 2, 2, 1]
    q.extendright(ext)
    t.extendleft(ext)
    assert list(q) == list(reversed(t))
    assert list(t) == list(reversed(q))
