## FunctionDef contain(container_of_nodes, node)
**contain**: The function of contain is to check if a given node is present in a container of nodes.
**parameters**:
- container_of_nodes: A container (such as a list or set) that holds nodes.
- node: The node to be checked for presence in the container.
**Code Description**:
The `contain` function takes in a container of nodes and a node as parameters. It uses a list comprehension to iterate over the container and checks if the given node is identical (using the `is` operator) to any of the nodes in the container. The function returns `True` if the node is found in the container, and `False` otherwise.

This function is used in various parts of the project. In the `opto\trace\bundle.py/FunModule/forward` function, the `contain` function is called to check if a node is present in the `container_of_nodes` list. It is used to determine the external dependencies of the operator function.

In the `opto\trace\utils.py/MinHeap/__contains__` function, the `contain` function is used to check if an item is present in the `self.heap` list.

The `contain` function is also used in the `tests\unit_tests\test_bundle.py/run` function to check if a node is present in a container of nodes.

**Note**: The `contain` function checks for identity (using the `is` operator) instead of value equality. This means that it will only return `True` if the node is the exact same object in memory as one of the nodes in the container.

**Output Example**: 
```python
container_of_nodes = [node(1), node(2), node(3)]
node = node(2)
print(contain(container_of_nodes, node))
# Output: True
```
## FunctionDef parse_eqs_to_dict(text)
**parse_eqs_to_dict**: The function of parse_eqs_to_dict is to parse a given text containing equations into a dictionary.

**parameters**: The parameters of this Function.
· text: A string containing equations separated by new lines. Each equation should be in the format `key=value`.

**Code Description**: The parse_eqs_to_dict function processes a string of equations and converts it into a dictionary where each key-value pair represents an equation. The function follows these steps:

1. **Splitting the Input Text**: The input text is split into individual lines using the newline character (`\n`) as the delimiter.
2. **Initialization**: An empty dictionary `result_dict` is initialized to store the parsed key-value pairs. A variable `last_key` is also initialized to keep track of the last processed key.
3. **Processing Each Line**:
   - The function iterates over each line in the split text.
   - If a line is empty, it is skipped.
   - If a line contains an equals sign (`=`), it is split into a key and a value at the first occurrence of the equals sign. The key is stripped of any leading or trailing whitespace, and the value has any backticks (`) removed. The key-value pair is then added to the dictionary, and `last_key` is updated to the current key.
   - If a line does not contain an equals sign but `last_key` is set, the line is considered a continuation of the previous value. The line is appended to the value of `last_key` in the dictionary, with any backticks removed.
4. **Returning the Result**: After processing all lines, the function returns the populated dictionary.

**Note**: 
- The function assumes that each equation is either on a single line or that subsequent lines without an equals sign are continuations of the previous value.
- Backticks (`) in the values are removed during processing.

**Output Example**: 
Given the input text:
```
x0 = 1
x1=2
x2=`2`
x3= def fun():\n    print('hello')\n
abc_test1=test
```
The function would return:
```
{
    'x0': '1',
    'x1': '2',
    'x2': '2',
    'x3': "def fun():\nprint('hello')",
    'abc_test1': 'test'
}
```
## ClassDef MinHeap
**MinHeap**: The function of MinHeap is to implement a minimum heap data structure, which supports efficient retrieval and removal of the smallest element.

**attributes**: The attributes of this Class.
· heap: A list that stores the elements of the heap.

**Code Description**: The MinHeap class provides a minimum heap implementation with various methods to manage the heap's elements. The class supports initialization with an optional array, element insertion, element removal, and peeking at the smallest element. It also includes internal methods to maintain the heap property.

- `__init__(self, arr=None)`: Initializes the heap. If an array is provided, it converts the array into a heap using the `heapify` method. Otherwise, it initializes an empty heap.
- `__contains__(self, item)`: Checks if an item is in the heap using a helper function `contain`.
- `__len__(self)`: Returns the number of elements in the heap.
- `push(self, item)`: Adds a new item to the heap and ensures the heap property is maintained by calling the `_siftup` method.
- `pop(self)`: Removes and returns the smallest item from the heap. It maintains the heap property by calling the `_siftdown` method after removing the root.
- `peek(self)`: Returns the smallest item without removing it from the heap.
- `_siftup(self, idx)`: Ensures the heap property is maintained from a given index upwards to the root.
- `_siftdown(self, idx)`: Ensures the heap property is maintained from a given index downwards to the leaves.
- `heapify(self, arr)`: Converts an array into a heap by copying the array and calling `_siftdown` on each non-leaf node.

