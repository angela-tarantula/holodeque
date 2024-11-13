import unittest
from collections import deque

from src.binary_holodeque import binarydeque


class TestBinarydeque(unittest.TestCase):

    def setUp(self):
        self.dq = deque([False, True])
        self.bdeque = binarydeque([False, True])

    def test_append_pushright(self):
        self.dq.append(False)
        self.bdeque.pushright(False)
        self.assertEqual(list(self.dq), list(self.bdeque))

    def test_appendleft_pushleft(self):
        self.dq.appendleft(True)
        self.bdeque.pushleft(True)
        self.assertEqual(list(self.dq), list(self.bdeque))

    def test_pop_popright(self):
        self.assertEqual(self.dq.pop(), self.bdeque.popright())
        self.assertEqual(list(self.dq), list(self.bdeque))

    def test_popleft_popleft(self):
        self.assertEqual(self.dq.popleft(), self.bdeque.popleft())
        self.assertEqual(list(self.dq), list(self.bdeque))

    def test_peekleft(self):
        self.assertEqual(self.dq[0], self.bdeque.peekleft())

    def test_peekright(self):
        self.assertEqual(self.dq[-1], self.bdeque.peekright())

    def test_extend_extendright(self):
        self.dq.extend([False, True])
        self.bdeque.extendright([False, True])
        self.assertEqual(list(self.dq), list(self.bdeque))

    def test_extendleft_extendleft(self):
        self.dq.extendleft([False, True])
        self.bdeque.extendleft([False, True])
        self.assertEqual(list(self.dq), list(self.bdeque))

    def test_concatright(self):
        bdeque2 = binarydeque([True, False])
        self.bdeque.concatright(bdeque2)
        self.assertEqual(list(self.bdeque), [False, True, True, False])

    def test_concatleft(self):
        bdeque2 = binarydeque([True, False])
        self.bdeque.concatleft(bdeque2)
        self.assertEqual(list(self.bdeque), [True, False, False, True])

    def test_copy(self):
        dq_copy = self.dq.copy()
        bdeque_copy = self.bdeque.copy()
        self.assertEqual(list(dq_copy), list(bdeque_copy))

    def test_rotate(self):
        self.dq.rotate(1)
        self.bdeque.rotate(1)
        self.assertEqual(list(self.dq), list(self.bdeque))

        self.dq.rotate(-1)
        self.bdeque.rotate(-1)
        self.assertEqual(list(self.dq), list(self.bdeque))

    def test_remove(self):
        self.dq.remove(True)
        self.bdeque.remove(True)
        self.assertEqual(list(self.dq), list(self.bdeque))

    def test_count(self):
        self.assertEqual(self.dq.count(True), self.bdeque.count(True))
        self.assertEqual(self.dq.count(False), self.bdeque.count(False))

    def test_reverse(self):
        self.dq.reverse()
        self.bdeque.reverse()
        self.assertEqual(list(self.dq), list(self.bdeque))

    def test_clear(self):
        self.dq.clear()
        self.bdeque.clear()
        self.assertEqual(list(self.dq), list(self.bdeque))


if __name__ == '__main__':
    unittest.main()
