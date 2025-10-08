import abc
import dataclasses
import math
import typing

from prymate import ast

__all__ = [
    "Object",
    "Hashable",
    "HashableObject",
    "Null",
    "Integer",
    "Boolean",
    "Float",
    "String",
    "Array",
    "Dictionary",
    "Function",
    "Builtin",
    "ReturnValue",
    "Error",
    "Environment",
]


class Object(abc.ABC):
    """Generic object type used by the evaluator."""

    @abc.abstractmethod
    def type(self) -> str:
        """Get a human-friendly concrete type name."""

        pass

    @abc.abstractmethod
    def __str__(self) -> str:
        """Get a human-friendly string representation of the object's value."""

        pass

    def is_truthy(self) -> bool:
        """Get the truth value of the object (is truthy or not)."""

        return True


class Eq(abc.ABC):
    """Trait for comparisions."""

    @abc.abstractmethod
    def __eq__(self, rhs: object) -> bool:
        pass


class Hashable(abc.ABC):
    """Generic class that requires implementation of __hash__ method."""

    @abc.abstractmethod
    def __hash__(self) -> int:
        pass


# can't find a better solution
class HashableObject(Object, Hashable):
    pass


class Error(Object):
    def __init__(self, message: str) -> None:
        self.message = message

    def type(self) -> str:
        return "ERROR"

    def __str__(self) -> str:
        return f"Error: {self.message}"


@dataclasses.dataclass
class Binding:
    mutable: bool
    object: Object


class Environment:
    """Represents scope of a program or a function."""

    def __init__(self, outer: "Environment | None" = None) -> None:
        self.store: dict[str, Binding] = {}
        self.outer = outer

    def get_binding(self, name: str) -> Object | None:
        """Get the value of a binding."""

        binding = self.store.get(name, None)

        if binding is not None:
            return binding.object

        if self.outer is not None:
            return self.outer.get_binding(name)

        return None

    def set_binding(self, name: str, value: Object, mutable: bool) -> None:
        self.store[name] = Binding(mutable, value)

    def update_binding(self, name: str, value: Object) -> Error | None:
        if name not in self.store:
            return Error(f"cannot find identifier {name}")

        if not self.store[name].mutable:
            return Error(f"cannot update const identifer {name}")

        self.store[name].object = value


class Null(Object, Eq):
    __instance: "Null | None" = None

    def __new__(cls) -> "Null":
        if cls.__instance is not None:
            return cls.__instance

        cls.__instance = super().__new__(cls)
        return cls.__instance

    def type(self) -> str:
        return "NULL"

    def __str__(self) -> str:
        return "null"

    @typing.override
    def is_truthy(self) -> bool:
        return False

    def __eq__(self, rhs: object) -> bool:
        return self is rhs


class Integer(HashableObject, Eq):
    def __init__(self, value: int) -> None:
        self.value = value

    def type(self) -> str:
        return "INTEGER"

    def __str__(self) -> str:
        return str(self.value)

    def __hash__(self) -> int:
        return hash(self.value)

    def __eq__(self, rhs: object) -> bool:
        if isinstance(rhs, Integer):
            return self.value == rhs.value

        if isinstance(rhs, Float):
            return math.isclose(float(self.value), rhs.value)

        return False


class Boolean(HashableObject, Eq):
    __instances: dict[bool, "Boolean"] = {}
    value: bool

    def __new__(cls, value: bool) -> "Boolean":
        if value not in cls.__instances:
            instance = super().__new__(cls)
            instance.value = value
            cls.__instances[value] = instance

        return cls.__instances[value]

    def __init__(self, value: bool) -> None:
        pass

    def type(self) -> str:
        return "BOOLEAN"

    def __str__(self) -> str:
        return str(self.value).lower()

    def __hash__(self) -> int:
        return hash(self.value)

    @typing.override
    def is_truthy(self) -> bool:
        return self.value

    def __eq__(self, rhs: object) -> bool:
        return self is rhs


class Float(Object, Eq):
    def __init__(self, value: float) -> None:
        self.value = value

    def type(self) -> str:
        return "FLOAT"

    def __str__(self) -> str:
        return str(self.value)

    def __eq__(self, rhs: object) -> bool:
        if isinstance(rhs, Float):
            return math.isclose(self.value, rhs.value)

        if isinstance(rhs, Integer):
            return math.isclose(self.value, float(rhs.value))

        return False


class String(HashableObject, Eq):
    def __init__(self, value: str) -> None:
        self.value = value

    def type(self) -> str:
        return "STRING"

    def __str__(self) -> str:
        return self.value

    def __hash__(self) -> int:
        return hash(self.value)

    def __eq__(self, rhs: object) -> bool:
        return isinstance(rhs, String) and self.value == rhs.value


class Array(Object):
    def __init__(self, elements: list[Object]) -> None:
        self.elements = elements

    def type(self) -> str:
        return "ARRAY"

    def __str__(self) -> str:
        return str(self.elements)


class Dictionary(Object):
    def __init__(self, entries: dict[HashableObject, Object]) -> None:
        self.entries = entries

    def type(self) -> str:
        return "DICTIONARY"

    def __str__(self) -> str:
        return str(self.entries)


class Function(Object):
    def __init__(
        self,
        env: Environment,
        parameters: list[ast.Identifier],
        body: ast.BlockStatement,
    ) -> None:
        self.env = env
        self.parameters = parameters
        self.body = body

    def type(self) -> str:
        return "FUNCTION"

    def __str__(self) -> str:
        return f"fn({', '.join(map(str, self.parameters))}) -> ..."


class Builtin(Object):
    def __init__(
        self, function: typing.Callable[[list[Object]], Object | None]
    ) -> None:
        self.function = function

    def type(self) -> str:
        return "BUILTIN"

    def __str__(self) -> str:
        return "builtin function"


class ReturnValue(Object):
    def __init__(self, value: Object) -> None:
        self.value = value

    def type(self) -> str:
        return "RETURN VALUE"

    def __str__(self) -> str:
        return str(self.value)
