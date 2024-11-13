from collections import deque

import pytest
from hypothesis import assume, given, settings
from hypothesis import strategies as st

from src.binary_holodeque import binarydeque

"""Draw strategies"""

@st.composite
def element_strategy(draw):
    element = draw(st.booleans())
    return element


@st.composite
def initial_list_strategy(draw):
    lst = draw(st.lists(st.booleans()))
    return lst


@st.composite
def initial_list_strategy_small_version(draw):
    lst = draw(st.lists(st.booleans(), min_size=2, max_size=10))
    return lst

@st.composite
def element_and_initial_list_strategy(draw):
    element = draw(st.booleans())
    lst = draw(st.lists(st.booleans()))
    return element, lst


@st.composite
def push_pop_strategy(draw):
    lst = draw(st.lists(st.booleans(), min_size=0, max_size=100))
    directions = draw(st.lists(st.booleans(), min_size=len(lst), max_size=len(lst)))
    return lst, directions


@st.composite
def two_lists(draw):
    lst1 = draw(st.lists(st.booleans(), min_size=0, max_size=100))
    lst2 = draw(st.lists(st.booleans(), min_size=len(lst1), max_size=len(lst1)))
    return lst1, lst2


@st.composite
def deque_simulation_strategy(draw):
    lst1 = draw(st.lists(st.booleans()))
    options = ["pushright", "pushleft", "popright",
               "popleft", "peekright", "peekleft"]
    actions = draw(
        st.lists(st.sampled_from(options)))
    lst2 = draw(st.lists(st.booleans(),
                min_size=len(actions), max_size=len(actions)))
    return lst1, lst2, actions


"""Tests"""

def test_empty_contains_nothing():
    hd = binarydeque()
    assert hd.size == hd._size == 0
    assert len(hd) == 0
    assert not hd


def test_maxlen():
    hd = binarydeque()
    assert hd.maxlen is None


def test_empty_popright_raises_index_error():
    hd = binarydeque()
    with pytest.raises(IndexError):
        hd.popright()
    assert not hd


def test_empty_popleft_raises_index_error():
    hd = binarydeque()
    with pytest.raises(IndexError):
        hd.popleft()
    assert not hd


def test_empty_peekright_raises_index_error():
    hd = binarydeque()
    with pytest.raises(IndexError):
        hd.peekright()
    assert not hd


def test_empty_peekleft_raises_index_error():
    hd = binarydeque()
    with pytest.raises(IndexError):
        hd.peekleft()
    assert not hd


@given(element_strategy())
def test_fist_push_makes_length_one(element):
    hd1 = binarydeque()
    hd1.pushright(element)
    assert hd1 and len(hd1) == 1
    hd2 = binarydeque()
    hd2.pushleft(element)
    assert hd2 and len(hd2) == 1


@given(element_strategy())
def test_first_pushes_are_equivalent(element):
    hd1 = binarydeque()
    hd1.pushright(element)
    hd2 = binarydeque()
    hd2.pushleft(element)
    assert hd1._matrix == hd2._matrix


@given(element_strategy())
def test_first_pushes_change_matrix(element):
    hd1 = binarydeque()
    hd1.pushright(element)
    hd2 = binarydeque()
    assert hd1._matrix != hd2._matrix


@given(element_strategy())
def test_first_peeks_dont_change_length(element):
    hd = binarydeque()
    hd.pushright(element)
    hd.peekleft()
    assert len(hd) == 1
    hd.peekright()
    assert len(hd) == 1


@given(element_strategy())
def test_first_peeks_dont_change_matrix(element):
    hd1 = binarydeque()
    hd1.pushright(element)
    hd2 = binarydeque()
    hd2.pushright(element)
    hd1.peekleft()
    assert hd1._matrix == hd2._matrix
    hd1.peekright()
    assert len(hd1) == 1
    assert hd1._matrix == hd2._matrix


@given(element_strategy())
def test_first_peeks_are_equivalent(element):
    hd = binarydeque()
    hd.pushright(element)
    assert hd.peekleft() == hd.peekright() == element


@given(element_strategy())
def test_pop_single_changes_matrix(element):
    hd1 = binarydeque()
    hd1.pushright(element)
    hd2 = binarydeque()
    hd2.pushright(element)
    hd2.popright()
    assert hd1._matrix != hd2._matrix
    hd2 = binarydeque()
    hd2.pushright(element)
    hd2.popleft()
    assert hd1._matrix != hd2._matrix


