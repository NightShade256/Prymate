from dataclasses import dataclass

__all__ = [
    "Node",
    "Statement",
    "Expression",
    "Program",
    "Identifier",
    "IntegerLiteral",
    "FloatLiteral",
    "BooleanLiteral",
    "StringLiteral",
    "ArrayLiteral",
    "DictionaryLiteral",
    "BlockStatement",
    "FunctionLiteral",
    "PrefixExpression",
    "InfixExpression",
    "IfExpression",
    "CallExpression",
    "IndexExpression",
    "ExpressionStatement",
    "LetStatement",
    "ConstStatement",
    "ReturnStatement",
    "ReassignStatement",
    "WhileStatement",
]


class Node:
    pass


class Statement(Node):
    pass


class Expression(Node):
    pass


@dataclass
class Program(Node):
    statements: list[Statement]


@dataclass
class Identifier(Expression):
    name: str


@dataclass
class IntegerLiteral(Expression):
    value: int


@dataclass
class FloatLiteral(Expression):
    value: float


@dataclass
class BooleanLiteral(Expression):
    value: bool


@dataclass(frozen=True)
class StringLiteral(Expression):
    value: str


@dataclass
class ArrayLiteral(Expression):
    elements: list[Expression]


@dataclass
class DictionaryLiteral(Expression):
    entries: list[tuple[Expression, Expression]]


@dataclass
class BlockStatement(Statement):
    statements: list[Statement]


@dataclass
class FunctionLiteral(Expression):
    body: BlockStatement
    parameters: list[Identifier]


@dataclass
class PrefixExpression(Expression):
    operator: str  # TODO: replace with an enum
    operand: Expression


@dataclass
class InfixExpression(Expression):
    left: Expression
    operator: str  # TODO: replace with an enum
    right: Expression


@dataclass
class IfExpression(Expression):
    condition: Expression
    consequence: BlockStatement
    alternative: BlockStatement | None


@dataclass
class CallExpression(Expression):
    function: Expression
    arguments: list[Expression]


@dataclass
class IndexExpression(Expression):
    expression: Expression
    index: Expression


@dataclass
class ExpressionStatement(Statement):
    expression: Expression


@dataclass
class LetStatement(Statement):
    lvalue: Identifier
    rvalue: Expression


@dataclass
class ConstStatement(Statement):
    lvalue: Identifier
    rvalue: Expression


@dataclass
class ReturnStatement(Statement):
    value: Expression


@dataclass
class ReassignStatement(Statement):
    lvalue: Identifier  # TODO: support mutable indexing of arrays
    rvalue: Expression


@dataclass
class WhileStatement(Statement):
    condition: Expression
    consequence: BlockStatement
