import pytest

from prymate import ast
from prymate.parser import Parser
from prymate.scanner import Scanner


def check_parser_errors(parser: Parser):
    if parser.parser_errors:
        fmt = f"Parser encountered {len(parser.parser_errors)} errors.\n"
        fmt += "\n".join(parser.parser_errors)

        pytest.fail(fmt)


def infix_expression_helper(
    expression: ast.Expression,
    left: ast.Expression,
    operator: str,
    right: ast.Expression,
):
    assert isinstance(expression, ast.InfixExpression)
    assert expression.left == left
    assert expression.operator == operator
    assert expression.right == right


@pytest.mark.parametrize(
    "source, identifier, expression",
    [
        ("let x = 5;", "x", ast.IntegerLiteral(5)),
        ("let y = true;", "y", ast.BooleanLiteral(True)),
        ("let foobar = y;", "foobar", ast.Identifier("y")),
        ("let foobar = 45.5;", "foobar", ast.FloatLiteral(45.5)),
        ('let asdf = "asdf";', "asdf", ast.StringLiteral("asdf")),
    ],
)
def test_let_statement(source: str, identifier: str, expression: ast.Expression):
    scanner = Scanner(source)
    parser = Parser(scanner)

    tree = parser.parse_program()

    print(tree)

    statement = tree.statements[0]
    check_parser_errors(parser)

    assert len(tree.statements) == 1
    assert isinstance(statement, ast.LetStatement)
    assert statement.lvalue.name == identifier
    assert statement.rvalue == expression


@pytest.mark.parametrize(
    "source, expression",
    [
        ("return 5;", ast.IntegerLiteral(5)),
        ("return true;", ast.BooleanLiteral(True)),
        ("return foobar;", ast.Identifier("foobar")),
    ],
)
def test_return_statement(source: str, expression: ast.Expression):
    scanner = Scanner(source)
    parser = Parser(scanner)

    tree = parser.parse_program()
    statement = tree.statements[0]
    check_parser_errors(parser)

    assert len(tree.statements) == 1
    assert isinstance(statement, ast.ReturnStatement)
    assert statement.value == expression


def test_identifier_statement():
    scanner = Scanner("foobar;")
    parser = Parser(scanner)

    tree = parser.parse_program()
    statement = tree.statements[0]
    check_parser_errors(parser)

    assert len(tree.statements) == 1
    assert isinstance(statement, ast.ExpressionStatement)
    assert isinstance(statement.expression, ast.Identifier)
    assert statement.expression.name == "foobar"


def test_integer_literal_statement():
    scanner = Scanner("5;")
    parser = Parser(scanner)

    tree = parser.parse_program()
    statement = tree.statements[0]
    check_parser_errors(parser)

    assert len(tree.statements) == 1
    assert isinstance(statement, ast.ExpressionStatement)
    assert isinstance(statement.expression, ast.IntegerLiteral)
    assert statement.expression.value == 5


def test_string_literal_statement():
    scanner = Scanner('"hello world";')
    parser = Parser(scanner)

    tree = parser.parse_program()
    statement = tree.statements[0]
    check_parser_errors(parser)

    assert len(tree.statements) == 1
    assert isinstance(statement, ast.ExpressionStatement)
    assert isinstance(statement.expression, ast.StringLiteral)
    assert statement.expression.value == "hello world"


@pytest.mark.parametrize(
    "source, operator, expression",
    [
        ("!5;", "!", ast.IntegerLiteral(5)),
        ("-15;", "-", ast.IntegerLiteral(15)),
        ("!true;", "!", ast.BooleanLiteral(True)),
        ("!false;", "!", ast.BooleanLiteral(False)),
    ],
)
def test_prefix_expression(source: str, operator: str, expression: ast.Expression):
    scanner = Scanner(source)
    parser = Parser(scanner)

    tree = parser.parse_program()
    statement = tree.statements[0]
    check_parser_errors(parser)

    assert len(tree.statements) == 1
    assert isinstance(statement, ast.ExpressionStatement)
    assert isinstance(statement.expression, ast.PrefixExpression)
    assert statement.expression.operator == operator
    assert statement.expression.operand == expression


