import pytest

from prymate import ast, evaluator, objects
from prymate.parser import Parser
from prymate.scanner import Scanner


def evaluate_runner(source: str):
    scanner = Scanner(source)
    parser = Parser(scanner)
    program = parser.parse_program()

    return evaluator.evaluate(objects.Environment(), program)


@pytest.mark.parametrize(
    "expression, result",
    [
        ("5", 5),
        ("10", 10),
        ("-5", -5),
        ("-10", -10),
        ("5 + 5 + 5 + 5 - 10", 10),
        ("2 * 2 * 2 * 2 * 2", 32),
        ("-50 + 100 + -50", 0),
        ("5 * 2 + 10", 20),
        ("5 + 2 * 10", 25),
        ("20 + 2 * -10", 0),
        ("50 / 2 * 2 + 10", 60),
        ("2 * (5 + 10)", 30),
        ("3 * 3 * 3 + 10", 37),
        ("3 * (3 * 3) + 10", 37),
        ("(5 + 10 * 2 + 15 / 3) * 2 + -10", 50),
        ("2 * 3 % 4 * 2", 4),
        ("2 * 3 % 4 * 2 - 10", -6),
        ("2.2 * 2", 4.4),
        ("12 / 6", 2.0),
        ("12.2 / 2", 6.1),
        ("1.5 * -1.5", -2.25),
    ],
)
def test_numeric_expression(expression: str, result: int | float):
    evaluated = evaluate_runner(expression)

    assert evaluated == (
        objects.Integer(result) if isinstance(result, int) else objects.Float(result)
    )


@pytest.mark.parametrize(
    "expression, result",
    [
        ("true", True),
        ("false", False),
        ("1 < 2", True),
        ("1 > 2", False),
        ("1 < 1", False),
        ("1 > 1", False),
        ("1 == 1", True),
        ("1 != 1", False),
        ("1 == 2", False),
        ("1.0 == 2", False),
        ("1.0 == 2.0", False),
        ("1 == 2.0", False),
        ("2.0 == 2", True),
        ("2.0 == 2.0", True),
        ("2 == 2.0", True),
        ("1.0 != 2", True),
        ("1 != 2.0", True),
        ("true == true", True),
        ("false == false", True),
        ("true == false", False),
        ("true != false", True),
        ("false != true", True),
        ("(1 < 2) == true", True),
        ("(1 < 2) == false", False),
        ("(1 > 2) == true", False),
        ("(1 > 2) == false", True),
        ('"hello" == "heloo"', False),
        ('"hello" == "hello"', True),
        ('"jj" == 1', False),
    ],
)
def test_bool_expression(expression: str, result: bool):
    evaluated = evaluate_runner(expression)
    assert evaluated is objects.Boolean(result)


@pytest.mark.parametrize(
    "expression, result",
    [
        ("!true", False),
        ("!false", True),
        ("!5", False),
        ("!!true", True),
        ("!!false", False),
        ("!!5", True),
    ],
)
def test_bang_operator(expression: str, result: bool):
    evaluated = evaluate_runner(expression)
    assert evaluated is objects.Boolean(result)


@pytest.mark.parametrize(
    "expression, result",
    [
        ("if (true) { 10 }", 10),
        ("if (false) { 10 }", None),
        ("if (1) { 10 }", 10),
        ("if (1 < 2) { 10 }", 10),
        ("if (1 > 2) { 10 }", None),
        ("if (1 > 2) { 10 } else { 20 }", 20),
        ("if (1 < 2) { 10 } else { 20 }", 10),
    ],
)
def test_if_expression(expression: str, result: int | None):
    evaluated = evaluate_runner(expression)

    assert evaluated == (
        objects.Integer(result) if isinstance(result, int) else objects.Null()
    )


@pytest.mark.parametrize(
    "source, result",
    [
        ("return 10;", 10),
        ("return 10; 9;", 10),
        ("return 2 * 5; 9;", 10),
        ("9; return 2 * 5; 9;", 10),
        ("9; return 2 * 5.2; 9;", 10.4),
    ],
)
def test_return_statements(source: str, result: int | float):
    evaluated = evaluate_runner(source)

    assert evaluated == (
        objects.Integer(result) if isinstance(result, int) else objects.Float(result)
    )


@pytest.mark.parametrize(
    "source, result",
    [
        ("5 + true;", "cannot perform operation: 5 + true"),
        ("5 + true; 5;", "cannot perform operation: 5 + true"),
        ("-true", "cannot apply `-` prefix operator on true"),
        ("true + false;", "cannot perform operation: true + false"),
        ("true % false;", "cannot perform operation: true % false"),
        ("5; true + false; 5", "cannot perform operation: true + false"),
        ("if (10 > 1) { true + false; }", "cannot perform operation: true + false"),
        (
            """
        132
        if (10 > 1) {
        if (10 > 1) {
        return true + false;
        }
        return 1;

        """,
            "cannot perform operation: true + false",
        ),
        ("foobar", "identifier foobar not found"),
        ('"Hello" - "World"', "cannot apply infix operator - on two string values"),
        (
            '{"name": "Monkey"}[fn(x) { x }];',
            "index FUNCTION not supported on DICTIONARY",
        ),
    ],
)
def test_error_handling(source: str, result: str):
    evaluated = evaluate_runner(source)
    assert isinstance(evaluated, objects.Error) and evaluated.message == result


