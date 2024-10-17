from __future__ import annotations
import trace
from typing import TYPE_CHECKING, Any, Dict

if TYPE_CHECKING:  # to prevent circular import
    from opto.trace.nodes import Node
from opto.trace.bundle import bundle
import copy


@bundle()
def clone(x: Any):
    """ This is a clone operator of x. """
    return copy.deepcopy(x)


def identity(x: Any):
    # identity(x) behaves the same as x.clone()
    return x.clone()


# Unary operators and functions


@bundle()
def pos(x: Any):
    """ This is a pos operator of x. """
    return +x


@bundle()
def neg(x: Any):
    """ This is a neg operator of x. """
    return -x


@bundle()
def abs(x: Any):
    """ This is an abs operator of x. """
    return abs(x)


@bundle()
def invert(x: Any):
    """ This is an invert operator of x. """
    return ~x


@bundle()
def round(x: Any, n: Any):
    """ This is a round operator of x. """
    return round(x, n)


@bundle()
def floor(x: Any):
    """ This is a floor operator of x. """
    import math

    return math.floor(x)


@bundle()
def ceil(x: Any):
    """ This is a ceil operator of x. """
    import math

    return math.ceil(x)


@bundle()
def trunc(x: Any):
    """ This is a trunc operator of x. """
    import math

    return math.trunc(x)


# Normal arithmetic operators


@bundle()
def add(x: Any, y: Any):
    """ This is an add operator of x and y. """
    return x + y


@bundle()
def subtract(x: Any, y: Any):
    """ This is a subtract operator of x and y. """
    return x - y


@bundle()
def multiply(x: Any, y: Any):
    """ This is a multiply operator of x and y. """
    return x * y


@bundle()
def floor_divide(x: Any, y: Any):
    """ This is a floor_divide operator of x and y. """
    return x // y


@bundle()
def divide(x: Any, y: Any):
    """ This is a divide operator of x and y. """
    return x / y


@bundle()
def mod(x: Any, y: Any):
    """ This is a mod operator of x and y. """
    return x % y


@bundle()
def node_divmod(x: Any, y: Any):
    """ This is a divmod operator of x and y. """
    return divmod(x, y)


@bundle()
def power(x: Any, y: Any):
    """ This is a power operator of x and y. """
    return x**y


@bundle()
def lshift(x: Any, y: Any):
    """ This is a lshift operator of x and y. """
    return x << y


@bundle()
def rshift(x: Any, y: Any):
    """ This is a rshift operator of x and y. """
    return x >> y


@bundle()
def and_(x: Any, y: Any):
    """ This is an and operator of x and y. """
    return x & y


@bundle()
def or_(x: Any, y: Any):
    """ This is an or operator of x and y. """
    return x | y


@bundle()
def xor(x: Any, y: Any):
    """ This is a xor operator of x and y. """
    return x ^ y


# Comparison methods


@bundle()
def lt(x: Any, y: Any):
    """ This is a lt operator of x and y. """
    return x < y


@bundle()
def le(x: Any, y: Any):
    """ This is a le operator of x and y. """
    return x <= y


@bundle()
def eq(x: Any, y: Any):
    """ This is an eq operator of x and y. """
    return x == y

@bundle()
def neq(x: Any, y: Any):
    """ This is a not eq operator of x and y. """
    return x != y

@bundle()
def ne(x: Any, y: Any):
    """ This is a ne operator of x and y. """
    return x != y


@bundle()
def ge(x: Any, y: Any):
    """ This is a ge operator of x and y. """
    return x >= y


@bundle()
def gt(x: Any, y: Any):
    """ This is a gt operator of x and y. """
    return x > y


# logical operators


@bundle()
def cond(condition: Any, x: Any, y: Any):
    """ This selects x if condition is True, otherwise y. """
    x, y, condition = x, y, condition  # This makes sure all data are read
    return x if condition else y


@bundle()
def not_(x: Any):
    """ This is a not operator of x. """
    return not x


@bundle()
def is_(x: Any, y: Any):
    """ Whether x is equal to y. """
    return x is y


@bundle()
def is_not(x: Any, y: Any):
    """ Whether x is not equal to y. """
    return x is not y


@bundle()
def in_(x: Any, y: Any):
    """ Whether x is in y. """
    return x in y


@bundle()
def not_in(x: Any, y: Any):
    """ Whether x is not in y. """
    return x not in y


# Indexing and slicing
@bundle()
def getitem(x: Any, index: Any):
    """ This is a getitem operator of x based on index. """
    return x[index]


@bundle()
def pop(x: Any, index: Any):
    """ This is a pop operator of x based on index. """
    return x.pop(index)


@bundle()
def len_(x: Any):
    """ This is a len operator of x. """
    return len(x)


# String operators
@bundle()
def ord_(x: Any):
    """ The unicode number of a character. """
    return ord(x)


@bundle()
def chr_(x: Any):
    """ The character of a unicode number. """
    return chr(x)


@bundle()
def concat(x: Any, y: Any):
    """ This is a concatenation operator of x and y. """
    return x + y


@bundle()
def lower(x: Any):
    """ This makes all characters in x lower case. """
    return x.lower()


@bundle()
def upper(x: Any):
    """ This makes all characters in x upper case. """
    return x.upper()


@bundle()
def title(x: Any):
    """ This makes the first character to upper case and the rest to lower case. """
    return x.title()


