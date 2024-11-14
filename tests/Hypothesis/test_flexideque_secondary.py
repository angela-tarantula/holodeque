from collections import deque

import pytest
from hypothesis import assume, given, settings
from hypothesis import strategies as st

from src.flexideque import flexideque

# integer size limits in C, relevant because deque is written in C
MIN = -(2**63)
MAX = (2**63) - 1

"""Draw strategies"""

alphabet_strategy_without_text = st.sets(
    st.one_of(
        st.integers(),
        st.floats(allow_infinity=False, allow_nan=False),
        st.booleans()
    ),
    min_size=2,
    max_size=10
)

@st.composite
def two_lists_without_text(draw):
    alphabet = draw(alphabet_strategy_without_text)
    lst1 = draw(st.lists(st.sampled_from(list(alphabet)),
                min_size=0, max_size=100))
    lst2 = draw(st.lists(st.sampled_from(list(alphabet)),
                min_size=len(lst1), max_size=len(lst1)))
    return lst1, lst2

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
def element_strategy(draw):
    alphabet = draw(alphabet_strategy)
    element = draw(st.sampled_from(list(alphabet)))
    return element


@st.composite
def initial_list_strategy(draw):
    alphabet = draw(alphabet_strategy)
    lst = draw(st.lists(st.sampled_from(list(alphabet))))
    return lst


@st.composite
def initial_list_strategy_small_version(draw):
    alphabet = draw(alphabet_strategy)
    lst = draw(st.lists(st.sampled_from(list(alphabet)), min_size=2, max_size=10))
    return lst


@st.composite
def list_and_index_strategy(draw):
    alphabet = draw(alphabet_strategy)
    lst = draw(st.lists(st.sampled_from(list(alphabet))))
    index = draw(st.integers(min_value=MIN, max_value=MAX))
    return lst, index


@st.composite
def list_and_element_strategy(draw):
    alphabet = draw(alphabet_strategy)
    lst = draw(st.lists(st.sampled_from(list(alphabet)), min_size=1))
    element = draw(st.sampled_from(lst))
    return lst, element


@st.composite
def list_and_nonelement_strategy(draw):
    alphabet = draw(alphabet_strategy)
    nonelement = alphabet.pop()
    lst = draw(st.lists(st.sampled_from(list(alphabet)), min_size=1, max_size=100))
    return lst, nonelement


@st.composite
def list_index_in_range_and_element_strategy(draw):
    alphabet = draw(alphabet_strategy)
    lst = draw(st.lists(st.sampled_from(list(alphabet)), min_size=1))
    index = draw(st.integers(min_value=-len(lst), max_value=len(lst)))
    element = draw(st.sampled_from(list(alphabet)))
    return lst, index, element


@st.composite
def list_index_out_of_range_and_element_strategy(draw):
    alphabet = draw(alphabet_strategy)
    lst = draw(st.lists(st.sampled_from(list(alphabet)), min_size=1))
    index = draw(st.sampled_from(
        [
            draw(st.integers(min_value=MIN, max_value=-len(lst)-1)),
            draw(st.integers(min_value=len(lst)+1, max_value=MAX))
        ]
    ))
    element = draw(st.sampled_from(list(alphabet)))
    return lst, index, element


@st.composite
def list_element_and_slice_strategy(draw):
    alphabet = draw(alphabet_strategy)
    lst = draw(st.lists(st.sampled_from(list(alphabet)), min_size=1))
    element = draw(st.sampled_from(lst))
    start = draw(st.integers(min_value=MIN, max_value=MAX))
    stop = draw(st.integers(min_value=MIN, max_value=MAX))
    return lst, element, start, stop


@st.composite
def list_nonelement_and_slice_strategy(draw):
    alphabet = draw(alphabet_strategy)
    nonelement = alphabet.pop()
    lst = draw(st.lists(st.sampled_from(list(alphabet)), min_size=1))
    start = draw(st.integers(min_value=MIN, max_value=MAX))
    stop = draw(st.integers(min_value=MIN, max_value=MAX))
    return lst, nonelement, start, stop


@st.composite
def push_pop_strategy(draw):
    alphabet = draw(alphabet_strategy)
    lst = draw(st.lists(st.sampled_from(list(alphabet)),
               min_size=0, max_size=100))
    directions = draw(
        st.lists(st.booleans(), min_size=len(lst), max_size=len(lst)))
    return lst, directions


