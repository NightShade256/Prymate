import inspect
import sys
import typing

from . import objects


# General Functions
def len_function(args: typing.List[objects.Object]) -> objects.Object:
    """Gives the length of a string, array or number of keys of a dictionary."""
    if len(args) != 1:
        return objects.Error(f"wrong number of arguments. got={len(args)}, want=1")

    arg = args[0]
    if isinstance(arg, objects.Array):
        return objects.Integer(len(arg.elements))
    elif isinstance(arg, objects.String):
        return objects.Integer(len(arg.value))
    else:
        return objects.Error(f"argument to `len` not supported, got {arg.tp().value}")


def exit_function(args: typing.List[objects.Object]) -> objects.Object:
    """Exits from the interpreter."""
    if len(args) != 0:
        return objects.Error(f"wrong number of arguments. got={len(args)}, want=0")

    sys.exit(0)


def type_function(args: typing.List[objects.Object]) -> objects.Object:
    """Returns the type of an object."""
    if len(args) != 1:
        return objects.Error(f"wrong number of arguments. got={len(args)}, want=1")

    arg: objects.Object = args[0]
    return objects.String(str(arg.tp().value))


def help_function(args: typing.List[objects.Object]) -> objects.Object:
    """Returns the help string of a builtin function.
    If no arguments are provided the list of inbuilt functions is provided."""
    if len(args) > 1 or len(args) < 0:
        return objects.Error(f"wrong number of arguments. got={len(args)}, want= <=1")

    if not args:
        return objects.String(", ".join(BUILTINS.keys()))

    arg = args[0]
    if not isinstance(arg, objects.Builtin):
        return objects.Error(f"argument to `len` not supported, got {arg.tp().value}")

    docstring = str(inspect.getdoc(arg.function))
    return objects.String(docstring)


def puts_function(args: typing.List[objects.Object]) -> objects.Object:
    """Prints the given arguments to stdout."""
    for arg in args:
        print(arg.inspect())

    return objects.Null()


def gets_function(args: typing.List[objects.Object]) -> objects.Object:
    """Accepts inputs from the user in the form of a string.
    You can provide an optional string that will serve as a
    prompt for the user."""

    if len(args) not in (0, 1):
        return objects.Error(f"wrong number of arguments. got={len(args)}, want= <=1")

    user_input: str

    if args:
        arg = args[0]
        if not isinstance(arg, objects.String):
            return objects.Error(
                f"argument to `gets` not supported, got {arg.tp().value}"
            )

        user_input = input(arg.value)
    else:
        user_input = input()

    return objects.String(user_input)


# Type Conversions
def int_function(args: typing.List[objects.Object]) -> objects.Object:
    """Converts a string or a float to an integer."""

    if len(args) != 1:
        return objects.Error(f"wrong number of arguments. got={len(args)}, want=1")

    arg = args[0]
    if not isinstance(arg, objects.String) and not isinstance(arg, objects.Float):
        return objects.Error(f"argument to `int` not supported, got {arg.tp().value}")

    str_value = arg.value
    try:
        int_value = int(str_value)
    except ValueError:
        return objects.Error("argument cannot be converted to an integer.")
    else:
        return objects.Integer(int_value)


def float_function(args: typing.List[objects.Object]) -> objects.Object:
    "Convert an int or a string to a float."
    if len(args) != 1:
        return objects.Error(f"wrong number of arguments. got={len(args)}, want=1")

    arg = args[0]
    if not isinstance(arg, objects.String) and not isinstance(arg, objects.Integer):
        return objects.Error("argument to `int` not supported, got {arg.tp().value}")

    str_value = arg.value
    try:
        float_value = float(str_value)
    except ValueError:
        return objects.Error("argument cannot be converted to an integer.")
    else:
        return objects.Float(float_value)


def str_function(args: typing.List[objects.Object]) -> objects.Object:
    "Converts any monkey object to its string representation."

    if len(args) != 1:
        return objects.Error(f"wrong number of arguments. got={len(args)}, want=1")

    str_val = str(args[0].inspect())
    return objects.String(str_val)


# Array Functions
def first_function(args: typing.List[objects.Object]) -> objects.Object:
    """Returns the first element of an array."""
    if len(args) != 1:
        return objects.Error(f"wrong number of arguments. got={len(args)}, want=1")

    arg = args[0]
    if not isinstance(arg, objects.Array):
        return objects.Error(f"argument to `first` not supported, got {arg.tp().value}")

    if arg.elements:
        return arg.elements[0]

    return objects.Null()


