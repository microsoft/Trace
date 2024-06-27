from __future__ import annotations
import trace
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # to prevent circular import
    from opto.trace.nodes import Node
from opto.trace.bundle import bundle
import copy


@bundle("[clone] This is a clone operator of x.", node_dict="auto")
def clone(x: Any):
    return copy.deepcopy(x)


def identity(x: Any):
    # identity(x) behaves the same as x.clone()
    return x.clone()


# Unary operators and functions


@bundle("[pos] This is a pos operator of x.", node_dict="auto")
def pos(x: Any):
    return +x


@bundle("[neg] This is a neg operator of x.", node_dict="auto")
def neg(x: Any):
    return -x


@bundle("[abs] This is an abs operator of x.", node_dict="auto")
def abs(x: Any):
    return abs(x)


@bundle("[invert] This is an invert operator of x.", node_dict="auto")
def invert(x: Any):
    return ~x


@bundle("[round] This is a round operator of x.", node_dict="auto")
def round(x: Any, n: Any):
    return round(x, n)


@bundle("[floor] This is a floor operator of x.", node_dict="auto")
def floor(x: Any):
    import math

    return math.floor(x)


@bundle("[ceil] This is a ceil operator of x.", node_dict="auto")
def ceil(x: Any):
    import math

    return math.ceil(x)


@bundle("[trunc] This is a trunc operator of x.", node_dict="auto")
def trunc(x: Any):
    import math

    return math.trunc(x)


# Normal arithmetic operators


@bundle("[add] This is an add operator of x and y.", node_dict="auto")
def add(x: Any, y: Any):
    return x + y


@bundle("[subtract] This is a subtract operator of x and y.", node_dict="auto")
def subtract(x: Any, y: Any):
    return x - y


@bundle("[multiply] This is a multiply operator of x and y.", node_dict="auto")
def multiply(x: Any, y: Any):
    return x * y


@bundle("[floor_divide] This is a floor_divide operator of x and y.", node_dict="auto")
def floor_divide(x: Any, y: Any):
    return x // y


@bundle("[divide] This is a divide operator of x and y.", node_dict="auto")
def divide(x: Any, y: Any):
    return x / y


@bundle("[mod] This is a mod operator of x and y.", node_dict="auto")
def mod(x: Any, y: Any):
    return x % y


@bundle("[divmod] This is a divmod operator of x and y.", node_dict="auto")
def divmod(x: Any, y: Any):
    return divmod(x, y)


@bundle("[power] This is a power operator of x and y.", node_dict="auto")
def power(x: Any, y: Any):
    return x**y


@bundle("[lshift] This is a lshift operator of x and y.", node_dict="auto")
def lshift(x: Any, y: Any):
    return x << y


@bundle("[rshift] This is a rshift operator of x and y.", node_dict="auto")
def rshift(x: Any, y: Any):
    return x >> y


@bundle("[and] This is an and operator of x and y.", node_dict="auto")
def and_(x: Any, y: Any):
    return x & y


@bundle("[or] This is an or operator of x and y.", node_dict="auto")
def or_(x: Any, y: Any):
    return x | y


@bundle("[xor] This is a xor operator of x and y.", node_dict="auto")
def xor(x: Any, y: Any):
    return x ^ y


# Comparison methods


@bundle("[lt] This is a lt operator of x and y.", node_dict="auto")
def lt(x: Any, y: Any):
    return x < y


@bundle("[le] This is a le operator of x and y.", node_dict="auto")
def le(x: Any, y: Any):
    return x <= y


@bundle("[eq] This is an eq operator of x and y.", node_dict="auto")
def eq(x: Any, y: Any):
    return x == y


@bundle("[ne] This is a ne operator of x and y.", node_dict="auto")
def ne(x: Any, y: Any):
    return x != y


@bundle("[ge] This is a ge operator of x and y.", node_dict="auto")
def ge(x: Any, y: Any):
    return x >= y


@bundle("[gt] This is a gt operator of x and y.", node_dict="auto")
def gt(x: Any, y: Any):
    return x > y


