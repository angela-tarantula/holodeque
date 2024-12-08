This is documentation of my amateurish attempt at algorithm design.

# Introduction

The double-ended queue, or **deque**, is a crucial data structure that supports **pushing**, **popping**, **peeking**, and **concatenating** elements from either the front or back in $O(1)$ time. In its textbook implementation, a deque is a doubly-linked list where each node stores one datum and memory is managed dynamically. But in performance-critical sections of code, every microsecond and byte of memory counts. This design incurs a 200% memory overhead because there are two pointers for each node, and it can be slow because each operation requires calling malloc() or free() for memory management. Modern performant implementations improve upon this by using fixed-length blocks between links. This approach reduces the overhead ratio by packing more data between links, decreasing the frequency of malloc() and free() calls per operation, and taking advantage of data locality within blocks. While this optimization is highly efficient, I've conceived of a new approach rooted in linear algebra that leverages matrix multiplication as a core operation, aiming to rival modern deque implementations. I concocted this prototype and discovered that it’s *pretty good actually* but not *better than the best*.

# Background

My initial investigation was focused on the simplest case, where the deque only accepts 2 different objects.

## Using an Integer as a Bit Stack for Performance

One technique, which I’m not the first to discover, is to represent a simple stack of boolean values (bits) using a single integer. This way, instead of managing a dynamic data structure or relying on heap allocations, you can use native CPU instructions to push, pop, and peek bits at O(1) cost. This can lead to noticeable performance improvements, especially in tight loops or memory-constrained environments. 

### How It Works:

When the stack is empty, the integer is zero. We will assume the top of the stack is the least significant bit (LSB).

```
long long S = 0;
```

**Peek**: Reading the LSB with a simple bitwise AND operation.

```
return S & 1
```

**Push**: A left-shift and a bitwise OR operation.

```
S = (S << 1) | b
```

**Pop**: Reading the LSB and then right-shifting.

```
LSB = S & 1
S = S >> 1
return LSB
```

Bitwise implementations of the bit-queue and bit-deque can be designed similarly with a bit more ingenuity (pun intended). 

# Making it Generic

## Using a Matrix Instead of an Integer

Modern BLAS (**Basic Linear Algebra Subprograms**) libraries achieve matrix multiplication at remarkable speeds, often outpacing the traditional memory operations involved in deque management. Inspired by this efficiency, I designed a deque structure that uses matrix multiplication as the central operation for deque manipulation. In this model, each element in the deque corresponds to a unique matrix, and the deque’s state is represented by the product of these matrices in sequence.

For example, a deque containing elements [𝑎, 𝑏, 𝑐, 𝑏, 𝑎, 𝑏] corresponds to a matrix $M=ABCBAB$, where {𝑎: $A$, 𝑏: $B$, 𝑐: $C$}. This approach leverages the non-commutative nature of matrix multiplication, ensuring that different sequences produce distinct states – provided that matrices $A, B, C, \ldots$ are chosen carefully.

### Operations

In my model, deque operations like push, pop, and concatenate are represented as matrix multiplications, effectively shifting memory management responsibilities from malloc() and free() calls to efficient BLAS routines. Adding an element, 𝑐, to the right side is right-sided multiplication, $M'=M\times C$, and adding an element to the left is left-side multiplication, $M'=C\times M$. Removing elements corresponds to multiplying by the inverse matrix at the respective side, such as $M' = M \times B^{-1}$ to remove 𝑏 from the right side, or $M' = A^{-1} \times M$ to remove 𝑎 from the left side. Concatenation of two deques is a multiplication of their matrices, $M’ = J \times K$, where the multiplication order corresponds to the concatenation order.

