import enum
import typing

from prymate import ast
from prymate.ast import Expression
from prymate.scanner import Scanner
from prymate.token import TokenType

__all__ = ["Parser"]


class Precedence(enum.Enum):
    LOWEST = 0  # lowest
    EQUALS = 1
    LESSGREATER = 2
    SUM = 3
    PRODUCT = 4
    PREFIX = 5
    CALL = 6
    INDEX = 7  # highest


OPERATOR_PRECEDENCE_TABLE = {
    TokenType.EQ: Precedence.EQUALS,
    TokenType.NOT_EQ: Precedence.EQUALS,
    TokenType.LT: Precedence.LESSGREATER,
    TokenType.GT: Precedence.LESSGREATER,
    TokenType.PLUS: Precedence.SUM,
    TokenType.MINUS: Precedence.SUM,
    TokenType.SLASH: Precedence.PRODUCT,
    TokenType.ASTERISK: Precedence.PRODUCT,
    TokenType.LPAREN: Precedence.CALL,
    TokenType.LBRACKET: Precedence.INDEX,
    TokenType.MODULO: Precedence.PRODUCT,
}


class Parser:
    def __init__(self, scanner: Scanner) -> None:
        self.scanner = scanner
        self.parser_errors: list[str] = []

        self.current = self.scanner.next_token()
        self.next = self.scanner.next_token()

        self.prefix_parse_fns = {
            TokenType.IDENT: self.parse_identifier,
            TokenType.INT: self.parse_numeric_literal,
            TokenType.BANG: self.parse_prefix_expression,
            TokenType.MINUS: self.parse_prefix_expression,
            TokenType.TRUE: self.parse_boolean_literal,
            TokenType.FALSE: self.parse_boolean_literal,
            TokenType.LPAREN: self.parse_grouped_expression,
            TokenType.IF: self.parse_if_expression,
            TokenType.FUNCTION: self.parse_function_literal,
            TokenType.STRING: self.parse_string_literal,
            TokenType.LBRACKET: self.parse_array_literal,
            TokenType.LBRACE: self.parse_dictionary_literal,
        }

        self.infix_parse_fns = {
            TokenType.PLUS: self.parse_infix_expression,
            TokenType.MINUS: self.parse_infix_expression,
            TokenType.SLASH: self.parse_infix_expression,
            TokenType.ASTERISK: self.parse_infix_expression,
            TokenType.EQ: self.parse_infix_expression,
            TokenType.NOT_EQ: self.parse_infix_expression,
            TokenType.LT: self.parse_infix_expression,
            TokenType.GT: self.parse_infix_expression,
            TokenType.LPAREN: self.parse_call_expression,
            TokenType.LBRACKET: self.parse_index_expression,
            TokenType.MODULO: self.parse_infix_expression,
        }

    def advance(self) -> None:
        """Advance by one token."""

        self.current = self.next
        self.next = self.scanner.next_token()

    def expect(self, ttype: TokenType) -> bool:
        """Compare next token's type with given type, if it's a match advance, else log error."""

        if self.next.type == ttype:
            self.advance()
            return True

        self.parser_errors.append(
            f"Expected next token's type to be {ttype}, instead got type {self.next.type}."
        )

        return False

    def current_precedence(self) -> Precedence:
        return OPERATOR_PRECEDENCE_TABLE.get(self.current.type, Precedence.LOWEST)

    def peek_precedence(self) -> Precedence:
        return OPERATOR_PRECEDENCE_TABLE.get(self.next.type, Precedence.LOWEST)

    def parse_program(self) -> ast.Program:
        """Parse the given token stream into an AST."""

        statements: list[ast.Statement] = []

        while self.current.type != TokenType.EOF:
            statement = self.parse_statement()

            if statement is not None:
                statements.append(statement)

            self.advance()

        return ast.Program(statements)

    def parse_statement(self) -> ast.Statement | None:
        match self.current.type:
            case TokenType.LET:
                return self.parse_let_statement()

            case TokenType.RETURN:
                return self.parse_return_statement()

            case TokenType.CONST:
                return self.parse_const_statement()

            case TokenType.WHILE:
                return self.parse_while_statement()

            case TokenType.IDENT if self.next.type == TokenType.ASSIGN:
                return self.parse_reassign_statement()

            case _:
                return self.parse_expression_statement()

    def parse_let_statement(self) -> ast.LetStatement | None:
        if not self.expect(TokenType.IDENT):
            return None

        lvalue = ast.Identifier(self.current.lexeme)

        if not self.expect(TokenType.ASSIGN):
            return None

        self.advance()

        if (rvalue := self.parse_expression(Precedence.LOWEST)) is None:
            return None

        if self.next.type == TokenType.SEMICOLON:
            self.advance()

        return ast.LetStatement(lvalue, rvalue)

    def parse_const_statement(self) -> ast.ConstStatement | None:
        if not self.expect(TokenType.IDENT):
            return None

        lvalue = ast.Identifier(self.current.lexeme)

        if not self.expect(TokenType.ASSIGN):
            return None

        self.advance()

        if (rvalue := self.parse_expression(Precedence.LOWEST)) is None:
            return None

        if self.next.type == TokenType.SEMICOLON:
            self.advance()

        return ast.ConstStatement(lvalue, rvalue)

    def parse_reassign_statement(self) -> ast.ReassignStatement | None:
        lvalue = ast.Identifier(self.current.lexeme)

        if not self.expect(TokenType.ASSIGN):
            return None

        self.advance()

        if (rvalue := self.parse_expression(Precedence.LOWEST)) is None:
            return None

        if self.next.type == TokenType.SEMICOLON:
            self.advance()

        return ast.ReassignStatement(lvalue, rvalue)

    def parse_while_statement(self) -> ast.WhileStatement | None:
        if not self.expect(TokenType.LPAREN):
            return None

        self.advance()

        if (condition := self.parse_expression(Precedence.LOWEST)) is None:
            return None

        if not self.expect(TokenType.RPAREN):
            return None

        if not self.expect(TokenType.LBRACE):
            return None

        consequence = self.parse_block_statement()

        # ext
        return ast.WhileStatement(condition, consequence)

    def parse_return_statement(self) -> ast.ReturnStatement | None:
        self.advance()

        if (value := self.parse_expression(Precedence.LOWEST)) is None:
            return None

        if self.next.type == TokenType.SEMICOLON:
            self.advance()

        return ast.ReturnStatement(value)

    def parse_expression_statement(self) -> ast.ExpressionStatement | None:
        if (expression := self.parse_expression(Precedence.LOWEST)) is None:
            return None

        if self.next.type == TokenType.SEMICOLON:
            self.advance()

        return ast.ExpressionStatement(expression)

    def parse_identifier(self) -> ast.Identifier:
        return ast.Identifier(self.current.lexeme)

    def parse_numeric_literal(
        self,
    ) -> ast.IntegerLiteral | ast.FloatLiteral | None:
        try:
            integer_value = int(self.current.lexeme)
        except ValueError:
            self.parser_errors.append(
                f"Could not parse {self.current.lexeme} as an integer."
            )

            return None

        if self.next.type == TokenType.DOT:
            self.advance()  # consume the integer literal
            self.advance()  # consume the dot

            try:
                return ast.FloatLiteral(float(f"{integer_value}.{self.current.lexeme}"))
            except ValueError:
                self.parser_errors.append(
                    f"Could not parse {self.current.lexeme} as a float."
                )

                return None
        else:
            return ast.IntegerLiteral(integer_value)

    def parse_boolean_literal(self) -> ast.BooleanLiteral:
        return ast.BooleanLiteral(TokenType.TRUE == self.current.type)

    def parse_string_literal(self) -> ast.StringLiteral:
        return ast.StringLiteral(self.current.lexeme[1:-1])  # remove the double quotes

    def parse_prefix_expression(self) -> ast.PrefixExpression | None:
        operator = self.current.lexeme

        # consume the unary operator
        self.advance()

        if (operand := self.parse_expression(Precedence.PREFIX)) is None:
            return None

        return ast.PrefixExpression(operator, operand)

    def parse_infix_expression(
        self, left: ast.Expression
    ) -> ast.InfixExpression | None:
        operator = self.current.lexeme
        precedence = self.current_precedence()

        self.advance()

        if (right := self.parse_expression(precedence)) is None:
            return None

        return ast.InfixExpression(left, operator, right)

    def parse_expression(self, precedence: Precedence) -> ast.Expression | None:
        if (
            prefix_parse_fn := self.prefix_parse_fns.get(self.current.type, None)
        ) is None:
            self.parser_errors.append(f"Invalid prefix token type: {self.current.type}")

            return None

        expression = prefix_parse_fn()

        while (
            self.next.type != TokenType.SEMICOLON
            and precedence.value < self.peek_precedence().value
        ):
            if (
                infix_parse_fn := self.infix_parse_fns.get(self.next.type, None)
            ) is None or expression is None:  # TODO: check this condition
                return expression

            self.advance()
            expression = infix_parse_fn(expression)

        return expression

    def parse_grouped_expression(self) -> ast.Expression | None:
        self.advance()
        expression = self.parse_expression(Precedence.LOWEST)

        if not self.expect(TokenType.RPAREN):
            return None

        return expression

    def parse_if_expression(self) -> ast.IfExpression | None:
        if not self.expect(TokenType.LPAREN):
            return None

        self.advance()

        if (condition := self.parse_expression(Precedence.LOWEST)) is None:
            return None

        if not self.expect(TokenType.RPAREN):
            return None

        if not self.expect(TokenType.LBRACE):
            return None

        consequence = self.parse_block_statement()
        alternative: ast.BlockStatement | None = None

        if self.next.type == TokenType.ELSE:
            self.advance()

            if not self.expect(TokenType.LBRACE):
                return None

            alternative = self.parse_block_statement()

        return ast.IfExpression(condition, consequence, alternative)

    def parse_block_statement(self) -> ast.BlockStatement:
        self.advance()

        # temporary storage
        statements: list[ast.Statement] = []

        while (
            self.current.type != TokenType.RBRACE and self.current.type != TokenType.EOF
        ):
            statment = self.parse_statement()

            if statment is not None:
                statements.append(statment)

            self.advance()

        return ast.BlockStatement(statements)

    def parse_function_literal(self) -> ast.FunctionLiteral | None:
        if not self.expect(TokenType.LPAREN):
            return None

        if (parameters := self.parse_function_parameters()) is None:
            return None

        if not self.expect(TokenType.LBRACE):
            return None

        body = self.parse_block_statement()
        return ast.FunctionLiteral(body, parameters)

    def parse_function_parameters(self) -> list[ast.Identifier] | None:
        identifiers: list[ast.Identifier] = []

        if self.next.type == TokenType.RPAREN:
            self.advance()
            return identifiers

        self.advance()

        identifier = ast.Identifier(self.current.lexeme)
        identifiers.append(identifier)

        while self.next.type == TokenType.COMMA:
            self.advance()
            self.advance()

            identifier = ast.Identifier(self.current.lexeme)
            identifiers.append(identifier)

        if not self.expect(TokenType.RPAREN):
            return None

        return identifiers

    def parse_call_expression(
        self, function: ast.Expression
    ) -> ast.CallExpression | None:
        if (arguments := self.parse_expression_list(TokenType.RPAREN)) is None:
            return None

        return ast.CallExpression(function, arguments)

    def parse_array_literal(self) -> ast.ArrayLiteral | None:
        if (elements := self.parse_expression_list(TokenType.RBRACKET)) is None:
            return None

        return ast.ArrayLiteral(elements)

    def parse_expression_list(
        self, end_delimiter: TokenType
    ) -> list[Expression] | None:
        arguments: typing.List[Expression] = []

        if self.next.type == end_delimiter:
            self.advance()
            return arguments

        self.advance()

        if (expression := self.parse_expression(Precedence.LOWEST)) is None:
            return None

        arguments.append(expression)

        while self.next.type == TokenType.COMMA:
            self.advance()
            self.advance()

            if (expression := self.parse_expression(Precedence.LOWEST)) is None:
                return None

            arguments.append(expression)

        if not self.expect(end_delimiter):
            return None

        return arguments

    def parse_index_expression(
        self, expression: ast.Expression
    ) -> ast.IndexExpression | None:
        self.advance()

        if (index := self.parse_expression(Precedence.LOWEST)) is None:
            return None

        if not self.expect(TokenType.RBRACKET):
            return None

        return ast.IndexExpression(expression, index)

    def parse_dictionary_literal(self) -> ast.DictionaryLiteral | None:
        pairs: list[tuple[Expression, Expression]] = []

        while self.next.type != TokenType.RBRACE:
            self.advance()
            key = self.parse_expression(Precedence.LOWEST)

            if key is None:
                return None

            if not self.expect(TokenType.COLON):
                return None

            self.advance()
            value = self.parse_expression(Precedence.LOWEST)

            if value is None:
                return None

            pairs.append((key, value))

            if self.next.type == TokenType.COMMA:
                self.advance()

        if not self.expect(TokenType.RBRACE):
            return None

        return ast.DictionaryLiteral(pairs)