@given(element_strategy())
def test_pop_single_makes_matrix_identity(element):
    empty_holodeque = binarydeque()
    hd = binarydeque()
    hd.pushright(element)
    hd.popright()
    assert hd._matrix == empty_holodeque._matrix
    hd.pushright(element)
    hd.popleft()
    assert hd._matrix == empty_holodeque._matrix


@given(element_strategy())
def test_pop_single_makes_empty(element):
    hd = binarydeque()
    hd.pushright(element)
    hd.popright()
    assert not hd and len(hd) == 0
    hd.pushright(element)
    hd.popleft()
    assert not hd and len(hd) == 0


@given(element_strategy())
def test_pop_singles_are_equivalent(element):
    hd = binarydeque()
    hd.pushright(element)
    assert element == hd.popright()
    hd.pushright(element)
    assert element == hd.popleft()


@given(initial_list_strategy())
def test_pushright_increments_length(lst):
    hd = binarydeque()
    size = 0
    for i in lst:
        hd.pushright(i)
        size += 1
        assert len(hd) == size


@given(initial_list_strategy())
def test_pushright_always_makes_new_matrix(lst):
    hd = binarydeque()
    matrices = set()

    def matrixtuple(matrix):
        return tuple(tuple(row) for row in matrix)

    matrices.add(matrixtuple(hd._matrix))
    for i in lst:
        hd.pushright(i)
        new_matrixtuple = matrixtuple(hd._matrix)
        assert new_matrixtuple not in matrices
        matrices.add(new_matrixtuple)


@given(initial_list_strategy())
def test_pushleft_increments_length(lst):
    hd = binarydeque()
    size = 0
    for i in lst:
        hd.pushleft(i)
        size += 1
        assert len(hd) == size


@given(initial_list_strategy())
def test_pushleft_always_makes_new_matrix(lst):
    hd = binarydeque()
    matrices = set()

    def matrixtuple(matrix):
        return tuple(tuple(row) for row in matrix)

    matrices.add(matrixtuple(hd._matrix))
    for i in lst:
        hd.pushleft(i)
        new_matrixtuple = matrixtuple(hd._matrix)
        assert new_matrixtuple not in matrices
        matrices.add(new_matrixtuple)


@given(initial_list_strategy())
def test_pushright_result_is_unique_to_parameter(lst):
    alphabet = {True, False}
    holodeques = [binarydeque() for _ in alphabet]
    for i in lst:
        for hd in holodeques:
            hd.pushright(i)
    for i, option in enumerate(alphabet):
        holodeques[i].pushright(option)

    def matrixtuple(matrix):
        return tuple(tuple(row) for row in matrix)

    matrices = set(matrixtuple(hd._matrix) for hd in holodeques)
    assert len(matrices) == len(alphabet)


@given(initial_list_strategy())
def test_pushleft_result_is_unique_to_parameter(lst):
    alphabet = {True, False}
    holodeques = [binarydeque() for _ in alphabet]
    for i in lst:
        for hd in holodeques:
            hd.pushright(i)
    for i, option in enumerate(alphabet):
        holodeques[i].pushleft(option)

    def matrixtuple(matrix):
        return tuple(tuple(row) for row in matrix)

    matrices = set(matrixtuple(hd._matrix) for hd in holodeques)
    assert len(matrices) == len(alphabet)


@given(element_and_initial_list_strategy())
def test_pushleft_is_associative_with_pushrights(pair):
    leftmost_element, lst = pair
    hd1 = binarydeque()
    hd2 = binarydeque()
    stop = len(lst) // 2
    for i in lst[:stop]:
        hd1.pushright(i)
        hd2.pushright(i)
    hd1.pushleft(leftmost_element)
    for i in lst[stop:]:
        hd1.pushright(i)
        hd2.pushright(i)
    hd2.pushleft(leftmost_element)
    assert hd1._matrix == hd2._matrix


@given(element_and_initial_list_strategy())
def test_pushright_is_associative_with_pushlefts(pair):
    rightmost_element, lst = pair
    hd1 = binarydeque()
    hd2 = binarydeque()
    stop = len(lst) // 2
    for i in lst[:stop]:
        hd1.pushleft(i)
        hd2.pushleft(i)
    hd1.pushright(rightmost_element)
    for i in lst[stop:]:
        hd1.pushleft(i)
        hd2.pushleft(i)
    hd2.pushright(rightmost_element)
    assert hd1._matrix == hd2._matrix


