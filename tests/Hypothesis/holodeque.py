import pytest
from src.holodeque import holodeque
from hypothesis import given, assume, settings, strategies as st
from itertools import permutations
from functools import reduce
from collections import Counter
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


"""Tests"""


@given(alphabet_strategy)
def test_empty_contains_nothing(alphabet):
    hd = holodeque(alphabet)
    assert not hd and len(hd) == 0


@given(alphabet_strategy)
def test_empty_popright_raises_index_error(alphabet):
    hd = holodeque(alphabet)
    with pytest.raises(IndexError):
        hd.popright()


@given(alphabet_strategy)
def test_empty_popleft_raises_index_error(alphabet):
    hd = holodeque(alphabet)
    with pytest.raises(IndexError):
        hd.popleft()


@given(alphabet_strategy)
def test_empty_peekright_raises_index_error(alphabet):
    hd = holodeque(alphabet)
    with pytest.raises(IndexError):
        hd.peekright()


@given(alphabet_strategy)
def test_empty_peekleft_raises_index_error(alphabet):
    hd = holodeque(alphabet)
    with pytest.raises(IndexError):
        hd.peekleft()


@given(alphabet_and_element_strategy())
def test_fist_push_makes_length_one(pair):
    alphabet, element = pair
    hd1 = holodeque(alphabet)
    hd1.pushright(element)
    assert hd1 and len(hd1) == 1
    hd2 = holodeque(alphabet)
    hd2.pushleft(element)
    assert hd2 and len(hd2) == 1


@given(alphabet_and_element_strategy())
def test_first_pushes_are_equivalent(pair):
    alphabet, element = pair
    hd1 = holodeque(alphabet)
    hd1.pushright(element)
    hd2 = holodeque(alphabet)
    hd2.pushleft(element)
    assert hd1._matrix == hd2._matrix


@given(alphabet_and_element_strategy())
def test_first_pushes_change_matrix(pair):
    alphabet, element = pair
    hd1 = holodeque(alphabet)
    hd1.pushright(element)
    hd2 = holodeque(alphabet)
    assert hd1._matrix != hd2._matrix


@given(alphabet_and_element_strategy())
def test_first_peeks_dont_change_length(pair):
    alphabet, element = pair
    hd = holodeque(alphabet)
    hd.pushright(element)
    hd.peekleft()
    assert len(hd) == 1
    hd.peekright()
    assert len(hd) == 1


@given(alphabet_and_element_strategy())
def test_first_peeks_dont_change_matrix(pair):
    alphabet, element = pair
    hd1 = holodeque(alphabet)
    hd1.pushright(element)
    hd2 = holodeque(alphabet)
    hd2.pushright(element)
    hd1.peekleft()
    assert hd1._matrix == hd2._matrix
    hd1.peekright()
    assert len(hd1) == 1
    assert hd1._matrix == hd2._matrix


@given(alphabet_and_element_strategy())
def test_first_peeks_are_equivalent(pair):
    alphabet, element = pair
    hd = holodeque(alphabet)
    hd.pushright(element)
    assert hd.peekleft() == hd.peekright() == element


@given(alphabet_and_element_strategy())
def test_pop_single_changes_matrix(pair):
    alphabet, element = pair
    hd1 = holodeque(alphabet)
    hd1.pushright(element)
    hd2 = holodeque(alphabet)
    hd2.pushright(element)
    hd2.popright()
    assert hd1._matrix != hd2._matrix
    hd2 = holodeque(alphabet)
    hd2.pushright(element)
    hd2.popleft()
    assert hd1._matrix != hd2._matrix


@given(alphabet_and_element_strategy())
def test_pop_single_makes_matrix_identity(pair):
    alphabet, element = pair
    empty_holodeque = holodeque(alphabet)
    hd = holodeque(alphabet)
    hd.pushright(element)
    hd.popright()
    assert hd._matrix == empty_holodeque._matrix
    hd.pushright(element)
    hd.popleft()
    assert hd._matrix == empty_holodeque._matrix


@given(alphabet_and_element_strategy())
def test_pop_single_makes_empty(pair):
    alphabet, element = pair
    hd = holodeque(alphabet)
    hd.pushright(element)
    hd.popright()
    assert not hd and len(hd) == 0
    hd.pushright(element)
    hd.popleft()
    assert not hd and len(hd) == 0


