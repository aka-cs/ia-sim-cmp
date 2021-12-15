from _parser.expression import Literal, Grouping, Unary, Binary, Expression
from tokenizer import TokenType
from .scope import Object
from .visitor import visitor


class Interpreter:

    def interpret(self, expressions: [Expression]):
        for expression in expressions:
            print(expression.eval(self))

    @visitor(Literal)
    def eval(self, literal: Literal):
        if type(literal.value) == Object:
            return literal.value.value
        return literal.value

    @visitor(Grouping)
    def eval(self, grouping: Grouping):
        return grouping.eval(self)

    @visitor(Unary)
    def eval(self, unary: Unary):
        right = unary.right.eval(self)
        if unary.operator.type == TokenType.MINUS:
            return -right
        elif unary.operator.type == TokenType.EXCLAMATION:
            return not right
        return None

    @visitor(Binary)
    def eval(self, binary: Binary):
        left = binary.left.eval(self)
        right = binary.right.eval(self)
        if binary.operator.type == TokenType.MINUS:
            return left - right
        if binary.operator.type == TokenType.PLUS:
            return left + right
        if binary.operator.type == TokenType.DIVIDE:
            return left / right
        if binary.operator.type == TokenType.MULTIPLY:
            return left * right
        if binary.operator.type == TokenType.EQUAL_EQUAL:
            return left == right
        if binary.operator.type == TokenType.EQUAL_DIFFERENT:
            return left != right
        if binary.operator.type == TokenType.LOWER:
            return left < right
        if binary.operator.type == TokenType.LOWER_EQUAL:
            return left <= right
        if binary.operator.type == TokenType.GREATER:
            return left > right
        if binary.operator.type == TokenType.GREATER_EQUAL:
            return left >= right
