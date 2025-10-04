import typing

from prymate.token import Token, TokenType, lookup_ident

__all__ = ["Lexer"]


class Lexer:
    """Represents the Monkey Language Lexer."""

    def __init__(self, code: str) -> None:
        self.code = code
        self.position = 0
        self.read_position = 0
        self.ch = ""

        self.read_char()

    def read_char(self) -> None:
        """Read a character from the input."""
        if self.read_position >= len(self.code):
            self.ch = "\0"
        else:
            self.ch = self.code[self.read_position]

        self.position = self.read_position
        self.read_position += 1

    def next_token(self) -> Token:
        """Generate the next token from the input."""

        tok: Token

        self.skip_whitespace()

        if self.ch == "=":
            if self.peek_char() == "=":
                ch = self.ch
                self.read_char()
                tok = Token(TokenType.EQ, ch + self.ch)
            else:
                tok = Token(TokenType.ASSIGN, self.ch)
        elif self.ch == "+":
            tok = Token(TokenType.PLUS, self.ch)
        elif self.ch == "-":
            tok = Token(TokenType.MINUS, self.ch)
        elif self.ch == "!":
            if self.peek_char() == "=":
                ch = self.ch
                self.read_char()
                tok = Token(TokenType.NOT_EQ, ch + self.ch)
            else:
                tok = Token(TokenType.BANG, self.ch)
        elif self.ch == "/":
            tok = Token(TokenType.SLASH, self.ch)
        elif self.ch == "*":
            tok = Token(TokenType.ASTERISK, self.ch)
        elif self.ch == "%":
            tok = Token(TokenType.MODULO, self.ch)
        elif self.ch == "<":
            tok = Token(TokenType.LT, self.ch)
        elif self.ch == ">":
            tok = Token(TokenType.GT, self.ch)
        elif self.ch == ";":
            tok = Token(TokenType.SEMICOLON, self.ch)
        elif self.ch == ":":
            tok = Token(TokenType.COLON, self.ch)
        elif self.ch == ",":
            tok = Token(TokenType.COMMA, self.ch)
        elif self.ch == ".":
            tok = Token(TokenType.DOT, self.ch)
        elif self.ch == "(":
            tok = Token(TokenType.LPAREN, self.ch)
        elif self.ch == ")":
            tok = Token(TokenType.RPAREN, self.ch)
        elif self.ch == "{":
            tok = Token(TokenType.LBRACE, self.ch)
        elif self.ch == "}":
            tok = Token(TokenType.RBRACE, self.ch)
        elif self.ch == '"':
            tok = Token(TokenType.STRING, self.read_string())
        elif self.ch == "[":
            tok = Token(TokenType.LBRACKET, self.ch)
        elif self.ch == "]":
            tok = Token(TokenType.RBRACKET, self.ch)
        elif self.ch == "\0":
            tok = Token(TokenType.EOF, "")
        else:
            if self.ch.isalpha() or self.ch == "_":
                ident = self.read_identifier()
                tok = Token(lookup_ident(ident), ident)
                return tok
            elif self.ch.isdigit():
                tok = Token(TokenType.INT, self.read_number())
                return tok
            else:
                tok = Token(TokenType.ILLEGAL, self.ch)

        self.read_char()
        return tok

    def read_identifier(self) -> str:
        """Read a identifier from the input."""

        pos = self.position
        while self.ch.isalpha() or self.ch == "_":
            self.read_char()

            # if EOF break the loop, else it raises an error.
            if self.ch == "\0":
                break

        return self.code[pos : self.position]

    def read_number(self) -> str:
        """Read a number from the input."""

        pos = self.position
        while self.ch.isdigit():
            self.read_char()

            # If EOF break the loop, else it raises an error.
            if self.ch == "\0":
                break

        return self.code[pos : self.position]

    def read_string(self) -> str:
        pos = self.position + 1
        while True:
            self.read_char()
            if self.ch == '"' or self.ch == "\0":
                break

        return self.code[pos : self.position]

    def skip_whitespace(self) -> None:
        """Skips the whitespaces in the input."""
        if self.ch == "\0":
            return

        while self.ch.isspace():
            self.read_char()

    def peek_char(self) -> typing.Union[str, int]:
        """Peek the next character in the input."""

        if self.read_position >= len(self.code):
            return 0
        else:
            return self.code[self.read_position]
