import enum
import typing

from .objects import Object

__all__ = ["Environment"]


class IdentType(enum.Enum):
    """Represents type of a identifier."""

    CONSTANT = 0
    VARIABLE = 1


class Identifier:
    """Represents an identifier."""

    def __init__(self, tp: IdentType, value: Object) -> None:
        self.tp = tp
        self.value = value


class Environment:
    """Represents scope of the program or function."""

    def __init__(self, **kwargs: "Environment") -> None:
        self.store: typing.Dict[str, Identifier] = {}
        self.outer = kwargs.get("outer", None)

    def get_var(self, name: str) -> typing.Optional[Object]:
        """Get a variable in the current environment."""

        # Get the variable from the store.
        var = self.store.get(name, None)

        # If var is None and there is no outer environment, return None.
        if var is None and self.outer is None:
            return None

        if var is None and self.outer is not None:
            return self.outer.get_var(name)
        elif var is not None:
            return var.value
        else:
            return None

    def set_var(self, name: str, val: Object, **kwargs: bool) -> Object:
        tp = (
            IdentType.VARIABLE if not kwargs.get("const", False) else IdentType.CONSTANT
        )

        self.store[name] = Identifier(tp, val)
        return val

    def reassign_var(self, name: str, val: Object) -> typing.Optional[bool]:
        if self.store.get(name, None) is None:
            return False

        tp = self.store[name].tp
        if tp == IdentType.CONSTANT:
            return None

        self.store[name].value = val
        return True
