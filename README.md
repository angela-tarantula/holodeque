# holodeque.py

### Introduction

The double-ended queue, or **deque**, is a crucial data structure that supports adding (**pushing**) and removing (**popping**) elements from either the front or back in $O(1)$ time. In its textbook implementation, a deque is a doubly-linked list where each node stores one datum and memory is managed dynamically. However, this design incurs a 200% memory overhead (two pointers for each node) and can be slow because each operation requires calling malloc() or free() for memory management.  Modern performant implementations improve upon this by using fixed-length blocks between links. This approach reduces the overhead ratio by packing more data between links, decreasing the frequency of malloc() and free() calls per operation, and taking advantage of data locality within blocks. While this optimization is highly efficient, I've conceived of a new approach rooted in linear algebra that leverages matrix multiplication as a core operation, aiming to rival or even outperform traditional deque implementations.

### Matrix-Multiplication-Based Deque

Modern BLAS (**Basic Linear Algebra Subprograms**) libraries achieve matrix multiplication at remarkable speeds, often outpacing the traditional memory operations involved in deque management. Inspired by this efficiency, I designed a deque structure that uses matrix multiplication as the central operation for deque manipulation. In this model, each element in the deque corresponds to a unique matrix, and the deque’s state is represented by the product of these matrices in sequence.

For example, a deque containing elements [𝑎, 𝑏, 𝑐, 𝑏, 𝑎, 𝑏] corresponds to a matrix $M=ABCBAB$, where each letter represents a unique matrix for that element, multiplied in the order of the deque. This approach leverages the non-commutative nature of matrix multiplication, ensuring that different sequences produce distinct states – provided that matrices $A, B, C, \ldots$ are chosen carefully (discussion *here* TODO).

### Operations

In my model, deque operations like push, pop, and **concatenate** are represented as matrix multiplications, effectively shifting memory management responsibilities from malloc() and free() calls to efficient BLAS routines. Adding an element to the right side is right-sided multiplication, $M'=M\times C$, and adding an element to the left is left-side multiplication, $M'=C\times M$. Removing elements corresponds to multiplying by the inverse matrix at the respective side, such as $M' = M \times B^{-1}$ to remove 𝑏 from the right side, or $M' = A^{-1} \times M$ to remove 𝑎 from the left side. Concatenation of two deques is a multiplication of their matrices, $M’ = J \times K$, where the multiplication order corresponds to the concatenation order.

There is one more central operation of a deque, called **peek**, which returns the element at either specified end of the deque without removing it. In my model, peek is not a matrix multiplication, but rather a matrix decomposition (discussion *here* TODO).

### Time + Space Complexity

I found a way to construct matrices such that a deque of size $N$ with $m$ elements has the following operation time complexities:

1. Push: $O(m^2)$
2. Pop: $O(m^2)$
3. Concatenate: $O(m^3)$
4. Peek: $O(m)$

This means when m << $N$, Each of these operations are $O(1)$ relative to the size of the deque.

The space complexity of my model is $O(m^2)$.

### Limitations

1. The operations are only $O(1)$ when $m$ << $N$.
2. Arithmetic operations are only truly $O(1)$ for fixed-width integers, but in my model, the integers in the matrix grow unbounded. Therefore, whether or not my model constitutes an $O(1)$ deque [depends on the model of computational complexity you use](https://stackoverflow.com/questions/78959192/time-complexity-of-this-dynamic-programming-algorithm-to-get-nth-fibonacci-numbe). I derive *here* (TODO) that the bitsize of the integers grows linearly with deque size by a factor of $\log_{2}{\phi}$, which means large-scale usage of my model is limited. However, there are many times when asymptotically-dominant models are weighed down by constants enough such that other models are preferred. I hope to find that the fast speed of arithmetic on modern machines can outpace malloc() and free() for meaningful deque sizes. This prototype is written in Python as a proof of concept, but to truly benchmark the performance, I will need to implement this in a lower-level language like C++ or Rust.
3. My model can only store immutable objects. This is because the matrix representation of the deque is a product of matrices, and the matrices are not changed once they are created.
4. My model is not thread-safe. This is because the matrix representation of the deque is not atomic, and multiple threads could modify it simultaneously. This can be different in another language though, or with more work on this one.

### About This Prototype

I chose an object-oriented design where BaseHolodeque is an abstract base class that is subclassed by holodeque, binarydeque, numpydeque, holodeque64, quickdeque, and polydeque.

holodeque - The main implementation of the holodeque. It uses Python's built-in list data structure to store the matrices.
binarydeque - A lightweight holodeque that stores only two different objects but is faster.
numpydeque - A holodeque that uses numpy arrays instead of Python lists to store the matrices. It utilizes BLAS routines for matrix multiplication, so in theory it's faster, but in practice the matrices are small enough that the overhead of numpy objects is not worth it.
holodeque64 - A holodeque that uses 64-bit integers instead of Python's arbitrary-precision integers. This is faster, but it limits the deque size.
quickdeque - A holodeque that manually implements explicit SIMD instructions. It also experiments with a few shortcuts to speed up matrix multiplication.
polydeque - Instead of a holodeque of size $m\times m$, it uses $m$ binarydeques. 

I type hint all my code and use mypy to check it. I also use unittest, pytest, and Hypothesis to test it.

The name “holodeque” is inspired by the holodeck in Star Trek. It’s a play on words but also fitting they share this notion of encoding information with transformations.

### Future Work

Warning: written hastily: I need to write a C++ implementation of this to truly benchmark the performance. I would also like to write a Rust implementation to see if it's faster. In C++ I want to switch from using abstract base class to an interface. There are probably other data structures which can be remodeled as matrix transformations. I also want to explore all the different ways to parallelize my code. I also want to try making it thread-safe.


### Notes to Self

try using fixed blocks but blocks are matrices instead of arrays

factors to consider when choosing matrices a b and c
use Integers bc floats imprecise
Small or it overflows quickly
Generalizable so it's scalable
invertible so pop can work
peekable - need to be able to decompose the matrix quickly just by knowing the size and possible factors