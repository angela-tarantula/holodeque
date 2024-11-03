from src.holodeque import holodeque
from hypothesis import given, settings, strategies as st
from itertools import permutations
from functools import reduce
from collections import Counter
from math import factorial

alphabet_strategy = st.sets(
    st.one_of(
        st.integers(),
        st.floats(allow_infinity=False, allow_nan=False),
        st.booleans(),
        st.text()
    ),
    min_size=2,
    max_size=10
)


@st.composite
def alphabet_and_initial_list_strategy_small_version(draw):
    alphabet = draw(alphabet_strategy)
    lst = draw(st.lists(st.sampled_from(
        list(alphabet)), min_size=2, max_size=10))
    return alphabet, lst


# takes 1 hour (3717.04s) but confirms uniqueness up to 10 (11+ can be proven mathematically)
@settings(deadline=None)
@given(alphabet_and_initial_list_strategy_small_version())
def test_all_permutations_are_unique(pair):
    alphabet, lst = pair
    matrices = set()

    def matrixtuple(matrix):
        return tuple(tuple(row) for row in matrix)

    for perm in permutations(range(len(lst))):
        hd = holodeque(alphabet)
        for val in perm:
            hd.pushright(lst[val])
        matrices.add(matrixtuple(hd._matrix))

    counts = Counter(lst)
    total_elements = sum(counts.values())
    total_permutations = factorial(total_elements)
    divisor = reduce(lambda x, y: x * factorial(y), counts.values(), 1)
    combinations = total_permutations // divisor
    assert len(matrices) == combinations
