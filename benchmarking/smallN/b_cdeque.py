"""benchmarking binarydeque against collections.deque for small n"""

import timeit
import random
from collections import deque
from holodeque.src.binary_holodeque import binarydeque as bdeque

# Test size
small_size = 5

# Create test data (all 0s and 1s)
small_data = [0, 1] * (small_size // 2)
random.shuffle(small_data)
d, bd = deque(small_data), bdeque(small_data)


def test_operation(module_name, operation, deque_type):
    if operation == "append/pushright":
        if module_name == "deque":
            return timeit.timeit(lambda: (deque_type.append(1), deque_type.pop()), number=10_000)
        else:
            return timeit.timeit(lambda: (deque_type.pushright(1), deque_type.popright()), number=10_000)
    elif operation == "appendleft/pushleft":
        if module_name == "deque":
            return timeit.timeit(lambda: (deque_type.appendleft(1), deque_type.popleft()), number=10_000)
        else:
            return timeit.timeit(lambda: (deque_type.pushleft(1), deque_type.popleft()), number=10_000)
    elif operation == "pop/popright":
        if module_name == "deque":
            return timeit.timeit(lambda: (deque_type.pop(), deque_type.append(1)), number=10_000)
        else:
            return timeit.timeit(lambda: (deque_type.popright(), deque_type.pushright(1)), number=10_000)
    elif operation == "popleft":
        if module_name == "deque":
            return timeit.timeit(lambda: (deque_type.popleft(), deque_type.appendleft(1)), number=10_000)
        else:
            return timeit.timeit(lambda: (deque_type.popleft(), deque_type.pushleft(1)), number=10_000)


# Testing append/pushright on small data
print("Testing append/pushright on small data:")
print("deque:", test_operation("deque", "append/pushright", d))
print("bdeque:", test_operation("bdeque", "append/pushright", bd))

# Testing appendleft/pushleft on small data
print("Testing appendleft/pushleft on small data:")
print("deque:", test_operation("deque", "appendleft/pushleft", d))
print("bdeque:", test_operation("bdeque", "appendleft/pushleft", bd))

# Testing pop/popright on small data
print("Testing pop/popright on small data:")
print("deque:", test_operation("deque", "pop/popright", d))
print("bdeque:", test_operation("bdeque", "pop/popright", bd))

# Testing popleft on small data
print("Testing popleft on small data:")
print("deque:", test_operation("deque", "popleft", d))
print("bdeque:", test_operation("bdeque", "popleft", bd))
