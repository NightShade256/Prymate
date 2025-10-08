from prymate import ast
from prymate.builtins import BUILTINS
from prymate.objects import (
    Array,
    Boolean,
    Builtin,
    Dictionary,
    Environment,
    Error,
    Float,
    Function,
    HashableObject,
    Integer,
    Null,
    Object,
    ReturnValue,
    String,
    Eq,
)

__all__ = [
    "evaluate",
    "eval_program",
]


def evaluate(env: Environment, node: ast.Node) -> Object | None:
    """Evaluate given AST recursively."""

    match node:
        case ast.Program():
            return eval_program(env, node.statements)

        case ast.Identifier():
            return eval_identifier(env, node)

        case ast.IntegerLiteral():
            return Integer(node.value)

        case ast.FloatLiteral():
            return Float(node.value)

        case ast.BooleanLiteral():
            return Boolean(node.value)

        case ast.StringLiteral():
            return String(node.value)

        case ast.ArrayLiteral():
            return eval_array_literal(env, node)

        case ast.DictionaryLiteral():
            return eval_dictionary_literal(env, node)

        case ast.BlockStatement():
            return eval_block_statement(env, node)

        case ast.FunctionLiteral():
            return Function(env, node.parameters, node.body)

        case ast.PrefixExpression():
            return eval_prefix_expression(env, node)

        case ast.InfixExpression():
            return eval_infix_expression(env, node)

        case ast.IfExpression():
            return eval_if_expression(env, node)

        case ast.CallExpression():
            return eval_call_expression(env, node)

        case ast.IndexExpression():
            return eval_index_expression(env, node)

        case ast.ExpressionStatement():
            return evaluate(env, node.expression)

        case ast.LetStatement():
            return eval_assignment_statement(env, node.lvalue, node.rvalue, True)

        case ast.ConstStatement():
            return eval_assignment_statement(env, node.lvalue, node.rvalue, False)

        case ast.ReturnStatement():
            return eval_return_statement(env, node)

        case ast.ReassignStatement():
            return eval_reassign_statement(env, node)

        case ast.WhileStatement():
            return eval_while_statement(env, node)

        case _:
            return None


def eval_program(env: Environment, statements: list[ast.Statement]) -> Object | None:
    result: Object | None = None

    for statement in statements:
        result = evaluate(env, statement)

        if isinstance(result, ReturnValue):
            return result.value

        if isinstance(result, Error):
            return result

    return result


def eval_identifier(env: Environment, node: ast.Identifier) -> Object:
    binding = env.get_binding(node.name)

    if binding is not None:
        return binding

    builtin = BUILTINS.get(node.name, None)

    if builtin is not None:
        return builtin

    return Error(f"identifier {node.name} not found")


def eval_expressions(
    env: Environment, expressions: list[ast.Expression]
) -> list[Object] | Error | None:
    results: list[Object] = []

    for expression in expressions:
        result = evaluate(env, expression)

        if result is None or isinstance(result, Error):
            return result

        results.append(result)

    return results


def eval_array_literal(env: Environment, node: ast.ArrayLiteral) -> Object | None:
    elements = eval_expressions(env, node.elements)

    if isinstance(elements, list):
        return Array(elements)

    return elements


def eval_dictionary_literal(
    env: Environment,
    node: ast.DictionaryLiteral,
) -> Object | None:
    entries: dict[HashableObject, Object] = {}

    for key_node, value_node in node.entries.items():
        key = evaluate(env, key_node)
        if key is None or isinstance(key, Error):
            return key

        if not isinstance(key, HashableObject):
            return Error(f"provided key {key.type()} is unhashable")

        value = evaluate(env, value_node)
        if value is None or isinstance(value, Error):
            return value

        entries[key] = value

    return Dictionary(entries)


def eval_block_statement(env: Environment, block: ast.BlockStatement) -> Object | None:
    result: Object | None = None

    for statement in block.statements:
        result = evaluate(env, statement)

        if result is not None:
            if isinstance(result, Error) or isinstance(result, ReturnValue):
                return result

    return result


def eval_prefix_expression(
    env: Environment, node: ast.PrefixExpression
) -> Object | None:
    operand = evaluate(env, node.operand)

    if operand is None or isinstance(operand, Error):
        return operand

    if node.operator == "!":
        return Boolean(not operand.is_truthy())

    if node.operator == "-":
        if isinstance(operand, Integer):
            return Integer(-operand.value)

        if isinstance(operand, Float):
            return Float(-operand.value)

        return Error(f"cannot apply `-` prefix operator on {str(operand)}")

    return Error(f"unknown prefix operator {node.operator}")


def create_numeric_object(value: int | float) -> Object:
    if isinstance(value, int):
        return Integer(value)

    return Float(value)