@given(alphabet_and_element_strategy())
def test_pop_singles_are_equivalent(pair):
    alphabet, element = pair
    hd = holodeque(alphabet)
    hd.pushright(element)
    assert element == hd.popright()
    hd.pushright(element)
    assert element == hd.popleft()


@given(alphabet_and_initial_list_strategy())
def test_pushright_increments_length(pair):
    alphabet, lst = pair
    hd = holodeque(alphabet)
    size = 0
    for i in lst:
        hd.pushright(i)
        size += 1
        assert len(hd) == size


@given(alphabet_and_initial_list_strategy())
def test_pushright_always_makes_new_matrix(pair):
    alphabet, lst = pair
    hd = holodeque(alphabet)
    matrices = set()

    def matrixtuple(matrix):
        return tuple(tuple(row) for row in matrix)

    matrices.add(matrixtuple(hd._matrix))
    for i in lst:
        hd.pushright(i)
        new_matrixtuple = matrixtuple(hd._matrix)
        assert new_matrixtuple not in matrices
        matrices.add(new_matrixtuple)


@given(alphabet_and_initial_list_strategy())
def test_pushleft_increments_length(pair):
    alphabet, lst = pair
    hd = holodeque(alphabet)
    size = 0
    for i in lst:
        hd.pushleft(i)
        size += 1
        assert len(hd) == size


@given(alphabet_and_initial_list_strategy())
def test_pushleft_always_makes_new_matrix(pair):
    alphabet, lst = pair
    hd = holodeque(alphabet)
    matrices = set()

    def matrixtuple(matrix):
        return tuple(tuple(row) for row in matrix)

    matrices.add(matrixtuple(hd._matrix))
    for i in lst:
        hd.pushleft(i)
        new_matrixtuple = matrixtuple(hd._matrix)
        assert new_matrixtuple not in matrices
        matrices.add(new_matrixtuple)


@given(alphabet_and_initial_list_strategy())
def test_pushright_result_is_unique_to_parameter(pair):
    alphabet, lst = pair
    holodeques = [holodeque(alphabet) for _ in alphabet]
    for i in lst:
        for hd in holodeques:
            hd.pushright(i)
    for i, option in enumerate(alphabet):
        holodeques[i].pushright(option)

    def matrixtuple(matrix):
        return tuple(tuple(row) for row in matrix)

    matrices = set(matrixtuple(hd._matrix) for hd in holodeques)
    assert len(matrices) == len(alphabet)


@given(alphabet_and_initial_list_strategy())
def test_pushleft_result_is_unique_to_parameter(pair):
    alphabet, lst = pair
    holodeques = [holodeque(alphabet) for _ in alphabet]
    for i in lst:
        for hd in holodeques:
            hd.pushright(i)
    for i, option in enumerate(alphabet):
        holodeques[i].pushleft(option)

    def matrixtuple(matrix):
        return tuple(tuple(row) for row in matrix)

    matrices = set(matrixtuple(hd._matrix) for hd in holodeques)
    assert len(matrices) == len(alphabet)


@given(alphabet_and_initial_list_strategy())
def test_pushleft_is_associative_with_pushrights(pair):
    alphabet, lst = pair
    hd1 = holodeque(alphabet)
    hd2 = holodeque(alphabet)
    stop = len(lst) // 2
    for i in lst[:stop]:
        hd1.pushright(i)
        hd2.pushright(i)
    leftmost_element = alphabet.pop()
    hd1.pushleft(leftmost_element)
    for i in lst[stop:]:
        hd1.pushright(i)
        hd2.pushright(i)
    hd2.pushleft(leftmost_element)
    assert hd1._matrix == hd2._matrix


@given(alphabet_and_initial_list_strategy())
def test_pushright_is_associative_with_pushlefts(pair):
    alphabet, lst = pair
    hd1 = holodeque(alphabet)
    hd2 = holodeque(alphabet)
    stop = len(lst) // 2
    for i in lst[:stop]:
        hd1.pushleft(i)
        hd2.pushleft(i)
    rightmost_element = alphabet.pop()
    hd1.pushright(rightmost_element)
    for i in lst[stop:]:
        hd1.pushleft(i)
        hd2.pushleft(i)
    hd2.pushright(rightmost_element)
    assert hd1._matrix == hd2._matrix


