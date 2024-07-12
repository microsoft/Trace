from graphviz import Digraph
import builtins
import re

# Get a list of all names in the builtins module
builtins_list = dir(builtins)
# Filter for function names; this includes exceptions, so you might want to refine this
global_functions_list = [name for name in builtins_list if callable(getattr(builtins, name))]


def contain(container_of_nodes, node):
    # check for identity instead of value
    return any([node is n for n in container_of_nodes])


def parse_eqs_to_dict(text):
    """
    Parse the text of equations into a didctionary

        x0 = 1
        x1=2
        x2=`2`
        x3= def fun():\n    print('hello')\n
        abc_test1=test

    would be parsed into

    {'x0': '1', 'x1': '2', 'x2': '2', 'x3': "def fun():\nprint('hello')", 'abc_test1': 'test'}
    """
    lines = text.split("\n")
    result_dict = {}
    last_key = None
    for line in lines:
        if line == "":
            continue
        if "=" in line:
            key, value = line.split("=", 1)
            last_key = key.strip()
            result_dict[last_key] = value.replace("`", "")
        elif last_key:
            result_dict[last_key] += "\n" + line.replace("`", "")
    return result_dict


class MinHeap:
    def __init__(self, arr=None):
        if arr is None:
            self.heap = []
        else:
            self.heap = arr
            self.heapify(self.heap)

    def __contains__(self, item):
        # return item in self.heap
        return contain(self.heap, item)

    def __len__(self):
        return len(self.heap)

    def push(self, item):
        self.heap.append(item)
        self._siftup(len(self.heap) - 1)

    def pop(self):
        if len(self.heap) == 1:
            return self.heap.pop()
        root = self.heap[0]
        self.heap[0] = self.heap.pop()  # Move the last element to the root
        self._siftdown(0)
        return root

    def peek(self):
        return self.heap[0] if self.heap else None

    def _siftup(self, idx):
        while idx > 0:
            parent_idx = (idx - 1) // 2
            # >
            if self.heap[parent_idx].gt(self.heap[idx]):
                self.heap[parent_idx], self.heap[idx] = self.heap[idx], self.heap[parent_idx]
                idx = parent_idx
            else:
                break

    def _siftdown(self, idx):
        last_idx = len(self.heap) - 1
        while True:
            left_child_idx = 2 * idx + 1
            right_child_idx = 2 * idx + 2
            smallest_idx = idx

            # if left_child_idx <= last_idx and self.heap[left_child_idx] < self.heap[smallest_idx]:
            if left_child_idx <= last_idx and self.heap[left_child_idx].lt(self.heap[smallest_idx]):
                smallest_idx = left_child_idx
            # if right_child_idx <= last_idx and self.heap[right_child_idx] < self.heap[smallest_idx]:
            if right_child_idx <= last_idx and self.heap[right_child_idx].lt(self.heap[smallest_idx]):
                smallest_idx = right_child_idx

            if smallest_idx != idx:
                self.heap[idx], self.heap[smallest_idx] = self.heap[smallest_idx], self.heap[idx]
                idx = smallest_idx
            else:
                break

    def heapify(self, arr):
        import copy

        self.heap = copy.copy(arr)
        for i in range((len(self.heap) - 2) // 2, -1, -1):
            self._siftdown(i)


def for_all_methods(decorator):
    """Applying a decorator to all methods of a class."""

    def decorate(cls):
        for name, attr in cls.__dict__.items():
            if callable(attr) and not name.startswith("__"):
                setattr(cls, name, decorator(attr))
        return cls

    return decorate
