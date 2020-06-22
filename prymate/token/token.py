import enum


class TokenType(enum.Enum):
    """The enumeration for different types of tokens."""

    ILLEGAL = "ILLEGAL"
    EOF = "EOF"

    # Identifiers and literals
    IDENT = "IDENT"
    INT = "INT"
    STRING = "STRING"

    # Operators
    ASSIGN = "="
    PLUS = "+"
    MINUS = "-"
    BANG = "!"
    ASTERISK = "*"
    SLASH = "/"

    LT = "<"
    GT = ">"

    EQ = "=="
    NOT_EQ = "!="

    # Delimiters
    COMMA = ","
    SEMICOLON = ";"
    COLON = ":"

    LPAREN = "("
    RPAREN = ")"
    LBRACE = "{"
    RBRACE = "}"
    LBRACKET = "["
    RBRACKET = "]"

    # Keywords
    FUNCTION = "FUNCTION"
    LET = "LET"
    TRUE = "TRUE"
    FALSE = "FALSE"
    IF = "IF"
    ELSE = "ELSE"
    RETURN = "RETURN"


class Token:
    """Represents a token."""

    def __init__(self, tp: TokenType, literal: str) -> None:
        self.tp = tp
        self.literal = literal

    def __repr__(self) -> str:
        return f"<Token type: {self.tp} literal: {self.literal}>"

    def __str__(self) -> str:
        return f"<Token type: {self.tp} literal: {self.literal}>"


KEYWORDS = {
    "fn": TokenType.FUNCTION,
    "let": TokenType.LET,
    "true": TokenType.TRUE,
    "false": TokenType.FALSE,
    "if": TokenType.IF,
    "else": TokenType.ELSE,
    "return": TokenType.RETURN,
}


def lookup_ident(ident: str) -> TokenType:
    return KEYWORDS.get(ident, TokenType.IDENT)