@given(push_pop_strategy())
def test_pushes_are_always_associative_by_direction(trio):
    alphabet, lst, directions = trio
    hd1 = holodeque(alphabet)
    for val, direction in zip(lst, directions):
        if direction:
            hd1.pushright(val)
        else:
            hd1.pushleft(val)
    hd2 = holodeque(alphabet)
    for val, direction in zip(lst, directions):
        if direction:
            hd2.pushright(val)
    for val, direction in zip(lst, directions):
        if not direction:
            hd2.pushleft(val)
    assert hd1._matrix == hd2._matrix


@given(alphabet_and_initial_list_strategy())
def test_pushleft_and_pushright_are_opposites(pair):
    alphabet, lst = pair
    hd1 = holodeque(alphabet)
    hd2 = holodeque(alphabet)
    left = 0
    right = len(lst) - 1
    while left < len(lst):
        hd1.pushright(lst[left])
        hd2.pushleft(lst[right])
        left += 1
        right -= 1
    assert hd1._matrix == hd2._matrix


@given(alphabet_and_initial_list_strategy())
def test_peekright_does_not_change_length(pair):
    alphabet, lst = pair
    assume(lst)
    hd = holodeque(alphabet)
    for i in lst:
        hd.pushright(i)
    length = len(hd)
    hd.peekright()
    assert len(hd) == length


@given(alphabet_and_initial_list_strategy())
def test_peekleft_does_not_change_length(pair):
    alphabet, lst = pair
    assume(lst)
    hd = holodeque(alphabet)
    for i in lst:
        hd.pushright(i)
    length = len(hd)
    hd.peekleft()
    assert len(hd) == length


@given(alphabet_and_initial_list_strategy())
def test_peekright_never_changes_length(pair):
    alphabet, lst = pair
    hd = holodeque(alphabet)
    size = 0
    for i in lst:
        size += 1
        hd.pushright(i)
        hd.peekright()
        assert size == len(hd)


@given(alphabet_and_initial_list_strategy())
def test_peekleft_constant_when_only_pushright(pair):
    alphabet, lst = pair
    hd = holodeque(alphabet)
    for i in lst:
        hd.pushright(i)
        assert hd.peekleft() == lst[0]


@given(alphabet_and_initial_list_strategy())
def test_peekright_constant_when_only_pushleft(pair):
    alphabet, lst = pair
    hd = holodeque(alphabet)
    for i in lst:
        hd.pushleft(i)
        assert hd.peekright() == lst[0]


@given(alphabet_and_initial_list_strategy())
def test_peekright_always_what_was_last_pushed(pair):
    alphabet, lst = pair
    hd = holodeque(alphabet)
    for i in lst:
        hd.pushright(i)
        assert hd.peekright() == i


@given(alphabet_and_initial_list_strategy())
def test_peekleft_always_what_was_last_pushed(pair):
    alphabet, lst = pair
    hd = holodeque(alphabet)
    for i in lst:
        hd.pushleft(i)
        assert hd.peekleft() == i


@given(alphabet_and_initial_list_strategy())
def test_peekright_result_is_unique_to_parameter(pair):
    alphabet, lst = pair
    holodeques = [holodeque(alphabet) for _ in alphabet]
    hd = holodeque(alphabet)
    for i in lst:
        for hd in holodeques:
            hd.pushright(i)
    for hd, option in zip(holodeques, alphabet):
        hd.pushright(option)
        assert hd.peekright() == option


@given(alphabet_and_initial_list_strategy())
def test_peekleft_result_is_unique_to_parameter(pair):
    alphabet, lst = pair
    holodeques = [holodeque(alphabet) for _ in alphabet]
    hd = holodeque(alphabet)
    for i in lst:
        for hd in holodeques:
            hd.pushright(i)
    for hd, option in zip(holodeques, alphabet):
        hd.pushleft(option)
        assert hd.peekleft() == option


@given(push_pop_strategy())
def test_peeks_are_never_changed_by_opposite_pushes(trio):
    alphabet, lst, directions = trio
    assume(lst)
    hd = holodeque(alphabet)
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


@given(alphabet_and_initial_list_strategy())
def test_popright_always_decrements_size(pair):
    alphabet, lst = pair
    hd = holodeque(alphabet)
    for i in lst:
        hd.pushright(i)
    size = len(hd)
    while size:
        size -= 1
        hd.popright()
        assert size == len(hd)


@given(alphabet_and_initial_list_strategy())
def test_popleft_always_decrements_size(pair):
    alphabet, lst = pair
    hd = holodeque(alphabet)
    for i in lst:
        hd.pushright(i)
    size = len(hd)
    while size:
        size -= 1
        hd.popleft()
        assert size == len(hd)


