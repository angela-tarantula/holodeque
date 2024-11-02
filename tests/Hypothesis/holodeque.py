import pytest
from src.holodeque import holodeque
from hypothesis import given, assume, strategies as st

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
def test_initialization(pair):
    alphabet, lst = pair
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
