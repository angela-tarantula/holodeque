import unittest
from collections import deque
from src.binary_holodeque import binarydeque


class TestBinarydeque(unittest.TestCase):

    def setUp(self):
        self.dq = deque([0, 1])
        self.bdeque = binarydeque([0, 1])

    def test_append_pushright(self):
        self.dq.append(0)
        self.bdeque.pushright(0)
        self.assertEqual(list(self.dq), list(self.bdeque))

    def test_appendleft_pushleft(self):
        self.dq.appendleft(1)
        self.bdeque.pushleft(1)
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
        self.dq.extend([0, 1])
        self.bdeque.extendright([0, 1])
        self.assertEqual(list(self.dq), list(self.bdeque))

    def test_extendleft_extendleft(self):
        self.dq.extendleft([0, 1])
        self.bdeque.extendleft([0, 1])
        self.assertEqual(list(self.dq), list(self.bdeque))

    def test_mergeright(self):
        bdeque2 = binarydeque([1, 0])
        self.bdeque.mergeright(bdeque2)
        self.assertEqual(list(self.bdeque), [0, 1, 1, 0])

    def test_mergeleft(self):
        bdeque2 = binarydeque([1, 0])
        self.bdeque.mergeleft(bdeque2)
        self.assertEqual(list(self.bdeque), [1, 0, 0, 1])

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
        self.dq.remove(1)
        self.bdeque.remove(1)
        self.assertEqual(list(self.dq), list(self.bdeque))

    def test_count(self):
        self.assertEqual(self.dq.count(1), self.bdeque.count(1))
        self.assertEqual(self.dq.count(0), self.bdeque.count(0))

    def test_reverse(self):
        self.dq.reverse()
        self.bdeque.reverse()
        self.assertEqual(list(self.dq), list(self.bdeque))

    def test_clear(self):
        self.dq.clear()
        self.bdeque.clear()
        self.assertEqual(list(self.dq), list(self.bdeque))

    def test_invalid_input(self):
        with self.assertRaises(ValueError):
            self.bdeque.pushright(2)


if __name__ == '__main__':
    unittest.main()
