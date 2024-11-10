"""Defines the abstract base class and iterator for a holodeque.

This holodeque represents a novel implementation of a double-ended queue (deque).
It utilizes a matrix to model the contained elements, employing left- and right-matrix 
multiplication to simulate pushing and popping from either end. This approach leverages 
the non-commutative nature of matrix multiplication, ensuring that each sequence of inputs 
corresponds to a unique output matrix.
"""

from abc import ABC, abstractmethod
from collections.abc import Hashable, Set
from typing import Any, Iterable, Iterator, Optional, Protocol, Self


# typing protocol
class NumberLike(Protocol):
    def __add__(self, other: Self) -> Self:
        ...

    def __sub__(self, other: Self) -> Self:
        ...

    def __mul__(self, other: Self) -> Self:
        ...

    def __floordiv__(self, other: Self) -> Self:
        ...

    def __gt__(self, other: Self) -> Any:
        ...

# typing protocol
class MatrixRow[R: NumberLike](Protocol):

    def __getitem__(self, index: int) -> R:
        ...

    def __setitem__(self, index: int, value: R) -> None:
        ...

    def __len__(self) -> int:
        ...

    def __iter__(self) -> Iterator[R]:
        ...


# typing protocol
class Matrix[S: NumberLike](Protocol):

    def __getitem__(self, index: int) -> MatrixRow[S]:
        ...

    def __len__(self) -> int:
        ...

    def __iter__(self) -> Iterator[MatrixRow[S]]:
        ...


