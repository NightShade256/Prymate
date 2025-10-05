import unittest

from prymate.ast import (
    ExpressionStatement,
    Identifier,
    IntegerLiteral,
    LetStatement,
    PrefixExpression,
    ReturnStatement,
    InfixExpression,
    Expression,
    BooleanLiteral,
    IfExpression,
    FunctionLiteral,
    CallExpression,
    StringLiteral,
    ArrayLiteral,
    IndexExpression,
    DictionaryLiteral,
    FloatLiteral,
)
from prymate.scanner import Scanner
from prymate.parser import Parser


class TestParser(unittest.TestCase):
    def test_let(self):
        tests = [
            ["let x = 5;", "x", 5],
            ["let y = true;", "y", True],
            ["let foobar = y;", "foobar", "y"],
        ]

        for tt in tests:
            lexer = Scanner(tt[0])
            parser = Parser(lexer)

            program = parser.parse_program()
            self._check_parser_errors(parser)

            self.assertEqual(
                len(program.statements),
                1,
                f"Expected no. of statements is 1, found {len(program.statements)}.",
            )

            stmt = program.statements[0]

            self._test_let_statement(stmt, tt[1])
            self._test_literal_exp(stmt.value, tt[2])

    def test_return(self):
        tests = [
            ["return 5;", 5],
            ["return true;", True],
            ["return foobar;", "foobar"],
        ]
        for tt in tests:
            lexer = Scanner(tt[0])
            parser = Parser(lexer)

            program = parser.parse_program()
            self._check_parser_errors(parser)

            self.assertEqual(
                len(program.statements),
                1,
                f"Expected 1 statements, found {len(program.statements)}.",
            )

            stmt = program.statements[0]
            if not isinstance(stmt, ReturnStatement):
                self.fail(f"Expected ReturnStatement, got {stmt}.")

            self.assertEqual(
                stmt.token_literal(),
                "return",
                f"Expected 'return', got {stmt.token_literal()}.",
            )

            self._test_literal_exp(stmt.return_value, tt[1])

    def test_identifier(self):
        inputcase = "foobar;"
        lexer = Scanner(inputcase)
        parser = Parser(lexer)
        program = parser.parse_program()

        self._check_parser_errors(parser)

        self.assertEqual(
            len(program.statements),
            1,
            f"Program has not enough statements, got {len(program.statements)}.",
        )

        if not isinstance(program.statements[0], ExpressionStatement):
            self.fail(f"program.statements[0] not a instance of ExpressionStatement.")

        ident = program.statements[0].expression
        if not isinstance(ident, Identifier):
            self.fail(f"Exp not a instance of Identifier.")

        self.assertEqual(
            ident.value, "foobar", f"ident.value != foobar, got {ident.value}."
        )
        self.assertEqual(
            ident.token_literal(),
            "foobar",
            f"ident.token_literal() != foobar, got {ident.token_literal()}.",
        )

    def test_integer_literal_statement(self):
        inputcase = "5;"
        lexer = Scanner(inputcase)
        parser = Parser(lexer)
        program = parser.parse_program()

        self._check_parser_errors(parser)

        self.assertEqual(
            len(program.statements),
            1,
            f"Program has not enough statements, got {len(program.statements)}.",
        )

        if not isinstance(program.statements[0], ExpressionStatement):
            self.fail(f"program.statements[0] not a instance of ExpressionStatement.")

        ident = program.statements[0].expression
        if not isinstance(ident, IntegerLiteral):
            self.fail(f"Exp not a instance of IntegerLiteral.")

        self.assertEqual(ident.value, 5, f"ident.value != 5, got {ident.value}.")
        self.assertEqual(
            ident.token_literal(),
            "5",
            f"ident.token_literal() != 5, got {ident.token_literal()}.",
        )

    def test_parsing_prefix_exp(self):
        prefix_tests = [
            ["!5;", "!", 5],
            ["-15;", "-", 15],
            ["!true", "!", True],
            ["!false", "!", False],
        ]

        for tt in prefix_tests:
            lexer = Scanner(tt[0])
            parser = Parser(lexer)

            program = parser.parse_program()
            self._check_parser_errors(parser)

            self.assertEqual(
                len(program.statements),
                1,
                f"Program has not enough statements, got {len(program.statements)}.",
            )

            if not isinstance(program.statements[0], ExpressionStatement):
                self.fail(
                    f"program.statements[0] not a instance of ExpressionStatement."
                )

            ident = program.statements[0].expression
            if not isinstance(ident, PrefixExpression):
                self.fail(f"Exp not a instance of PrefixExpression.")

            self.assertEqual(
                ident.operator,
                tt[1],
                f"ident.operator != {tt[1]}, got {ident.operator}.",
            )

            self._test_literal_exp(ident.right, tt[2])

    def test_parsing_infix_exp(self):
        infix_tests = [
            ["5 + 5;", 5, "+", 5],
            ["5 - 5;", 5, "-", 5],
            ["5 * 5;", 5, "*", 5],
            ["1.5 * 1.5;", 1.5, "*", 1.5],
            ["5 / 5;", 5, "/", 5],
            ["5 % 5;", 5, "%", 5],
            ["5 > 5;", 5, ">", 5],
            ["5 < 5;", 5, "<", 5],
            ["5 == 5;", 5, "==", 5],
            ["5 != 5;", 5, "!=", 5],
            ["true == true", True, "==", True],
            ["true != false", True, "!=", False],
            ["false == false", False, "==", False],
        ]

        for tt in infix_tests:
            lexer = Scanner(tt[0])
            parser = Parser(lexer)

            program = parser.parse_program()
            self._check_parser_errors(parser)

            self.assertEqual(
                len(program.statements),
                1,
                f"Program has not enough statements, got {len(program.statements)}.",
            )

            if not isinstance(program.statements[0], ExpressionStatement):
                self.fail(
                    f"program.statements[0] not a instance of ExpressionStatement."
                )

            ident = program.statements[0].expression
            self._test_infix_exp(ident, tt[1], tt[2], tt[3])

    def test_complex_exp(self):
        tests = [
            ["-a * b", "((-a) * b)"],
            ["!-a", "(!(-a))"],
            ["a + b + c", "((a + b) + c)"],
            ["a + b - c", "((a + b) - c)"],
            ["a * b * c", "((a * b) * c)"],
            ["a * b / c", "((a * b) / c)"],
            ["a + b / c", "(a + (b / c))"],
            ["a + b % c", "(a + (b % c))"],
            ["a + b * c + d / e - f", "(((a + (b * c)) + (d / e)) - f)"],
            ["3 + 4; -5 * 5", "(3 + 4)((-5) * 5)"],
            ["5 > 4 == 3 < 4", "((5 > 4) == (3 < 4))"],
            ["5 < 4 != 3 > 4", "((5 < 4) != (3 > 4))"],
            ["3 + 4 * 5 == 3 * 1 + 4 * 5", "((3 + (4 * 5)) == ((3 * 1) + (4 * 5)))"],
            ["3 + 4 * 5 == 3 * 1 + 4 * 5", "((3 + (4 * 5)) == ((3 * 1) + (4 * 5)))"],
            [
                "3.12 + 4 * 5.3 == 3 * 1 + 4 * 5",
                "((3.12 + (4 * 5.3)) == ((3 * 1) + (4 * 5)))",
            ],
            ["true", "true"],
            ["false", "false"],
            ["3 > 5 == false", "((3 > 5) == false)"],
            ["3.5 > 5.039411 == false", "((3.5 > 5.039411) == false)"],
            ["3 < 5 == true", "((3 < 5) == true)"],
            ["1 + (2 + 3) + 4", "((1 + (2 + 3)) + 4)"],
            ["(5 + 5) * 2", "((5 + 5) * 2)"],
            ["2 / (5 + 5)", "(2 / (5 + 5))"],
            ["-(5 + 5)", "(-(5 + 5))"],
            ["!(true == true)", "(!(true == true))"],
            ["a + add(b * c) + d", "((a + add((b * c))) + d)"],
            [
                "add(a, b, 1, 2 * 3, 4 + 5, add(6, 7 * 8))",
                "add(a, b, 1, (2 * 3), (4 + 5), add(6, (7 * 8)))",
            ],
            ["add(a + b + c * d / f + g)", "add((((a + b) + ((c * d) / f)) + g))"],
            ["a * [1, 2, 3, 4][b * c] * d", "((a * ([1, 2, 3, 4][(b * c)])) * d)"],
            [
                "add(a * b[2], b[1], 2 * [1, 2][1])",
                "add((a * (b[2])), (b[1]), (2 * ([1, 2][1])))",
            ],
        ]

        for tt in tests:
            lexer = Scanner(tt[0])
            parser = Parser(lexer)
            program = parser.parse_program()
            self._check_parser_errors(parser)

            actual = str(program)

            self.assertEqual(actual, tt[1], f"Expected {tt[1]}, got {str(program)}.")

    def test_if_expression(self):
        input_case = "if (x < y) { x }"

        lexer = Scanner(input_case)
        parser = Parser(lexer)

        program = parser.parse_program()

        self._check_parser_errors(parser)

        self.assertEqual(
            len(program.statements),
            1,
            f"Program has not enough statements, got {len(program.statements)}.",
        )

        stmt = program.statements[0]

        if not isinstance(stmt, ExpressionStatement):
            self.fail(f"Expected ExpressionStatement, got {stmt}.")

        exp = stmt.expression
        if not isinstance(exp, IfExpression):
            self.fail(f"Expected IfExpression, got {exp}.")

        self._test_infix_exp(exp.condition, "x", "<", "y")

        self.assertEqual(
            len(exp.consequence.statements),
            1,
            f"If Consequence has not enough statements, got {len(program.statements)}.",
        )

        consequence = exp.consequence.statements[0]

        if not isinstance(consequence, ExpressionStatement):
            self.fail(f"Expected ExpressionStatement, got {consequence}.")

        self._test_identifier(consequence.expression, "x")
        if hasattr(exp, "alternative"):
            self.fail(f"Expression's alternative is not None, got {exp.alternative}.")

    def test_if_else_exp(self):
        input_case = "if (x < y) { x } else { y }"

        lexer = Scanner(input_case)
        parser = Parser(lexer)

        program = parser.parse_program()

        self._check_parser_errors(parser)

        self.assertEqual(
            len(program.statements),
            1,
            f"Program has not enough statements, got {len(program.statements)}.",
        )

        stmt = program.statements[0]

        if not isinstance(stmt, ExpressionStatement):
            self.fail(f"Expected ExpressionStatement, got {stmt}.")

        exp = stmt.expression
        if not isinstance(exp, IfExpression):
            self.fail(f"Expected IfExpression, got {exp}.")

        self._test_infix_exp(exp.condition, "x", "<", "y")

        self.assertEqual(
            len(exp.consequence.statements),
            1,
            f"If Consequence has not enough statements, got {len(program.statements)}.",
        )

        consequence = exp.consequence.statements[0]

        if not isinstance(consequence, ExpressionStatement):
            self.fail(f"Expected ExpressionStatement, got {consequence}.")

        self._test_identifier(consequence.expression, "x")

        self.assertEqual(
            len(exp.alternative.statements),
            1,
            f"exp.alternative was not None, got {exp.alternative}",
        )

        alt = exp.alternative.statements[0]
        if not isinstance(alt, ExpressionStatement):
            self.fail(f"Expected ExpressionStatement, got {alt}.")
        self._test_identifier(alt.expression, "y")

    def test_function_literal_parsing(self):
        input_case = "fn(x, y) { x + y; }"

        lexer = Scanner(input_case)
        parser = Parser(lexer)

        program = parser.parse_program()

        self._check_parser_errors(parser)

        self.assertEqual(
            len(program.statements),
            1,
            f"Program has not enough statements, got {len(program.statements)}.",
        )

        stmt = program.statements[0]

        if not isinstance(stmt, ExpressionStatement):
            self.fail(f"Expected ExpressionStatement, got {stmt}.")

        exp = stmt.expression
        if not isinstance(exp, FunctionLiteral):
            self.fail(f"Expected FunctionLiteral, got {exp}.")

        self.assertEqual(
            len(exp.parameters), 2, f"Expected 2 params, got {len(exp.parameters)}."
        )
        self._test_literal_exp(exp.parameters[0], "x")
        self._test_literal_exp(exp.parameters[1], "y")

        self.assertEqual(
            len(exp.body.statements),
            1,
            f"Expected 1 statement, got {len(exp.body.statements)}.",
        )

        body_stmt = exp.body.statements[0]
        if not isinstance(body_stmt, ExpressionStatement):
            self.fail(f"Expected ExpressionStatement, got {body_stmt}.")

        self._test_infix_exp(body_stmt.expression, "x", "+", "y")

    def test_fnparameter_parsing(self):
        tests = [
            ["fn() {};", []],
            ["fn(x) {};", ["x"]],
            ["fn(x, y, z) {};", ["x", "y", "z"]],
        ]

        for tt in tests:
            lexer = Scanner(tt[0])
            parser = Parser(lexer)

            program = parser.parse_program()
            self._check_parser_errors(parser)

            stmt = program.statements[0]
            function = stmt.expression

            self.assertEqual(
                len(function.parameters),
                len(tt[1]),
                f"Expected {len(tt[1])} params, got {len(function.parameters)}.",
            )

            for i, ident in enumerate(tt[1]):
                self._test_literal_exp(function.parameters[i], ident)

    def test_callexp_parsing(self):
        input_case = "add(1, 2 * 3, 4 + 5)"
        lexer = Scanner(input_case)
        parser = Parser(lexer)

        program = parser.parse_program()
        self._check_parser_errors(parser)

        self.assertEqual(
            len(program.statements),
            1,
            f"Program has not enough statements, got {len(program.statements)}.",
        )

        stmt = program.statements[0]

        if not isinstance(stmt, ExpressionStatement):
            self.fail(f"Expected ExpressionStatement, got {stmt}.")

        exp = stmt.expression
        if not isinstance(exp, CallExpression):
            self.fail(f"Expected CallExpression, got {exp}.")

        self._test_identifier(exp.function, "add")
        self.assertEqual(
            len(exp.arguments), 3, f"Wrong length of args, got {len(exp.arguments)}."
        )

        self._test_literal_exp(exp.arguments[0], 1)
        self._test_infix_exp(exp.arguments[1], 2, "*", 3)
        self._test_infix_exp(exp.arguments[2], 4, "+", 5)

    def test_string_literal_exp(self):
        input_case = '"hello world";'
        lexer = Scanner(input_case)
        parser = Parser(lexer)

        program = parser.parse_program()
        self._check_parser_errors(parser)

        stmt = program.statements[0]
        literal = stmt.expression

        if not isinstance(literal, StringLiteral):
            self.fail(f"literal is not a StringLiteral, got {literal}.")

        self.assertEqual(
            literal.value,
            "hello world",
            f"literal value expected 'hello world', got {literal.value}.",
        )

    def test_parsing_array_literals(self):
        input_case = "[1, 2 * 2, 3 + 3]"
        lexer = Scanner(input_case)
        parser = Parser(lexer)

        program = parser.parse_program()
        self._check_parser_errors(parser)

        stmt = program.statements[0]
        array = stmt.expression
        if not isinstance(array, ArrayLiteral):
            self.fail(f"exp not ast.ArrayLiteral. got={array}")

        self.assertEqual(
            len(array.elements),
            3,
            f"len(array.elements) not 3. got={len(array.elements)}",
        )

        self._test_int_literal(array.elements[0], 1)
        self._test_infix_exp(array.elements[1], 2, "*", 2)
        self._test_infix_exp(array.elements[2], 3, "+", 3)

    def test_parsing_index_exp(self):
        input_case = "myArray[1 + 1]"
        lexer = Scanner(input_case)
        parser = Parser(lexer)

        program = parser.parse_program()
        self._check_parser_errors(parser)

        stmt = program.statements[0]
        index_exp = stmt.expression

        if not isinstance(index_exp, IndexExpression):
            self.fail(f"exp not ast.IndexExpression. got={index_exp}")

        self._test_identifier(
            index_exp.left, "myArray",
        )
        self._test_infix_exp(index_exp.index, 1, "+", 1)

    def test_parsing_dict(self):
        input_case = '{"one": 1, "two": 2, "three": 3}'
        lexer = Scanner(input_case)
        parser = Parser(lexer)

        program = parser.parse_program()
        self._check_parser_errors(parser)

        stmt = program.statements[0].expression
        if not isinstance(stmt, DictionaryLiteral):
            self.fail(f"Expected DictionaryLiteral, got {stmt}.")

        self.assertEqual(
            len(stmt.pairs), 3, f"hash.pairs has wrong length. got {len(stmt.pairs)}."
        )

        tests = {"one": 1, "two": 2, "three": 3}

        for key, val in stmt.pairs.items():
            if not isinstance(key, StringLiteral):
                self.fail(f"key not StringLiteral, got {key}.")

            expected = tests[str(key)]
            self._test_int_literal(val, expected)

    def test_parsing_dict_withexp(self):
        input_case = '{"one": 0 + 1, "two": 10 - 8, "three": 15 / 5}'
        lexer = Scanner(input_case)
        parser = Parser(lexer)

        program = parser.parse_program()
        self._check_parser_errors(parser)

        stmt = program.statements[0].expression
        if not isinstance(stmt, DictionaryLiteral):
            self.fail(f"Expected DictionaryLiteral, got {stmt}.")

        self.assertEqual(
            len(stmt.pairs), 3, f"hash.pairs has wrong length. got {len(stmt.pairs)}."
        )

        tests = {
            "one": lambda e: self._test_infix_exp(e, 0, "+", 1),
            "two": lambda e: self._test_infix_exp(e, 10, "-", 8),
            "three": lambda e: self._test_infix_exp(e, 15, "/", 5),
        }

        for key, val in stmt.pairs.items():
            if not isinstance(key, StringLiteral):
                self.fail(f"key not StringLiteral, got {key}.")

            test_func = tests.get(str(key), None)
            self.assertNotEqual(
                test_func, None, f"No test function for key {str(key)} found."
            )
            test_func(val)

    def test_parsing_emptydict(self):
        input_case = "{}"
        lexer = Scanner(input_case)
        parser = Parser(lexer)

        program = parser.parse_program()
        self._check_parser_errors(parser)

        stmt = program.statements[0].expression
        if not isinstance(stmt, DictionaryLiteral):
            self.fail(f"Expected DictionaryLiteral, got {stmt}.")

        self.assertEqual(
            len(stmt.pairs), 0, f"hash.pairs has wrong length. got {len(stmt.pairs)}."
        )

    def _test_int_literal(self, il: IntegerLiteral, value: int):
        if not isinstance(il, IntegerLiteral):
            self.fail(f"Exp not a instance of IntegerLiteral. Found {il}.")

        self.assertEqual(il.value, value, f"il.value is {il.value}, expected {value}.")
        self.assertEqual(
            il.token_literal(),
            str(value),
            f"il.token_literal() is {il.token_literal()}, expected {str(value)}.",
        )

    def _test_bool_literal(self, bl: BooleanLiteral, value: bool):
        if not isinstance(bl, BooleanLiteral):
            self.fail(f"Expected BooleanLiteral, got {bl}.")
        self.assertEqual(bl.value, value, f"Expected {value}, got {bl.value}")
        self.assertEqual(
            bl.token_literal(), str(value).lower(), f"Expected {value}, got {bl.value}"
        )

    def _test_identifier(self, exp: Identifier, value: str):
        if not isinstance(exp, Identifier):
            self.fail(f"Expected Identifier, got {exp}.")

        self.assertEqual(exp.value, value, f"Expected {value}, got {exp.value}")
        self.assertEqual(
            exp.token_literal(), value, f"Expected {value}, got {exp.token_literal()}"
        )

    def _test_literal_exp(self, exp: Expression, expected):
        if isinstance(expected, bool):
            self._test_bool_literal(exp, expected)
        elif isinstance(expected, int):
            self._test_int_literal(exp, expected)
        elif isinstance(expected, float):
            self._test_float_literal(exp, expected)
        elif isinstance(expected, str):
            self._test_identifier(exp, expected)

    def _test_float_literal(self, fl: FloatLiteral, value: int):
        if not isinstance(fl, FloatLiteral):
            self.fail(f"Exp not a instance of FloatLiteral. Found {fl}.")

        self.assertEqual(fl.value, value, f"fl.value is {fl.value}, expected {value}.")
        self.assertEqual(
            fl.token_literal(),
            str(value),
            f"il.token_literal() is {fl.token_literal()}, expected {str(value)}.",
        )

    def _test_infix_exp(self, exp: InfixExpression, left, operator, right):
        if not isinstance(exp, InfixExpression):
            self.fail(f"Expected InfixExpression, got {exp}.")

        self._test_literal_exp(exp.left, left)
        self.assertEqual(
            exp.operator, operator, f"Expected {operator}, got {exp.operator}."
        )
        self._test_literal_exp(exp.right, right)

    def _test_let_statement(self, statement, name):
        self.assertEqual(
            statement.token_literal(),
            "let",
            f"statement.token_literal() not let, got {statement.token_literal()}.",
        )
        if not isinstance(statement, LetStatement):
            self.fail(f"statement not LetStatement, got {statement}.")

        self.assertEqual(
            statement.name.value,
            name,
            f"stmt.name.value not {name}, got {statement.name.value}.",
        )
        self.assertEqual(
            statement.name.token_literal(),
            name,
            f"token_literal() not {name}, got {statement.name.token_literal()}.",
        )

    def _check_parser_errors(self, parser: Parser):
        errors = parser.errors
        if errors:
            fmt = f"Parser encountered {len(errors)} errors.\n"
            for error in errors:
                fmt += f"{error}\n"
            self.fail(fmt)
            for x in errors:
                print(f"Parser error: {x}")


if __name__ == "__main__":
    unittest.main()
