import pytest
from collections import deque
from src.holodeque import holodeque
from hypothesis import given, assume
from hypothesis.strategies import integers, frozensets, lists, data, composite, sampled_from


@composite
def alphabet_and_element(draw):
    alphabet = draw(frozensets(integers(), min_size=2))
    element = draw(sampled_from(list(alphabet)))
    return alphabet, element


@given(frozensets(integers(), min_size=2))
def test_empty_contains_nothing(alphabet):
    hd = holodeque(alphabet)
    assert not hd and len(hd) == 0


@given(frozensets(integers(), min_size=2))
def test_empty_popright_raises_index_error(alphabet):
    hd = holodeque(alphabet)
    with pytest.raises(IndexError):
        hd.popright()


@given(frozensets(integers(), min_size=2))
def test_empty_popleft_raises_index_error(alphabet):
    hd = holodeque(alphabet)
    with pytest.raises(IndexError):
        hd.popleft()


@given(frozensets(integers(), min_size=2))
def test_empty_peekright_raises_index_error(alphabet):
    hd = holodeque(alphabet)
    with pytest.raises(IndexError):
        hd.peekright()


@given(frozensets(integers(), min_size=2))
def test_empty_peekleft_raises_index_error(alphabet):
    hd = holodeque(alphabet)
    with pytest.raises(IndexError):
        hd.peekleft()


@given(alphabet_and_element())
def test_fist_push_makes_length_one(pair):
    alphabet, element = pair
    hd1 = holodeque(alphabet)
    hd1.pushright(element)
    assert hd1 and len(hd1) == 1
    hd2 = holodeque(alphabet)
    hd2.pushleft(element)
    assert hd2 and len(hd2) == 1


@given(alphabet_and_element())
def test_first_pushes_are_equivalent(pair):
    alphabet, element = pair
    hd1 = holodeque(alphabet)
    hd1.pushright(element)
    hd2 = holodeque(alphabet)
    hd2.pushleft(element)
    assert hd1._matrix == hd2._matrix


@given(alphabet_and_element())
def test_first_pushes_change_matrix(pair):
    alphabet, element = pair
    hd1 = holodeque(alphabet)
    hd1.pushright(element)
    hd2 = holodeque(alphabet)
    assert hd1._matrix != hd2._matrix


@given(alphabet_and_element())
def test_first_peeks_dont_change_length(pair):
    alphabet, element = pair
    hd = holodeque(alphabet)
    hd.pushright(element)
    hd.peekleft()
    assert len(hd) == 1
    hd.peekright()
    assert len(hd) == 1


@given(alphabet_and_element())
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


@given(alphabet_and_element())
def test_first_peeks_are_equivalent(pair):
    alphabet, element = pair
    hd = holodeque(alphabet)
    hd.pushright(element)
    assert hd.peekleft() == hd.peekright() == element


@given(alphabet_and_element())
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


@given(alphabet_and_element())
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


@given(alphabet_and_element())
def test_pop_single_makes_empty(pair):
    alphabet, element = pair
    hd = holodeque(alphabet)
    hd.pushright(element)
    hd.popright()
    assert not hd and len(hd) == 0
    hd.pushright(element)
    hd.popleft()
    assert not hd and len(hd) == 0


@given(alphabet_and_element())
def test_pop_singles_are_equivalent(pair):
    alphabet, element = pair
    hd = holodeque(alphabet)
    hd.pushright(element)
    assert element == hd.popright()
    hd.pushright(element)
    assert element == hd.popleft()


@given(frozensets(integers(), min_size=2), data())
def test_pushright_increments_length(alphabet, data):
    lst = data.draw(lists(sampled_from(list(alphabet))))
    hd = holodeque(alphabet)
    size = 0
    for i in lst:
        hd.pushright(i)
        size += 1
        assert len(hd) == size
        

@given(frozensets(integers(), min_size=2), data())
def test_pushright_always_makes_new_matrix(alphabet, data):
    lst = data.draw(lists(sampled_from(list(alphabet))))
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

# add more tests here before testing initialization

@given(frozensets(integers(), min_size=2), data())
def test_initialization(alphabet, data):
    lst = data.draw(lists(sampled_from(list(alphabet))))
    hd1 = holodeque(alphabet)
    hd2 = holodeque(alphabet, lst)
    for i in lst:
        hd1.pushright(i)
    for i in reversed(lst):
        assert hd1.popright() == hd2.popright()
    assert not hd1
    assert not hd2

# @given(st.frozensets(st.integers(), min_size=1, max_size=10), )
# def test_pushright(alphabet, val):
# test order of alphabet