@pytest.mark.parametrize(
    "source, left, operator, right",
    [
        ("5 + 5;", ast.IntegerLiteral(5), "+", ast.IntegerLiteral(5)),
        ("5 - 5;", ast.IntegerLiteral(5), "-", ast.IntegerLiteral(5)),
        ("5 * 5;", ast.IntegerLiteral(5), "*", ast.IntegerLiteral(5)),
        ("1.5 * 1.5;", ast.FloatLiteral(1.5), "*", ast.FloatLiteral(1.5)),
        ("5 / 5;", ast.IntegerLiteral(5), "/", ast.IntegerLiteral(5)),
        ("5 % 5;", ast.IntegerLiteral(5), "%", ast.IntegerLiteral(5)),
        ("5 > 5;", ast.IntegerLiteral(5), ">", ast.IntegerLiteral(5)),
        ("5 < 5;", ast.IntegerLiteral(5), "<", ast.IntegerLiteral(5)),
        ("5 == 5;", ast.IntegerLiteral(5), "==", ast.IntegerLiteral(5)),
        ("5 != 5;", ast.IntegerLiteral(5), "!=", ast.IntegerLiteral(5)),
        ("true == true;", ast.BooleanLiteral(True), "==", ast.BooleanLiteral(True)),
        ("true != false;", ast.BooleanLiteral(True), "!=", ast.BooleanLiteral(False)),
        ("false == false;", ast.BooleanLiteral(False), "==", ast.BooleanLiteral(False)),
    ],
)
def test_infix_expression(
    source: str, left: ast.Expression, operator: str, right: ast.Expression
):
    scanner = Scanner(source)
    parser = Parser(scanner)

    tree = parser.parse_program()
    statement = tree.statements[0]
    check_parser_errors(parser)

    assert len(tree.statements) == 1
    assert isinstance(statement, ast.ExpressionStatement)
    infix_expression_helper(statement.expression, left, operator, right)


def test_if_expression():
    scanner = Scanner("if (x < y) { x };")
    parser = Parser(scanner)

    tree = parser.parse_program()
    statement = tree.statements[0]
    check_parser_errors(parser)

    assert len(tree.statements) == 1
    assert isinstance(statement, ast.ExpressionStatement)
    assert isinstance(statement.expression, ast.IfExpression)

    infix_expression_helper(
        statement.expression.condition, ast.Identifier("x"), "<", ast.Identifier("y")
    )

    consequence = statement.expression.consequence
    alternative = statement.expression.alternative

    assert len(consequence.statements) == 1
    assert isinstance(consequence.statements[0], ast.ExpressionStatement)
    assert consequence.statements[0].expression == ast.Identifier("x")
    assert alternative is None


def test_if_else_expression():
    scanner = Scanner("if (x < y) { x } else { y }")
    parser = Parser(scanner)

    tree = parser.parse_program()
    statement = tree.statements[0]
    check_parser_errors(parser)

    assert len(tree.statements) == 1
    assert isinstance(statement, ast.ExpressionStatement)
    assert isinstance(statement.expression, ast.IfExpression)

    infix_expression_helper(
        statement.expression.condition, ast.Identifier("x"), "<", ast.Identifier("y")
    )

    consequence = statement.expression.consequence
    alternative = statement.expression.alternative

    assert len(consequence.statements) == 1
    assert isinstance(consequence.statements[0], ast.ExpressionStatement)
    assert consequence.statements[0].expression == ast.Identifier("x")

    assert alternative is not None
    assert len(alternative.statements) == 1
    assert isinstance(alternative.statements[0], ast.ExpressionStatement)
    assert alternative.statements[0].expression == ast.Identifier("y")


@pytest.mark.parametrize(
    "source, parameters",
    [
        ("fn() {};", []),
        ("fn(x) {};", [ast.Identifier("x")]),
        (
            "fn(x, y, z) {};",
            [ast.Identifier("x"), ast.Identifier("y"), ast.Identifier("z")],
        ),
    ],
)
def test_function_parameter(source: str, parameters: list[ast.Expression]):
    scanner = Scanner(source)
    parser = Parser(scanner)

    tree = parser.parse_program()
    statement = tree.statements[0]
    check_parser_errors(parser)

    assert len(tree.statements) == 1
    assert isinstance(statement, ast.ExpressionStatement)
    assert isinstance(statement.expression, ast.FunctionLiteral)
    assert statement.expression.parameters == parameters


def test_function_literal():
    scanner = Scanner("fn(x, y) { x + y; }")
    parser = Parser(scanner)

    tree = parser.parse_program()
    statement = tree.statements[0]
    check_parser_errors(parser)

    assert len(tree.statements) == 1
    assert isinstance(statement, ast.ExpressionStatement)
    assert isinstance(statement.expression, ast.FunctionLiteral)

    parameters = statement.expression.parameters
    body = statement.expression.body

    assert len(parameters) == 2
    assert parameters[0] == ast.Identifier("x")
    assert parameters[1] == ast.Identifier("y")

    assert len(body.statements) == 1
    assert isinstance(body.statements[0], ast.ExpressionStatement)

    infix_expression_helper(
        body.statements[0].expression, ast.Identifier("x"), "+", ast.Identifier("y")
    )


