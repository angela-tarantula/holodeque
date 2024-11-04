"""profiling collections.deque at small n"""
import cProfile
import pstats
from collections import deque


def test_performance():
    # Example setup for testing performance of mdeque
    d = deque()
    for _ in range(1_000_000):  # Simulate a large number of operations
        d.append(1)
        d.appendleft(0)
        d.pop()
        d.popleft()


# Profile the function
cProfile.run('test_performance()', 'profile_results')

p = pstats.Stats('profile_results')
# Sort by cumulative time, print top 10 functions
p.strip_dirs().sort_stats('cumulative').print_stats(10)
