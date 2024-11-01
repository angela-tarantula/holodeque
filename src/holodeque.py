"""A fixed-alphabet holodeque implementation."""

from typing import Optional, Iterable, override
from src.abstract_holodeque import HolodequeBase, Matrix
from collections.abc import Hashable, Set


class holodeque[T: Hashable](HolodequeBase[T]):
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
    def __init__(self, alphabet: Set[T], iterable: Iterable[T] = (), maxlen: Optional[int] = None, **kwargs) -> None:
        """Initializes a holodeque with the provided iterable.

        Args:
            alphabet: The set of unique elements that the holodeque can contain.
            iterable: An Iterable of elements to populate the holodeque.
            maxlen: Optional maximum size of the holodeque; if not None, restricts
                    the number of elements.
            _kwargs: A dictionary for additional optional parameters.
        """
        super().__init__(maxlen=maxlen, alphabet=frozenset(alphabet), **kwargs)
        if not alphabet:
            raise ValueError("alphabet must be non-empty")
        self._matrix: Matrix[int] = self.identity(len(alphabet))
        self._shape: int = len(alphabet)
        self._alphabet: frozenset[T] = frozenset(alphabet)
        self._element_tuple: tuple[T, ...] = tuple(alphabet)
        self._element_map: dict[T, int] = {
            letter: i for i, letter in enumerate(self._element_tuple)}
        self.extendright(iterable)

    @override
    def _get_axis(self, element: T) -> int:
        if element not in self._alphabet:
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
