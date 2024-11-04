"""benchmarking binarydeque against collections.deque for large n"""

import timeit
from collections import deque

from src.binary_holodeque import binarydeque as bdeque

# Test size
large_size = 1_000_000

# Create test data (all 0s and 1s)
large_data = [0, 1] * (large_size // 2)
d, bd = deque(large_data), bdeque(large_data)


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


# Testing append/pushright on large data
print("Testing append/pushright on large data:")
print("deque:", test_operation("deque", "append/pushright", d))
print("bdeque:", test_operation("bdeque", "append/pushright", bd))

# Testing appendleft/pushleft on large data
print("Testing appendleft/pushleft on large data:")
print("deque:", test_operation("deque", "appendleft/pushleft", d))
print("bdeque:", test_operation("bdeque", "appendleft/pushleft", bd))

# Testing pop/popright on large data
print("Testing pop/popright on large data:")
print("deque:", test_operation("deque", "pop/popright", d))
print("bdeque:", test_operation("bdeque", "pop/popright", bd))

# Testing popleft on large data
print("Testing popleft on large data:")
print("deque:", test_operation("deque", "popleft", d))
print("bdeque:", test_operation("bdeque", "popleft", bd))
