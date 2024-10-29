"""profiling list at small n"""

import cProfile
import pstats


def test_performance():
    # Example setup for testing performance of mdeque
    l = []
    for _ in range(1_000_000):  # Simulate a large number of operations
        l.append(1)
        l.insert(0, 0)
        l.pop(0)
        l.pop()


# Profile the function
cProfile.run('test_performance()', 'profile_results')

p = pstats.Stats('profile_results')
# Sort by cumulative time, print top 10 functions
p.strip_dirs().sort_stats('cumulative').print_stats(10)
