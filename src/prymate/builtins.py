import inspect
import sys

from prymate.objects import (
    Array,
    Builtin,
    Dictionary,
    Error,
    Float,
    Integer,
    Null,
    Object,
    String,
)

__all__ = ["BUILTINS"]


def len_function(args: list[Object]) -> Integer | Error:
    """Get the length of an object as an INTEGER."""

    if len(args) != 1:
        return Error(f"wrong number of arguments. got={len(args)}, want=1")

    match args[0]:
        case Array():
            return Integer(len(args[0].elements))

        case String():
            return Integer(len(args[0].value))

        case Dictionary():
            return Integer(len(args[0].entries))

        case _:
            return Error(f"argument to `len` not supported, got {args[0].type()}")


def exit_function(args: list[Object]) -> Error | None:
    """Exit the interpreter with the given INTEGER exit code (default 0)."""

    if len(args) > 1:
        return Error(f"wrong number of arguments. got={len(args)}, want<=1")

    if len(args) == 1:
        if not isinstance(args[0], Integer):
            return Error(f"argument to `exit` not supported, got {args[0].type()}")

        sys.exit(args[0].value)

    sys.exit(0)


def type_function(args: list[Object]) -> String | Error:
    """Return the type of an object as a STRING."""

    if len(args) != 1:
        return Error(f"wrong number of arguments. got={len(args)}, want=1")

    return String(args[0].type())


def help_function(args: list[Object]) -> String | Error:
    """Return the help doc-string of a builtin function as a STRING.
    If no arguments are provided, a list of inbuilt functions is provided."""

    if len(args) > 1:
        return Error(f"wrong number of arguments. got={len(args)}, want<=1")

    if not args:
        return String(", ".join(BUILTINS.keys()))

    if not isinstance(args[0], Builtin):
        return Error(f"argument to `help` not supported, got {args[0].type()}")

    return String(str(inspect.getdoc(args[0].function)))


def puts_function(args: list[Object]) -> Null:
    """Print the given arguments to stdout."""

    print("\n".join(str(args)))
    return Null()


def gets_function(args: list[Object]) -> String | Error:
    """Accept input from the user in the form of a STRING.
    An optional STRING can be provided that will serve as a prompt for the user."""

    if len(args) > 1:
        return Error(f"wrong number of arguments. got={len(args)}, want<=1")

    if len(args) == 0:
        return String(input())

    if not isinstance(args[0], String):
        return Error(f"argument to `gets` not supported, got {args[0].type()}")

    return String(input(args[0].value))


def int_function(args: list[Object]) -> Integer | Error:
    """Convert a STRING or a FLOAT to an INTEGER."""

    if len(args) != 1:
        return Error(f"wrong number of arguments. got={len(args)}, want=1")

    if not isinstance(args[0], String) and not isinstance(args[0], Float):
        return Error(f"argument to `int` not supported, got {args[0].type()}")

    try:
        return Integer(int(args[0].value))
    except ValueError:
        return Error("argument cannot be converted to an integer")


def float_function(args: list[Object]) -> Float | Error:
    "Convert an INTEGER or a STRING to a FLOAT."

    if len(args) != 1:
        return Error(f"wrong number of arguments. got={len(args)}, want=1")

    if not isinstance(args[0], String) and not isinstance(args[0], Integer):
        return Error(f"argument to `float` not supported, got {args[0].type()}")

    try:
        return Float(float(args[0].value))
    except ValueError:
        return Error("argument cannot be converted to a float")


def str_function(args: list[Object]) -> String | Error:
    "Convert any value to its STRING representation."

    if len(args) != 1:
        return Error(f"wrong number of arguments. got={len(args)}, want=1")

    return String(str(args[0]))


def first_function(args: list[Object]) -> Object:
    """Return the first element of an ARRAY."""

    if len(args) != 1:
        return Error(f"wrong number of arguments. got={len(args)}, want=1")

    if not isinstance(args[0], Array):
        return Error(f"argument to `first` not supported, got {args[0].type()}")

    if len(args[0].elements) > 0:
        return args[0].elements[0]

    return Null()


def last_function(args: list[Object]) -> Object:
    """Return the last element of an ARRAY."""

    if len(args) != 1:
        return Error(f"wrong number of arguments. got={len(args)}, want=1")

    if not isinstance(args[0], Array):
        return Error(f"argument to `last` not supported, got {args[0].type()}")

    if len(args[0].elements) > 0:
        return args[0].elements[-1]

    return Null()


def rest_function(args: list[Object]) -> Object:
    """Return a new ARRAY with all elements except the first."""

    if len(args) != 1:
        return Error(f"wrong number of arguments. got={len(args)}, want=1")

    if not isinstance(args[0], Array):
        return Error(f"argument to `rest` not supported, got {args[0].type()}")

    if len(args[0].elements) > 0:
        return Array(args[0].elements[1:])

    return Null()


def push_function(args: list[Object]) -> Object:
    """Create a copy of provided ARRAY, with given element being appended."""

    if len(args) != 2:
        return Error(f"wrong number of arguments. got={len(args)}, want=2")

    if not isinstance(args[0], Array):
        return Error(f"argument to `push` not supported, got {args[0].type()}")

    return Array([*args[0].elements, args[1]])


def abs_function(args: list[Object]) -> Object:
    """Gives the absolute value of an INTEGER or FLOAT."""

    if len(args) != 1:
        return Error(f"wrong number of arguments. got={len(args)}, want=1")

    if not isinstance(args[0], Integer) and not isinstance(args[0], Float):
        return Error(f"argument to `abs` not supported, got {args[0].type()}")

    if isinstance(args[0], Integer):
        return Integer(abs(args[0].value))
    else:
        return Float(abs(args[0].value))


BUILTINS = {
    "len": Builtin(len_function),
    "exit": Builtin(exit_function),
    "type": Builtin(type_function),
    "help": Builtin(help_function),
    "puts": Builtin(puts_function),
    "gets": Builtin(gets_function),
    "int": Builtin(int_function),
    "float": Builtin(float_function),
    "str": Builtin(str_function),
    "first": Builtin(first_function),
    "last": Builtin(last_function),
    "rest": Builtin(rest_function),
    "push": Builtin(push_function),
    "abs": Builtin(abs_function),
}
