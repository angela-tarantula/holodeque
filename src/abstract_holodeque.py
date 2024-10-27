"""Defines the abstract base class and iterator for a holodeque.

This holodeque represents a novel implementation of a double-ended queue (deque).
It utilizes a matrix to model the contained elements, employing left- and right-matrix 
multiplication to simulate pushing and popping from either end. This approach leverages 
the non-commutative nature of matrix multiplication, ensuring that each sequence of inputs 
corresponds to a unique output matrix.
"""

from typing import Iterable, Iterator, Callable, Hashable, Optional, Any, Self, Protocol, SupportsInt
from abc import ABC, abstractmethod
import operator

# TODO: parallelize peekright, pushes, and pops

# typing protocol
class MatrixRow[R: SupportsInt](Protocol):

    def __getitem__(self, index: int) -> R:
        ...

    def __setitem__(self, index: int, value: R) -> None:
        ...

    def __len__(self) -> int:
        ...

    def __iter__(self) -> Iterator[R]:
        ...


# typing protocol
class Matrix[S: SupportsInt](Protocol):

    def __getitem__(self, index: int) -> MatrixRow[S]:
        ...

    def __len__(self) -> int:
        ...

    def __iter__(self) -> Iterator[MatrixRow[S]]:
        ...


class HolodequeBase[T: Hashable](ABC):
    """Abstract base class for the holodeque data structure.

    Attributes:
        _matrix: A square matrix representing the state of the holodeque.
        _shape: The dimension of the base matrix (its width and height).
        _size: The current number of elements in the holodeque.
        _maxlen: The maximum allowed size of the holodeque; None if unbounded.
        _kwargs: A dictionary for additional optional parameters.
    """

    def __init__(self, iterable: Iterable[T] = (), maxlen: Optional[int] = None, **kwargs) -> None:
        """Initializes a holodeque with the provided iterable.

        Args:
            iterable: An Iterable of elements to populate the holodeque.
            maxlen: Optional maximum size of the holodeque; if not None, restricts
                    the number of elements.
            kwargs: Additional keyword arguments for use by subclasses.

        Raises:e
            ValueError: If maxlen is negative.
        """
        self._matrix: Matrix[int] = self._initialize_matrix()
        self._shape: int = len(self._matrix)
        self._size: int = 0

        if maxlen is not None and maxlen < 0:
            raise ValueError("maxlen must be non-negative")

        self._maxlen: Optional[int] = maxlen
        self._kwargs = kwargs

        self.extendright(iterable)

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

    @staticmethod
    def identity(n: int) -> Matrix[int]:
        """Creates an nxn identity matrix.

        Args:
            n: A positive integer representing the size of the matrix.

        Returns:
            A Matrix representing the nxn identity matrix. For example:

                             [[1, 0, 0]
                        I3 =  [0, 1, 0]
                              [0, 0, 1]]

        Raises:
            ValueError: If n is not a positive integer.
        """
        if n <= 0:
            raise ValueError("n must be a positive integer.")
        return [[int(i == j) for j in range(n)] for i in range(n)]

    @abstractmethod
    def _initialize_matrix(self) -> Matrix[int]:
        """Initializes the base matrix for the holodeque.

        Returns:
            A square Matrix representing the initial state of the holodeque.
        """
        ...

    @abstractmethod
    def _handle_overflow(self, from_left: bool = True) -> Optional[bool]:
        """Handles overflow when the holodeque reaches its maximum size.

        This method defines the behavior of the holodeque when an attempt is made
        to push a new element into a full holodeque.

        Args:
            from_left: A bool indicating the origin of the push.

        Returns:
            An optional bool indicating the success of the overflow handling.

        Raises:
            IndexError: If the holodeque cannot handle the overflow.
        """
        ...

    @abstractmethod
    def _get_axis(self, element: T) -> int:
        """Obtains the provided element's corresponding axis in the base matrix.

        Args:
            element: An element for which the axis is being requested.
                     Validity of the element is not guaranteed.

        Returns:
            The int axis that corresponds to the element.

        Raises:
            TypeError: If the holodeque does not accept the type of the element.
            ValueError: If the holodeque does not accept the value of the element.
        """
        ...

    @abstractmethod
    def _get_element(self, axis: int) -> T:
        """Obtains the element corresponding to a provided axis in the base matrix.

        Args:
            axis: An int axis whose element is being requested. 
                  Validity of the axis is assumed.

        Returns:
            The element that corresponds to the axis.
        """
        ...

    def _view_row(self, i: int) -> Iterable[int]:
        return (num for num in self._matrix[i])

    def _view_column(self, i: int) -> Iterable[int]:
        return (row[i] for row in self._matrix)

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
        sign: int = -1 if reverse else 1

        for i in range(self._shape):
            if i != axis:
                for j in range(self._shape):
                    if left:
                        # Add all other rows to row of axis
                        self._matrix[axis][j] += sign * self._matrix[i][j]
                    else:
                        # Add column of axis to all other columns
                        self._matrix[j][i] += sign * self._matrix[j][axis]

    def _peekleft(self) -> int:
        """Obtains the axis that corresponds to the rightmost element of the holodeque.

        Returns:
            The int index of the largest row of the base matrix.
        """
        # Search the last column for the maximum and return the index of its first occurrence
        return max(range(self._shape), key=lambda i: self._matrix[i][-1])

    # TODO: do peekleft, if size==1 return; else look at that row
    
    def _peekright(self) -> int:
        """Obtains the axis of the leftmost element of the holodeque.

        Returns:
            The int index of the smallest column of the base matrix.
        """

        # Initialize a candidates list to track potential column indices
        candidates = [True] * self._shape

        for row in self._matrix:
            minimum: int = min(row)
            for j, val in enumerate(row):
                if val > minimum:
                    candidates[j] = False
        return candidates.index(True)

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

    # TODO: combine with _peekleft method
    def peekleft(self) -> T:
        """Peek the leftmost element in the holodeque.

        Returns:
            The leftmost element in the holodeque.

        Raises:
            IndexError: If the holodeque is empty when attempting to peek.
        """
        if not self._size:
            raise IndexError("peek from an empty holodeque")

        index: int = self._peekleft()
        return self._get_element(index)

    # TODO: combine with _peekright method
    def peekright(self) -> T:
        """Peek the rightmost element in the holodeque.

        Returns:
            The rightmost element in the holodeque.

        Raises:
            IndexError: If the holodeque is empty when attempting to peek.
        """
        if not self._size:
            raise IndexError("peek from an empty holodeque")

        index: int = self._peekright()
        return self._get_element(index)

    def popleft(self) -> T:
        """Remove and return the leftmost element in the holodeque.

        Returns:
            The leftmost element in the holodeque.

        Raises:
            IndexError: If the holodeque is empty when attempting to pop.
        """
        if not self._size:
            raise IndexError("pop from an empty holodeque")

        index: int = self._peekleft()
        self._transform(index, left=True, reverse=True)
        self._size -= 1
        return self._get_element(index)

    def popright(self) -> T:
        """Remove and return the rightmost element in the holodeque.

        Returns:
            The rightmost element in the holodeque.

        Raises:
            IndexError: If the holodeque is empty when attempting to pop.
        """
        if not self._size:
            raise IndexError("pop from an empty holodeque")

        index: int = self._peekright()
        self._transform(index, left=False, reverse=True)
        self._size -= 1
        return self._get_element(index)

    def extendleft(self, iterable: Iterable[T]) -> None:
        """Extend the left end of the holodeque with an iterable.

        Args:
            iterable: An Iterable of elements to add to the
              holodeque from the left-hand side.
        """
        if isinstance(iterable, type(self)):
            self.mergeleft(iterable)
        else:
            for elem in iterable:
                self.pushleft(elem)

    def extendright(self, iterable: Iterable[T]) -> None:
        """Extend the right end of the holodeque with an iterable.

        Args:
            iterable: An Iterable of elements to add to the
              holodeque from the right-hand side.
        """
        if isinstance(iterable, type(self)):
            self.mergeright(iterable)
        else:
            for elem in iterable:
                self.pushright(elem)

    # TODO: ask GPT preview about this one
    def mergeleft(self, other: Self) -> None:
        """Concatenate another holodeque to the left end of this holodeque.

        Instead of adding elements from the other holodeque one at a time,
        this method performs a left multiplication of their base matrices.
        This implementation utilizes dynamic programming to update
        the columns of this holodeque's base matrix.

        Args:
            other: Another holodeque to be concatenated on the left side.
        """
        for i in range(self._shape):  # calculate col(i)
            line: list[int] = [0] * self._shape
            for j in range(self._shape):
                for k in range(self._shape):
                    line[j] += other._matrix[j][k] * self._matrix[k][i]
            for j in range(self._shape):  # update col(i)
                self._matrix[j][i] = line[j]
        self._size += other.size

    # TODO ask GPT preview about this too
    def mergeright(self, other: Self) -> None:
        """Concatenate another holodeque to the right end of this holodeque.

        Instead of adding elements from the other holodeque one at a time,
        this method performs a right multiplication of their base matrices.
        This implementation utilizes dynamic programming to update
        the rows of this holodeque's base matrix.

        Args:
            other: Another holodeque to be concatenated on the right side.
        """
        for i in range(self._shape):  # calculate row(i)
            line: list[int] = [0] * self._shape
            for j in range(self._shape):
                for k in range(self._shape):
                    line[j] += self._matrix[i][k] * other._matrix[k][j]
            for j in range(self._shape):  # update row(i)
                self._matrix[i][j] = line[j]
        self._size += other.size

    def clear(self) -> None:
        """Empties the holodeque.

        Resets the base matrix in-place into an identity matrix of the same shape.
        """
        if self._size:
            for i in range(self._shape):
                for j in range(self._shape):
                    self._matrix[i][j] = int(i == j)
            self._size = 0

    def __iter__(self) -> Iterator[T]:
        """Returns an iterator that can traverse a copy of the holodeque from left to right."""
        return HolodequeIterator[T](self, reverse=False)

    def __reversed__(self) -> Iterator[T]:
        """Returns an iterator that can traverse a copy of the holodeque from right to left."""
        return HolodequeIterator[T](self, reverse=True)

    def reverse(self) -> None:
        """Reverses the holodeque in-place."""
        reverse_iterator: Iterator[T] = reversed(self)
        self.clear()
        for element in reverse_iterator:
            self.pushright(element)

    def __contains__(self, element: T) -> bool:
        index: int = self._get_axis(element)
        return any(self._matrix[index][i] != int(index == i) for i in range(self._shape))

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
        try:
            while index < self._size:
                if self.peekleft() == element:
                    self.popleft()
                    return
                self.pushright(self.popleft())
                index += 1
            raise ValueError(f"{element} not in holodeque")
        finally:
            self.rotate(index)

    def copy(self: Self) -> Self:
        """Create and return a new holodeque with identical contents."""
        return self.__class__(iterable=self, maxlen=self._maxlen, **self._kwargs)

    def __len__(self) -> int:
        return self._size

    # TODO: make this wrap around too, and get rid of iter()
    def __getitem__(self, index: int) -> T:
        if index < 0:
            index += self._size
        if index < 0 or index >= self._size:
            raise IndexError("holodeque index out of range")
        iterator: Iterator[T] = iter(self)
        for _ in range(index):
            next(iterator)
        return next(iterator)

    def __setitem__(self, index: int, value: T) -> None:
        if index < 0:
            index += self._size
        if index < 0 or index >= self._size:
            raise IndexError("deque index out of range")
        if index > self._size // 2:
            index -= self._size
        if index >= 0:
            for _ in range(index):
                self.pushright(self.popleft())
            self.popleft()
            self.pushleft(value)
            for _ in range(index):
                self.pushleft(self.popright())
        else:
            index = -index - 1
            for _ in range(index):
                self.pushleft(self.popright())
            self.popright()
            self.pushright(value)
            for _ in range(index):
                self.pushright(self.popleft())

    # TODO make this wrap around
    def __delitem__(self, index: int) -> None:
        if index < 0:
            index = ~index
        if index >= self._size:
            raise IndexError("deque index out of range")
        i: int = 0
        try:
            for i in range(self._size):
                if i == index:
                    self.popleft()
                    return
                self.pushright(self.popleft())
        finally:
            self.rotate(i)

    def __repr__(self) -> str:
        return str(vars(self))

    def __str__(self) -> str:
        str_matrix: list[list[str]] = [
            [str(elem) for elem in row] for row in self._matrix]
        max_width: int = max(len(elem) for row in str_matrix for elem in row)
        formatted_rows: list[str] = [
            " ".join(f"{elem:>{max_width}}" for elem in row) for row in str_matrix]
        return "\n".join(formatted_rows)

    def __hash__(self):
        raise TypeError("Holodeque is unhashable")

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, type(self)):
            return list(self) == list(other)
        else:
            return NotImplemented

    def __ne__(self, other: Any) -> bool:
        if isinstance(other, type(self)):
            return list(self) != list(other)
        else:
            return NotImplemented

    def __lt__(self, other: Any) -> bool:
        if isinstance(other, type(self)):
            return list(self) < list(other)
        else:
            return NotImplemented

    def __le__(self, other: Any) -> bool:
        if isinstance(other, type(self)):
            return list(self) <= list(other)
        else:
            return NotImplemented

    def __gt__(self, other: Any) -> bool:
        if isinstance(other, type(self)):
            return list(self) > list(other)
        else:
            return NotImplemented

    def __ge__(self, other: Any) -> bool:
        if isinstance(other, type(self)):
            return list(self) >= list(other)
        else:
            return NotImplemented

    def __add__(self, matdeq: Self) -> Self:
        if isinstance(matdeq, type(self)):
            new_copy: Self = self.copy()
            new_copy.mergeright(matdeq)
            return new_copy
        return NotImplemented

    def __iadd__(self, matdeq: Self) -> Self:
        if isinstance(matdeq, type(self)):
            self.mergeright(matdeq)
            return self
        return NotImplemented

    def __sub__(self, matdeq: Self) -> Self:
        if isinstance(matdeq, type(self)):
            new_copy: Self = self.copy()
            new_copy.mergeleft(matdeq)
            return new_copy
        return NotImplemented

    def __isub__(self, matdeq: Self) -> Self:
        if isinstance(matdeq, type(self)):
            self.mergeleft(matdeq)
            return self
        return NotImplemented


class HolodequeIterator[U: Hashable]:
    """Iterator for traversing a holodeque.

    Yields each element from the holodeque by popping from a copy.

    Attributes:
        _holodeq: A destructable holodeque copy.
        _reverse: If True, yields elements from right to left; otherwise,
           yields elements from left to right.
    """

    def __init__(self, holodeq: HolodequeBase[U], reverse: bool = False):
        """Initializes the iterator for a holodeque.

        Args:
            holodeq: A holodeque to iterate over.
            reverse: A bool indicating the direction of iteration.
        """
        self._holodeq: HolodequeBase[U] = holodeq.copy()
        self._reverse: bool = reverse

    def __iter__(self) -> Iterator[U]:
        return self

    def __next__(self) -> U:
        if not self._holodeq.size:
            raise StopIteration
        return self._holodeq.popright() if self._reverse else self._holodeq.popleft()

        """
        while self._holodeq.size:
            if self._reverse:
                return self._holodeq.popright()
            else:
                return self._holodeq.popleft()
        raise StopIteration"""
