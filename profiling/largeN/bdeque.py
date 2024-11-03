"""profiling binarydeque at large n"""

from src.binary_holodeque import binarydeque as bdeque

import cProfile
import pstats

bd = bdeque(x%2 for x in range(1_000_000))

def test_performance():
    # Example setup for testing performance of mdeque
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
