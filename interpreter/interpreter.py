from _parser.expression import Literal, Grouping, Unary, Binary, Expression
from tokenizer import TokenType


class Interpreter:

    def interpret(self, expression: Expression):
        print(expression.eval(self))

    @staticmethod
    def eval_literal(literal: Literal):
        return literal.value

    def eval_grouping(self, grouping: Grouping):
        return grouping.eval(self)

    def eval_unary(self, unary: Unary):
        right = unary.right.eval(self)
        if unary.operator.type == TokenType.MINUS:
            return -right
        elif unary.operator.type == TokenType.EXCLAMATION:
            return not right
        return None

    def eval_binary(self, binary: Binary):
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
