"""An abstract class for holodeques with alphabets (set of acceptable input)."""

from abc import ABC, abstractmethod
from collections.abc import Hashable, Set
from typing import Iterable, Optional, override

from src.base_holodeque import BaseHolodeque, Matrix, NumberLike


class AlphabeticHolodeque[NL: NumberLike, T: Hashable](BaseHolodeque[NL, T], ABC):
    """Abstract base class for holodeques with alphabets (set of acceptable input).

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
        
        Raises:
            ValueError: If maxlen is negative or the alphabet contains less than 2 elements.
        """
        super().__init__(iterable, maxlen=maxlen, alphabet=frozenset(alphabet))
        if len(alphabet) < 2:
            raise ValueError("alphabet must contain at least 2 elements")
        self._matrix: Matrix[NL] = self._identity(len(alphabet))
        self._shape: int = len(alphabet)
        self._alphabet: frozenset[T] = frozenset(alphabet)
        self._element_tuple: tuple[T, ...] = tuple(alphabet)
        self._element_map: dict[T, int] = {
            letter: i for i, letter in enumerate(self._element_tuple)}
        self.extendright(iterable)

    @property
    def shape(self) -> int:
        """The dimension of the holodeque base matrix."""
        return self._shape
    
    @property
    def alphabet(self) -> Set[T]:
        """The set of unique elements that the holodeque can contain."""
        return self._alphabet

    @abstractmethod
    def _identity(self, n: int) -> Matrix[NL]:
        """Creates an nxn identity matrix"""
        
    @override
    def pushleft(self, element: T) -> None:
        index: int = self._get_axis(element)
        if self._size == self._maxlen:
            self._handle_overflow(from_left=True)
        self._transform(index, left=True, reverse=False)
        self._size += 1
    
    @override
    def pushright(self, element: T) -> None:
        index: int = self._get_axis(element)
        if self._size == self._maxlen:
            self._handle_overflow(from_left=False)
        self._transform(index, left=False, reverse=False)
        self._size += 1
        
    @override
    def peekleft(self) -> T:
        if not self._size:
            raise IndexError("peek from an empty holodeque")
        return self._get_element(self._leftmost_axis())
    
    @override
    def peekright(self) -> T:
        if not self._size:
            raise IndexError("peek from an empty holodeque")
        return self._get_element(self._rightmost_axis())
    
    @override
    def popleft(self) -> T:
        if not self._size:
            raise IndexError("pop from an empty holodeque")
        left_axis: int = self._leftmost_axis()
        self._transform(left_axis, left=True, reverse=True)
        self._size -= 1
        return self._get_element(left_axis)
    
    @override
    def popright(self) -> T:
        if not self._size:
            raise IndexError("pop from an empty holodeque")
        right_axis: int = self._rightmost_axis()
        self._transform(right_axis, left=False, reverse=True)
        self._size -= 1
        return self._get_element(right_axis)

    def _get_axis(self, element: T) -> int:
        """Obtains the provided element's corresponding axis in the base matrix.

        Args:
            element: An element for which the axis is being requested.
                     Validity of the element is not guaranteed.

        Returns:
            The int axis that corresponds to the element.

        Raises:
            ValueError: If the holodeque does not accept the value of the element.
        """
        if element not in self._alphabet:
            raise ValueError(
                f"The holodeque does not accept the element: {element}")
        return self._element_map[element]

    def _get_element(self, axis: int) -> T:
        """Obtains the element corresponding to a provided axis in the base matrix.

        Args:
            axis: An int axis whose element is being requested. 
                  Validity of the axis is assumed.

        Returns:
            The element that corresponds to the axis.
        """
        return self._element_tuple[axis]
    
    def _leftmost_axis(self) -> int:
        """Obtains the axis that corresponds to the leftmost element of the holodeque.

        The key insight is that the index of the first occurrence of the maximum value
        in the last column marks the axis of the leftmost element.

        Returns:
            The int index of the row with the largest value in the last column of thebase matrix.
        """
        return max(range(self._shape), key=lambda x: self._matrix[x][-1])
    
    def _rightmost_axis(self) -> int:
        """Obtains the axis that corresponds to the rightmost element of the holodeque.

        The key insight is that the index of the minimum value of the row at the
        leftmost element's axis marks the axis of the rightmost element.

        Returns:
            The int index of the column with the smallest value in the row of the left element.
        """
        left_axis: int = max(range(self._shape),
                             key=lambda x: self._matrix[x][-1])
        if self._size == 1:
            return left_axis
        return min(range(self._shape), key=lambda x: self._matrix[left_axis][x])

    @abstractmethod
    def _transform(self, axis: int, left: bool = True, reverse: bool = False) -> None:
        """Applies the specified transformation to the base matrix.

        Modifies the matrix in-place, avoiding full matrix multiplication.

        Args:
            axis: The int index of the row or column defining the transformation.
            left: If True, simulates left-side multiplication; otherwise,
                  simulates right-side multiplication.
            reverse: If True, applies the inverse transformation; otherwise,
                     applies the direct transformation.
        """
    
    @override
    def __contains__(self, element: T) -> bool:
        try:
            index: int = self._get_axis(element)
            return bool(self._matrix[index][index-1])
        except ValueError:
            return False