# logical operators


@bundle("[cond] This selects x if condition is True, otherwise y.", node_dict="auto")
def cond(condition: Any, x: Any, y: Any):
    x, y, condition = x, y, condition  # This makes sure all data are read
    return x if condition else y


@bundle("[not] This is a not operator of x.", node_dict="auto")
def not_(x: Any):
    return not x


@bundle("[is] Whether x is equal to y.", node_dict="auto")
def is_(x: Any, y: Any):
    return x is y


@bundle("[is_not] Whether x is not equal to y.", node_dict="auto")
def is_not(x: Any, y: Any):
    return x is not y


@bundle("[in] Whether x is in y.", node_dict="auto")
def in_(x: Any, y: Any):
    return x in y


@bundle("[not_in] Whether x is not in y.", node_dict="auto")
def not_in(x: Any, y: Any):
    return x not in y


# Indexing and slicing
@bundle("[getitem] This is a getitem operator of x based on index.", node_dict="auto")
def getitem(x: Any, index: Any):
    return x[index]


@bundle("[pop] This is a pop operator of x based on index.", node_dict="auto")
def pop(x: Any, index: Any):
    return x.pop(index)


@bundle("[len] This is a len operator of x.", node_dict="auto")
def len_(x: Any):
    return len(x)


# String operators
@bundle("[ord] The unicode number of a character.", node_dict="auto")
def ord_(x: Any):
    return ord(x)


@bundle("[chr] The character of a unicode number.", node_dict="auto")
def chr_(x: Any):
    return chr(x)


@bundle("[concat] This is a concatenation operator of x and y.", node_dict="auto")
def concat(x: Any, y: Any):
    return x + y


@bundle("[lower] This makes all characters in x lower case.", node_dict="auto")
def lower(x: Any):
    return x.lower()


@bundle("[upper] This makes all characters in x upper case.", node_dict="auto")
def upper(x: Any):
    return x.upper()


@bundle("[title] This makes the first character to upper case and the rest to lower case.", node_dict="auto")
def title(x: Any):
    return x.title()


@bundle(
    "[swapcase] Swaps the case of all characters: uppercase character to lowercase and vice-versa.", node_dict="auto"
)
def swapcase(x: Any):
    return x.swapcase()


@bundle("[capitalize] Converts the first character of a string to uppercase.", node_dict="auto")
def capitalize(x: Any):
    return x.capitalize()


@bundle(
    "[split] Splits the string by finding a substring y in string x, return the first part and second part of string x without y.",
    node_dict="auto",
)
def split(x: Any, y: Any, maxsplit: Any = -1):
    return x.split(y, maxsplit)


@bundle("[strip] Removes the leading and trailing characters of x.", node_dict="auto")
def strip(x: Any, chars=None):
    return x.strip(chars)


@bundle("[replace] Replaces all occurrences of substring y in string x with z.", node_dict="auto")
def replace(x: Any, old: Any, new: Any, count: Any = -1):
    return x.replace(old, new, count)


@bundle("[format] Fills in a string template with content, str.format()", node_dict="auto")
def format(x: Any, *args, **kwargs):
    return x.format(*args, **kwargs)


# Exception operator
@bundle("[error] x triggers an error during execution. The error message is e.", node_dict="auto")
def throws_exception(e: Any, input_params: Any):
    return e


@bundle("[getattr] This operator gets attr of node.", node_dict="auto")
def node_getattr(obj: Node, attr: str):
    return obj[attr] if isinstance(obj, dict) else getattr(obj, attr)


@bundle(
    """[call] This operator calls the function `fun` with args (args_0, args_1, etc.) and kwargs. If there are no args or kwargs, i.e. call(fun=function_name), the function takes no input.""",
    node_dict="auto",
    unpack_input=False,
    allow_external_dependencies=True,
)
def call(fun: Node, *args, **kwargs):
    # Run the function as it is
    fun = fun._data
    # Call the node with the input arguments
    assert callable(fun), "The function must be callable."
    output = fun(*args, **kwargs)
    return output
