# holodeque

A holodeque is an implementation of a deque with a maxtrix called the base matrix. An empty holodeque is represented with an identity matrix. Pushing to the left corresponds to left multiplication. Pushing to the right corresponds to right multiplication. Popping from the left corresponds to left multiplication with an inverse. Popping from the right corresponds to right multiplication with an inverse. Peeking from either side involves inspecting the base matrix.

Let the size of the holodeque be n. Let the alphabet of input it accepts be A, and let the size of the alphabet be m = |A|. Then the shape of the base matrix will be mxm, hence the SC is O(m^2). The TC of all holodeque operations is O(m). Therefore, the holodeque is only truly a deque with O(1) operations when m << n. This is the main limitation of the holodeque.

The advantage of the holodeque is that all push/pop/peek operations are performed by the ALU, which avoids the overhead of allocating and deallocating memory. So it turns out that the holodeque outperforms the traditional linked list implementation of the deque when m and n are sufficiently small. The open question that I'm experimenting is what sizes of m and n outperform linked list implementations. It would be great if, for most use-cases where m << n, m and n are sufficiently small, such that this novel implementation is advantageous.

The following is a detailed explanation of how the main operations work. It will assume that m = 4, but it generalizes. Let A = {0, 1, 2, 3}.

The base matrix:

It starts out as the 4x4 identity matrix.

			[1, 0, 0, 0]
	       M = I4 = [0, 1, 0, 0]
		   	[0, 0, 1, 0]
			[0, 0, 0, 1]

The input matrices:

Each input has a corresponding input matrix, assigned arbitrarily, but following this pattern:

     [1, 1, 1, 1]       [1, 0, 0, 0]       [1, 0, 0, 0]       [1, 0, 0, 0]
 0 = [0, 1, 0, 0]   1 = [1, 1, 1, 1]   2 = [0, 1, 0, 0]   3 = [0, 1, 0 ,0]
     [0, 0, 1, 0]       [0, 0, 1, 0]       [1, 1, 1, 1]       [0, 0, 1, 0]
     [0, 0, 0, 0]       [0, 0, 0, 0]       [0, 0, 0, 0]       [1, 1, 1, 1]

Their inverses are also inportant and follow a simple pattern:

    [1, -1, -1, -1]     [ 1, 0,  0,  0]     [ 1,  0, 0,  0]     [ 1,  0,  0, 0]
0 = [0,  1,  0,  0] 1 = [-1, 1, -1, -1] 2 = [ 0,  1, 0,  0] 3 = [ 0,  1,  0, 0]
    [0,  0,  1,  0]     [ 0, 0,  1,  0]     [-1, -1, 1, -1]     [ 0,  0,  1, 0]
    [0,  0,  0,  0]     [ 0, 0,  0,  0]     [ 0,  0, 0,  0]     [-1, -1, -1, 1]

Any time we want to push an element onto the holodeque, we simply multiply the base matrix with the element's input matrix. Matrix multiplication is not commutative, so multiplying on the left and right will typically result in different products. Thus, to push the element left, perform a left multiplication (E x M). To push the element right, perform a right multiplication (M x E).

Any time we want to pop an element from the holodeque, we first peek at the element at that end, then multiply by that the inverse of that element's input matrix. For example, let's say we want to pop left. First we peek left and get that element's input matrix, E. Then we do left multiplication with E's inverse (E^-1 x M). If we were popping from the right, it would have been M x E^-1.

Peeking is performed differently depending on the direction. To peek left, we look at the last column of the base matrix and find the maximum value in it. Next, find the index of the first row containing that maximum. This index is the index that was all 1s in the leftmost matrix, and essentially tells you the leftmost element. To peek right, we first get the index from the second step of peeking left. If the size of the holodeque is 1, then this index tells us the rightmost element. Otherwise, we look at the row at that index, and find the minimum value of it. The row should have only one minimum, and the index of the column containing that minimum is the index that was all 1s in the rightmost matrix, and essentially tells you the rightmost element.

The proof of why this all works is found in proof.txt.
