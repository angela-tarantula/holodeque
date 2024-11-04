"""profiling a lightweight binarydeque implementation at small n"""

import cProfile
import pstats


class ezdeque:

    def __init__(self):
        self.topleft = 1000000000
        self.topright = 100000000
        self.bottomleft = 100000000
        self.bottomright = 1000000000

    def pushleft(self, val):
        if val:
            self.bottomleft += self.topleft
            self.bottomright += self.topright
        else:
            self.topleft += self.bottomleft
            self.topright += self.bottomright

    def pushright(self, val):
        if val:
            self.topleft += self.topright
            self.bottomleft += self.bottomright
        else:
            self.topright += self.topleft
            self.bottomright += self.bottomleft

    def popleft(self):
        if self.topleft >= self.bottomleft:
            self.topleft -= self.bottomleft
            self.topright -= self.bottomright
            return 1
        else:
            self.bottomleft -= self.topleft
            self.bottomright -= self.topright
            return 0

    def popright(self):
        if self.topleft <= self.topright:
            self.topright -= self.topleft
            self.bottomright -= self.bottomleft
            return 0
        else:
            self.topleft -= self.topright
            self.bottomleft -= self.bottomright
            return 1


def test_performance():
    # Example setup for testing performance of mdeque
    ezd = ezdeque()
    for _ in range(1_000_000):  # Simulate a large number of operations
        ezd.pushright(1)
        ezd.pushleft(0)
        ezd.popright()
        ezd.popleft()


# Profile the function
cProfile.run('test_performance()', 'profile_results')

p = pstats.Stats('profile_results')
# Sort by cumulative time, print top 10 functions
p.strip_dirs().sort_stats('cumulative').print_stats(10)
