import typing
from typing import List

from prymate.token import Token

__all__ = [
    "Node",
    "Expression",
    "Identifier",
    "IntegerLiteral",
    "ExpressionStatement",
    "LetStatement",
    "Program",
    "ReturnStatement",
    "Statement",
    "PrefixExpression",
    "InfixExpression",
    "BooleanLiteral",
    "IfExpression",
    "BlockStatement",
    "FunctionLiteral",
    "CallExpression",
    "StringLiteral",
    "ArrayLiteral",
    "IndexExpression",
    "DictionaryLiteral",
    "FloatLiteral",
    "ReassignStatement",
    "ConstStatement",
    "WhileStatement",
]


class Node:
    """Class that represents a node."""

    def token_literal(self) -> str:
        raise NotImplementedError()

    def __str__(self) -> str:
        return ""


class Statement(Node):
    """Class that represents a statement node."""

    pass


class Expression(Node):
    """Class that represents an expression node."""

    pass


class Program(Node):
    """Represents the root node in the program AST."""

    def __init__(self) -> None:
        self.statements: typing.List[Statement] = []

    def __str__(self) -> str:
        fmt = ""
        for x in self.statements:
            fmt += str(x)
        return fmt

    def token_literal(self) -> str:
        if self.statements:
            return self.statements[0].token_literal()

        return ""


class Identifier(Expression):
    def __init__(self, token: Token, value: str) -> None:
        self.token = token
        self.value = value

    def __str__(self) -> str:
        return self.value

    def expression_node(self) -> None:
        pass

    def token_literal(self) -> str:
        return self.token.literal


class LetStatement(Statement):
    def __init__(self, token: Token) -> None:
        self.token = token
        self.name: Identifier
        self.value: Expression

    def __str__(self) -> str:
        fmt = f"{self.token_literal()} {str(self.name)} = "
        fmt += str(self.value) if self.value is not None else ""
        fmt += ";"
        return fmt

    def statement_node(self) -> None:
        pass

    def token_literal(self) -> str:
        return self.token.literal


class ReturnStatement(Statement):
    def __init__(self, token: Token) -> None:
        self.token = token
        self.return_value: Expression

    def __str__(self) -> str:
        fmt = f"{self.token_literal()} "
        fmt += str(self.return_value) if self.return_value is not None else ""
        fmt += ";"
        return fmt

    def statement_node(self) -> None:
        pass

    def token_literal(self) -> str:
        return self.token.literal


class ReassignStatement(Statement):
    def __init__(self, token: Token) -> None:
        self.token = token
        self.name: Identifier
        self.value: Expression

    def __str__(self) -> str:
        fmt = f"{str(self.name)} = "
        fmt += str(self.value) if self.value is not None else ""
        fmt += ";"
        return fmt

    def statement_node(self) -> None:
        pass

    def token_literal(self) -> str:
        return self.token.literal


class ConstStatement(Statement):
    def __init__(self, token: Token) -> None:
        self.token = token
        self.name: Identifier
        self.value: Expression

    def __str__(self) -> str:
        fmt = f"{self.token_literal()} {str(self.name)} = "
        fmt += str(self.value) if self.value is not None else ""
        fmt += ";"
        return fmt

    def statement_node(self) -> None:
        pass

    def token_literal(self) -> str:
        return self.token.literal


class WhileStatement(Statement):
    def __init__(self, token: Token) -> None:
        self.token = token
        self.condition: Expression
        self.consequence: BlockStatement

    def __str__(self) -> str:
        fmt = f"while{str(self.condition)} {str(self.consequence)}"
        return fmt

    def token_literal(self) -> str:
        return self.token.literal

    def statement_node(self) -> None:
        pass


class ExpressionStatement(Statement):
    def __init__(self, token: Token) -> None:
        self.token = token
        self.expression: Expression

    def __str__(self) -> str:
        fmt = str(self.expression) if self.expression is not None else ""
        return fmt

    def statement_node(self) -> None:
        pass

    def token_literal(self) -> str:
        return self.token.literal


class IntegerLiteral(Expression):
    def __init__(self, token: Token) -> None:
        self.token = token
        self.value: int

    def __str__(self) -> str:
        return self.token.literal

    def token_literal(self) -> str:
        return self.token.literal