@given(push_pop_strategy())
def test_pushes_are_always_associative_by_direction(pair):
    lst, directions = pair
    hd1 = binarydeque()
    for val, direction in zip(lst, directions):
        if direction:
            hd1.pushright(val)
        else:
            hd1.pushleft(val)
    hd2 = binarydeque()
    for val, direction in zip(lst, directions):
        if direction:
            hd2.pushright(val)
    for val, direction in zip(lst, directions):
        if not direction:
            hd2.pushleft(val)
    assert hd1._matrix == hd2._matrix


@given(initial_list_strategy())
def test_pushleft_and_pushright_are_opposites(lst):
    hd1 = binarydeque()
    hd2 = binarydeque()
    left = 0
    right = len(lst) - 1
    while left < len(lst):
        hd1.pushright(lst[left])
        hd2.pushleft(lst[right])
        left += 1
        right -= 1
    assert hd1._matrix == hd2._matrix


@given(initial_list_strategy())
def test_peekright_does_not_change_length(lst):
    assume(lst)
    hd = binarydeque()
    for i in lst:
        hd.pushright(i)
    length = len(hd)
    hd.peekright()
    assert len(hd) == length


@given(initial_list_strategy())
def test_peekleft_does_not_change_length(lst):
    assume(lst)
    hd = binarydeque()
    for i in lst:
        hd.pushright(i)
    length = len(hd)
    hd.peekleft()
    assert len(hd) == length


@given(initial_list_strategy())
def test_peekright_never_changes_length(lst):
    hd = binarydeque()
    size = 0
    for i in lst:
        size += 1
        hd.pushright(i)
        hd.peekright()
        assert size == len(hd)


@given(initial_list_strategy())
def test_peekleft_constant_when_only_pushright(lst):
    hd = binarydeque()
    for i in lst:
        hd.pushright(i)
        assert hd.peekleft() == lst[0]


@given(initial_list_strategy())
def test_peekright_constant_when_only_pushleft(lst):
    hd = binarydeque()
    for i in lst:
        hd.pushleft(i)
        assert hd.peekright() == lst[0]


@given(initial_list_strategy())
def test_peekright_always_what_was_last_pushed(lst):
    hd = binarydeque()
    for i in lst:
        hd.pushright(i)
        assert hd.peekright() == i


@given(initial_list_strategy())
def test_peekleft_always_what_was_last_pushed(lst):
    hd = binarydeque()
    for i in lst:
        hd.pushleft(i)
        assert hd.peekleft() == i


@given(initial_list_strategy())
def test_peekright_result_is_unique_to_parameter(lst):
    alphabet = {True, False}
    holodeques = [binarydeque() for _ in alphabet]
    hd = binarydeque()
    for i in lst:
        for hd in holodeques:
            hd.pushright(i)
    for hd, option in zip(holodeques, alphabet):
        hd.pushright(option)
        assert hd.peekright() == option


@given(initial_list_strategy())
def test_peekleft_result_is_unique_to_parameter(lst):
    alphabet = {True, False}
    holodeques = [binarydeque() for _ in alphabet]
    hd = binarydeque()
    for i in lst:
        for hd in holodeques:
            hd.pushright(i)
    for hd, option in zip(holodeques, alphabet):
        hd.pushleft(option)
        assert hd.peekleft() == option


@given(push_pop_strategy())
def test_peeks_are_never_changed_by_opposite_pushes(pair):
    lst, directions = pair
    assume(lst)
    hd = binarydeque()
    leftmost = rightmost = lst[0]
    for val, direction in zip(lst, directions):
        if direction:
            rightmost = val
            hd.pushright(val)
        else:
            leftmost = val
            hd.pushleft(val)
        assert hd.peekleft() == leftmost
        assert hd.peekright() == rightmost


@given(initial_list_strategy())
def test_popright_always_decrements_size(lst):
    hd = binarydeque()
    for i in lst:
        hd.pushright(i)
    size = len(hd)
    while size:
        size -= 1
        hd.popright()
        assert size == len(hd)


@given(initial_list_strategy())
def test_popleft_always_decrements_size(lst):
    hd = binarydeque()
    for i in lst:
        hd.pushright(i)
    size = len(hd)
    while size:
        size -= 1
        hd.popleft()
        assert size == len(hd)


