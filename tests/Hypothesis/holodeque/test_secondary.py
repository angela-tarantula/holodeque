from collections import Counter, deque
from functools import reduce
from itertools import permutations
from math import factorial

import pytest
from hypothesis import assume, given, settings
from hypothesis import strategies as st

from src.holodeque import holodeque

MIN = -(2**63)
MAX = (2**63) - 1

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
def alphabet_list_and_index_strategy(draw):
    alphabet = draw(alphabet_strategy)
    lst = draw(st.lists(st.sampled_from(list(alphabet))))
    index = draw(st.integers(min_value=MIN, max_value=MAX))
    return alphabet, lst, index


@st.composite
def alphabet_list_and_element_strategy(draw):
    alphabet = draw(alphabet_strategy)
    lst = draw(st.lists(st.sampled_from(list(alphabet)), min_size=1))
    element = draw(st.sampled_from(lst))
    return alphabet, lst, element


@st.composite
def alphabet_list_and_nonelement_strategy(draw):
    alphabet = draw(alphabet_strategy)
    lst = draw(st.lists(st.sampled_from(list(alphabet)), min_size=1))
    element = draw(
        st.one_of(
            st.integers(),
            st.floats(allow_infinity=False, allow_nan=False),
            st.booleans(),
            st.text()
        ).filter(lambda x: x not in lst)
    )
    return alphabet, lst, element


@st.composite
def alphabet_list_index_in_range_and_element_strategy(draw):
    alphabet = draw(alphabet_strategy)
    lst = draw(st.lists(st.sampled_from(list(alphabet)), min_size=1))
    index = draw(st.integers(min_value=-len(lst), max_value=len(lst)))
    element = draw(st.sampled_from(list(alphabet)))
    return alphabet, lst, index, element


@st.composite
def alphabet_list_index_out_of_range_and_element_strategy(draw):
    alphabet = draw(alphabet_strategy)
    lst = draw(st.lists(st.sampled_from(list(alphabet)), min_size=1))
    index = draw(st.sampled_from(
        [
            draw(st.integers(min_value=MIN, max_value=-len(lst)-1)),
            draw(st.integers(min_value=len(lst)+1, max_value=MAX))
        ]
    ))
    element = draw(st.sampled_from(list(alphabet)))
    return alphabet, lst, index, element


@st.composite
def alphabet_list_element_and_slice_strategy(draw):
    alphabet = draw(alphabet_strategy)
    lst = draw(st.lists(st.sampled_from(list(alphabet)), min_size=1))
    element = draw(st.sampled_from(lst))
    start = draw(st.integers(min_value=MIN, max_value=MAX))
    stop = draw(st.integers(min_value=MIN, max_value=MAX))
    return alphabet, lst, element, start, stop


@st.composite
def alphabet_list_nonelement_and_slice_strategy(draw):
    alphabet = draw(alphabet_strategy)
    lst = draw(st.lists(st.sampled_from(list(alphabet)), min_size=1))
    element = draw(
        st.one_of(
            st.integers(),
            st.floats(allow_infinity=False, allow_nan=False),
            st.booleans(),
            st.text()
        ).filter(lambda x: x not in lst)
    )
    start = draw(st.integers(min_value=MIN, max_value=MAX))
    stop = draw(st.integers(min_value=MIN, max_value=MAX))
    return alphabet, lst, element, start, stop


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
def two_alphabets_two_lists(draw):
    alphabet1 = draw(alphabet_strategy)
    alphabet2 = draw(alphabet_strategy)
    length1 = draw(st.integers(min_value=0, max_value=100))
    length2 = draw(st.integers(min_value=0, max_value=100))
    lst1 = draw(st.lists(st.sampled_from(list(alphabet1)),
                min_size=length1, max_size=length1))
    lst2 = draw(st.lists(st.sampled_from(list(alphabet2)),
                min_size=length2, max_size=length2))
    return alphabet1, alphabet2, lst1, lst2


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


"""Tests"""


@given(alphabet_list_and_index_strategy())
def test_rotate_can_be_undone(trio):
    alphabet, lst, index = trio
    hd = holodeque(alphabet, lst)
    hd.rotate(index)
    hd.rotate(-index)
    assert lst == list(hd)


@given(alphabet_list_and_index_strategy())
def test_rotate_against_deque(trio):
    alphabet, lst, index = trio
    hd = holodeque(alphabet, lst)
    d = deque(lst)
    hd.rotate(index)
    d.rotate(index)
    assert list(hd) == list(d)


@given(alphabet_list_and_element_strategy())
def test_count_when_present(trio):
    alphabet, lst, element = trio
    hd = holodeque(alphabet, lst)
    d = deque(lst)
    assert hd.count(element) == d.count(element)
    assert list(hd) == list(d)


@given(alphabet_list_and_nonelement_strategy())
def test_count_when_not_present(trio):
    alphabet, lst, element = trio
    hd = holodeque(alphabet, lst)
    d = deque(lst)
    assert hd.count(element) == d.count(element)
    assert list(hd) == list(d)


@given(alphabet_list_and_element_strategy())
def test_remove_when_present(trio):
    alphabet, lst, element = trio
    hd = holodeque(alphabet, lst)
    d = deque(lst)
    hd.remove(element)
    d.remove(element)
    assert list(hd) == list(d)