class PrefixExpression(Expression):
    def __init__(self, token: Token, operator: str) -> None:
        self.token = token
        self.operator: str = operator
        self.right: Expression

    def __str__(self) -> str:
        return f"({self.operator}{str(self.right)})"

    def token_literal(self) -> str:
        return self.token.literal


class InfixExpression(Expression):
    def __init__(self, token: Token, operator: str, left: Expression) -> None:
        self.token = token
        self.left = left
        self.operator = operator
        self.right: Expression

    def __str__(self) -> str:
        return f"({str(self.left)} {self.operator} {str(self.right)})"

    def token_literal(self) -> str:
        return self.token.literal


class BooleanLiteral(Expression):
    def __init__(self, token: Token, value: bool) -> None:
        self.token = token
        self.value = value

    def __str__(self) -> str:
        return self.token.literal

    def token_literal(self) -> str:
        return self.token.literal


class IfExpression(Expression):
    def __init__(self, token: Token) -> None:
        self.token = token
        self.condition: Expression
        self.consequence: BlockStatement
        self.alternative: BlockStatement

    def __str__(self) -> str:
        fmt = f"if{str(self.condition)} {str(self.consequence)}"
        if self.alternative is not None:
            fmt += f"else {str(self.alternative)}"

        return fmt

    def token_literal(self) -> str:
        return self.token.literal


class BlockStatement(Statement):
    def __init__(self, token: Token) -> None:
        self.token = token
        self.statements: typing.List[Statement] = []

    def __str__(self) -> str:
        fmt = ""
        for x in self.statements:
            fmt += str(x)

        return fmt

    def token_literal(self) -> str:
        return self.token.literal


class FunctionLiteral(Expression):
    def __init__(self, token: Token) -> None:
        self.token = token
        self.parameters: typing.List[Identifier] = []
        self.body: BlockStatement

    def __str__(self) -> str:
        fmt = f"{self.token_literal()}("
        params = [str(x) for x in self.parameters]
        fmt += ", ".join(params)
        fmt += ") " + str(self.body)
        return fmt

    def token_literal(self) -> str:
        return self.token.literal


class CallExpression(Expression):
    def __init__(self, token: Token, function: Expression) -> None:
        self.token = token
        self.function = function
        self.arguments: typing.List[Expression] = []

    def __str__(self) -> str:
        fmt = ""
        args = []
        for a in self.arguments:
            args.append(str(a))

        fmt += str(self.function)
        fmt += "("
        fmt += ", ".join(args)
        fmt += ")"

        return fmt

    def token_literal(self) -> str:
        return self.token.literal


class StringLiteral(Expression):
    def __init__(self, token: Token, value: str) -> None:
        self.token = token
        self.value = value

    def __str__(self) -> str:
        return self.token.literal

    def token_literal(self) -> str:
        return self.token.literal


class ArrayLiteral(Expression):
    def __init__(self, token: Token) -> None:
        self.token = token
        self.elements: List[Expression] = []

    def __str__(self) -> str:
        elements = []
        for x in self.elements:
            elements.append(str(x))

        return f"[{', '.join(elements)}]"

    def token_literal(self) -> str:
        return self.token.literal


class IndexExpression(Expression):
    def __init__(self, token: Token, left: Expression) -> None:
        self.token = token
        self.left = left
        self.index: Expression

    def __str__(self) -> str:
        return f"({str(self.left)}[{str(self.index)}])"

    def token_literal(self) -> str:
        return self.token.literal


class DictionaryLiteral(Expression):
    def __init__(self, token: Token) -> None:
        self.token = token
        self.pairs: typing.Dict[Expression, Expression] = {}

    def __str__(self) -> str:
        fmt = "{"
        pairs = []
        for key, value in self.pairs.items():
            pairs.append(f"{str(key)}:{str(value)}")
        fmt += ", ".join(pairs)
        fmt += "}"
        return fmt

    def token_literal(self) -> str:
        return self.token.literal


class FloatLiteral(Expression):
    def __init__(self, token: Token) -> None:
        self.token = token
        self.value: float

    def __str__(self) -> str:
        return str(self.value)

    def token_literal(self) -> str:
        return str(self.value)
