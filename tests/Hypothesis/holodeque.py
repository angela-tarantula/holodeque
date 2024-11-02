import pytest
from collections import deque
from src.holodeque import holodeque
from hypothesis import given, assume
from hypothesis.strategies import integers, frozensets, lists, data, composite, sampled_from


@composite
def alphabet_and_element(draw):
    alphabet = draw(frozensets(integers(), min_size=1))
    element = draw(sampled_from(list(alphabet)))
    return alphabet, element

@given(frozensets(integers(), min_size=1))
def test_empty(alphabet):
    hd = holodeque(alphabet)
    assert not hd and len(hd) == 0

@given(frozensets(integers(), min_size=1))
def test_empty_popright(alphabet):
    hd = holodeque(alphabet)
    with pytest.raises(IndexError):
        hd.popright()

@given(frozensets(integers(), min_size=1))
def test_empty_popleft(alphabet):
    hd = holodeque(alphabet)
    with pytest.raises(IndexError):
        hd.popleft()

@given(frozensets(integers(), min_size=1))
def test_empty_peekright(alphabet):
    hd = holodeque(alphabet)
    with pytest.raises(IndexError):
        hd.peekright()

@given(frozensets(integers(), min_size=1))
def test_empty_peekleft(alphabet):
    hd = holodeque(alphabet)
    with pytest.raises(IndexError):
        hd.peekleft()

@given(alphabet_and_element())
def test_empty_pushright(pair):
    alphabet, element = pair
    hd = holodeque(alphabet)
    hd.pushright(element)
    assert len(hd) == 1
    assert element == hd.peekright()
    assert  element == hd.popright()
    assert not hd

@given(alphabet_and_element())
def test_empty_pushleft(pair):
    alphabet, element = pair
    hd = holodeque(alphabet)
    hd.pushleft(element)
    assert len(hd) == 1
    assert element == hd.peekleft()
    assert element == hd.popleft()
    assert not hd


# @given(st.frozensets(st.integers(), min_size=1, max_size=10), )
# def test_pushright(alphabet, val):
# test order of alphabet