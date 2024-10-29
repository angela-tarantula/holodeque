"""profiling binarydeque at small n"""

import timeit
from holodeque.src.binary_holodeque import binarydeque as bdeque

import cProfile
import pstats


def test_performance():
    # Example setup for testing performance of mdeque
    bd = bdeque()
    for _ in range(1_000_000):  # Simulate a large number of operations
        bd.pushright(1)
        bd.pushleft(0)
        bd.popright()
        bd.popleft()


# Profile the function
cProfile.run('test_performance()', 'profile_results')

p = pstats.Stats('profile_results')
# Sort by cumulative time, print top 10 functions
p.strip_dirs().sort_stats('cumulative').print_stats(10)
