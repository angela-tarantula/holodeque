from collections import deque
from src.holodeque import holodeque
from hypothesis import given, assume
from hypothesis import strategies as st

@given(st.lists(st.integers()))
def test_popright(values):
    assume(values)
    hd = holodeque(iterable=values, alphabet=set(values))
    dq = deque(values)
    while hd and dq:
        assert hd.popright() == dq.pop()

@given(st.lists(st.integers()))


if __name__ == "__main__":
    test_popright()