def last_function(args: typing.List[objects.Object]) -> objects.Object:
    """Returns the last element of an array."""
    if len(args) != 1:
        return objects.Error(f"wrong number of arguments. got={len(args)}, want=1")

    arg = args[0]
    if not isinstance(arg, objects.Array):
        return objects.Error(f"argument to `last` not supported, got {arg.tp().value}")

    if arg.elements:
        return arg.elements[-1]

    return objects.Null()


def rest_function(args: typing.List[objects.Object]) -> objects.Object:
    """Returns a new array with all the elements of the argument array,
    except the first."""
    if len(args) != 1:
        return objects.Error(f"wrong number of arguments. got={len(args)}, want=1")

    arg = args[0]
    if not isinstance(arg, objects.Array):
        return objects.Error(f"argument to `rest` not supported, got {arg.tp().value}")

    array = arg.elements
    if array:
        return objects.Array(list(array[1:]))

    return objects.Null()


def push_function(args: typing.List[objects.Object]) -> objects.Object:
    """Creates a new array with the element provided by the user appended to it.
    The first argument should be the array, and the second should be the element."""
    if len(args) != 2:
        return objects.Error(f"wrong number of arguments. got={len(args)}, want=2")

    arg = args[0]
    if not isinstance(arg, objects.Array):
        return objects.Error(f"argument to `push` not supported, got {arg.tp().value}")

    array = arg.elements
    new_array = list(array)
    new_array.append(args[1])
    return objects.Array(new_array)


def zip_function(args: typing.List[objects.Object]) -> objects.Object:
    """Creates an array from the elements of the arrays provided as arguments.

    The length of the resulting array will be equal to the length of the smallest
    array. This is similar to the zip function found in Python."""

    if len(args) < 2:
        return objects.Error(f"wrong number of arguments. got={len(args)}, want= >=2")

    elements = []

    for arg in args:
        if not isinstance(arg, objects.Array):
            return objects.Error(
                f"argument to `zip` not supported, got {arg.tp().value}"
            )
        elif not arg.elements:
            return objects.Error("An argument to `zip` is empty.")
        else:
            elements.append(arg.elements)

    zipped_array = [list(x) for x in zip(*elements)]
    zipped_array = [objects.Array(list(x)) for x in zipped_array]

    return objects.Array(zipped_array)


def sumarr_function(args: typing.List[objects.Object]) -> objects.Object:
    """Returns the sum of the integer and float elements in an array.
    If there is any other element except that of the type INTEGER
    or FLOAT an error will be returned instead."""
    if len(args) != 1:
        return objects.Error(f"wrong number of arguments. got={len(args)}, want=1")

    arg = args[0]
    if not isinstance(arg, objects.Array):
        return objects.Error(
            f"argument to `sumarr` not supported, got {arg.tp().value}"
        )

    array_sum: typing.Union[int, float] = 0
    for element in arg.elements:
        if not isinstance(element, objects.Integer) and not isinstance(
            element, objects.Float
        ):
            return objects.Error("array contains a non-INTEGER or non-FLOAT element")

        array_sum += element.value

    if isinstance(array_sum, float):
        return objects.Float(array_sum)
    else:
        return objects.Integer(array_sum)


# Numeric Functions
def abs_function(args: typing.List[objects.Object]) -> objects.Object:
    """Gives the absolute value of an integer or float."""
    if len(args) != 1:
        return objects.Error(f"wrong number of arguments. got={len(args)}, want=1")

    arg = args[0]
    if not isinstance(arg, objects.Integer) and not isinstance(arg, objects.Float):
        return objects.Error(f"argument to `abs` not supported, got {arg.tp().value}")

    if isinstance(arg.value, float):
        return objects.Float(abs(arg.value))
    else:
        return objects.Integer(abs(arg.value))


# Builtin Definitions
BUILTINS = {
    "len": objects.Builtin(len_function),
    "exit": objects.Builtin(exit_function),
    "type": objects.Builtin(type_function),
    "help": objects.Builtin(help_function),
    "puts": objects.Builtin(puts_function),
    "gets": objects.Builtin(gets_function),
    "int": objects.Builtin(int_function),
    "float": objects.Builtin(float_function),
    "str": objects.Builtin(str_function),
    "abs": objects.Builtin(abs_function),
    "first": objects.Builtin(first_function),
    "last": objects.Builtin(last_function),
    "rest": objects.Builtin(rest_function),
    "push": objects.Builtin(push_function),
    "zip": objects.Builtin(zip_function),
    "sumarr": objects.Builtin(sumarr_function),
}
