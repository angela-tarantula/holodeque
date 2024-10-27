# Holodeque

A **holodeque** is an implementation of a deque using a matrix called the **base matrix**. An empty holodeque is represented by an identity matrix. The operations on the holodeque are defined as follows:

- **Pushing to the left** corresponds to left multiplication.
- **Pushing to the right** corresponds to right multiplication.
- **Popping from the left** corresponds to left multiplication with an inverse.
- **Popping from the right** corresponds to right multiplication with an inverse.
- **Peeking from either side** involves inspecting the base matrix.

### Complexity Analysis

Let \( n \) be the size of the holodeque and \( A \) be the alphabet of input it accepts, where the size of the alphabet is \( m = |A| \). The shape of the base matrix will be \( m \times m \), hence the space complexity (SC) is \( O(m^2) \). The time complexity (TC) of all holodeque operations is \( O(m) \). Therefore, the holodeque is only truly a deque with \( O(1) \) operations when \( m << n \). This is the main limitation of the holodeque.

### Advantages

The advantage of the holodeque is that all push, pop, and peek operations are performed by the ALU, which avoids the overhead of allocating and deallocating memory. As a result, the holodeque outperforms the traditional linked list implementation of the deque when both \( m \) and \( n \) are sufficiently small. 

An open question for experimentation is determining the sizes of \( m \) and \( n \) that outperform linked list implementations. It would be ideal for most use cases, where \( m << n \), that both \( m \) and \( n \) are small enough to make this novel implementation advantageous.

### Detailed Explanation of Operations

The following is a detailed explanation of how the main operations work. It will assume that \( m = 4 \), but the principles generalize. Let \( A = \{0, 1, 2, 3\} \).

#### Base Matrix

The base matrix starts out as the \( 4 \times 4 \) identity matrix:

\[
M = I_4 = \begin{bmatrix}
1 & 0 & 0 & 0 \\
0 & 1 & 0 & 0 \\
0 & 0 & 1 & 0 \\
0 & 0 & 0 & 1
\end{bmatrix}
\]

#### Input Matrices

Each input has a corresponding input matrix, assigned arbitrarily, but following this pattern:

\[
\begin{align*}
0 & = \begin{bmatrix}
1 & 1 & 1 & 1 \\
0 & 1 & 0 & 0 \\
0 & 0 & 1 & 0 \\
0 & 0 & 0 & 0
\end{bmatrix} \\
1 & = \begin{bmatrix}
1 & 0 & 0 & 0 \\
1 & 1 & 1 & 1 \\
0 & 0 & 1 & 0 \\
0 & 0 & 0 & 0
\end{bmatrix} \\
2 & = \begin{bmatrix}
1 & 0 & 0 & 0 \\
0 & 1 & 0 & 0 \\
1 & 1 & 1 & 1 \\
0 & 0 & 1 & 0
\end{bmatrix} \\
3 & = \begin{bmatrix}
1 & 0 & 0 & 0 \\
0 & 1 & 0 & 0 \\
0 & 0 & 1 & 0 \\
1 & 1 & 1 & 1
\end{bmatrix}
\end{align*}
\]

Their inverses are also important and follow a simple pattern:

\[
\begin{align*}
0 & = \begin{bmatrix}
1 & -1 & -1 & -1 \\
0 & 1 & 0 & 0 \\
0 & 0 & 1 & 0 \\
0 & 0 & 0 & 0
\end{bmatrix} \\
1 & = \begin{bmatrix}
1 & 0 & 0 & 0 \\
-1 & 1 & -1 & -1 \\
0 & 0 & 1 & 0 \\
0 & 0 & 0 & 0
\end{bmatrix} \\
2 & = \begin{bmatrix}
1 & 0 & 0 & 0 \\
0 & 0 & 1 & 0 \\
-1 & -1 & 1 & -1 \\
0 & 0 & 0 & 0
\end{bmatrix} \\
3 & = \begin{bmatrix}
1 & 0 & 0 & 0 \\
0 & 0 & 1 & 0 \\
0 & 0 & 0 & 0 \\
-1 & -1 & -1 & 1
\end{bmatrix}
\end{align*}
\]

### Pushing and Popping

- **Pushing an Element**: To push an element onto the holodeque, multiply the base matrix with the element's input matrix. Matrix multiplication is not commutative, so multiplying on the left and right will generally yield different results. 

  - To push the element left: \( E \times M \) (left multiplication).
  - To push the element right: \( M \times E \) (right multiplication).

- **Popping an Element**: To pop an element from the holodeque, first peek at the element at that end, then multiply by the inverse of that element's input matrix. For example, to pop left:
  1. Peek left to obtain the element's input matrix, \( E \).
  2. Perform left multiplication with \( E^{-1} \): \( E^{-1} \times M \).

  If popping from the right, it would be \( M \times E^{-1} \).

### Peeking

Peeking is performed differently depending on the direction:

- **Peek Left**: Look at the last column of the base matrix and find the maximum value. The index of the first row containing that maximum indicates the leftmost element.

- **Peek Right**: 
  1. Use the index obtained from peeking left.
  2. If the size of the holodeque is 1, this index indicates the rightmost element.
  3. Otherwise, check the row at that index to find the minimum value. The index of the column containing that minimum indicates the rightmost element.

### Proof

The proof of why this implementation works can be found in `proof.txt`.

