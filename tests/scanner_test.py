import unittest

from prymate.scanner import Scanner
from prymate.token import TokenType

TEST_INPUT = """
let five = 5;
let ten = 10;

let add = fn(x, y) {
    x + y;
};

let result = add(five, ten);
!-/*5;
5 < 10 > 5;

if (5 < 10) {
    return true;
} else {
    return false;
}

10 == 10;
10 != 9;
10let
"foobar"
"foo bar"
[1, 2];
:
%
..
const
"""


class TestLexer(unittest.TestCase):
    def test_output(self):
        expected_output = [
            [TokenType.LET, "let"],
            [TokenType.IDENT, "five"],
            [TokenType.ASSIGN, "="],
            [TokenType.INT, "5"],
            [TokenType.SEMICOLON, ";"],
            [TokenType.LET, "let"],
            [TokenType.IDENT, "ten"],
            [TokenType.ASSIGN, "="],
            [TokenType.INT, "10"],
            [TokenType.SEMICOLON, ";"],
            [TokenType.LET, "let"],
            [TokenType.IDENT, "add"],
            [TokenType.ASSIGN, "="],
            [TokenType.FUNCTION, "fn"],
            [TokenType.LPAREN, "("],
            [TokenType.IDENT, "x"],
            [TokenType.COMMA, ","],
            [TokenType.IDENT, "y"],
            [TokenType.RPAREN, ")"],
            [TokenType.LBRACE, "{"],
            [TokenType.IDENT, "x"],
            [TokenType.PLUS, "+"],
            [TokenType.IDENT, "y"],
            [TokenType.SEMICOLON, ";"],
            [TokenType.RBRACE, "}"],
            [TokenType.SEMICOLON, ";"],
            [TokenType.LET, "let"],
            [TokenType.IDENT, "result"],
            [TokenType.ASSIGN, "="],
            [TokenType.IDENT, "add"],
            [TokenType.LPAREN, "("],
            [TokenType.IDENT, "five"],
            [TokenType.COMMA, ","],
            [TokenType.IDENT, "ten"],
            [TokenType.RPAREN, ")"],
            [TokenType.SEMICOLON, ";"],
            [TokenType.BANG, "!"],
            [TokenType.MINUS, "-"],
            [TokenType.SLASH, "/"],
            [TokenType.ASTERISK, "*"],
            [TokenType.INT, "5"],
            [TokenType.SEMICOLON, ";"],
            [TokenType.INT, "5"],
            [TokenType.LT, "<"],
            [TokenType.INT, "10"],
            [TokenType.GT, ">"],
            [TokenType.INT, "5"],
            [TokenType.SEMICOLON, ";"],
            [TokenType.IF, "if"],
            [TokenType.LPAREN, "("],
            [TokenType.INT, "5"],
            [TokenType.LT, "<"],
            [TokenType.INT, "10"],
            [TokenType.RPAREN, ")"],
            [TokenType.LBRACE, "{"],
            [TokenType.RETURN, "return"],
            [TokenType.TRUE, "true"],
            [TokenType.SEMICOLON, ";"],
            [TokenType.RBRACE, "}"],
            [TokenType.ELSE, "else"],
            [TokenType.LBRACE, "{"],
            [TokenType.RETURN, "return"],
            [TokenType.FALSE, "false"],
            [TokenType.SEMICOLON, ";"],
            [TokenType.RBRACE, "}"],
            [TokenType.INT, "10"],
            [TokenType.EQ, "=="],
            [TokenType.INT, "10"],
            [TokenType.SEMICOLON, ";"],
            [TokenType.INT, "10"],
            [TokenType.NOT_EQ, "!="],
            [TokenType.INT, "9"],
            [TokenType.SEMICOLON, ";"],
            [TokenType.INT, "10"],
            [TokenType.LET, "let"],
            [TokenType.STRING, "foobar"],
            [TokenType.STRING, "foo bar"],
            [TokenType.LBRACKET, "["],
            [TokenType.INT, "1"],
            [TokenType.COMMA, ","],
            [TokenType.INT, "2"],
            [TokenType.RBRACKET, "]"],
            [TokenType.SEMICOLON, ";"],
            [TokenType.COLON, ":"],
            [TokenType.MODULO, "%"],
            [TokenType.DOT, "."],
            [TokenType.DOT, "."],
            [TokenType.CONST, "const"],
            [TokenType.EOF, ""],
        ]

        test_lexer = Scanner(TEST_INPUT)

        for tt in expected_output:
            tok = test_lexer.scan_token()

            self.assertEqual(tok.ttype, tt[0], f"Should be {tt[0]}")
            self.assertEqual(tok.lexeme, tt[1], f"Should be {tt[1]}")


if __name__ == "__main__":
    unittest.main()
