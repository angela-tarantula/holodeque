"""A fixed-alphabet holodeque in pure Python."""
from abc import ABC
from collections.abc import Iterable, Set
from typing import Any, Optional, Self, override

from src.base_holodeque import BaseHolodeque, Matrix


class flexideque(BaseHolodeque[int, Any], ABC):
    """A pure-python holodeque with a flexible alphabet.

    Attributes:
        _matrix: A square matrix representing the state of the holodeque.
        _shape: The dimension of the base matrix (its width and height).
        _size: The current number of elements in the holodeque.
        _maxlen: The maximum allowed size of the holodeque; None if unbounded.
        _element_tuple: An tuple of acceptable input for the holodeque.
        _element_map: A hashmap that maps each containable element to an index in _element_tuple.
    """

    @override
    def __init__(self, iterable: Iterable[Any] = (), *, maxlen: Optional[int] = None) -> None:
        """Initializes a holodeque with the provided iterable.

        Args:
            iterable: An Iterable of elements to populate the holodeque.
            maxlen: Optional maximum size of the holodeque; if not None, restricts
                    the number of elements.
        """
        super().__init__(maxlen=maxlen)
        self._matrix: Matrix[int] = [[1]]
        self._shape: int = 1
        self._element_list: list[Any] = []
        self._element_map: dict[Any, int] = {}
        self.extendright(iterable)

    @property
    def shape(self) -> int:
        """The dimension of the holodeque base matrix."""
        return self._shape - 1

    @property
    def alphabet(self) -> Set[Any]:
        """The set of unique elements that the holodeque can contain."""
        return frozenset(self._element_list)

    @override
    def pushleft(self, element: Any) -> None:
        if self._size == self._maxlen:
            self._handle_overflow(from_left=True)
        index: int = self._get_axis(element)
        self._transform(index, left=True, reverse=False)
        self._size += 1

    @override
    def pushright(self, element: Any) -> None:
        if self._size == self._maxlen:
            self._handle_overflow(from_left=False)
        index: int = self._get_axis(element)
        self._transform(index, left=False, reverse=False)
        self._size += 1

    @override
    def peekleft(self) -> Any:
        if not self._size:
            raise IndexError("peek from an empty holodeque")
        return self._get_element(self._leftmost_axis())

    @override
    def peekright(self) -> Any:
        if not self._size:
            raise IndexError("peek from an empty holodeque")
        return self._get_element(self._rightmost_axis())

    @override
    def popleft(self) -> Any:
        if not self._size:
            raise IndexError("pop from an empty holodeque")
        left_axis: int = self._leftmost_axis()
        left_element: Any = self._get_element(left_axis)
        self._transform(left_axis, left=True, reverse=True)
        self._size -= 1
        self._reshape(left_axis)
        return left_element

    @override
    def popright(self) -> Any:
        if not self._size:
            raise IndexError("pop from an empty holodeque")
        right_axis: int = self._rightmost_axis()
        right_element: Any = self._get_element(right_axis)
        self._transform(right_axis, left=False, reverse=True)
        self._size -= 1
        self._reshape(right_axis)
        return right_element

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
        for i in range(self._shape):
            if i == axis:
                continue
            for j in range(self._shape):
                match (left, reverse):
                    case (True, True):
                        # Subtract other rows from row of axis
                        self._matrix[axis][j] -= self._matrix[i][j]
                    case (True, False):
                        # Add other rows to row of axis
                        self._matrix[axis][j] += self._matrix[i][j]
                    case (False, True):
                        # Subtract column of axis from other columns
                        self._matrix[j][i] -= self._matrix[j][axis]
                    case (False, False):
                        # Add column of axis to other columns
                        self._matrix[j][i] += self._matrix[j][axis]

    def _get_axis(self, element: Any) -> int:
        """Obtains the provided element's corresponding axis in the base matrix.

        If the element is not mapped to any index, a new row and column are added
        to the base matrix, and the element is mapped to the new index.

        Args:
            element: An element for which the axis is being requested.
                    Validity of the element is not guaranteed.

        Returns:
            The int axis that corresponds to the element.

        Raises:
            ValueError: If the holodeque does not accept the value of the element.
        """
        if element not in self._element_map:
            self._element_list.append(element)
            self._element_map[element] = self._shape - 1
            for row in self._matrix:
                row.append(row[-1])  # type: ignore
            self._matrix[-1][-1] = 0
            self._matrix.append([0] * (self._shape) + [1])  # type: ignore
            self._shape += 1
        return self._element_map[element]

    def _get_element(self, axis: int) -> Any:
        """Obtains the element corresponding to a provided axis in the base matrix.

        Args:
            axis: An int axis whose element is being requested. 
                  Validity of the axis is assumed.

        Returns:
            The element that corresponds to the axis.
        """
        return self._element_list[axis]

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

    def _reshape(self, index: int) -> None:
        if all(self._matrix[index][i] == int(i == index) for i in range(self._shape)):
            self._matrix.pop()  # type: ignore
            for row in self._matrix:
                row.pop()  # type: ignore
            self._shape -= 1
            self._element_list[index], self._element_list[-1] = self._element_list[-1], self._element_list[index]
            self._element_map[self._element_list[index]] = index
            del self._element_map[self._element_list.pop()]
            self._matrix[index], self._matrix[-1] = self._matrix[-1], self._matrix[index]  # type: ignore
            for row in self._matrix:
                row[index], row[-1] = row[-1], row[index]

    @override
    def concatleft(self, other: Self) -> None:
        raise NotImplementedError

    @override
    def concatright(self, other: Self) -> None:
        raise NotImplementedError

    @override
    def clear(self) -> None:
        self._matrix.clear()  # type: ignore
        self._matrix.append([1])  # type: ignore
        self._shape = 1
        self._element_list.clear()
        self._element_map.clear()
        self._size = 0

    @override
    def __contains__(self, element: Any) -> bool:
        try:
            index: int = self._get_axis(element)
            return bool(self._matrix[index][index-1])
        except ValueError:
            return False

    @override
    def copy(self: Self) -> Self:
        new_holodeque: Self = self.__class__(maxlen=self._maxlen)
        new_holodeque._matrix = [[self._matrix[i][j]
                                  for j in range(self._shape)] for i in range(self._shape)]
        new_holodeque._shape = self._shape
        new_holodeque._element_list = [self._element_list[i]
                                       for i in range(len(self._element_list))]
        new_holodeque._element_map = {
            key: value for key, value in self._element_map.items()}
        new_holodeque._size = self._size
        return new_holodeque

    @override
    def __add__(self, other: Self) -> Self:
        raise NotImplementedError

    @override
    def __radd__(self, other: Self) -> Self:
        raise NotImplementedError

    @override
    def __iadd__(self, other: Self) -> Self:
        raise NotImplementedError

    @override
    def __mul__(self, multiple: int) -> Self:
        raise NotImplementedError

    @override
    def __rmul__(self, multiple: int) -> Self:
        raise NotImplementedError

    @override
    def __imul__(self, multiple: int) -> Self:
        raise NotImplementedError