@given(push_pop_strategy())
def test_pops_always_decrement_size_even_mixed(pair):
    lst, directions = pair
    hd = binarydeque()
    for i in lst:
        hd.pushright(i)
    size = len(hd)
    while size:
        size -= 1
        if directions[size]:
            hd.popright()
        else:
            hd.popleft()
        assert size == len(hd)


@given(initial_list_strategy())
def test_popright_unchanged_by_pushleft(lst):
    assume(lst)
    hd = binarydeque()
    for i in lst:
        hd.pushleft(i)
    assert hd.peekright() == lst[0] == hd.popright()


@given(initial_list_strategy())
def test_popleft_unchanged_by_pushright(lst):
    assume(lst)
    hd = binarydeque()
    for i in lst:
        hd.pushright(i)
    assert hd.peekleft() == lst[0] == hd.popleft()


@given(initial_list_strategy())
def test_popright_returns_last_pushright_value(lst):
    hd = binarydeque()
    for i in lst:
        hd.pushright(i)
        assert hd.peekright() == i == hd.popright()
        hd.pushright(i)


@given(initial_list_strategy())
def test_popleft_returns_last_pushleft_value(lst):
    hd = binarydeque()
    for i in lst:
        hd.pushleft(i)
        assert hd.peekleft() == i == hd.popleft()
        hd.pushleft(i)


@given(push_pop_strategy())
def test_popright_always_returns_rightmost(pair):
    lst, directions = pair
    hd = binarydeque()
    rightmost = 0
    for val, direction in zip(lst, directions):
        hd.pushleft(val)
        if direction:
            assert hd.popright() == lst[rightmost]
            rightmost += 1


@given(push_pop_strategy())
def test_popleft_always_returns_leftmost(pair):
    lst, directions = pair
    hd = binarydeque()
    leftmost = 0
    for val, direction in zip(lst, directions):
        hd.pushright(val)
        if direction:
            assert hd.popleft() == lst[leftmost]
            leftmost += 1


@given(initial_list_strategy())
def test_peekright_constant_when_popleft(lst):
    assume(lst)
    hd = binarydeque()
    for i in lst:
        hd.pushright(i)
    rightmost = lst[-1]
    while hd:
        assert hd.peekright() == rightmost
        hd.popleft()


@given(initial_list_strategy())
def test_peekleft_constant_when_popright(lst):
    assume(lst)
    hd = binarydeque()
    for i in lst:
        hd.pushright(i)
    leftmost = lst[0]
    while hd:
        assert hd.peekleft() == leftmost
        hd.popright()


@given(initial_list_strategy())
def test_extendright_from_empty(lst):
    hd1 = binarydeque()
    for i in lst:
        hd1.pushright(i)
    hd2 = binarydeque()
    hd2.extendright(lst)
    assert hd1._matrix == hd2._matrix


@given(initial_list_strategy())
def test_extendleft_from_empty(lst):
    hd1 = binarydeque()
    for i in lst:
        hd1.pushleft(i)
    hd2 = binarydeque()
    hd2.extendleft(lst)
    assert hd1._matrix == hd2._matrix


@given(initial_list_strategy())
def test_initialization(lst):
    hd1 = binarydeque()
    hd2 = binarydeque(iterable=lst)
    for i in lst:
        hd1.pushright(i)
    assert hd1._matrix == hd2._matrix


@given(two_lists())
def test_extendright(pair):
    lst1, lst2 = pair
    hd1 = binarydeque(iterable=lst1)
    for i in lst2:
        hd1.pushright(i)
    hd2 = binarydeque(iterable = lst1 + lst2)
    assert hd1._matrix == hd2._matrix


@given(two_lists())
def test_extendleft(pair):
    lst1, lst2 = pair
    hd1 = binarydeque(iterable=lst1)
    for i in lst2:
        hd1.pushleft(i)
    hd2 = binarydeque(iterable = list(reversed(lst2)) + lst1)
    assert hd1._matrix == hd2._matrix


@given(two_lists())
def test_concatright(pair):
    lst1, lst2 = pair
    hd1 = binarydeque(iterable=lst1)
    hd2 = binarydeque(iterable=lst2)
    hd1.concatright(hd2)
    hd3 = binarydeque(iterable = lst1 + lst2)
    assert hd1._matrix == hd3._matrix


@given(two_lists())
def test_concatleft(pair):
    lst1, lst2 = pair
    hd1 = binarydeque(iterable=lst1)
    hd2 = binarydeque(iterable=lst2)
    hd1.concatleft(hd2)
    hd3 = binarydeque(iterable = lst2 + lst1)
    assert hd1._matrix == hd3._matrix


