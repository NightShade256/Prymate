import enum
import typing

from prymate import ast
from prymate import objects  # for typing information

__all__ = [
    "Boolean",
    "Error",
    "Integer",
    "Null",
    "Object",
    "ObjectType",
    "ReturnValue",
    "Function",
    "String",
    "Builtin",
    "Array",
    "Hashable",
    "Dictionary",
    "HashKey",
    "HashPair",
    "Float",
]


class ObjectType(enum.Enum):

    # Basic types
    INTEGER = "INTEGER"
    FLOAT = "FLOAT"
    BOOLEAN = "BOOLEAN"
    STRING = "STRING"
    NULL = "NULL"

    # Composite types
    ARRAY = "ARRAY"
    DICTIONARY = "DICTIONARY"

    # Interpreter stubs
    RETURN_VALUE = "RETURN_VALUE"
    FUNCTION = "FUNCTION"
    BUILTIN = "BUILTIN"
    ERROR = "ERROR"


class HashKey:
    def __init__(self, tp: ObjectType, value: int):
        self.tp = tp
        self.value = value

    def __eq__(self, other: typing.Any) -> bool:
        if isinstance(other, HashKey):
            if other.tp == self.tp and other.value == self.value:
                return True

        return False

    def __ne__(self, other: typing.Any) -> bool:
        if isinstance(other, HashKey):
            if other.tp == self.tp and other.value == self.value:
                return False

        return True

    def __hash__(self) -> int:
        return hash(f"{self.tp}-{self.value}")


class Object:
    def tp(self) -> ObjectType:
        raise NotImplementedError()

    def inspect(self) -> str:
        raise NotImplementedError()


class Hashable:
    def hashkey(self) -> HashKey:
        raise NotImplementedError()


class Integer(Object, Hashable):
    def __init__(self, value: int) -> None:
        self.value = value

    def tp(self) -> ObjectType:
        return ObjectType.INTEGER

    def inspect(self) -> str:
        return str(self.value)

    def hashkey(self) -> HashKey:
        return HashKey(self.tp(), self.value)


class Float(Object, Hashable):
    def __init__(self, value: float) -> None:
        self.value = value

    def tp(self) -> ObjectType:
        return ObjectType.FLOAT

    def inspect(self) -> str:
        return str(self.value)

    def hashkey(self) -> HashKey:
        return HashKey(self.tp(), hash(self.value))


class Boolean(Object, Hashable):
    _false_instance: typing.Optional["Boolean"] = None
    _true_instance: typing.Optional["Boolean"] = None

    def __new__(cls, value: bool) -> "Boolean":
        if value:
            if cls._true_instance is not None:
                return cls._true_instance
            else:
                new_true_instance: "Boolean" = super().__new__(cls)
                cls._true_instance = new_true_instance
                return new_true_instance

        else:
            if cls._false_instance is not None:
                return cls._false_instance
            else:
                new_false_instance: "Boolean" = super().__new__(cls)
                cls._false_instance = new_false_instance
                return new_false_instance

    def __init__(self, value: bool) -> None:
        self.value = value

    def tp(self) -> ObjectType:
        return ObjectType.BOOLEAN

    def inspect(self) -> str:
        return str(self.value).lower()

    def hashkey(self) -> HashKey:
        val = 1 if self.value else 0
        return HashKey(self.tp(), val)


class Null(Object):

    _instance: typing.Optional["Null"] = None

    def __new__(cls) -> "Null":
        if cls._instance is not None:
            return cls._instance
        else:
            new_null_instance: "Null" = super().__new__(cls)
            cls._instance = new_null_instance
            return new_null_instance

    def tp(self) -> ObjectType:
        return ObjectType.NULL

    def inspect(self) -> str:
        return "null"


class ReturnValue(Object):
    def __init__(self, value: Object) -> None:
        self.value = value

    def tp(self) -> ObjectType:
        return ObjectType.RETURN_VALUE

    def inspect(self) -> str:
        return self.value.inspect()


class Error(Object):
    def __init__(self, message: str) -> None:
        self.message = message

    def tp(self) -> ObjectType:
        return ObjectType.ERROR

    def inspect(self) -> str:
        return f"Error: {self.message}"


class Function(Object):
    def __init__(
        self,
        parameters: typing.List[ast.Identifier],
        body: ast.BlockStatement,
        env: "objects.Environment",
    ) -> None:
        self.parameters = parameters
        self.body = body
        self.env = env

    def tp(self) -> ObjectType:
        return ObjectType.FUNCTION

    def inspect(self) -> str:
        params = [str(x) for x in self.parameters]
        fmt_params = ", ".join(params)

        fmt = f"fn({fmt_params}) " + "{" + f"\n{str(self.body)}\n" + "}"
        return fmt


class String(Object, Hashable):
    def __init__(self, value: str) -> None:
        self.value = value

    def tp(self) -> ObjectType:
        return ObjectType.STRING

    def inspect(self) -> str:
        return self.value

    def hashkey(self) -> HashKey:
        return HashKey(self.tp(), hash(self.value))


class Array(Object):
    def __init__(
        self, elements: typing.Union[typing.List[Object], typing.List["Array"]]
    ) -> None:
        self.elements = elements

    def tp(self) -> ObjectType:
        return ObjectType.ARRAY

    def inspect(self) -> str:
        elements = [x.inspect() for x in self.elements]
        return f"[{', '.join(elements)}]"


class HashPair:
    def __init__(self, key: Object, value: Object) -> None:
        self.key = key
        self.value = value


class Dictionary(Object):
    def __init__(self, pairs: typing.Dict[HashKey, HashPair]) -> None:
        self.pairs = pairs

    def tp(self) -> ObjectType:
        return ObjectType.DICTIONARY

    def inspect(self) -> str:
        fmt = "{"
        pairs = []
        for pair in self.pairs.values():
            pairs.append(f"{pair.key.inspect()}: {pair.value.inspect()}")

        fmt += ", ".join(pairs) + "}"
        return fmt


class Builtin(Object):
    def __init__(
        self, function: typing.Callable[[typing.List[Object]], Object]
    ) -> None:
        self.function = function

    def tp(self) -> ObjectType:
        return ObjectType.BUILTIN

    def inspect(self) -> str:
        return "builtin function"
