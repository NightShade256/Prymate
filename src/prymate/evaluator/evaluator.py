import typing

from prymate import ast, objects

__all__ = [
    "evaluate",
    "eval_program",
]


def evaluate(
    node: ast.Node, env: objects.Environment
) -> typing.Optional[objects.Object]:
    """Evaluate AST recursively."""
    if isinstance(node, ast.Program):
        return eval_program(node.statements, env)
    elif isinstance(node, ast.ExpressionStatement):
        return evaluate(node.expression, env)
    elif isinstance(node, ast.IntegerLiteral):
        return objects.Integer(node.value)
    elif isinstance(node, ast.FloatLiteral):
        return objects.Float(node.value)
    elif isinstance(node, ast.BooleanLiteral):
        if node.value:
            return objects.Boolean(True)

        return objects.Boolean(False)
    elif isinstance(node, ast.StringLiteral):
        value = str(node.value)
        return objects.String(value)
    elif isinstance(node, ast.PrefixExpression):
        right = evaluate(node.right, env)
        if is_error(right) or right is None:
            return right

        return eval_prefix_exp(node.operator, right)
    elif isinstance(node, ast.InfixExpression):
        left = evaluate(node.left, env)
        if is_error(left) or left is None:
            return left

        right = evaluate(node.right, env)
        if is_error(right) or right is None:
            return right

        return eval_infix_exp(node.operator, left, right)
    elif isinstance(node, ast.BlockStatement):
        return eval_block_statements(node, env)
    elif isinstance(node, ast.IfExpression):
        return eval_if_exp(node, env)
    elif isinstance(node, ast.ReturnStatement):
        val = evaluate(node.return_value, env)
        if is_error(val) or val is None:
            return val

        return objects.ReturnValue(val)
    elif isinstance(node, ast.LetStatement):
        exp = node.value
        if not isinstance(exp, ast.Expression):
            return None

        val = evaluate(exp, env)
        if is_error(val) or val is None:
            return val

        env.set_var(node.name.value, val)
    elif isinstance(node, ast.ReassignStatement):
        exp = node.value
        if not isinstance(exp, ast.Expression):
            return None

        val = evaluate(exp, env)
        if is_error(val) or val is None:
            return val

        success = env.reassign_var(node.name.value, val)
        if success is None:
            return objects.Error(f"cannot modify const identifier: {node.name.value}")
        elif not success:
            return objects.Error(f"identifier not found: {node.name.value}")
    elif isinstance(node, ast.WhileStatement):
        return eval_while_stmt(node, env)
    elif isinstance(node, ast.ConstStatement):
        exp = node.value
        if not isinstance(exp, ast.Expression):
            return None

        val = evaluate(exp, env)
        if is_error(val) or val is None:
            return val

        env.set_var(node.name.value, val, const=True)
    elif isinstance(node, ast.Identifier):
        return eval_identifier(node, env)
    elif isinstance(node, ast.FunctionLiteral):
        params = node.parameters
        body = node.body
        return objects.Function(params, body, env)
    elif isinstance(node, ast.CallExpression):
        function = evaluate(node.function, env)
        if is_error(function) or function is None:
            return function

        args = eval_exps(node.arguments, env)
        if args is None:
            return args

        if len(args) == 1 and isinstance(args[0], objects.Error):
            return args[0]

        return apply_function(function, args)
    elif isinstance(node, ast.ArrayLiteral):
        elements = eval_exps(node.elements, env)
        if elements is None:
            return elements

        if len(elements) == 1 and isinstance(elements[0], objects.Error):
            return elements[0]

        return objects.Array(elements)
    elif isinstance(node, ast.IndexExpression):
        left = evaluate(node.left, env)
        if is_error(left) or left is None:
            return left

        index = evaluate(node.index, env)
        if is_error(index) or index is None:
            return index

        return eval_index_expression(left, index)
    elif isinstance(node, ast.DictionaryLiteral):
        return eval_dictionary_literal(node, env)

    return None


def eval_program(
    stmts: typing.List[ast.Statement], env: objects.Environment
) -> typing.Optional[objects.Object]:
    result: typing.Optional[objects.Object] = None

    for statement in stmts:
        result = evaluate(statement, env)
        if isinstance(result, objects.ReturnValue):
            return result.value
        elif isinstance(result, objects.Error):
            return result

    return result


def eval_prefix_exp(operator: str, right: objects.Object) -> objects.Object:
    if operator == "!":
        return eval_bang_operator_exp(right)
    elif operator == "-":
        return eval_minus_preoperator_exp(right)
    else:
        return objects.Error(f"unknown operator: {operator}{right.tp().value}")