@bundle()
def swapcase(x: Any):
    """ Swaps the case of all characters: uppercase character to lowercase and vice-versa. """
    return x.swapcase()


@bundle()
def capitalize(x: Any):
    """ Converts the first character of a string to uppercase. """
    return x.capitalize()


@bundle()
def split(x: Any, y: Any, maxsplit: Any = -1):
    """ Splits the string by finding a substring y in string x, return the first part and second part of string x without y. """
    return x.split(y, maxsplit)


@bundle()
def strip(x: Any, chars=None):
    """ Removes the leading and trailing characters of x. """
    return x.strip(chars)


@bundle()
def replace(x: Any, old: Any, new: Any, count: Any = -1):
    """ Replaces all occurrences of substring y in string x with z. """
    return x.replace(old, new, count)


@bundle()
def format(x: Any, *args, **kwargs):
    """ Fills in a string template with content, str.format(). """
    return x.format(*args, **kwargs)

@bundle()
def join(x: Any, *y: Any):
    """ Joins a sequence y with different strs with x: "\n".join(["a", "b", "c"]) -> "a\nb\nc". """
    return x.join(y)

@bundle()
def node_getattr(obj: Node, attr: str):
    """ This operator gets attr of obj. """
    return getattr(obj, attr)


@bundle(
    _process_inputs=False,
    allow_external_dependencies=True,
)
def call(fun: Node, *args, **kwargs):
    """ This operator calls the function `fun` with args (args_0, args_1, etc.) and kwargs. If there are no args or kwargs, i.e. call(fun=function_name), the function takes no input. """
    # Run the function as it is
    fun = fun._data
    # Call the node with the input arguments
    assert callable(fun), "The function must be callable."
    output = fun(*args, **kwargs)
    return output


@bundle()
def to_list(x: Any):
    """ This converts x to a list.  """
    return list(x)

# dict operators

@bundle()
def keys(x: Dict):
    """ Return the keys of a dictionary x as a list. """
    if not isinstance(x, dict):
        raise AttributeError(f"{type(x)} object has no attribute 'values'.")

    return [k for k in x.keys()]

@bundle()
def values(x: Dict):
    """ Return the values of a dictionary x as a list. """
    if not isinstance(x, dict):
        raise AttributeError(f"{type(x)} object has no attribute 'values'.")

    return [k for k in x.values()]

# dict in-place operators

@bundle()
def dict_update(x: Dict, y: Dict):
    """ Update the dictionary x with the dictionary y. """
    x = copy.copy(x)
    x.update(y)
    return x

@bundle()
def dict_pop(x: Dict, key: Any):
    """ Pop the key from the dictionary x. """
    x = copy.copy(x)
    x.pop(key)
    return x

@bundle()
def dict_popitem(x: Dict):
    """ Pop the last item from the dictionary x. """
    x = copy.copy(x)
    x.popitem()
    return x

# list in-place operators

@bundle()
def list_append(x: Any, y: Any):
    """ Append y to x. """
    x = copy.copy(x)
    x.append(y)
    return x

@bundle()
def list_clear(x: Any):
    """ Clear x. """
    x = copy.copy(x)
    x.clear()
    return x

@bundle()
def list_extend(x: Any, y: Any):
    """ Extend x with y. """
    x = copy.copy(x)
    x.extend(y)
    return x

@bundle()
def list_insert(x: Any, index: Any, y: Any):
    """ Insert y at index in x. """
    x = copy.copy(x)
    x.insert(index, y)
    return x

@bundle()
def list_pop(x: Any, index: Any):
    """ Pop the index from x. """
    x = copy.copy(x)
    x.pop(index)
    return x

@bundle()
def list_remove(x: Any, y: Any):
    """ Remove y from x. """
    x = copy.copy(x)
    x.remove(y)
    return x


@bundle()
def list_reverse(x: Any):
    """ Reverse x. """
    x = copy.copy(x)
    x.reverse()
    return x


@bundle()
def list_sort(x: Any, key: Any = None, reverse: Any = False):
    """ Sort x. """
    x = copy.copy(x)
    x.sort(key=key, reverse=reverse)
    return x


# set in-place operators
@bundle()
def set_add(x: Any, y: Any):
    """ Add y to x. """
    x = copy.copy(x)
    x.add(y)
    return x

@bundle()
def set_clear(x: Any):
    """ Clear x. """
    x = copy.copy(x)
    x.clear()
    return x

@bundle()
def set_discard(x: Any, y: Any):
    """ Discard y from x. """
    x = copy.copy(x)
    x.discard(y)
    return x

@bundle()
def set_intersection_update(x: Any, y: Any):
    """ Update x with the intersection of x and y. """
    x = copy.copy(x)
    x.intersection_update(y)
    return x

@bundle()
def set_pop(x: Any):
    """ Pop an element from x. """
    x = copy.copy(x)
    x.pop()
    return x

@bundle()
def set_remove(x: Any, y: Any):
    """ Remove y from x. """
    x = copy.copy(x)
    x.remove(y)
    return x

@bundle()
def set_symmetric_difference_update(x: Any, y: Any):
    """ Update x with the symmetric difference of x and y. """
    x = copy.copy(x)
    x.symmetric_difference_update(y)
    return x

@bundle()
def set_update(x: Any, y: Any):
    """ Update x with y. """
    x = copy.copy(x)
    x.update(y)
    return x