from prymate.token import get_identifier_type, Token, TokenType

__all__ = ["Scanner"]


class Scanner:
    """Converts Monkey source code into a stream of tokens."""

    def __init__(self, source: str) -> None:
        self.source = source + "\0"  # handle EOF in a simpler way
        self.start = 0
        self.current = 0

    def make_token(self, ttype: TokenType) -> Token:
        """Construct a token with the proper lexeme based on Scanner position."""

        return Token(ttype, self.source[self.start : self.current])

    def is_eof(self):
        """Indicate whether end of file has been reached."""

        return self.source[self.current] == "\0"

    def advance(self) -> str:
        """Read a single character from the source."""

        self.current += 1
        return self.source[self.current - 1]

    def match(self, expected: str) -> bool:
        """Compare with current character and consume it if it's a match."""

        if self.is_eof() or self.source[self.current] != expected:
            return False

        self.current += 1
        return True

    def peek(self) -> str:
        """Get the current character without consuming it."""

        return self.source[self.current]

    def skip_whitespace(self) -> None:
        """Skips all whitespace, till the next non-whitespace character in the source."""

        while True:
            match self.peek():
                case " " | "\r" | "\t" | "\n":
                    self.advance()

                case _:
                    return

    def read_string(self) -> Token:
        "Scan a string enclosed in double quotes."

        while self.peek() != '"' and not self.is_eof():
            self.advance()

        if self.is_eof():
            return self.make_token(TokenType.ERROR)

        self.advance()
        return self.make_token(TokenType.STRING)

    def read_integer(self) -> Token:
        "Scan an integer."

        while self.peek().isdigit():
            self.advance()

        return self.make_token(TokenType.INT)

    def read_identifier(self) -> Token:
        "Scan an identifer or a keyword."

        while self.peek().isalpha() or self.peek().isdigit():
            self.advance()

        return self.make_token(
            get_identifier_type(self.source[self.start : self.current])
        )

    def scan_token(self) -> Token:
        """Generate next token from the given source."""

        self.skip_whitespace()
        self.start = self.current

        if self.is_eof():
            return self.make_token(TokenType.EOF)

        c = self.advance()

        match c:
            case "=":
                if self.match("="):
                    return self.make_token(TokenType.EQ)

                return self.make_token(TokenType.ASSIGN)

            case "+":
                return self.make_token(TokenType.PLUS)

            case "-":
                return self.make_token(TokenType.MINUS)

            case "!":
                if self.match("="):
                    return self.make_token(TokenType.NOT_EQ)

                return self.make_token(TokenType.BANG)

            case "*":
                return self.make_token(TokenType.ASTERISK)

            case "/":
                return self.make_token(TokenType.SLASH)

            case "%":
                return self.make_token(TokenType.MODULO)

            case "<":
                return self.make_token(TokenType.LT)

            case ">":
                return self.make_token(TokenType.GT)

            case ",":
                return self.make_token(TokenType.COMMA)

            case ";":
                return self.make_token(TokenType.SEMICOLON)

            case ":":
                return self.make_token(TokenType.COLON)

            case ".":
                return self.make_token(TokenType.DOT)

            case "(":
                return self.make_token(TokenType.LPAREN)

            case ")":
                return self.make_token(TokenType.RPAREN)

            case "{":
                return self.make_token(TokenType.LBRACE)

            case "}":
                return self.make_token(TokenType.RBRACE)

            case "[":
                return self.make_token(TokenType.LBRACKET)

            case "]":
                return self.make_token(TokenType.RBRACKET)

            case '"':
                return self.read_string()

            case _:
                if c.isalpha() or c == "_":
                    return self.read_identifier()

                if c.isdigit():
                    return self.read_integer()

                pass

        return self.make_token(TokenType.ERROR)