The MinHeap class is utilized in the `backward` method of the `Node` class in `opto\trace\nodes.py`. In this context, MinHeap is used to manage a priority queue for nodes during a backward pass operation. The `backward` method initializes a MinHeap with the current node and uses it to efficiently process nodes in the correct order, ensuring that feedback is propagated correctly through the graph.

**Note**: 
- The elements stored in the heap must support comparison operations (`lt` and `gt` methods).
- The `contain` function used in `__contains__` is assumed to be defined elsewhere in the codebase.

**Output Example**: 
- `push(item)`: Adds `item` to the heap.
- `pop()`: Returns the smallest element, e.g., `3`.
- `peek()`: Returns the smallest element without removing it, e.g., `3`.
- `__len__()`: Returns the number of elements in the heap, e.g., `5`.
- `__contains__(item)`: Returns `True` if `item` is in the heap, otherwise `False`.
### FunctionDef __init__(self, arr)
**__init__**: The function of __init__ is to initialize a MinHeap object, optionally transforming an input array into a valid min-heap.

**parameters**: The parameters of this Function.
· arr: An optional array to be transformed into a min-heap. If not provided, an empty heap is initialized.

**Code Description**: The __init__ method is the constructor for the MinHeap class. It initializes the heap based on the provided input array. If no array is provided (`arr` is `None`), it initializes an empty list to represent the heap. If an array is provided, it assigns this array to the heap and then calls the `heapify` method to transform the array into a valid min-heap.

The `heapify` method is responsible for ensuring that the array satisfies the heap property, where each parent node is less than or equal to its child nodes. This transformation is crucial for the correct functioning of the heap operations.

**Note**: Points to note about the use of the code
- If an array is provided during initialization, it will be automatically transformed into a min-heap.
- The `heapify` method modifies the heap in place and ensures the heap property is maintained.
- Proper initialization of the heap is essential for the efficiency and correctness of subsequent heap operations such as insertion and deletion.
***
### FunctionDef __contains__(self, item)
**__contains__**: The function of `__contains__` is to check if a given item is present in the heap of the `MinHeap` class.

**parameters**: The parameters of this function.
· item: The item to be checked for presence in the heap.

**Code Description**: The `__contains__` function is a special method in Python that allows the use of the `in` keyword to check for the presence of an item in an instance of the `MinHeap` class. This function takes a single parameter, `item`, which represents the item to be checked.

Internally, the function calls the `contain` function, passing `self.heap` and `item` as arguments. The `contain` function iterates over the `self.heap` list and checks if the `item` is identical to any of the elements in the list using the `is` operator. If the `item` is found, the `contain` function returns `True`; otherwise, it returns `False`.

This method provides a convenient way to check for the presence of an item in the heap, leveraging the identity check mechanism provided by the `contain` function.

**Note**: The `contain` function checks for identity (using the `is` operator) instead of value equality. This means that `__contains__` will only return `True` if the `item` is the exact same object in memory as one of the elements in `self.heap`.

**Output Example**:
```python
min_heap = MinHeap()
min_heap.heap = [node(1), node(2), node(3)]
item = node(2)
print(item in min_heap)
# Output: True
```
***
### FunctionDef __len__(self)
**__len__**: The function of __len__ is to return the number of elements in the MinHeap.

**parameters**: The parameters of this Function.
· self: Refers to the instance of the MinHeap class.

**Code Description**: The __len__ method is a special method in Python that is used to define the behavior of the len() function for instances of a class. In this case, the __len__ method is implemented for the MinHeap class. When len() is called on an instance of MinHeap, this method returns the number of elements currently stored in the heap. It achieves this by returning the length of the internal list self.heap, which is used to store the heap elements.

**Note**: 
- This method does not take any parameters other than self.
- It is important to ensure that self.heap is always a list, as the len() function is called on it.

**Output Example**: 
If the MinHeap instance contains 5 elements, calling len(min_heap_instance) will return 5.
***
### FunctionDef push(self, item)
**push**: The function of push is to add a new item to the MinHeap and maintain the heap property.

**parameters**: The parameters of this Function.
· item: The item to be added to the heap.

**Code Description**: The push function is a method of the MinHeap class that adds a new item to the heap and ensures that the heap property is maintained. When an item is pushed onto the heap, it is first appended to the end of the heap list. This operation increases the size of the heap by one.

After appending the new item, the push function calls the _siftup method with the index of the newly added item, which is the last index of the heap list. The _siftup method is responsible for moving the new item up the heap until the heap property is restored. The heap property in a MinHeap requires that each parent node is less than or equal to its child nodes. The _siftup method ensures that this property is maintained by comparing the new item with its parent and swapping them if necessary. This process continues iteratively until the new item is in a position where the heap property is satisfied or it becomes the root of the heap.