@given(alphabet_list_and_nonelement_strategy())
def test_remove_when_not_present(trio):
    alphabet, lst, element = trio
    hd = holodeque(alphabet, lst)
    d = deque(lst)
    with pytest.raises(ValueError):
        hd.remove(element)
    with pytest.raises(ValueError):
        d.remove(element)
    assert list(hd) == list(d)


@given(alphabet_list_and_element_strategy())
def test_contain_when_present(trio):
    alphabet, lst, element = trio
    hd = holodeque(alphabet, lst)
    d = deque(lst)
    assert element in hd and element in d
    assert list(hd) == list(d)


@given(alphabet_list_and_nonelement_strategy())
def test_contain_when_not_present(trio):
    alphabet, lst, element = trio
    hd = holodeque(alphabet, lst)
    d = deque(lst)
    assert element not in hd and element not in d
    assert list(hd) == list(d)


@given(alphabet_list_index_in_range_and_element_strategy())
def test_insert_in_range_against_deque(quartet):
    alphabet, lst, index, element = quartet
    hd = holodeque(alphabet, lst)
    d = deque(lst)
    hd.insert(index, element)
    d.insert(index, element)
    assert list(hd) == list(d)


@given(alphabet_list_index_out_of_range_and_element_strategy())
def test_insert_out_of_range_against_deque(quartet):
    alphabet, lst, index, element = quartet
    hd = holodeque(alphabet, lst)
    d = deque(lst)
    hd.insert(index, element)
    d.insert(index, element)
    assert list(hd) == list(d)


@given(alphabet_list_index_in_range_and_element_strategy())
def test_getitem_in_range_against_deque(quartet):
    alphabet, lst, index, _ = quartet
    if index == len(lst):
        index -= 1
    hd = holodeque(alphabet, lst)
    d = deque(lst)
    assert hd[index] == d[index]
    assert list(hd) == list(d)


@given(alphabet_list_index_out_of_range_and_element_strategy())
def test_getitem_out_of_range_against_deque(quartet):
    alphabet, lst, index, _ = quartet
    if index > len(lst):
        index -= 1
    hd = holodeque(alphabet, lst)
    d = deque(lst)
    with pytest.raises(IndexError):
        hd[index]
    with pytest.raises(IndexError):
        d[index]
    assert list(hd) == list(d)


@given(alphabet_list_index_in_range_and_element_strategy())
def test_setitem_in_range_against_deque(quartet):
    alphabet, lst, index, element = quartet
    if index == len(lst):
        index -= 1
    hd = holodeque(alphabet, lst)
    d = deque(lst)
    hd[index] = element
    d[index] = element
    assert list(hd) == list(d)


@given(alphabet_list_index_out_of_range_and_element_strategy())
def test_setitem_out_of_range_against_deque(quartet):
    alphabet, lst, index, element = quartet
    if index > len(lst):
        index -= 1
    hd = holodeque(alphabet, lst)
    d = deque(lst)
    with pytest.raises(IndexError):
        hd[index] = element
    with pytest.raises(IndexError):
        d[index] = element
    assert list(hd) == list(d)


@given(alphabet_list_index_in_range_and_element_strategy())
def test_delitem_in_range_against_deque(quartet):
    alphabet, lst, index, _ = quartet
    if index == len(lst):
        index -= 1
    hd = holodeque(alphabet, lst)
    d = deque(lst)
    del hd[index]
    del d[index]
    assert list(hd) == list(d)


@given(alphabet_list_index_out_of_range_and_element_strategy())
def test_delitem_out_of_range_against_deque(quartet):
    alphabet, lst, index, _ = quartet
    if index > len(lst):
        index -= 1
    hd = holodeque(alphabet, lst)
    d = deque(lst)
    with pytest.raises(IndexError):
        del hd[index]
    with pytest.raises(IndexError):
        del d[index]
    assert list(hd) == list(d)


@given(alphabet_list_and_element_strategy())
def test_index_when_present(trio):
    alphabet, lst, element = trio
    hd = holodeque(alphabet, lst)
    d = deque(lst)
    assert hd.index(element) == d.index(element)
    assert list(hd) == list(d)


@given(alphabet_list_and_nonelement_strategy())
def test_index_when_not_present(trio):
    alphabet, lst, element = trio
    hd = holodeque(alphabet, lst)
    d = deque(lst)
    with pytest.raises(ValueError):
        hd.index(element)
    with pytest.raises(ValueError):
        d.index(element)
    assert list(hd) == list(d)

@settings(max_examples=5_000, deadline=None)
@given(alphabet_list_element_and_slice_strategy())
def test_index_slize_when_present(quintet):
    alphabet, lst, element, start, stop = quintet
    hd = holodeque(alphabet, lst)
    d = deque(lst)
    if element in lst[start:stop]:
        assert hd.index(element, start, stop) == d.index(element, start, stop)
    else:
        with pytest.raises(ValueError):
            hd.index(element, start, stop)
        with pytest.raises(ValueError):
            d.index(element, start, stop)
    assert list(hd) == list(d)
       

# repr, hash, < etc,
# compatible add radd & iadd, no sub or div, mult rmult & imult
# maxlen and its effects