@given(push_pop_strategy())
def test_pops_always_decrement_size_even_mixed(trio):
    alphabet, lst, directions = trio
    hd = holodeque(alphabet)
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


@given(alphabet_and_initial_list_strategy())
def test_popright_unchanged_by_pushleft(pair):
    alphabet, lst = pair
    assume(lst)
    hd = holodeque(alphabet)
    for i in lst:
        hd.pushleft(i)
    assert hd.peekright() == lst[0] == hd.popright()


@given(alphabet_and_initial_list_strategy())
def test_popleft_unchanged_by_pushright(pair):
    alphabet, lst = pair
    assume(lst)
    hd = holodeque(alphabet)
    for i in lst:
        hd.pushright(i)
    assert hd.peekleft() == lst[0] == hd.popleft()


@given(alphabet_and_initial_list_strategy())
def test_popright_returns_last_pushright_value(pair):
    alphabet, lst = pair
    hd = holodeque(alphabet)
    for i in lst:
        hd.pushright(i)
        assert hd.peekright() == i == hd.popright()
        hd.pushright(i)


@given(alphabet_and_initial_list_strategy())
def test_popleft_returns_last_pushleft_value(pair):
    alphabet, lst = pair
    hd = holodeque(alphabet)
    for i in lst:
        hd.pushleft(i)
        assert hd.peekleft() == i == hd.popleft()
        hd.pushleft(i)


@given(push_pop_strategy())
def test_popright_always_returns_rightmost(trio):
    alphabet, lst, directions = trio
    hd = holodeque(alphabet)
    rightmost = 0
    for val, direction in zip(lst, directions):
        hd.pushleft(val)
        if direction:
            assert hd.popright() == lst[rightmost]
            rightmost += 1


@given(push_pop_strategy())
def test_popleft_always_returns_leftmost(trio):
    alphabet, lst, directions = trio
    hd = holodeque(alphabet)
    leftmost = 0
    for val, direction in zip(lst, directions):
        hd.pushright(val)
        if direction:
            assert hd.popleft() == lst[leftmost]
            leftmost += 1


@given(alphabet_and_initial_list_strategy())
def test_peekright_constant_when_popleft(pair):
    alphabet, lst = pair
    assume(lst)
    hd = holodeque(alphabet)
    for i in lst:
        hd.pushright(i)
    rightmost = lst[-1]
    while hd:
        assert hd.peekright() == rightmost
        hd.popleft()


@given(alphabet_and_initial_list_strategy())
def test_peekleft_constant_when_popright(pair):
    alphabet, lst = pair
    assume(lst)
    hd = holodeque(alphabet)
    for i in lst:
        hd.pushright(i)
    leftmost = lst[0]
    while hd:
        assert hd.peekleft() == leftmost
        hd.popright()


@given(alphabet_and_initial_list_strategy())
def test_extendright_from_empty(pair):
    alphabet, lst = pair
    hd1 = holodeque(alphabet)
    for i in lst:
        hd1.pushright(i)
    hd2 = holodeque(alphabet)
    hd2.extendright(lst)
    assert hd1._matrix == hd2._matrix


@given(alphabet_and_initial_list_strategy())
def test_extendleft_from_empty(pair):
    alphabet, lst = pair
    hd1 = holodeque(alphabet)
    for i in lst:
        hd1.pushleft(i)
    hd2 = holodeque(alphabet)
    hd2.extendleft(lst)
    assert hd1._matrix == hd2._matrix


@given(alphabet_and_initial_list_strategy())
def test_initialization(pair):
    alphabet, lst = pair
    hd1 = holodeque(alphabet)
    hd2 = holodeque(alphabet, lst)
    for i in lst:
        hd1.pushright(i)
    assert hd1._matrix == hd2._matrix


@given(two_lists())
def test_extendright(trio):
    alphabet, lst1, lst2 = trio
    hd1 = holodeque(alphabet, lst1)
    for i in lst2:
        hd1.pushright(i)
    hd2 = holodeque(alphabet, lst1 + lst2)
    assert hd1._matrix == hd2._matrix


@given(two_lists())
def test_extendleft(trio):
    alphabet, lst1, lst2 = trio
    hd1 = holodeque(alphabet, lst1)
    for i in lst2:
        hd1.pushleft(i)
    hd2 = holodeque(alphabet, list(reversed(lst2)) + lst1)
    assert hd1._matrix == hd2._matrix