The push function is used in the backward method of the Node class in the context of a priority queue. In the backward method, nodes are processed in a specific order, and the MinHeap is used to manage this order efficiently. When a parent node needs to be added to the queue, the push function is called to insert the parent node into the MinHeap, ensuring that the heap property is maintained and the nodes are processed in the correct order.

**Note**:
- The push function relies on the _siftup method to maintain the heap property.
- The heap property ensures that the smallest element is always at the root of the MinHeap.
- The elements in the heap must implement the gt method correctly for the _siftup method to function properly.
- The push function is integral to the operation of the MinHeap in managing the order of nodes in the backward method of the Node class.
***
### FunctionDef pop(self)
**pop**: The function of pop is to remove and return the root element from the heap.

**parameters**:
- self: The instance of the MinHeap class.

**Code Description**:
The pop function is a method of the MinHeap class that is used to remove and return the root element from the heap. The function first checks if the length of the heap is equal to 1, which indicates that there is only one element in the heap. In this case, the function simply calls the pop method of the heap list and returns the popped element.

If there are more than one element in the heap, the function proceeds to assign the value of the root element (the first element in the heap) to the variable "root". Then, it replaces the root element with the last element in the heap by assigning the popped element from the heap list to the index 0 of the heap list. This step is necessary to maintain the heap property after removing the root element.

After replacing the root element, the function calls the _siftdown method to sift down the new root element to its correct position in the heap. This ensures that the heap property is maintained and the new root element is correctly positioned relative to its children.

Finally, the function returns the original root element that was stored in the "root" variable.

The pop function is called by other methods in the MinHeap class, such as the heapify method. It relies on the _siftdown method to maintain the heap property after removing the root element.

**Note**:
- The pop function assumes that the heap is represented as a list.
- The function modifies the heap in place and does not return any value.
- Proper use of the pop function is crucial for maintaining the correctness of heap operations and ensuring that the heap property is maintained.

**Output Example**:
If the heap is [5, 7, 9, 11, 13] and the pop function is called, the function will remove and return the root element, which is 5. After the pop operation, the heap will be [7, 9, 11, 13].
***
### FunctionDef peek(self)
**peek**: The function of peek is to return the smallest element in the MinHeap without removing it.

**parameters**: The parameters of this Function.
· None

**Code Description**: The peek function is a method of the MinHeap class. It checks if the heap list is non-empty. If the heap contains elements, it returns the first element of the heap list, which is the smallest element due to the properties of a MinHeap. If the heap is empty, it returns None. This function allows users to inspect the smallest element in the heap without modifying the heap structure.

**Note**: 
- The peek function does not alter the state of the heap.
- It is a read-only operation and is useful for checking the minimum element efficiently.

**Output Example**: 
- If the heap is [1, 3, 5, 7], peek() will return 1.
- If the heap is empty, peek() will return None.
***
### FunctionDef _siftup(self, idx)
**_siftup**: The function of _siftup is to maintain the heap property by moving an element up the heap until the heap property is restored.

**parameters**: The parameters of this Function.
· idx: The index of the element to be moved up in the heap.

**Code Description**: The _siftup function is a helper method used to maintain the heap property in a MinHeap data structure. When an element is added to the heap, it may violate the heap property, which requires that each parent node is less than or equal to its child nodes. The _siftup function corrects this by comparing the element at the given index (idx) with its parent. If the element is smaller than its parent, they are swapped. This process continues iteratively until the element is in a position where the heap property is satisfied, or it becomes the root of the heap.

The function is called by the push method of the MinHeap class. When a new item is added to the heap using the push method, the item is appended to the end of the heap list. The _siftup function is then called with the index of this new item (which is the last index of the list). This ensures that the new item is moved to its correct position in the heap, maintaining the heap property.

**Note**: 
- The _siftup function assumes that the heap property is only violated between the element at the given index and its parent. It does not check or correct violations further up the tree.
- This function is designed to work with a MinHeap, where the smallest element should always be at the root.
- The function relies on the gt method of the elements in the heap to compare their values. Ensure that the elements in the heap implement this method correctly.
***
### FunctionDef _siftdown(self, idx)
**_siftdown**: The function of _siftdown is to maintain the heap property by sifting down an element at a given index in the heap.

**parameters**: The parameters of this Function.
· idx: The index of the element to be sifted down in the heap.

**Code Description**: The _siftdown function is a helper method used to ensure that the heap property is maintained after an element has been moved to a new position in the heap. This function is particularly useful in operations where the heap structure might be violated, such as after removing the root element or during the initial heap construction.

The function operates as follows:
1. It calculates the index of the last element in the heap.
2. It enters a loop where it calculates the indices of the left and right children of the current element.
3. It initializes the smallest index as the current index.
4. It compares the current element with its left and right children to find the smallest element among them.
5. If one of the children is smaller than the current element, it swaps the current element with the smallest child and updates the current index to the index of the smallest child.
6. The loop continues until the current element is smaller than both of its children or it has no children.

