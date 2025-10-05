import dataclasses
import enum

__all__ = ["get_identifier_type", "TokenType", "Token"]


class TokenType(enum.Enum):
    """Enumeration of all token types used by the lexer."""

    # Special tokens
    ERROR = "ERROR"
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
    MODULO = "%"  # ext
    LT = "<"
    GT = ">"
    EQ = "=="
    NOT_EQ = "!="

    # Delimiters
    COMMA = ","
    SEMICOLON = ";"
    COLON = ":"
    DOT = "."  # ext
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
    CONST = "CONST"  # ext
    WHILE = "WHILE"  # ext


@dataclasses.dataclass
class Token:
    """Represents a lexical token with its type, and literal (if any)."""

    ttype: TokenType
    lexeme: str


# Reserved identifiers (keywords) list for the Monkey language.
MONKEY_KEYWORDS = {
    "fn": TokenType.FUNCTION,
    "let": TokenType.LET,
    "true": TokenType.TRUE,
    "false": TokenType.FALSE,
    "if": TokenType.IF,
    "else": TokenType.ELSE,
    "return": TokenType.RETURN,
    "const": TokenType.CONST,  # ext
    "while": TokenType.WHILE,  # ext
}


def get_identifier_type(ident: str) -> TokenType:
    """Return the keyword token type if the identifier is reserved, otherwise TokenType.IDENT."""

    return MONKEY_KEYWORDS.get(ident, TokenType.IDENT)