def test_call_expression():
    expected_output = [
        ast.IntegerLiteral(1),
        ast.InfixExpression(ast.IntegerLiteral(2), "*", ast.IntegerLiteral(3)),
        ast.InfixExpression(ast.IntegerLiteral(4), "+", ast.IntegerLiteral(5)),
    ]

    scanner = Scanner("add(1, 2 * 3, 4 + 5)")
    parser = Parser(scanner)

    tree = parser.parse_program()
    statement = tree.statements[0]
    check_parser_errors(parser)

    assert len(tree.statements) == 1
    assert isinstance(statement, ast.ExpressionStatement)
    assert isinstance(statement.expression, ast.CallExpression)
    assert statement.expression.function == ast.Identifier("add")
    assert statement.expression.arguments == expected_output


def test_array_literal():
    expected_output = [
        ast.IntegerLiteral(1),
        ast.InfixExpression(ast.IntegerLiteral(2), "*", ast.IntegerLiteral(2)),
        ast.InfixExpression(ast.IntegerLiteral(3), "+", ast.IntegerLiteral(3)),
    ]

    scanner = Scanner("[1, 2 * 2, 3 + 3]")
    parser = Parser(scanner)

    tree = parser.parse_program()
    statement = tree.statements[0]
    check_parser_errors(parser)

    assert len(tree.statements) == 1
    assert isinstance(statement, ast.ExpressionStatement)
    assert isinstance(statement.expression, ast.ArrayLiteral)
    assert statement.expression.elements == expected_output


def test_index_expression():
    scanner = Scanner("myArray[1 + 1]")
    parser = Parser(scanner)

    tree = parser.parse_program()
    statement = tree.statements[0]
    check_parser_errors(parser)

    assert len(tree.statements) == 1
    assert isinstance(statement, ast.ExpressionStatement)
    assert isinstance(statement.expression, ast.IndexExpression)

    assert statement.expression.expression == ast.Identifier("myArray")
    assert statement.expression.index == ast.InfixExpression(
        ast.IntegerLiteral(1), "+", ast.IntegerLiteral(1)
    )


def test_empty_dicitionary_literal():
    scanner = Scanner("{}")
    parser = Parser(scanner)

    tree = parser.parse_program()
    statement = tree.statements[0]
    check_parser_errors(parser)

    assert len(tree.statements) == 1
    assert isinstance(statement, ast.ExpressionStatement)
    assert isinstance(statement.expression, ast.DictionaryLiteral)
    assert statement.expression.entries == {}


def test_dictionary_literal():
    expected_output = {
        ast.StringLiteral("one"): ast.IntegerLiteral(1),
        ast.StringLiteral("two"): ast.IntegerLiteral(2),
        ast.StringLiteral("three"): ast.IntegerLiteral(3),
    }

    scanner = Scanner('{"one": 1, "two": 2, "three": 3}')
    parser = Parser(scanner)

    tree = parser.parse_program()
    statement = tree.statements[0]
    check_parser_errors(parser)

    assert len(tree.statements) == 1
    assert isinstance(statement, ast.ExpressionStatement)
    assert isinstance(statement.expression, ast.DictionaryLiteral)
    assert statement.expression.entries == expected_output


def test_dictionary_literal_with_expression():
    expected_output = {
        ast.StringLiteral("one"): ast.InfixExpression(
            ast.IntegerLiteral(0), "+", ast.IntegerLiteral(1)
        ),
        ast.StringLiteral("two"): ast.InfixExpression(
            ast.IntegerLiteral(10), "-", ast.IntegerLiteral(8)
        ),
        ast.StringLiteral("three"): ast.InfixExpression(
            ast.IntegerLiteral(15), "/", ast.IntegerLiteral(5)
        ),
    }

    scanner = Scanner('{"one": 0 + 1, "two": 10 - 8, "three": 15 / 5}')
    parser = Parser(scanner)

    tree = parser.parse_program()
    statement = tree.statements[0]
    check_parser_errors(parser)

    assert len(tree.statements) == 1
    assert isinstance(statement, ast.ExpressionStatement)
    assert isinstance(statement.expression, ast.DictionaryLiteral)
    assert statement.expression.entries == expected_output