class BaseHolodeque[NL: NumberLike, T: Hashable](ABC):
    """Abstract base class for the holodeque data structure.

    Attributes:
        _matrix: A square matrix representing the state of the holodeque.
        _shape: The dimension of the base matrix (its width and height).
        _size: The current number of elements in the holodeque.
        _maxlen: The maximum allowed size of the holodeque; None if unbounded.
        _alphabet: The set of unique elements that the holodeque can contain.
        _kwargs: A dictionary for additional optional parameters.
    """

    def __init__(self, iterable: Iterable[T] = (), *, maxlen: Optional[int] = None, **kwargs) -> None:
        """Initializes a holodeque with the provided iterable.

        Args:
            maxlen: Optional maximum size of the holodeque; if not None, restricts
                    the number of elements.
            kwargs: Additional keyword arguments for use by subclasses.

        Raises:
            ValueError: If maxlen is negative.
        """
        if maxlen is not None and maxlen < 0:
            raise ValueError("maxlen must be non-negative")
        self._matrix: Matrix[NL]
        self._shape: int
        self._alphabet: Set[T]
        self._size: int = 0
        self._maxlen: Optional[int] = maxlen
        self._kwargs = kwargs

    @property
    def shape(self) -> int:
        """The dimension of the holodeque base matrix."""
        return self._shape

    @property
    def size(self) -> int:
        """The current number of elements in the holodeque."""
        return self._size

    @property
    def maxlen(self) -> Optional[int]:
        """The maximum size of the holodeque."""
        return self._maxlen

    @property
    def alphabet(self) -> Set[T]:
        """The set of unique elements that the holodeque can contain."""
        return self._alphabet

    @abstractmethod
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

    @abstractmethod
    def _get_element(self, axis: int) -> T:
        """Obtains the element corresponding to a provided axis in the base matrix.

        Args:
            axis: An int axis whose element is being requested. 
                  Validity of the axis is assumed.

        Returns:
            The element that corresponds to the axis.
        """

    def _handle_overflow(self, from_left: bool = True) -> None:
        """Handles overflow when the holodeque reaches its maximum size.

        Pops an element from the side opposite the push.

        Args:
            from_left: A bool indicating the origin of the push.
        """
        if self._size:
            if from_left:
                self.popright()
            else:
                self.popleft()

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
                        # Add row other rows to row of axis
                        self._matrix[axis][j] += self._matrix[i][j]
                    case (False, True):
                        # Subtract column of axis from other columns
                        self._matrix[j][i] -= self._matrix[j][axis]
                    case (False, False):
                        # Add column of axis to other columns
                        self._matrix[j][i] += self._matrix[j][axis]

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

    def pushleft(self, element: T) -> None:
        """Add an element to the left end of the holodeque.

        Args:
            element: The element to be added to the left side of the holodeque.

        Raises:
            TypeError: If the element has an invalid type.
            ValueError: If the element has an invalid value.
        """
        index: int = self._get_axis(element)
        if self._size == self._maxlen:
            self._handle_overflow(from_left=True)
        self._transform(index, left=True, reverse=False)
        self._size += 1

    def pushright(self, element: T) -> None:
        """Add an element to the right end of the holodeque.

        Args:
            element: The element to be added to the right side of the holodeque.

        Raises:
            TypeError: If the element has an invalid type.
            ValueError: If the element has an invalid value.
        """
        index: int = self._get_axis(element)
        if self._size == self._maxlen:
            self._handle_overflow(from_left=False)
        self._transform(index, left=False, reverse=False)
        self._size += 1

    def peekleft(self) -> T:
        """Peek the leftmost element in the holodeque.

        Returns:
            The leftmost element in the holodeque.

        Raises:
            IndexError: If the holodeque is empty when attempting to peek.
        """
        if not self._size:
            raise IndexError("peek from an empty holodeque")
        return self._get_element(self._leftmost_axis())

    def peekright(self) -> T:
        """Peek the rightmost element in the holodeque.

        Returns:
            The rightmost element in the holodeque.

        Raises:
            IndexError: If the holodeque is empty when attempting to peek.
        """
        if not self._size:
            raise IndexError("peek from an empty holodeque")
        return self._get_element(self._rightmost_axis())

    def popleft(self) -> T:
        """Remove and return the leftmost element in the holodeque.

        Returns:
            The leftmost element in the holodeque.

        Raises:
            IndexError: If the holodeque is empty when attempting to pop.
        """
        if not self._size:
            raise IndexError("pop from an empty holodeque")
        left_axis: int = self._leftmost_axis()
        self._transform(left_axis, left=True, reverse=True)
        self._size -= 1
        return self._get_element(left_axis)

    def popright(self) -> T:
        """Remove and return the rightmost element in the holodeque.

        Returns:
            The rightmost element in the holodeque.

        Raises:
            IndexError: If the holodeque is empty when attempting to pop.
        """
        if not self._size:
            raise IndexError("pop from an empty holodeque")
        right_axis: int = self._rightmost_axis()
        self._transform(right_axis, left=False, reverse=True)
        self._size -= 1
        return self._get_element(right_axis)

    def extendleft(self, iterable: Iterable[T]) -> None:
        """Extend the left end of the holodeque with an iterable.

        Args:
            iterable: An Iterable of elements to add to the
              holodeque from the left-hand side.
        """
        for elem in iterable:
            self.pushleft(elem)

    def extendright(self, iterable: Iterable[T]) -> None:
        """Extend the right end of the holodeque with an iterable.

        Args:
            iterable: An Iterable of elements to add to the
              holodeque from the right-hand side.
        """
        try:
            self.concatright(iterable)  # type: ignore
        except:
            for elem in iterable:
                self.pushright(elem)

    @abstractmethod
    def concatleft(self, other: Self) -> None:
        """Concatenate another holodeque to the left end of this holodeque.

        Performs in-place left multiplication of their base matrices.

        Args:
            other: Another holodeque to be concatenated on the left side.

        Raises:
            ValueError: If the other holodeque has a different base matrix shape, 
              has its elements mapped differently, or if concat would exceed maxlen.
        """

    @abstractmethod
    def concatright(self, other: Self) -> None:
        """Concatenate another holodeque to the right end of this holodeque.

        Performs in-place right multiplication of their base matrices.

        Args:
            other: Another holodeque to be concatenated on the right side.

        Raises:
            ValueError: If the other holodeque has a different base matrix shape, 
              has its elements mapped differently, or if concat would exceed maxlen.
        """

    @abstractmethod
    def clear(self) -> None:
        """Empties the holodeque.

        Resets the base matrix in-place into an identity matrix of the same shape.
        """

    def __iter__(self) -> Iterator[T]:
        """Returns an iterator that can traverse a copy of the holodeque from left to right."""
        return HolodequeIterator[NL, T](self, reverse=False)

    def __reversed__(self) -> Iterator[T]:
        """Returns an iterator that can traverse a copy of the holodeque from right to left."""
        return HolodequeIterator[NL, T](self, reverse=True)

    def reverse(self) -> None:
        """Reverses the holodeque in-place."""
        reverse_iterator: Iterator[T] = reversed(self)
        self.clear()
        for element in reverse_iterator:
            self.pushright(element)

    def __contains__(self, element: T) -> bool:
        try:
            index: int = self._get_axis(element)
            return any(self._matrix[index][i] != int(index == i) for i in range(self._shape))
        except ValueError:
            return False

    def count(self, element: T) -> int:
        """Counts the occurrences of an element in the holodeque."""
        return sum(element == item for item in self)

    def rotate(self, n: int = 1) -> None:
        """Rotates the holodeque `n` steps to the right (or left if `n` is negative).

        Before performing the rotation, it determines the most efficient direction.

        Args:
            n: The int number of positions to rotate to the right (if positive)
               or to the left (if negative).
        """
        if self._size <= 1:
            return

        halflen: int = self._size // 2
        if n > halflen or n < -halflen:
            n %= self._size
            if n > halflen:
                n -= self._size
            elif n < -halflen:
                n += self._size
        while n > 0:
            self.pushleft(self.popright())
            n -= 1
        while n < 0:
            self.pushright(self.popleft())
            n += 1

    def remove(self, element: T) -> None:
        """Removes the first instance of the specified element from the left end.

        Args:
            element: The element to remove upon its first occurrence.

        Raises:
            ValueError: If the element is not present in the holodeque.
        """
        index: int = 0
        while index < self._size:
            if self.peekleft() == element:
                self.popleft()
                self.rotate(index)
                return
            self.pushright(self.popleft())
            index += 1
        raise ValueError(f"'{element}' not in holodeque")

    def insert(self, index: int, element: T) -> None:
        if index < 0:
            index += self._size
        if index < 0:
            index = 0
        elif index > self._size:
            index = self._size
        if index < (self._size + 1) // 2:
            for _ in range(index):
                self.pushright(self.popleft())
            self.pushleft(element)
            for _ in range(index):
                self.pushleft(self.popright())
        else:
            for _ in range(self._size - index):
                self.pushleft(self.popright())
            self.pushright(element)
            for _ in range((self._size - 1) - index):
                self.pushright(self.popleft())

    def index(self, target: T, start: int = 0, stop: int = None) -> int:  # type: ignore
        if start < 0:
            start += self._size
        if stop is None:
            stop = self._size
        if stop < 0:
            stop += self._size
        for i, element in enumerate(self):
            if i >= start and i < stop and element == target:
                return i
        raise ValueError(f"'{target}' not in holodeque")

    def copy(self: Self) -> Self:
        """Create and return a new holodeque with identical contents."""
        new_holodeque: Self = self.__class__(
            maxlen=self._maxlen, **self._kwargs)
        if self._maxlen != 0:
            new_holodeque.concatright(self)
        return new_holodeque

    def __len__(self) -> int:
        return self._size

    def __getitem__(self, index: int) -> T:
        if index < 0:
            index += self._size
        if index < 0 or index >= self._size:
            raise IndexError("holodeque index out of range")
        if index > self._size // 2:
            index -= self._size
        desired_item: T
        if index >= 0:
            for _ in range(index):
                self.pushright(self.popleft())
            desired_item = self.peekleft()
            for _ in range(index):
                self.pushleft(self.popright())
        else:
            index = -index - 1
            for _ in range(index):
                self.pushleft(self.popright())
            desired_item = self.peekright()
            for _ in range(index):
                self.pushright(self.popleft())
        return desired_item

    def __setitem__(self, index: int, element: T) -> None:
        if index < 0:
            index += self._size
        if index < 0 or index >= self._size:
            raise IndexError("holodeque index out of range")
        if index > self._size // 2:
            index -= self._size
        if index >= 0:
            for _ in range(index):
                self.pushright(self.popleft())
            self.popleft()
            self.pushleft(element)
            for _ in range(index):
                self.pushleft(self.popright())
        else:
            index = -index - 1
            for _ in range(index):
                self.pushleft(self.popright())
            self.popright()
            self.pushright(element)
            for _ in range(index):
                self.pushright(self.popleft())

    def __delitem__(self, index: int) -> None:
        if index < 0:
            index += self._size
        if index < 0 or index >= self._size:
            raise IndexError("holodeque index out of range")
        if index > self._size // 2:
            index -= self._size
        if index >= 0:
            for _ in range(index):
                self.pushright(self.popleft())
            self.popleft()
            for _ in range(index):
                self.pushleft(self.popright())
        else:
            index = -index - 1
            for _ in range(index):
                self.pushleft(self.popright())
            self.popright()
            for _ in range(index):
                self.pushright(self.popleft())

    def __repr__(self) -> str:
        result: list[str] = [f"{type(self).__name__}({list(self)}"]
        if self._maxlen is not None:
            result.append(f", maxlen={self._maxlen}")
        for key, value in self._kwargs.items():
            result.append(f", {key}={value}")
        result.append(")")
        return "".join(result)

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, type(self)) and list(self) == list(other)

    def __ne__(self, other: Any) -> bool:
        return not isinstance(other, type(self)) or list(self) != list(other)

    def __lt__(self, other: Any) -> bool:
        if isinstance(other, type(self)):
            return list(self) < list(other)
        else:
            raise TypeError(f"'<' not supported between instances of holodeque and '{
                            type(other).__name__}'")

    def __le__(self, other: Any) -> bool:
        if isinstance(other, type(self)):
            return list(self) <= list(other)
        else:
            raise TypeError(f"'<=' not supported between instances of holodeque and '{
                            type(other).__name__}'")

    def __gt__(self, other: Any) -> bool:
        if isinstance(other, type(self)):
            return list(self) > list(other)
        else:
            raise TypeError(f"'>' not supported between instances of holodeque and '{
                            type(other).__name__}'")

    def __ge__(self, other: Any) -> bool:
        if isinstance(other, type(self)):
            return list(self) >= list(other)
        else:
            raise TypeError(f"'>=' not supported between instances of holodeque and '{
                            type(other).__name__}'")

    def __add__(self, other: Self) -> Self:
        new_copy: Self = self.copy()
        new_copy.concatright(other)
        return new_copy

    def __radd__(self, other: Self) -> Self:
        new_copy: Self = self.copy()
        new_copy.concatright(other)
        return new_copy

    def __iadd__(self, other: Self) -> Self:
        self.concatright(other)
        return self

    def __mul__(self, multiple: int) -> Self:
        if isinstance(multiple, int):
            if multiple <= 0:
                return self.__class__(maxlen=self._maxlen, **self._kwargs)
            elif multiple == 1:
                return self.copy()
            result = self.copy()
            if result._maxlen is not None and result._maxlen < result._size * multiple:
                while result._size + self._size <= result._maxlen:
                    result.concatright(self)
                for element in reversed(result):
                    if result._size == result._maxlen:
                        break
                    result.pushleft(element)
                return result
            else:
                for _ in range(multiple - 1):
                    result.concatright(self)
                return result
        else:
            raise TypeError(
                f"can't multiply sequence by non-int of type {type(multiple).__name__}")

    def __rmul__(self, multiple: int) -> Self:
        return self.__mul__(multiple)

    def __imul__(self, multiple: int) -> Self:
        if isinstance(multiple, int):
            if multiple <= 0:
                self.clear()
                return self
            elif multiple == 1:
                return self
            temp = self.copy()
            if self._maxlen is not None and self._maxlen < self._size * multiple:
                while self._size + temp._size <= self._maxlen:
                    self.concatright(temp)
                for element in reversed(temp):
                    if self._size == self._maxlen:
                        break
                    self.pushleft(element)
                return self
            for _ in range(multiple - 1):
                self.concatright(temp)
            return self
        else:
            raise TypeError(
                f"can't multiply sequence by non-int of type {type(multiple).__name__}")


class HolodequeIterator[NL2: NumberLike, T2: Hashable]:
    """Iterator for traversing a holodeque.

    Yields each element from the holodeque by popping from a copy.

    Attributes:
        _holodeq: A destructable holodeque copy.
        _reverse: If True, yields elements from right to left; otherwise,
           yields elements from left to right.
    """

    def __init__(self, holodeq: BaseHolodeque[NL2, T2], reverse: bool = False) -> None:
        """Initializes the iterator for a holodeque.

        Args:
            holodeq: A holodeque to iterate over.
            reverse: A bool indicating the direction of iteration.
        """
        self._holodeq: BaseHolodeque[NL2, T2] = holodeq.copy()
        self._reverse: bool = reverse

    def __iter__(self) -> Iterator[T2]:
        return self

    def __next__(self) -> T2:
        if not self._holodeq.size:
            raise StopIteration
        return self._holodeq.popright() if self._reverse else self._holodeq.popleft()