@st.composite
def two_lists(draw):
    alphabet = draw(alphabet_strategy)
    lst1 = draw(st.lists(st.sampled_from(list(alphabet)),
                min_size=0, max_size=100))
    lst2 = draw(st.lists(st.sampled_from(list(alphabet)),
                min_size=len(lst1), max_size=len(lst1)))
    return lst1, lst2


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
    return lst1, lst2, actions


"""Tests"""


@given(list_and_index_strategy())
def test_rotate_can_be_undone(pair):
    lst, index = pair
    hd = flexideque(iterable=lst)
    hd.rotate(index)
    hd.rotate(-index)
    assert lst == list(hd)


@given(list_and_index_strategy())
def test_rotate_against_deque(pair):
    lst, index = pair
    hd = flexideque(iterable=lst)
    d = deque(lst)
    hd.rotate(index)
    d.rotate(index)
    assert list(hd) == list(d)


@given(list_and_element_strategy())
def test_count_when_present(pair):
    lst, element = pair
    hd = flexideque(iterable=lst)
    d = deque(lst)
    assert hd.count(element) == d.count(element)
    assert list(hd) == list(d)


@given(list_and_nonelement_strategy())
def test_count_when_not_present(pair):
    lst, nonelement = pair
    hd = flexideque(iterable=lst)
    d = deque(lst)
    assert hd.count(nonelement) == d.count(nonelement)
    assert list(hd) == list(d)


@given(list_and_element_strategy())
def test_remove_when_present(pair):
    lst, element = pair
    hd = flexideque(iterable=lst)
    d = deque(lst)
    hd.remove(element)
    d.remove(element)
    assert list(hd) == list(d)


@given(list_and_nonelement_strategy())
def test_remove_when_not_present(pair):
    lst, nonelement = pair
    hd = flexideque(iterable=lst)
    d = deque(lst)
    with pytest.raises(ValueError):
        hd.remove(nonelement)
    with pytest.raises(ValueError):
        d.remove(nonelement)
    assert list(hd) == list(d)


@given(list_and_element_strategy())
def test_contain_when_present(pair):
    lst, element = pair
    hd = flexideque(iterable=lst)
    d = deque(lst)
    assert element in hd and element in d
    assert list(hd) == list(d)


@given(list_and_nonelement_strategy())
def test_contain_when_not_present(pair):
    lst, nonelement = pair
    hd = flexideque(iterable=lst)
    d = deque(lst)
    assert nonelement not in hd and nonelement not in d
    assert list(hd) == list(d)


@given(list_index_in_range_and_element_strategy())
def test_insert_in_range_against_deque(trio):
    lst, index, element = trio
    hd = flexideque(iterable=lst)
    d = deque(lst)
    hd.insert(index, element)
    d.insert(index, element)
    assert list(hd) == list(d)


@given(list_index_out_of_range_and_element_strategy())
def test_insert_out_of_range_against_deque(trio):
    lst, index, element = trio
    hd = flexideque(iterable=lst)
    d = deque(lst)
    hd.insert(index, element)
    d.insert(index, element)
    assert list(hd) == list(d)


@given(list_index_in_range_and_element_strategy())
def test_getitem_in_range_against_deque(trio):
    lst, index, _ = trio
    if index == len(lst):
        index -= 1
    hd = flexideque(iterable=lst)
    d = deque(lst)
    assert hd[index] == d[index]
    assert list(hd) == list(d)


@given(list_index_out_of_range_and_element_strategy())
def test_getitem_out_of_range_against_deque(trio):
    lst, index, _ = trio
    if index > len(lst):
        index -= 1
    hd = flexideque(iterable=lst)
    d = deque(lst)
    with pytest.raises(IndexError):
        hd[index]
    with pytest.raises(IndexError):
        d[index]
    assert list(hd) == list(d)


@given(list_index_in_range_and_element_strategy())
def test_setitem_in_range_against_deque(trio):
    lst, index, element = trio
    if index == len(lst):
        index -= 1
    hd = flexideque(iterable=lst)
    d = deque(lst)
    hd[index] = element
    d[index] = element
    assert list(hd) == list(d)


