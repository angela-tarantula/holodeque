import timeit
import cProfile
import pstats

class Node:
    def __init__(self, value=None, next=None, prev=None):
         self.value = value
         self.next = next
         self.prev = prev

class LinkedList:

    def __init__(self):
        self.head = Node()
        self.tail = Node()
        self.head.next = self.tail
        self.tail.prev = self.head
    
    def pushright(self, value):
        new_node = Node(value)
        new_node.prev = self.tail.prev
        new_node.next = self.tail
        self.tail.prev.next = new_node
        self.tail.prev = new_node
    
    def pushleft(self, value):
        new_node = Node(value)
        new_node.next = self.head.next
        new_node.prev = self.head
        self.head.next.prev = new_node
        self.head.next = new_node
    
    def popright(self):
        if self.tail.prev == self.head:
            return None
        value = self.tail.prev.value
        self.tail.prev = self.tail.prev.prev
        self.tail.prev.next = self.tail
        return value
    
    def popleft(self):
        if self.head.next == self.tail:
            return None
        value = self.head.next.value
        self.head.next = self.head.next.next
        self.head.next.prev = self.head
        return value

def test_performance():
    # Example setup for testing performance of mdeque
    ll = LinkedList()
    for _ in range(1_000_000):  # Simulate a large number of operations
        ll.pushright(1)
        ll.pushleft(0)
        ll.popright()
        ll.popleft()


# Profile the function
cProfile.run('test_performance()', 'profile_results')

p = pstats.Stats('profile_results')
# Sort by cumulative time, print top 10 functions
p.strip_dirs().sort_stats('cumulative').print_stats(10)
