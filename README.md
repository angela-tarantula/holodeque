# Holodeque: A Novel Deque Implementation Using Matrix Multiplication

## Table of Contents

1. [Overview](#overview)
2. [Background and Motivation](#background-and-motivation)
3. [Bitwise Stack and Queue Foundations](#bitwise-stack-and-queue-foundations)
4. [Matrix-Based Deque Implementation](#matrix-based-deque-implementation)
   - [Core Idea](#core-idea)
   - [Operations](#operations)
   - [Time Complexity](#time-complexity)
   - [Limitations](#limitations)
5. [Getting Started](#getting-started)
   - [Installation](#installation)
   - [Quickstart Examples](#quickstart-examples)
6. [Testing and Verification](#testing-and-verification)
7. [Future Work](#future-work)
8. [Choosing the Matrices](#choosing-the-matrices)
9. [Acknowledgments](#acknowledgments)

## Overview

**Holodeque** is a prototype of a double-ended queue (deque) implementation that explores unconventional territory: replacing traditional pointer-based linking or block-based arrays with matrix multiplication operations. Inspired by the speed of modern BLAS (Basic Linear Algebra Subprograms) libraries, this approach encodes the deque state as a product of matrices, where each element corresponds to a matrix factor. While this concept is more of a theoretical exploration than a direct competitor to highly optimized, state-of-the-art deque implementations, the prototype showcases how linear algebra techniques might open new avenues for data structure design.

## Background and Motivation

A traditional deque supports operations like pushing, popping, peeking, and concatenation from both ends in constant time. However, linked-list-based implementations incur memory overhead (two pointers per element) and frequent dynamic allocations, while block-based implementations still must manage memory at a finer granularity. In performance-critical applications, reducing overhead and improving speed is essential.

Modern solutions pack multiple elements per allocation block, reducing overhead and improving cache locality. Here, I approach efficiency from a new angle: by mapping elements to matrices and representing deque operations with matrix multiplication, I’m leveraging highly optimized linear algebra routines, potentially improving performance in certain specialized contexts.

## Bitwise Stack and Queue Foundations

Before diving into the matrix-based approach, a simpler optimization sets the stage: using a single integer as a bit stack. This compact representation allows O(1) push, pop, and peek without heap allocations:
- **Peek**: `return S & 1`
- **Push**: `S = (S << 1) | b`
- **Pop**: `LSB = S & 1; S = S >> 1; return LSB`

Similar principles can be extended to bit-queues and bit-deques, providing a baseline of how low-level tricks can yield performance benefits.

## Matrix-Based Deque Implementation

### Core Idea

Instead of pointers or arrays, each deque element (e.g., `a`, `b`, `c`) is represented by a corresponding matrix (`A`, `B`, `C`). The entire deque’s state is the product of these matrices. For example, `[a, b, c, b, a, b]` corresponds to `M = A B C B A B`. Non-commutative matrix multiplication ensures that distinct sequences produce unique results, assuming carefully chosen matrices.

### Operations

- **pushright**: `M' = M × C`
- **pushleft**: `M' = A × M`
- **popright**: `M' = M × B⁻¹`
- **popleft**: `M' = A⁻¹ × M`
- **concatright**: `M' = M × W`
- **concatleft**: `M' = W × M`

Peeking involves a form of factorization to identify the element at an end. This depends on the chosen matrix set.

### Time Complexity

Let `m` be the number of distinct elements in the deque. Operations scale as follows:
- **Push/Pop**: O(m²)
- **Concatenate**: O(m³)
- **Peek**: O(m)

When `m` is significantly smaller than the deque size `N`, these operations are effectively O(1) relative to `N`.

### Limitations

1. Operations are only effectively O(1) when `m << N`.
2. Only immutable objects are supported, as each object’s corresponding matrix must remain stable.
3. Potential for integer overflow exists; using arbitrary-precision arithmetic trades performance for correctness.

## Getting Started

### Installation

1. Ensure Python 3.12 or later is installed.
2. Clone the repository.
3. Optionally, install dependencies for testing and linear algebra backends:

```
pip3 install mypy pytest hypothesis numpy
```

### Quickstart Examples

View documentation:

```
pydoc src/holodeque.py
```

Basic usage:

```
python3
>>> from src.holodeque import holodeque
>>> deque = holodeque(alphabet={0,1,2,3,4,5,6,7,8,9}) # accepts digits 0-9
>>> for i in range(10):
...     if i % 2:
...         deque.pushleft(i)
...     else:
...         deque.pushright(i)
>>> print(deque)
holodeque([9, 7, 5, 3, 1, 0, 2, 4, 6, 8], alphabet=frozenset({0, 1, 2, 3, 4, 5, 6, 7, 8, 9}))
```

Flexible alphabet:

```
python3
>>> from src.flexideque import flexideque
>>> deque = flexideque() # no prior specification of alphabet required
>>> from random import random
>>> for i in range(10):
...     deque.pushright(random())
```

## Testing and Verification

Type checking with `mypy`:

```
mypy src/
```

Run all tests (requires `pytest`, `hypothesis`, and `numpy`):

```
pytest
```

A special one-hour test to verify non-commutativity:

```
pytest tests/Hypothesis/uniqueness.py
```

I provide over 370 tests, including exhaustive hypothesis-driven checks and a side-by-side comparison with `collections.deque` to confirm correctness on standard tasks (e.g., the “Valid Parentheses” LeetCode problem).

## Future Work

- **Low-Level Implementation**: Porting to C++ or Rust for tighter benchmarking and potentially higher performance.
- **Thread-Safety**: Leveraging BLAS routines that are thread-safe for parallel deque operations.
- **Alternative Matrices**: Experimenting with different matrix constructions to ensure non-commutativity and potentially improve performance.

## Choosing the Matrices

For `|alphabet| = n`, each element’s matrix is an `n × n` identity matrix with a single row replaced by all ones. This construction:

1. Scales easily with `n`.
2. Guarantees non-commutativity.
3. Minimizes integer growth to reduce overflow risk.
4. Taking the inverse of these matrices is as simple as negating the row filled with ones.
5. Enables fast push, peek, and pop operations. Check the code for specific shortcuts it allows.


## Acknowledgments

The name “holodeque” is a nod to the Star Trek holodeck, symbolizing the encoding of complex states within transformations.