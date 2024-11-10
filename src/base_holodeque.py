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
            iterable: An Iterable of elements to populate the holodeque.
            maxlen: Optional maximum size of the holodeque; if not None, restricts
                    the number of elements.
            kwargs: Additional keyword arguments for use by subclasses.

        Raises:
            ValueError: If maxlen is negative.
        """
        if maxlen is not None and maxlen < 0:
            raise ValueError("maxlen must be non-negative")
        self._matrix: Matrix[NL]
        self._shape = 2
        self._alphabet: Set[T] = set()
        self._size: int = 0
        self._maxlen: Optional[int] = maxlen
        self._kwargs = kwargs

    @property
    def size(self) -> int:
        """The current number of elements in the holodeque."""
        return self._size

    @property
    def maxlen(self) -> Optional[int]:
        """The maximum size of the holodeque."""
        return self._maxlen

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

    @abstractmethod
    def pushleft(self, element: T) -> None:
        """Add an element to the left end of the holodeque.

        Args:
            element: The element to be added to the left side of the holodeque.

        Raises:
            TypeError: If the element has an invalid type.
            ValueError: If the element has an invalid value.
        """

    @abstractmethod
    def pushright(self, element: T) -> None:
        """Add an element to the right end of the holodeque.

        Args:
            element: The element to be added to the right side of the holodeque.

        Raises:
            TypeError: If the element has an invalid type.
            ValueError: If the element has an invalid value.
        """

    @abstractmethod
    def peekleft(self) -> T:
        """Peek the leftmost element in the holodeque.

        Returns:
            The leftmost element in the holodeque.

        Raises:
            IndexError: If the holodeque is empty when attempting to peek.
        """

    @abstractmethod
    def peekright(self) -> T:
        """Peek the rightmost element in the holodeque.

        Returns:
            The rightmost element in the holodeque.

        Raises:
            IndexError: If the holodeque is empty when attempting to peek.
        """

    @abstractmethod
    def popleft(self) -> T:
        """Remove and return the leftmost element in the holodeque.

        Returns:
            The leftmost element in the holodeque.

        Raises:
            IndexError: If the holodeque is empty when attempting to pop.
        """

    @abstractmethod
    def popright(self) -> T:
        """Remove and return the rightmost element in the holodeque.

        Returns:
            The rightmost element in the holodeque.

        Raises:
            IndexError: If the holodeque is empty when attempting to pop.
        """

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
            ValueError: If the other holodeque's alphabet doesn't match,
                or if concatenation would exceed maxlen.
        """

    @abstractmethod
    def concatright(self, other: Self) -> None:
        """Concatenate another holodeque to the right end of this holodeque.

        Performs in-place right multiplication of their base matrices.

        Args:
            other: Another holodeque to be concatenated on the right side.

        Raises:
            ValueError: If the other holodeque's alphabet doesn't match,
                or if concatenation would exceed maxlen.
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

    @abstractmethod
    def __contains__(self, element: T) -> bool:
        ...

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
        if not isinstance(other, type(self)):
            raise NotImplementedError
        new_copy: Self = self.copy()
        new_copy.concatright(other)
        return new_copy

    def __radd__(self, other: Self) -> Self:
        if not isinstance(other, type(self)):
            raise NotImplementedError
        new_copy: Self = self.copy()
        new_copy.concatright(other)
        return new_copy

    def __iadd__(self, other: Self) -> Self:
        if not isinstance(other, type(self)):
            raise NotImplementedError
        self.concatright(other)
        return self

    def __mul__(self, multiple: int) -> Self:
        if not isinstance(multiple, int):
            raise NotImplementedError
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
        if not isinstance(multiple, int):
            raise NotImplementedError
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
