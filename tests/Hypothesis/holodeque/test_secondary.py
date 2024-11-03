import pytest
from src.holodeque import holodeque
from hypothesis import given, assume, settings, strategies as st
from itertools import permutations
from functools import reduce
from collections import Counter, deque
from math import factorial

"""Draw strategies"""

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
def alphabet_and_element_strategy(draw):
    alphabet = draw(st.frozensets(st.integers(), min_size=2))
    element = draw(st.sampled_from(list(alphabet)))
    return alphabet, element


@st.composite
def alphabet_and_initial_list_strategy(draw):
    alphabet = draw(alphabet_strategy)
    lst = draw(st.lists(st.sampled_from(list(alphabet))))
    return alphabet, lst


@st.composite
def alphabet_and_initial_list_strategy_small_version(draw):
    alphabet = draw(alphabet_strategy)
    lst = draw(st.lists(st.sampled_from(
        list(alphabet)), min_size=2, max_size=10))
    return alphabet, lst


@st.composite
def push_pop_strategy(draw):
    alphabet = draw(alphabet_strategy)
    length = draw(st.integers(min_value=0, max_value=100))
    lst = draw(st.lists(st.sampled_from(list(alphabet)),
               min_size=length, max_size=length))
    directions = draw(
        st.lists(st.booleans(), min_size=length, max_size=length))
    return alphabet, lst, directions


@st.composite
def two_lists(draw):
    alphabet = draw(alphabet_strategy)
    length = draw(st.integers(min_value=0, max_value=100))
    lst1 = draw(st.lists(st.sampled_from(list(alphabet)),
                min_size=length, max_size=length))
    lst2 = draw(st.lists(st.sampled_from(list(alphabet)),
                min_size=length, max_size=length))
    return alphabet, lst1, lst2


@st.composite
def deque_simulation_strategy(draw):
    alphabet = draw(alphabet_strategy)
    lst1 = draw(st.lists(st.sampled_from(list(alphabet))))
    options = ["pushright", "pushleft", "popright",
               "popleft", "peekright", "peekleft"]
    actions = draw(
        st.lists(st.sampled_from(options)))
    lst2 = draw(st.lists(st.sampled_from(list(alphabet)),
                min_size=len(actions), max_size=len(actions)))
    return alphabet, lst1, lst2, actions