@pytest.mark.parametrize(
    "source, result",
    [
        ("let a = 5; a;", 5),
        ("let a = 5 * 5; a;", 25),
        ("let a = 5; let b = a; b;", 5),
        ("let a = 5; let b = a; let c = a + b + 5; c;", 15),
    ],
)
def test_let_statements(source: str, result: int):
    evaluated = evaluate_runner(source)
    assert evaluated == objects.Integer(result)


def test_function_object():
    evaluated = evaluate_runner("fn(x) { x + 2; };")

    assert (
        isinstance(evaluated, objects.Function)
        and len(evaluated.parameters) == 1
        and evaluated.parameters[0] == ast.Identifier("x")
    )

    assert evaluated.body == ast.BlockStatement(
        [
            ast.ExpressionStatement(
                ast.InfixExpression(ast.Identifier("x"), "+", ast.IntegerLiteral(2))
            )
        ]
    )


@pytest.mark.parametrize(
    "source, result",
    [
        ("let identity = fn(x) { x; }; identity(5);", 5),
        ("let identity = fn(x) { return x; }; identity(5);", 5),
        ("let double = fn(x) { x * 2; }; double(5);", 10),
        ("let add = fn(x, y) { x + y; }; add(5, 5);", 10),
        ("let add = fn(x, y) { x + y; }; add(5 + 5, add(5, 5));", 20),
        ("fn(x) { x; }(5)", 5),
    ],
)
def test_function_application(source: str, result: int):
    evaluated = evaluate_runner(source)
    assert evaluated == objects.Integer(result)


def test_string_literal():
    evaluated = evaluate_runner('"Hello, World!"')
    assert evaluated == objects.String("Hello, World!")


def test_string_concatenation():
    evaluated = evaluate_runner('"Hello" + " " + "World!"')
    assert evaluated == objects.String("Hello World!")


@pytest.mark.parametrize(
    "source, result",
    [
        ('len("")', 0),
        ('len("four")', 4),
        ('len("hello world")', 11),
        ("len(1)", "argument to `len` not supported, got INTEGER"),
        ('len("one", "two")', "wrong number of arguments. got=2, want=1"),
    ],
)
def test_builtin_functions(source: str, result: int | str):
    evaluated = evaluate_runner(source)

    if isinstance(evaluated, objects.Integer):
        assert evaluated.value == result

    if isinstance(evaluated, objects.Error):
        assert evaluated.message == result


def test_array_literals():
    evaluated = evaluate_runner("[1, 2 * 2, 3 + 3];")

    assert isinstance(evaluated, objects.Array) and evaluated.elements == [
        objects.Integer(1),
        objects.Integer(4),
        objects.Integer(6),
    ]


@pytest.mark.parametrize(
    "source, result",
    [
        ("[1, 2, 3][0]", 1),
        ("[1, 2, 3][1]", 2),
        ("[1, 2, 3][2]", 3),
        ("let i = 0; [1][i];", 1),
        ("[1, 2, 3][1 + 1];", 3),
        ("let myArray = [1, 2, 3]; myArray[2];", 3),
        ("let myArray = [1, 2, 3]; myArray[0] + myArray[1] + myArray[2];", 6),
        ("let myArray = [1, 2, 3]; let i = myArray[0]; myArray[i]", 2),
        ("[1, 2, 3][3]", None),
        ("[1, 2, 3][-1]", None),
    ],
)
def test_array_index_exp(source: str, result: int | None):
    evaluated = evaluate_runner(source)

    assert evaluated == (
        objects.Integer(result) if isinstance(result, int) else objects.Null()
    )


def test_dictionary():
    evaluated = evaluate_runner("""
        let two = "two";
        {
            "one": 10 - 9,
            "two": 1 + 1,
            "thr" + "ee": 6 / 2,
            4: 4,
            -4: 4,
            true: 5,
            false: 6
        }
        """)

    expected = {
        objects.String("one"): objects.Integer(1),
        objects.String("two"): objects.Integer(2),
        objects.String("three"): objects.Integer(3),
        objects.Integer(4): objects.Integer(4),
        objects.Integer(-4): objects.Integer(4),
        objects.Boolean(True): objects.Integer(5),
        objects.Boolean(False): objects.Integer(6),
    }

    assert isinstance(evaluated, objects.Dictionary) and evaluated.entries == expected


@pytest.mark.parametrize(
    "source, result",
    [
        ('{"foo": 5}["foo"]', 5),
        ('{"foo": 5}["bar"]', None),
        ('let key = "foo"; {"foo": 5}[key]', 5),
        ('{}["foo"]', None),
        ("{5: 5}[5]", 5),
        ("{true: 5}[true]", 5),
        ("{false: 5}[false]", 5),
    ],
)
def test_dict_index_exp(source: str, result: int | None):
    evaluated = evaluate_runner(source)

    assert evaluated == (
        objects.Integer(result) if isinstance(result, int) else objects.Null()
    )