In my model, peek is not a matrix multiplication, but rather a matrix decomposition that depends on how $A$, $B$, $C$, etc. are chosen. In this prototype, I chose [this pattern](#choosing-a-b-c-etc).

We access $A$, $B$, and $C$ from 𝑎, 𝑏, and 𝑐, respectively, by using a hashmap. If the number of distinct elements in the deque is known ahead of time, the hashmap conversion can be replaced with a hard-coded algorithm to save time.

As an added benefit, if we utilize the BLAS libraries and frameworks like Numpy or TensorFlow, all these operations will be thread-safe.

# About This Prototype

I titled this project “holodeque” as an homage to the holodeck in Star Trek. It’s a play on words but also fitting because they share this notion of encoding information with transformations.

### Organization

I chose an object-oriented design where BaseHolodeque is an abstract base class that is subclassed by holodeque, binarydeque, numpydeque, holodeque64, quickdeque, and polydeque.

- holodeque - The pure-python implementation of the holodeque concept that accepts a fixed set of input.
- binarydeque - A lightweight holodeque that only accepts a set of two input, but is faster.
- fexideque - A holodeque that can accept a mutable set of any number of input, but is slower.
- numpydeque - A holodeque that uses numpy arrays of 64-bit integers for the base matrix.

### Time Complexity

Let $N$ = the size of the deque, and $m$ = the number of elements in it. I devised an implementation with the following operations:

1. Push: $O(m^2)$
2. Pop: $O(m^2)$
3. Concatenate: $O(m^3)$
4. Peek: $O(m)$

This means when m << $N$, Each of these operations are $O(1)$ relative to the size of the deque.

### Limitations

1. The operations are only $O(1)$ when $m$ << $N$.
2. My model can only store immutable objects. Otherwise, the conversion of each object to a unique matrix would be unstable.
3. As was the case for the bit-stack integer, this model is susceptible to integer overflow. We could use arbitrary-precision integer libraries, or languages that provide this functionality out of the box, such as Python and Haskell, but this compromises performance.

### Trying It Yourself

You can read the documentation like this:

```
pydoc src/holodeque.py
```

You can import any of the modules in the `src` folder and give it a spin. For example, from the root you can try the following commands:

```
python3 # you need at least python 3.12
>>> from src.holodeque import holodeque
>>> deque = holodeque(alphabet={0,1,2,3,4,5,6,7,8,9}) # accepts digits 0-9
>>> for i in range(10):
...     if i % 2:
...         deque.pushleft(i)
...     else:
...         deque.pushright(i)
>>> print(deque)
holodeque([9, 7, 5, 3, 1, 0, 2, 4, 6, 8], alphabet=frozenset({0, 1, 2, 3, 4, 5, 6, 7, 8, 9}))
>>> from src.flexideque import flexideque
>>> deque = flexideque() # no prior specification of alphabet required
>>> from random import random
>>> for i in range(10):
...     deque.pushright(random()) # works
```

### Testing

I type hint all my code and use mypy to check it. If you have installed mypy, you can run the following command to verify this yourself:
```
pip3 install mypy
mypy src/
````
I also wrote 371 tests using unittest, pytest, and Hypothesis. If you have pytest, hypothesis, and numpy all installed, you can run the following command check attempt them:
```
pip3 install pytest hypothesis numpy
pytest
````
There is one more test which you can run like so:
```
pytest tests/Hypothesis/uniqueness.py
```
But it should take a whole hour to run. It exhaustively proves non-commutativity of the chosen matrices for deque size up to 10. It is not an actual proof for all deque sizes, but it is useful for debugging when I tinker with the chosen matrices, because the test will fail quickly if the matrices aren't commutative.

Each test file under ./tests/Hypothesis/ is titled in one of two formats:

 - **test_\<module\>_essentials.py**: A suite of test checking that the basic functionality works. The tests are strategically ordered so that the first failure reveals the exact error occurring. The tests use Hypothesis to make sure that general rules are followed, such as associativity of concatenation.
 - **test_\<module\>_secondary.py**: A suite of tests checking that secondary functionality works, such as magic methods and the maxlen parameter.

 There is one more test file ./tests/application/test_parentheses.py that basically runs the holodeque side by side against collections.deque to solve a basic leetcode problem (20. Valid Parentheses). If confirms that both deque implementations find the same answer.

### Future Work

- Switch to a low level language.
  - This will allow more accurate benchmarking.
  - Python doesn’t allow interfaces, but ideally the abstract base class is replaced with an interface when I switch to C++.
- Try making it thread-safe.
- Find another set of matrices that are all non-commutative with each other and test it against my first attempt.

### Choosing $A$, $B$, $C$, etc

I chose a simple, scalable pattern for this prototype. To demonstrate it, I will first give an example. Let $alphabet$ be the set of distinct objects that the holodeque accepts. When |$alphabet$| = $3$, then objects 𝑎, 𝑏, 𝑐 are represented by the following matrices:

```
{
𝑎: [[1,1,1],
    [0,1,0],
    [0,0,1]], 

𝑏: [[1,0,0],
    [1,1,1],
    [0,0,1]], 

𝑐: [[1,0,0],
    [0,1,0],
    [1,1,1]]
}
```

In the general case, when |alphabet| = $n$, each of the $n$ matrices are $n\times n$. They are all identity matrices in which a different, single row is replaced by a row filled with 1s.

This construction is convenient for many reasons:
1. The matrices can be constructed formulaically and do not need to be hard-coded
2. The pattern is scalable
3. Each matrix’s inverse can also be derived formulaically: simply negate all the 1s of the special row filled with 1s.
4. Left-multiplication can be reduced to a few row additions (try it)
5. Right-multiplication can be reduced to a few column additions (try it)
6. By using small numbers, each multiplication doesn’t grow the product by that much, which prolongs the stable period before integer overflow or cost-intensive arbitrary-precision operations.

I considered using floating point numbers, but floating point arithmetic errors are so frequent they compromise the reliability.

This construction also guarantees non-commutativity. I made a handwritten proof found *here* (TODO).