@given(list_index_out_of_range_and_element_strategy())
def test_setitem_out_of_range_against_deque(trio):
    lst, index, element = trio
    if index > len(lst):
        index -= 1
    hd = flexideque(iterable=lst)
    d = deque(lst)
    with pytest.raises(IndexError):
        hd[index] = element
    with pytest.raises(IndexError):
        d[index] = element
    assert list(hd) == list(d)


@given(list_index_in_range_and_element_strategy())
def test_delitem_in_range_against_deque(trio):
    lst, index, _ = trio
    if index == len(lst):
        index -= 1
    hd = flexideque(iterable=lst)
    d = deque(lst)
    del hd[index]
    del d[index]
    assert list(hd) == list(d)


@given(list_index_out_of_range_and_element_strategy())
def test_delitem_out_of_range_against_deque(trio):
    lst, index, _ = trio
    if index > len(lst):
        index -= 1
    hd = flexideque(iterable=lst)
    d = deque(lst)
    with pytest.raises(IndexError):
        del hd[index]
    with pytest.raises(IndexError):
        del d[index]
    assert list(hd) == list(d)


@given(list_and_element_strategy())
def test_index_when_present(pair):
    lst, element = pair
    hd = flexideque(iterable=lst)
    d = deque(lst)
    assert hd.index(element) == d.index(element)
    assert list(hd) == list(d)


@given(list_and_nonelement_strategy())
def test_index_when_not_present(pair):
    lst, nonelement = pair
    hd = flexideque(iterable=lst)
    d = deque(lst)
    with pytest.raises(ValueError):
        hd.index(nonelement)
    with pytest.raises(ValueError):
        d.index(nonelement)
    assert list(hd) == list(d)


@settings(max_examples=5_000, deadline=None)
@given(list_element_and_slice_strategy())
def test_index_slize_when_present(quartet):
    lst, element, start, stop = quartet
    hd = flexideque(iterable=lst)
    d = deque(lst)
    if element in lst[start:stop]:
        assert hd.index(element, start, stop) == d.index(element, start, stop)
    else:
        with pytest.raises(ValueError):
            hd.index(element, start, stop)
        with pytest.raises(ValueError):
            d.index(element, start, stop)
    assert list(hd) == list(d)


@given(initial_list_strategy())
def test_repr(lst):
    hd = flexideque(iterable=lst)
    d = deque(lst)
    assert repr(hd)[:5] == "flexi"
    assert repr(hd)[5:] == repr(d)[:]


@given(two_lists_without_text())
def test_comparisons_against_deque(pair):
    lst1, lst2 = pair
    if len(lst1) < len(lst2):
        lst1, lst2 = lst2, lst1
    hd1 = flexideque(iterable=lst1)
    hd2 = flexideque(iterable=lst2)
    d1 = deque(lst1)
    d2 = deque(lst2)
    assert (hd1 == hd2) == (d1 == d2)
    assert list(hd1) == list(d1) and list(hd2) == list(d2)
    assert (hd1 != hd2) == (d1 != d2)
    assert list(hd1) == list(d1) and list(hd2) == list(d2)
    assert (hd1 < hd2) == (d1 < d2)
    assert list(hd1) == list(d1) and list(hd2) == list(d2)
    assert (hd1 <= hd2) == (d1 <= d2)
    assert list(hd1) == list(d1) and list(hd2) == list(d2)
    assert (hd1 > hd2) == (d1 > d2)
    assert list(hd1) == list(d1) and list(hd2) == list(d2)
    assert (hd1 >= hd2) == (d1 >= d2)
    assert list(hd1) == list(d1) and list(hd2) == list(d2)


@given(list_and_element_strategy())
def test_maxlen_against_deque(pair):
    lst, element = pair
    assume(lst)
    hd = flexideque(iterable=lst, maxlen=len(lst))
    d = deque(lst, maxlen=len(lst))
    assert list(hd) == list(d) == lst
    d.append(element)
    hd.pushright(element)
    assert list(hd) == list(d)
    d.appendleft(element)
    hd.pushleft(element)
    assert list(hd) == list(d)
    d.extend(lst)
    hd.extendright(lst)
    assert list(hd) == list(d) == lst
    d.extendleft(lst)
    hd.extendleft(lst)
    assert list(hd) == list(d) == list(reversed(lst))
    assume(lst)
    d2 = deque(lst, maxlen=(len(lst) // 2) + 1)
    hd2 = flexideque(iterable=lst, maxlen=(len(lst) // 2) + 1)
    assert list(hd2) == list(d2)