def eval_bang_operator_exp(right: objects.Object) -> objects.Object:
    if right is objects.Boolean(True):
        return objects.Boolean(False)
    elif right is objects.Boolean(False):
        return objects.Boolean(True)
    elif right is objects.Null():
        return objects.Boolean(True)
    else:
        return objects.Boolean(False)


def eval_minus_preoperator_exp(right: objects.Object) -> objects.Object:
    if not isinstance(right, objects.Integer) and not isinstance(right, objects.Float):
        return objects.Error(f"unknown operator: -{right.tp().value}")

    if isinstance(right, objects.Integer):
        return objects.Integer(-right.value)
    else:
        return objects.Float(-right.value)


def eval_infix_exp(
    operator: str, left: objects.Object, right: objects.Object
) -> objects.Object:
    if (isinstance(left, objects.Integer) or isinstance(left, objects.Float)) and (
        isinstance(right, objects.Integer) or isinstance(right, objects.Float)
    ):
        return eval_numeric_infix_exp(operator, left, right)
    elif isinstance(left, objects.Boolean) and isinstance(right, objects.Boolean):
        return eval_bool_infix_exp(operator, left, right)
    elif isinstance(left, objects.String) and isinstance(right, objects.String):
        return eval_string_infix_exp(operator, left, right)
    elif operator == "==":
        return to_boolean_singleton(left is right)
    elif operator == "!=":
        return to_boolean_singleton(left is not right)
    elif left.tp() != right.tp():
        return objects.Error(
            f"type mismatch: {left.tp().value} {operator} {right.tp().value}"
        )
    else:
        return objects.Error(
            f"unknown operator: {left.tp().value} {operator} {right.tp().value}"
        )


def eval_numeric_infix_exp(
    operator: str,
    left: typing.Union[objects.Integer, objects.Float],
    right: typing.Union[objects.Integer, objects.Float],
) -> objects.Object:
    left_val = left.value
    right_val = right.value

    if operator == "+":
        return create_numeric_object(left_val + right_val)
    elif operator == "-":
        return create_numeric_object(left_val - right_val)
    elif operator == "*":
        return create_numeric_object(left_val * right_val)
    elif operator == "/":
        return create_numeric_object(left_val / right_val)
    elif operator == "%":
        return create_numeric_object(left_val % right_val)
    elif operator == "<":
        return to_boolean_singleton(left_val < right_val)
    elif operator == ">":
        return to_boolean_singleton(left_val > right_val)
    elif operator == "==":
        return to_boolean_singleton(left_val == right_val)
    elif operator == "!=":
        return to_boolean_singleton(left_val != right_val)
    else:
        return objects.Error(
            f"unknown operator: {left.tp().value} {operator} {right.tp().value}"
        )


def create_numeric_object(value: typing.Union[int, float]) -> objects.Object:
    if isinstance(value, float):
        return objects.Float(value)
    elif isinstance(value, int):
        return objects.Integer(value)
    else:
        return objects.Error(f"Cannot create a numeric object out of value {value}.")


def eval_bool_infix_exp(
    operator: str, left: objects.Boolean, right: objects.Boolean
) -> objects.Object:
    if operator == "==":
        return to_boolean_singleton(left is right)
    elif operator == "!=":
        return to_boolean_singleton(left is not right)
    else:
        return objects.Error(
            f"unknown operator: {left.tp().value} {operator} {right.tp().value}"
        )


def eval_string_infix_exp(
    operator: str, left: objects.String, right: objects.String
) -> objects.Object:
    if operator == "+":
        return objects.String(left.value + right.value)
    elif operator == "==":
        return to_boolean_singleton(left.value == right.value)
    elif operator == "!=":
        return to_boolean_singleton(left.value != right.value)
    else:
        return objects.Error(
            f"unknown operator: {left.tp().value} {operator} {right.tp().value}"
        )


def eval_if_exp(
    exp: ast.IfExpression, env: objects.Environment
) -> typing.Optional[objects.Object]:
    condition = evaluate(exp.condition, env)
    if is_error(condition) or condition is None:
        return condition

    if is_truthy(condition):
        return evaluate(exp.consequence, env)
    elif hasattr(exp, "alternative"):
        return evaluate(exp.alternative, env)
    else:
        return objects.Null()


def eval_while_stmt(
    stmt: ast.WhileStatement, env: objects.Environment
) -> typing.Optional[objects.Object]:
    while True:
        condition = evaluate(stmt.condition, env)
        if is_error(condition) or condition is None:
            return condition

        if is_truthy(condition):
            consequence = evaluate(stmt.consequence, env)

            if is_error(consequence):
                return consequence

        else:
            break

    return None