def eval_numeric_infix_expression(
    left: Integer | Float,
    operator: str,
    right: Integer | Float,
) -> Object:
    match operator:
        case "+":
            return create_numeric_object(left.value + right.value)
        case "-":
            return create_numeric_object(left.value - right.value)
        case "*":
            return create_numeric_object(left.value * right.value)
        case "/":
            return create_numeric_object(left.value / right.value)
        case "%":
            return create_numeric_object(left.value % right.value)
        case "<":
            return Boolean(left.value < right.value)
        case ">":
            return Boolean(left.value > right.value)
        case _:
            return Error(
                f"cannot apply infix operator {operator} on two numeric values"
            )


def eval_string_infix_expression(left: String, operator: str, right: String) -> Object:
    match operator:
        case "+":
            return String(left.value + right.value)

        case _:
            return Error(f"cannot apply infix operator {operator} on two string values")


def eval_infix_expression(env: Environment, node: ast.InfixExpression) -> Object | None:
    left = evaluate(env, node.left)
    if left is None or isinstance(left, Error):
        return left

    right = evaluate(env, node.right)
    if right is None or isinstance(right, Error):
        return right

    if node.operator == "==":
        return (
            Boolean(left is right)
            if not (isinstance(left, Eq) and isinstance(right, Eq))
            else Boolean(left == right)
        )

    if node.operator == "!=":
        return (
            Boolean(left is not right)
            if not (isinstance(left, Eq) and isinstance(right, Eq))
            else Boolean(left != right)
        )

    if isinstance(left, String) and isinstance(right, String):
        return eval_string_infix_expression(left, node.operator, right)

    if isinstance(left, (Integer, Float)) and isinstance(right, (Integer, Float)):
        return eval_numeric_infix_expression(left, node.operator, right)

    return Error(f"cannot perform operation: {str(left)} {node.operator} {str(right)}")


def eval_if_expression(env: Environment, node: ast.IfExpression) -> Object | None:
    condition = evaluate(env, node.condition)

    if condition is None or isinstance(condition, Error):
        return condition

    if condition.is_truthy():
        return evaluate(env, node.consequence)

    if node.alternative is not None:
        return evaluate(env, node.alternative)

    return Null()


def eval_call_expression(env: Environment, node: ast.CallExpression) -> Object | None:
    function = evaluate(env, node.function)

    if function is None or isinstance(function, Error):
        return function

    arguments = eval_expressions(env, node.arguments)

    if not isinstance(arguments, list):
        return arguments

    match function:
        case Function():
            new_env = Environment(function.env)

            for i, parameter in enumerate(function.parameters):
                try:
                    new_env.set_binding(parameter.name, arguments[i], True)
                except IndexError:
                    return Error(
                        f"{parameter.name} argument missing from function call"
                    )

            evaluated = evaluate(new_env, function.body)

            if isinstance(evaluated, ReturnValue):
                return evaluated.value

            return evaluated

        case Builtin():
            return function.function(arguments)

        case _:
            return Error(f"not a function: {function.type()}")


def eval_array_index_expression(array: Array, index: Integer) -> Object:
    if index.value < 0 or index.value > len(array.elements) - 1:
        return Null()

    return array.elements[index.value]


def eval_dictionary_index_expression(
    dictionary: Dictionary, index: HashableObject
) -> Object:
    entry = dictionary.entries.get(index, None)

    if entry is None:
        return Null()

    return entry


def eval_index_expression(env: Environment, node: ast.IndexExpression) -> Object | None:
    expression = evaluate(env, node.expression)
    if expression is None or isinstance(expression, Error):
        return expression

    index = evaluate(env, node.index)
    if index is None or isinstance(index, Error):
        return index

    if isinstance(expression, Array) and isinstance(index, Integer):
        return eval_array_index_expression(expression, index)

    if isinstance(expression, Dictionary) and isinstance(index, HashableObject):
        return eval_dictionary_index_expression(expression, index)

    return Error(f"index operator not supported: {str(expression)}")


def eval_assignment_statement(
    env: Environment, lvalue: ast.Identifier, rvalue: ast.Expression, mutable: bool
) -> Object | None:
    value = evaluate(env, rvalue)

    if value is None or isinstance(value, Error):
        return value

    env.set_binding(lvalue.name, value, mutable)


def eval_return_statement(env: Environment, node: ast.ReturnStatement) -> Object | None:
    value = evaluate(env, node.value)

    if value is None or isinstance(value, Error):
        return value

    return ReturnValue(value)


def eval_reassign_statement(
    env: Environment, node: ast.ReassignStatement
) -> Object | None:
    value = evaluate(env, node.rvalue)

    if value is None or isinstance(value, Error):
        return value

    return env.update_binding(node.lvalue.name, value)


def eval_while_statement(
    env: Environment, statement: ast.WhileStatement
) -> Object | None:
    while True:
        condition = evaluate(env, statement.condition)

        if condition is None or isinstance(condition, Error):
            return condition

        if condition.is_truthy():
            consequence = evaluate(env, statement.consequence)

            if isinstance(consequence, Error):
                return consequence
        else:
            break
