import unittest
from collections import deque
from holodeque.src.binary_holodeque import binarydeque


class TestBinarydeque(unittest.TestCase):

    def setUp(self):
        self.dq = deque([0, 1])
        self.mdq = binarydeque([0, 1])

    def test_append_pushright(self):
        self.dq.append(0)
        self.mdq.pushright(0)
        self.assertEqual(list(self.dq), list(self.mdq))

    def test_appendleft_pushleft(self):
        self.dq.appendleft(1)
        self.mdq.pushleft(1)
        self.assertEqual(list(self.dq), list(self.mdq))

    def test_pop_popright(self):
        self.assertEqual(self.dq.pop(), self.mdq.popright())
        self.assertEqual(list(self.dq), list(self.mdq))

    def test_popleft_popleft(self):
        self.assertEqual(self.dq.popleft(), self.mdq.popleft())
        self.assertEqual(list(self.dq), list(self.mdq))

    def test_peekleft(self):
        self.assertEqual(self.dq[0], self.mdq.peekleft())

    def test_peekright(self):
        self.assertEqual(self.dq[-1], self.mdq.peekright())

    def test_extend_extendright(self):
        self.dq.extend([0, 1])
        self.mdq.extendright([0, 1])
        self.assertEqual(list(self.dq), list(self.mdq))

    def test_extendleft_extendleft(self):
        self.dq.extendleft([0, 1])
        self.mdq.extendleft([0, 1])
        self.assertEqual(list(self.dq), list(self.mdq))

    def test_mergeright(self):
        mdq2 = binarydeque([1, 0])
        self.mdq.mergeright(mdq2)
        self.assertEqual(list(self.mdq), [0, 1, 1, 0])

    def test_mergeleft(self):
        mdq2 = binarydeque([1, 0])
        self.mdq.mergeleft(mdq2)
        self.assertEqual(list(self.mdq), [1, 0, 0, 1])

    def test_copy(self):
        dq_copy = self.dq.copy()
        mdq_copy = self.mdq.copy()
        self.assertEqual(list(dq_copy), list(mdq_copy))

    def test_rotate(self):
        self.dq.rotate(1)
        self.mdq.rotate(1)
        self.assertEqual(list(self.dq), list(self.mdq))

        self.dq.rotate(-1)
        self.mdq.rotate(-1)
        self.assertEqual(list(self.dq), list(self.mdq))

    def test_remove(self):
        self.dq.remove(1)
        self.mdq.remove(1)
        self.assertEqual(list(self.dq), list(self.mdq))

    def test_count(self):
        self.assertEqual(self.dq.count(1), self.mdq.count(1))
        self.assertEqual(self.dq.count(0), self.mdq.count(0))

    def test_reverse(self):
        self.dq.reverse()
        self.mdq.reverse()
        self.assertEqual(list(self.dq), list(self.mdq))

    def test_clear(self):
        self.dq.clear()
        self.mdq.clear()
        self.assertEqual(list(self.dq), list(self.mdq))

    def test_invalid_input(self):
        with self.assertRaises(ValueError):
            self.mdq.pushright(2)


if __name__ == '__main__':
    unittest.main()
