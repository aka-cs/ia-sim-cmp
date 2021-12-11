"""
expression -> equality
equality -> comparison ( ("!=" | "==") comparison)*
comparison -> term ( (">" | ">=" | "<" | "<=") term)*
term ->  factor ( ( "-" | "+" ) factor)*
factor -> unary ( ( "/" | "*" ) unary)*
unary -> ( "!" | "-" ) unary | primary
primary -> NUMBER | STRING | "true" | "false" | "null" | "(" expression ")"
"""

from tokenizer.token_ import Token, TokenType
from .expression import Expression, Binary, Unary, Literal, Grouping


class Parser:
    def __init__(self, tokens: [Token]):
        self.current = 0
        self.tokens = tokens

    def parse(self):
        return self.expression()

    def expression(self) -> Expression:
        return self.equality()

    def binary(self, expression, *types: [TokenType]) -> Binary:
        expr = expression()
        while self.match(*types):
            operator = self.previous()
            right = expression()
            expr = Binary(expr, operator, right)

        return expr

    def equality(self) -> Expression:
        return self.binary(self.comparison, TokenType.EQUAL_EQUAL, TokenType.EQUAL_DIFFERENT)

    def comparison(self) -> Expression:
        return self.binary(self.term, TokenType.GREATER, TokenType.GREATER_EQUAL, TokenType.LOWER_EQUAL, TokenType.LOWER)

    def term(self) -> Expression:
        return self.binary(self.factor, TokenType.GREATER, TokenType.PLUS, TokenType.MINUS)

    def factor(self) -> Expression:
        return self.binary(self.unary, TokenType.MULTIPLY, TokenType.DIVIDE)

    def unary(self) -> Expression:
        if self.match(TokenType.EXCLAMATION, TokenType.MINUS):
            operator = self.previous()
            right = self.unary()
            return Unary(operator, right)
        return self.primary()

    def primary(self) -> Expression:
        if self.match(TokenType.FALSE):
            return Literal(False)
        if self.match(TokenType.TRUE):
            return Literal(True)
        if self.match(TokenType.NULL):
            return Literal(None)
        if self.match(TokenType.NUMBER, TokenType.STRING):
            return Literal(self.previous().text)
        if self.match(TokenType.LEFT_PARENTHESIS):
            expr = self.expression()
            if not self.check(TokenType.RIGHT_PARENTHESIS):
                raise Exception()
            self.advance()
            return Grouping(expr)
        raise Exception()

    def match(self, *types: [TokenType]):
        for token_type in types:
            if self.check(token_type):
                self.advance()
                return True
        return False

    def previous(self) -> Token:
        return self.tokens[self.current - 1]

    def advance(self) -> Token:
        self.current += 1
        return self.previous()

    def check(self, token_type: TokenType) -> bool:
        return not self.is_at_end() and self.peek().type == token_type

    def is_at_end(self) -> bool:
        return self.peek().type == TokenType.EOF

    def peek(self) -> Token:
        return self.tokens[self.current]
