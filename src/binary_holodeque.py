"""A binary holodeque implementation."""

from typing import Iterable, Optional, Self, override

from src.base_holodeque import BaseHolodeque, Matrix


class binarydeque(BaseHolodeque[int, bool]):
    """A holodeque that only accepts 0 and 1.

    Attributes:
        _matrix: A square matrix representing the state of the holodeque.
        _shape: The dimension of the base matrix (its width and height).
        _size: The current number of elements in the holodeque.
        _maxlen: The maximum allowed size of the holodeque; None if unbounded.
    """

    @override
    def __init__(self, iterable: Iterable[bool] = (), *, maxlen: Optional[int] = None) -> None:
        """Initializes a holodeque with the provided iterable.

        Args:
            iterable: An Iterable of elements to populate the holodeque.
            maxlen: Optional maximum size of the holodeque; if not None, restricts
                    the number of elements.
        """
        super().__init__(maxlen=maxlen)
        self._matrix: Matrix[int] = [[1, 0], [0, 1]]
        self.extendright(iterable)
        
    @override
    def pushleft(self, index: bool) -> None:
        if self._size == self._maxlen:
            self._handle_overflow(from_left=True)
        self._matrix[index][0] += self._matrix[1-index][0]
        self._matrix[index][1] += self._matrix[1-index][1]
        self._size += 1
    
    @override
    def pushright(self, index: bool) -> None:
        if self._size == self._maxlen:
            self._handle_overflow(from_left=False)
        self._matrix[0][1-index] += self._matrix[0][index]
        self._matrix[1][1-index] += self._matrix[1][index]
        self._size += 1
    
    @override
    def peekleft(self) -> bool:
        if not self._size:
            raise IndexError("peek from an empty holodeque")
        return self._matrix[1][1] > self._matrix[0][1]
    
    @override
    def peekright(self) -> bool:
        if not self._size:
            raise IndexError("peek from an empty holodeque")
        return (self._matrix[0][0] > self._matrix[0][1] >= self._matrix[1][1]
                or self._matrix[1][0] >= self._matrix[1][1] > self._matrix[0][1])
    
    @override
    def popleft(self) -> bool:
        if not self._size:
            raise IndexError("pop from an empty holodeque")
        index: bool = self.peekleft()
        self._matrix[index][0] -= self._matrix[1-index][0]
        self._matrix[index][1] -= self._matrix[1-index][1]
        self._size -= 1
        return index
    
    @override
    def popright(self) -> bool:
        if not self._size:
            raise IndexError("pop from an empty holodeque")
        index: bool = self.peekright()
        self._matrix[0][1-index] -= self._matrix[0][index]
        self._matrix[1][1-index] -= self._matrix[1][index]
        self._size -= 1
        return index
    
    @override
    def concatleft(self, other: Self) -> None:
        if self._maxlen is not None and self._size + other._size > self._maxlen:
            raise ValueError(
                "incompatible holodeque because it would exceed maximum length")
        if self is other:
            other = self.copy()
        self._matrix[0][0], self._matrix[1][0] = (
            (
                (other._matrix[0][0] * self._matrix[0][0])
                + (other._matrix[0][1] * self._matrix[1][0])
            ),
            (
                (other._matrix[1][0] * self._matrix[0][0])
                + (other._matrix[1][1] * self._matrix[1][0])
            )
        )
        self._matrix[0][1], self._matrix[1][1] = (
            (
                (other._matrix[0][0] * self._matrix[0][1])
                + (other._matrix[0][1] * self._matrix[1][1])
            ),
            (
                (other._matrix[1][0] * self._matrix[0][1])
                + (other._matrix[1][1] * self._matrix[1][1])
            )
        )
        self._size += other.size
    
    @override
    def concatright(self, other: Self) -> None:
        if self._maxlen is not None and self._size + other._size > self._maxlen:
            raise ValueError(
                "incompatible holodeque because it would exceed maximum length")
        if self is other:
            other = self.copy()
        self._matrix[0][0], self._matrix[0][1] = (
            (
                (self._matrix[0][0] * other._matrix[0][0])
                + (self._matrix[0][1] * other._matrix[1][0])
            ),
            (
                (self._matrix[0][0] * other._matrix[0][1])
                + (self._matrix[0][1] * other._matrix[1][1])
            )
        )
        self._matrix[1][0], self._matrix[1][1] = (
            (
                (self._matrix[1][0] * other._matrix[0][0])
                + (self._matrix[1][1] * other._matrix[1][0])
            ),
            (
                (self._matrix[1][0] * other._matrix[0][1])
                + (self._matrix[1][1] * other._matrix[1][1])
            )
        )
        self._size += other._size
        
    @override
    def clear(self) -> None:
        if self._size:
            self._matrix[0][0] = self._matrix[1][1] = 1
            self._matrix[0][1] = self._matrix[1][0] = 0
            self._size = 0
 
    @override
    def reverse(self) -> None:
        self._matrix[0][0], self._matrix[1][1] = self._matrix[1][1], self._matrix[0][0]
        
    @override
    def __contains__(self, index: bool) -> bool:
        return bool(self._matrix[index][1-index])

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
    ext = [False, False, False, False, True, True, False]
    q.extendright(ext)
    t.extendleft(ext)
    assert list(q) == list(reversed(t))
    assert list(t) == list(reversed(q))