def eval_block_statements(
    block: ast.BlockStatement, env: objects.Environment
) -> typing.Optional[objects.Object]:
    result: typing.Optional[objects.Object] = None

    for stmt in block.statements:
        result = evaluate(stmt, env)

        if result is not None:
            tp = result.tp()
            if tp == objects.ObjectType.RETURN_VALUE or tp == objects.ObjectType.ERROR:
                return result

    return result


def eval_identifier(node: ast.Identifier, env: objects.Environment) -> objects.Object:
    val = env.get_var(node.value)
    if val is not None:
        return val

    val = objects.BUILTINS.get(node.value, None)
    if val is not None:
        return val

    return objects.Error(f"identifier not found: {node.value}")


def eval_dictionary_literal(
    node: ast.DictionaryLiteral, env: objects.Environment
) -> typing.Optional[objects.Object]:
    pairs = {}

    for keynode, valnode in node.pairs.items():
        key = evaluate(keynode, env)
        if is_error(key) or key is None:
            return key

        if not isinstance(key, objects.Hashable):
            return objects.Error(f"unusable as hash key: {key.tp().value}")

        value = evaluate(valnode, env)
        if is_error(value) or value is None:
            return value

        hashed = key.hashkey()
        pairs[hashed] = objects.HashPair(key, value)

    return objects.Dictionary(pairs)


def eval_exps(
    exps: typing.List[ast.Expression], env: objects.Environment
) -> typing.Optional[typing.List[objects.Object]]:
    result = []

    for exp in exps:
        evaluated = evaluate(exp, env)
        if evaluated is None:
            return evaluated

        if is_error(evaluated):
            return [evaluated]

        result.append(evaluated)

    return result


def apply_function(
    fn: objects.Object, args: typing.List[objects.Object]
) -> typing.Optional[objects.Object]:
    if isinstance(fn, objects.Function):
        extended_env = extend_function_env(fn, args)
        if isinstance(extended_env, objects.Error):
            return extended_env
        evaluated = evaluate(fn.body, extended_env)
        if evaluated is None:
            return evaluated

        return unwrap_return_value(evaluated)
    elif isinstance(fn, objects.Builtin):
        return fn.function(args)
    else:
        return objects.Error(f"not a function: {fn.tp()}")


def extend_function_env(
    fn: objects.Function, args: typing.List[objects.Object]
) -> typing.Union[objects.Environment, objects.Error]:
    env = objects.Environment(outer=fn.env)

    for count, param in enumerate(fn.parameters):
        try:
            env.set_var(param.value, args[count])
        except IndexError:
            return objects.Error(f"{param.value} argument missing from function call.")

    return env


def unwrap_return_value(obj: objects.Object) -> objects.Object:
    if isinstance(obj, objects.ReturnValue):
        return obj.value

    return obj


def eval_index_expression(
    left: objects.Object, index: objects.Object
) -> objects.Object:
    if isinstance(left, objects.Array) and isinstance(index, objects.Integer):
        return eval_array_index_exp(left, index)
    elif isinstance(left, objects.Dictionary):
        return eval_dict_index_exp(left, index)
    else:
        return objects.Error(f"index operator not supported: {left.tp().value}")


def eval_array_index_exp(
    array: objects.Array, index: objects.Integer
) -> objects.Object:
    idx = index.value
    max_len = len(array.elements) - 1

    if idx < 0 or idx > max_len:
        return objects.Null()

    return array.elements[idx]


def eval_dict_index_exp(
    dictionary: objects.Dictionary, index: objects.Object
) -> objects.Object:

    if not isinstance(index, objects.Hashable):
        return objects.Error(f"unusable as dictionary key: {index.tp().value}")

    pair = dictionary.pairs.get(index.hashkey(), None)
    if pair is None:
        return objects.Null()

    return pair.value


def to_boolean_singleton(case: bool) -> objects.Boolean:
    if case:
        return objects.Boolean(True)

    return objects.Boolean(False)


def is_truthy(obj: objects.Object) -> bool:
    if obj is objects.Null():
        return False
    elif obj is objects.Boolean(True):
        return True
    elif obj is objects.Boolean(False):
        return False
    else:
        return True


def is_error(obj: typing.Any) -> bool:
    """Check if the provided argument is a Error Object."""
    if obj is not None and isinstance(obj, objects.Object):
        return isinstance(obj, objects.Error)

    return False