The function is called by the pop and heapify methods of the MinHeap class:
- In the pop method, _siftdown is used after the root element is removed and the last element is moved to the root position. This ensures that the new root element is correctly positioned to maintain the heap property.
- In the heapify method, _siftdown is called for each non-leaf element in the array to transform the array into a valid heap.

**Note**: Points to note about the use of the code
- The function assumes that the heap is represented as a list and that each element in the heap has a method lt for comparison.
- The function modifies the heap in place and does not return any value.
- Proper use of _siftdown is crucial for maintaining the efficiency and correctness of heap operations such as insertion, deletion, and heap construction.
***
### FunctionDef heapify(self, arr)
**heapify**: The function of heapify is to transform an arbitrary array into a valid min-heap.

**parameters**: The parameters of this Function.
· arr: The array to be transformed into a min-heap.

**Code Description**: The heapify function is designed to convert a given array into a min-heap, ensuring that the heap property is maintained throughout the array. This function is a method of the MinHeap class and operates as follows:

1. The function begins by importing the copy module and creating a shallow copy of the input array `arr` to avoid modifying the original array. This copy is stored in the instance variable `self.heap`.
2. It then iterates over the indices of the non-leaf elements of the array in reverse order, starting from the last non-leaf node and moving towards the root. The range for this iteration is calculated as `(len(self.heap) - 2) // 2` to `-1`.
3. For each index `i` in this range, the function calls the helper method `_siftdown(i)`. The _siftdown method is responsible for maintaining the heap property by sifting down the element at index `i` to its correct position in the heap.

The heapify function is called during the initialization of the MinHeap object if an array is provided. This ensures that any array passed to the MinHeap constructor is automatically transformed into a valid min-heap.

**Note**: Points to note about the use of the code
- The heapify function assumes that the elements of the array have a method `lt` for comparison, which is used by the _siftdown method.
- The function modifies the heap in place and does not return any value.
- Proper use of the heapify function is crucial for initializing the heap correctly, which in turn ensures the efficiency and correctness of subsequent heap operations such as insertion and deletion.
***
## FunctionDef for_all_methods(decorator)
**for_all_methods**: The function of for_all_methods is to apply a decorator to all methods of a class.

**parameters**:
- decorator: The decorator function that will be applied to all methods of the class.

**Code Description**:
The `for_all_methods` function is a higher-order function that takes a decorator as input and returns a new decorator. The returned decorator can be used to decorate a class, applying the input decorator to all methods of the class.

The `for_all_methods` function first defines an inner function called `decorate`. This function takes a class as input and iterates over all the attributes of the class using the `__dict__` attribute. For each attribute that is callable (i.e., a method) and does not start with "__" (i.e., not a special method), the function applies the input decorator to the method using the `setattr` function. This effectively replaces the original method with the decorated version.

Finally, the `decorate` function returns the modified class with the decorated methods.

The `for_all_methods` function itself returns the `decorate` function, allowing it to be used as a decorator for classes.

**Note**:
- The input decorator should be a function that takes a method as input and returns a new method.
- The input decorator will be applied to all methods of the class, including inherited methods.
- The input decorator will replace the original methods with the decorated versions.

**Output Example**:
```python
@for_all_methods
def my_decorator(method):
    def wrapper(*args, **kwargs):
        # Do something before calling the method
        result = method(*args, **kwargs)
        # Do something after calling the method
        return result
    return wrapper

@my_decorator
class MyClass:
    def method1(self):
        # Method implementation

    def method2(self):
        # Method implementation
```

In the above example, the `my_decorator` function is applied to all methods of the `MyClass` class using the `for_all_methods` decorator. The `my_decorator` function wraps each method, allowing additional functionality to be added before and after the method is called.
### FunctionDef decorate(cls)
**decorate**: The function of decorate is to apply a decorator to all callable methods of a class, excluding special methods.

**parameters**: The parameters of this Function.
· cls: The class whose methods will be decorated.

**Code Description**: The decorate function iterates over all attributes of the provided class (cls). For each attribute, it checks if the attribute is callable (i.e., a method) and if its name does not start with double underscores (which would indicate a special method). If both conditions are met, the function applies a decorator to the method using the setattr function, which updates the class with the decorated method. Finally, the function returns the modified class.

**Note**: 
- This function assumes that a decorator function named decorator is already defined and available in the scope where decorate is used.
- Special methods (those starting with double underscores) are not decorated by this function.

**Output Example**: 
If you have a class MyClass with methods method1 and method2, after applying the decorate function, both method1 and method2 will be decorated with the decorator function. The class will be returned with these modifications.
***
