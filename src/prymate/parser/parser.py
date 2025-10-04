import enum
import typing

from prymate import ast
from prymate.ast import Expression
from prymate.lexer import Lexer
from prymate.token import Token, TokenType

__all__ = ["Parser"]


# Precedence enumeration.
class Precedences(enum.Enum):
    LOWEST = 0
    EQUALS = 1
    LESSGREATER = 2
    SUM = 3
    PRODUCT = 4
    PREFIX = 5
    CALL = 6
    INDEX = 7


# Define precedences for the operators.
OP_PRECEDENCES = {
    TokenType.EQ: Precedences.EQUALS,
    TokenType.NOT_EQ: Precedences.EQUALS,
    TokenType.LT: Precedences.LESSGREATER,
    TokenType.GT: Precedences.LESSGREATER,
    TokenType.PLUS: Precedences.SUM,
    TokenType.MINUS: Precedences.SUM,
    TokenType.SLASH: Precedences.PRODUCT,
    TokenType.ASTERISK: Precedences.PRODUCT,
    TokenType.LPAREN: Precedences.CALL,
    TokenType.LBRACKET: Precedences.INDEX,
    TokenType.MODULO: Precedences.PRODUCT,
}


class Parser:
    def __init__(self, lexer: Lexer) -> None:

        # State variables
        self.lexer = lexer
        self.errors: typing.List[str] = []
        self.prefix_parse_fns: typing.Dict[
            TokenType, typing.Callable[[], typing.Optional[Expression]]
        ] = {}
        self.infix_parse_fns: typing.Dict[
            TokenType, typing.Callable[[Expression], typing.Optional[Expression]]
        ] = {}

        # Initial state configuration
        self.current_token = self.lexer.next_token()
        self.peek_token = self.lexer.next_token()

        # Register Prefixes
        self.register_prefix(TokenType.IDENT, self.parse_identifier)
        self.register_prefix(TokenType.INT, self.parse_numeric_literal)
        self.register_prefix(TokenType.BANG, self.parse_prefix_expression)
        self.register_prefix(TokenType.MINUS, self.parse_prefix_expression)
        self.register_prefix(TokenType.TRUE, self.parse_boolean_literal)
        self.register_prefix(TokenType.FALSE, self.parse_boolean_literal)
        self.register_prefix(TokenType.LPAREN, self.parse_grouped_expression)
        self.register_prefix(TokenType.IF, self.parse_if_expression)
        self.register_prefix(TokenType.FUNCTION, self.parse_function_literal)
        self.register_prefix(TokenType.STRING, self.parse_string_literal)
        self.register_prefix(TokenType.LBRACKET, self.parse_array_literal)
        self.register_prefix(TokenType.LBRACE, self.parse_dict_literal)

        # Register Infixes
        self.register_infix(TokenType.PLUS, self.parse_infix_expression)
        self.register_infix(TokenType.MINUS, self.parse_infix_expression)
        self.register_infix(TokenType.SLASH, self.parse_infix_expression)
        self.register_infix(TokenType.ASTERISK, self.parse_infix_expression)
        self.register_infix(TokenType.EQ, self.parse_infix_expression)
        self.register_infix(TokenType.NOT_EQ, self.parse_infix_expression)
        self.register_infix(TokenType.LT, self.parse_infix_expression)
        self.register_infix(TokenType.GT, self.parse_infix_expression)
        self.register_infix(TokenType.LPAREN, self.parse_call_expression)
        self.register_infix(TokenType.LBRACKET, self.parse_index_exp)
        self.register_infix(TokenType.MODULO, self.parse_infix_expression)

    def next_token(self) -> None:
        """Update the current and peek tokens, with next tokens in the stream."""
        self.current_token = self.peek_token
        self.peek_token = self.lexer.next_token()

    def parse_program(self) -> ast.Program:
        """Parse the given input into AST."""
        program = ast.Program()

        while self.current_token.tp != TokenType.EOF:
            stmt = self.parse_statement()
            if stmt is not None:
                program.statements.append(stmt)
            self.next_token()

        return program

    def parse_statement(self) -> typing.Optional[ast.Statement]:
        if self.current_token.tp == TokenType.LET:
            return self.parse_let_statement()
        elif self.current_token.tp == TokenType.RETURN:
            return self.parse_return_statement()
        elif self.current_token.tp == TokenType.CONST:
            return self.parse_const_statement()
        elif self.current_token.tp == TokenType.WHILE:
            return self.parse_while_statement()
        elif (
            self.current_token.tp == TokenType.IDENT
            and self.peek_token.tp == TokenType.ASSIGN
        ):
            return self.parse_reassign_statement()
        else:
            return self.parse_expression_statement()

    def parse_let_statement(self) -> typing.Optional[ast.LetStatement]:
        stmt = ast.LetStatement(self.current_token)

        if not self.expect_peek(TokenType.IDENT):
            return None

        stmt.name = ast.Identifier(self.current_token, self.current_token.literal)

        if not self.expect_peek(TokenType.ASSIGN):
            return None

        self.next_token()

        val = self.parse_expression(Precedences.LOWEST)
        if val is None:
            return None

        stmt.value = val

        if self.peek_token.tp == TokenType.SEMICOLON:
            self.next_token()

        return stmt

    def parse_const_statement(self) -> typing.Optional[ast.ConstStatement]:
        stmt = ast.ConstStatement(self.current_token)

        if not self.expect_peek(TokenType.IDENT):
            return None

        stmt.name = ast.Identifier(self.current_token, self.current_token.literal)

        if not self.expect_peek(TokenType.ASSIGN):
            return None

        self.next_token()

        val = self.parse_expression(Precedences.LOWEST)
        if val is None:
            return None

        stmt.value = val

        if self.peek_token.tp == TokenType.SEMICOLON:
            self.next_token()

        return stmt

    def parse_reassign_statement(self) -> typing.Optional[ast.ReassignStatement]:
        stmt = ast.ReassignStatement(Token(TokenType.ASSIGN, "="))
        stmt.name = ast.Identifier(self.current_token, self.current_token.literal)

        if not self.expect_peek(TokenType.ASSIGN):
            return None

        self.next_token()
        val = self.parse_expression(Precedences.LOWEST)
        if val is None:
            return None

        stmt.value = val

        if self.peek_token.tp == TokenType.SEMICOLON:
            self.next_token()

        return stmt

    def parse_while_statement(self) -> typing.Optional[ast.WhileStatement]:
        exp = ast.WhileStatement(self.current_token)

        if not self.expect_peek(TokenType.LPAREN):
            return None

        self.next_token()

        cond = self.parse_expression(Precedences.LOWEST)
        if cond is None:
            return None

        exp.condition = cond

        if not self.expect_peek(TokenType.RPAREN):
            return None

        if not self.expect_peek(TokenType.LBRACE):
            return None

        exp.consequence = self.parse_block_statement()

        return exp

    def parse_return_statement(self) -> typing.Optional[ast.ReturnStatement]:
        stmt = ast.ReturnStatement(self.current_token)
        self.next_token()
        ret = self.parse_expression(Precedences.LOWEST)
        if ret is None:
            return None
        stmt.return_value = ret

        if self.peek_token.tp == TokenType.SEMICOLON:
            self.next_token()

        return stmt

    def parse_expression_statement(self) -> typing.Optional[ast.ExpressionStatement]:
        stmt = ast.ExpressionStatement(self.current_token)

        exp = self.parse_expression(Precedences.LOWEST)
        if exp is None:
            return None

        stmt.expression = exp
        if self.peek_token.tp == TokenType.SEMICOLON:
            self.next_token()

        return stmt

    def parse_expression(
        self, precedence: Precedences
    ) -> typing.Optional[ast.Expression]:

        prefix = self.prefix_parse_fns.get(self.current_token.tp, None)
        if prefix is None:
            self.prefix_parse_error(self.current_token.tp)
            return None

        left_exp = prefix()

        while (
            self.peek_token.tp != TokenType.SEMICOLON
            and precedence.value < self.peek_precedence().value
        ):
            infix = self.infix_parse_fns.get(self.peek_token.tp, None)
            if infix is None:
                return left_exp

            self.next_token()

            if left_exp is None:
                return None

            left_exp = infix(left_exp)

        return left_exp

    def parse_identifier(self) -> ast.Identifier:
        return ast.Identifier(self.current_token, self.current_token.literal)

    def parse_numeric_literal(
        self,
    ) -> typing.Union[ast.IntegerLiteral, ast.FloatLiteral, None]:
        try:
            value = int(self.current_token.literal)
        except ValueError:
            msg = f"Could not parse {self.current_token.literal} as integer."
            self.errors.append(msg)
            return None

        lit: typing.Union[ast.IntegerLiteral, ast.FloatLiteral]

        if not self.peek_token.tp == TokenType.DOT:
            lit = ast.IntegerLiteral(self.current_token)
            lit.value = value
        else:
            lit = ast.FloatLiteral(self.peek_token)
            self.next_token()
            self.next_token()
            rep = f"{value}.{self.current_token.literal}"

            try:
                val = float(rep)
            except ValueError:
                msg = f"Could not parse {self.current_token.literal} as float."
                self.errors.append(msg)
                return None

            lit.value = val

        return lit

    def parse_boolean_literal(self) -> ast.BooleanLiteral:
        return ast.BooleanLiteral(
            self.current_token, TokenType.TRUE == self.current_token.tp
        )

    def parse_prefix_expression(self) -> typing.Optional[ast.PrefixExpression]:
        exp = ast.PrefixExpression(self.current_token, self.current_token.literal)
        self.next_token()

        right = self.parse_expression(Precedences.PREFIX)
        if right is None:
            return None

        exp.right = right

        return exp

    def parse_infix_expression(
        self, left: ast.Expression
    ) -> typing.Optional[ast.InfixExpression]:
        exp = ast.InfixExpression(self.current_token, self.current_token.literal, left)

        precedence = self.current_precedence()
        self.next_token()

        right = self.parse_expression(precedence)
        if right is None:
            return None

        exp.right = right
        return exp

    def parse_grouped_expression(self) -> typing.Optional[ast.Expression]:
        self.next_token()
        exp = self.parse_expression(Precedences.LOWEST)

        if not self.expect_peek(TokenType.RPAREN):
            return None

        return exp

    def parse_if_expression(self) -> typing.Optional[ast.IfExpression]:
        exp = ast.IfExpression(self.current_token)

        if not self.expect_peek(TokenType.LPAREN):
            return None

        self.next_token()

        cond = self.parse_expression(Precedences.LOWEST)
        if cond is None:
            return None

        exp.condition = cond

        if not self.expect_peek(TokenType.RPAREN):
            return None

        if not self.expect_peek(TokenType.LBRACE):
            return None

        exp.consequence = self.parse_block_statement()

        if self.peek_token.tp == TokenType.ELSE:
            self.next_token()

            if not self.expect_peek(TokenType.LBRACE):
                return None

            exp.alternative = self.parse_block_statement()

        return exp

    def parse_block_statement(self) -> ast.BlockStatement:
        block = ast.BlockStatement(self.current_token)
        self.next_token()

        while (
            not self.current_token.tp == TokenType.RBRACE
            and not self.current_token.tp == TokenType.EOF
        ):
            stmt = self.parse_statement()
            if stmt is not None:
                block.statements.append(stmt)

            self.next_token()

        return block

    def parse_function_literal(self) -> typing.Optional[ast.FunctionLiteral]:
        lit = ast.FunctionLiteral(self.current_token)

        if not self.expect_peek(TokenType.LPAREN):
            return None

        params = self.parse_function_parameters()
        if params is None:
            return params

        lit.parameters = params

        if not self.expect_peek(TokenType.LBRACE):
            return None

        lit.body = self.parse_block_statement()
        return lit

    def parse_function_parameters(self) -> typing.Optional[typing.List[ast.Identifier]]:
        idents: typing.List[ast.Identifier] = []

        if self.peek_token.tp == TokenType.RPAREN:
            self.next_token()
            return idents

        self.next_token()
        ident = ast.Identifier(self.current_token, self.current_token.literal)
        idents.append(ident)

        while self.peek_token.tp == TokenType.COMMA:
            self.next_token()
            self.next_token()

            ident = ast.Identifier(self.current_token, self.current_token.literal)
            idents.append(ident)

        if not self.expect_peek(TokenType.RPAREN):
            return None

        return idents

    def parse_call_expression(
        self, function: ast.Expression
    ) -> typing.Optional[ast.CallExpression]:
        exp = ast.CallExpression(self.current_token, function)
        args = self.parse_exp_list(TokenType.RPAREN)
        if args is None:
            return args

        exp.arguments = args
        return exp

    def parse_array_literal(self) -> typing.Optional[ast.ArrayLiteral]:
        array = ast.ArrayLiteral(self.current_token)
        elems = self.parse_exp_list(TokenType.RBRACKET)
        if elems is None:
            return elems

        array.elements = elems
        return array

    def parse_exp_list(
        self, end: TokenType
    ) -> typing.Optional[typing.List[Expression]]:
        args: typing.List[Expression] = []

        if self.peek_token.tp == end:
            self.next_token()
            return args

        self.next_token()
        exp = self.parse_expression(Precedences.LOWEST)
        if exp is None:
            return None

        args.append(exp)

        while self.peek_token.tp == TokenType.COMMA:
            self.next_token()
            self.next_token()

            exp = self.parse_expression(Precedences.LOWEST)
            if exp is None:
                return None

            args.append(exp)

        if not self.expect_peek(end):
            return None

        return args

    def parse_string_literal(self) -> ast.StringLiteral:
        return ast.StringLiteral(self.current_token, self.current_token.literal)

    def parse_index_exp(
        self, left: ast.Expression
    ) -> typing.Optional[ast.IndexExpression]:
        exp = ast.IndexExpression(self.current_token, left)
        self.next_token()

        index = self.parse_expression(Precedences.LOWEST)
        if index is None:
            return None

        exp.index = index

        if not self.expect_peek(TokenType.RBRACKET):
            return None

        return exp

    def parse_dict_literal(self) -> typing.Optional[ast.DictionaryLiteral]:
        dictionary = ast.DictionaryLiteral(self.current_token)

        while self.peek_token.tp != TokenType.RBRACE:
            self.next_token()
            key = self.parse_expression(Precedences.LOWEST)

            if not self.expect_peek(TokenType.COLON):
                return None

            self.next_token()
            value = self.parse_expression(Precedences.LOWEST)

            if key is None or value is None:
                return None

            dictionary.pairs[key] = value

            if self.peek_token.tp != TokenType.RBRACE and not self.expect_peek(
                TokenType.COMMA
            ):
                return None

        if not self.expect_peek(TokenType.RBRACE):
            return None

        return dictionary

    def expect_peek(self, tp: TokenType) -> bool:
        if self.peek_token.tp == tp:
            self.next_token()
            return True

        self.peek_error(tp)
        return False

    def peek_error(self, tp: TokenType) -> None:
        msg = f"Expected next token to be {tp}, instead got {self.peek_token.tp}."
        self.errors.append(msg)

    def prefix_parse_error(self, tp: TokenType) -> None:
        msg = f"Cannot parse {tp} prefix token."
        self.errors.append(msg)

    def register_prefix(
        self, tp: TokenType, fn: typing.Callable[[], typing.Optional[Expression]]
    ) -> None:
        self.prefix_parse_fns[tp] = fn

    def register_infix(
        self,
        tp: TokenType,
        fn: typing.Callable[[Expression], typing.Optional[Expression]],
    ) -> None:
        self.infix_parse_fns[tp] = fn

    def peek_precedence(self) -> Precedences:
        return OP_PRECEDENCES.get(self.peek_token.tp, Precedences.LOWEST)

    def current_precedence(self) -> Precedences:
        return OP_PRECEDENCES.get(self.current_token.tp, Precedences.LOWEST)
