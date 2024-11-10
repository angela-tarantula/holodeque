"""An abstract subclass of BaseHolodeque for holodeques with alphabets."""

from abc import ABC, abstractmethod
from collections.abc import Hashable, Set
from typing import Iterable, Optional, override

from src.base_holodeque import BaseHolodeque, Matrix, NumberLike


class AlphabeticHolodeque[NL: NumberLike, T: Hashable](BaseHolodeque[NL, T],ABC):
    """Abstract base class for holodeques with alphabets.

    Attributes:
        _matrix: A square matrix representing the state of the holodeque.
        _shape: The dimension of the base matrix (its width and height).
        _size: The current number of elements in the holodeque.
        _maxlen: The maximum allowed size of the holodeque; None if unbounded.
        _alphabet: The set of unique elements that the holodeque can contain.
    """
    
    @override
    def __init__(self, iterable: Iterable[T] = (), *, alphabet: Set[T], maxlen: Optional[int] = None) -> None:
        """Initializes a holodeque with the provided iterable.

        Args:
            iterable: An Iterable of elements to populate the holodeque.
            alphabet: The set of unique elements that the holodeque can contain.
            maxlen: Optional maximum size of the holodeque; if not None, restricts
                    the number of elements.
        """
        super().__init__(maxlen=maxlen, alphabet=frozenset(alphabet))
        if len(alphabet) < 2:
            raise ValueError("alphabet must contain at least 2 elements")
        self._matrix: Matrix[NL] = self._identity(len(alphabet))
        self._shape: int = len(alphabet)
        self._alphabet: frozenset[T] = frozenset(alphabet)
        self._element_tuple: tuple[T, ...] = tuple(alphabet)
        self._element_map: dict[T, int] = {
            letter: i for i, letter in enumerate(self._element_tuple)}
        self.extendright(iterable)
    
    @abstractmethod
    def _identity(self, n: int) -> Matrix[NL]:
        """Creates an nxn identity matrix"""
    
    @override
    def _get_axis(self, element: T) -> int:
        if element not in self._alphabet:
            raise ValueError(
                f"The holodeque does not accept the element: {element}")
        return self._element_map[element]

    @override
    def _get_element(self, axis: int) -> T:
        return self._element_tuple[axis]