@given(two_lists())
def test_mergeright(trio):
    alphabet, lst1, lst2 = trio
    hd1 = holodeque(alphabet, lst1)
    hd2 = holodeque(alphabet, lst2)
    hd1.mergeright(hd2)
    hd3 = holodeque(alphabet, lst1 + lst2)
    assert hd1._matrix == hd3._matrix


@given(two_lists())
def test_mergeleft(trio):
    alphabet, lst1, lst2 = trio
    hd1 = holodeque(alphabet, lst1)
    hd2 = holodeque(alphabet, lst2)
    hd1.mergeleft(hd2)
    hd3 = holodeque(alphabet, lst2 + lst1)
    assert hd1._matrix == hd3._matrix


@given(two_lists())
def test_mergeleft_is_opposite_of_mergeright(trio):
    alphabet, lst1, lst2 = trio
    hd1 = holodeque(alphabet, lst1)
    hd2 = holodeque(alphabet, lst2)
    hd3 = holodeque(alphabet, lst1)
    hd4 = holodeque(alphabet, lst2)
    hd1.mergeright(hd2)
    hd4.mergeleft(hd3)
    assert hd1._matrix == hd4._matrix


@given(alphabet_and_initial_list_strategy())
def test_mergeself(pair):
    alphabet, lst = pair
    hd1 = holodeque(alphabet, lst)
    hd2 = holodeque(alphabet, lst)
    hd1.mergeright(hd1)
    hd2.mergeleft(hd2)
    hd3 = holodeque(alphabet, lst + lst)
    assert hd1._matrix == hd2._matrix == hd3._matrix


@given(alphabet_and_initial_list_strategy())
def test_mergeright_requires_holodeque(pair):
    alphabet, lst = pair
    hd = holodeque(alphabet)
    with pytest.raises(TypeError):
        hd.mergeright(lst)


@given(alphabet_and_initial_list_strategy())
def test_mergeleft_requires_holodeque(pair):
    alphabet, lst = pair
    hd = holodeque(alphabet)
    with pytest.raises(TypeError):
        hd.mergeleft(lst)


@given(two_lists())
def test_extendright_with_another_holodeque_calls_mergeright(trio):
    alphabet, lst1, lst2 = trio
    hd1 = holodeque(alphabet, lst1)
    hd2 = holodeque(alphabet, lst1)
    hd3 = holodeque(alphabet, lst2)
    hd4 = holodeque(alphabet, lst2)
    hd1.extendright(hd3)
    hd2.mergeright(hd4)
    assert hd1._matrix == hd2._matrix


@given(alphabet_and_initial_list_strategy())
def test_copy(pair):
    alphabet, lst = pair
    hd1 = holodeque(alphabet, lst)
    hd2 = hd1.copy()
    assert hd1._alphabet == hd2._alphabet
    def convert(x): return hd2._get_axis(hd1._get_element(x))
    for i in range(len(alphabet)):
        for j in range(len(alphabet)):
            hd1._matrix[i][j] == hd2._matrix[convert(i)][convert(j)]
    assert hd1._maxlen == hd2._maxlen
    assert hd1._kwargs == hd2._kwargs
    
@given(alphabet_and_initial_list_strategy())
def test_iterator(pair):
    alphabet, lst = pair
    hd = holodeque(alphabet, lst)
    assert list(hd) == lst

@given(alphabet_and_initial_list_strategy())
def test_reversed(pair):
    alphabet, lst = pair
    hd = holodeque(alphabet, lst)
    assert list(reversed(hd)) == list(reversed(lst))




# takes 1 hour (3717.04s) but confirms uniqueness up to 10 (11+ can be proven mathematically)
# @settings(deadline=None)
# @given(alphabet_and_initial_list_strategy_small_version())
# def test_all_permutations_are_unique(pair):
#     alphabet, lst = pair
#     matrices = set()

#     def matrixtuple(matrix):
#         return tuple(tuple(row) for row in matrix)

#     for perm in permutations(range(len(lst))):
#         hd = holodeque(alphabet)
#         for val in perm:
#             hd.pushright(lst[val])
#         matrices.add(matrixtuple(hd._matrix))

#     counts = Counter(lst)
#     total_elements = sum(counts.values())
#     total_permutations = factorial(total_elements)
#     divisor = reduce(lambda x, y: x * factorial(y), counts.values(), 1)
#     combinations = total_permutations // divisor
#     assert len(matrices) == combinations