@given(two_lists())
def test_concatleft_is_opposite_of_concatright(pair):
    lst1, lst2 = pair
    hd1 = binarydeque(iterable=lst1)
    hd2 = binarydeque(iterable=lst2)
    hd3 = binarydeque(iterable=lst1)
    hd4 = binarydeque(iterable=lst2)
    hd1.concatright(hd2)
    hd4.concatleft(hd3)
    assert hd1._matrix == hd4._matrix


@given(initial_list_strategy())
def test_concatself(lst):
    hd1 = binarydeque(iterable=lst)
    hd2 = binarydeque(iterable=lst)
    hd1.concatright(hd1)
    hd2.concatleft(hd2)
    hd3 = binarydeque(iterable = lst + lst)
    assert hd1._matrix == hd2._matrix == hd3._matrix


@given(two_lists())
def test_extendright_with_another_holodeque_calls_concatright(pair):
    lst1, lst2 = pair
    hd1 = binarydeque(iterable=lst1)
    hd2 = binarydeque(iterable=lst1)
    hd3 = binarydeque(iterable=lst2)
    hd4 = binarydeque(iterable=lst2)
    hd1.extendright(hd3)
    hd2.concatright(hd4)
    assert hd1._matrix == hd2._matrix


@given(initial_list_strategy())
def test_copy(lst):
    hd1 = binarydeque(iterable=lst)
    hd2 = hd1.copy()
    assert hd1 is not hd2
    for i in range(2):
        for j in range(2):
            hd1._matrix[i][j] == hd2._matrix[i][j]
    assert hd1._matrix is not hd2._matrix
    assert hd1._maxlen == hd2._maxlen
    assert hd1._kwargs == hd2._kwargs and hd1._kwargs is not hd2._kwargs


@given(initial_list_strategy())
def test_iterator(lst):
    hd = binarydeque(iterable=lst)
    assert list(hd) == lst


@given(initial_list_strategy())
def test_reversed(lst):
    hd = binarydeque(iterable=lst)
    assert list(reversed(hd)) == list(reversed(lst))


@given(initial_list_strategy())
def test_equality(lst):
    hd1 = binarydeque(iterable=lst)
    hd2 = binarydeque(iterable=lst)
    assert hd1 == hd2
    assert not (hd1 != hd2)


@given(two_lists())
def test_inequality(pair):
    lst1, lst2 = pair
    hd1 = binarydeque(iterable=lst1)
    hd2 = binarydeque(iterable=lst2)
    assert (lst1 == lst2) == (hd1 == hd2)
    assert (lst1 != lst2) == (hd1 != hd2)
    assert (not (hd1 == hd2)) == (hd1 != hd2)


@given(initial_list_strategy())
def test_clear(lst):
    hd1 = binarydeque()
    hd2 = binarydeque(iterable=lst)
    hd2.clear()
    assert hd1 == hd2


@settings(max_examples=5_000, deadline=None)
@given(deque_simulation_strategy())
def test_deque_simulation(trio):
    lst1, lst2, actions = trio
    hd = binarydeque(iterable=lst1)
    d = deque(lst1)
    assert list(d) == list(hd)
    for data, decision in zip(lst2, actions):
        match decision:
            case "pushleft":
                d.appendleft(data)
                hd.pushleft(data)
            case "pushright":
                d.append(data)
                hd.pushright(data)
            case "popleft":
                if d and hd:
                    assert d.popleft() == hd.popleft()
                else:
                    assert not d and not hd
                    with pytest.raises(IndexError):
                        d.popleft()
                    with pytest.raises(IndexError):
                        hd.popleft()
            case "popright":
                if d and hd:
                    assert d.pop() == hd.popright()
                else:
                    assert not d and not hd
                    with pytest.raises(IndexError):
                        d.pop()
                    with pytest.raises(IndexError):
                        hd.popright()
            case "peekleft":
                if d and hd:
                    assert d[0] == hd.peekleft()
                else:
                    assert not d and not hd
                    with pytest.raises(IndexError):
                        d[0]
                    with pytest.raises(IndexError):
                        hd.peekleft()
            case "peekright":
                if d and hd:
                    assert d[-1] == hd.peekright()
                else:
                    assert not d and not hd
                    with pytest.raises(IndexError):
                        d[-1]
                    with pytest.raises(IndexError):
                        hd.peekright()
        assert list(d) == list(hd)
