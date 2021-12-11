from dataclasses import dataclass
from abc import abstractmethod
from tokenizer.token_ import Token
from tokenizer.token_type import TokenType


class Expression:

    @abstractmethod
    def eval(self):
        pass


@dataclass
class Binary(Expression):
    left: Expression
    operator: Token
    right: Expression

    def eval(self):
        left = self.left.eval()
        right = self.right.eval()
        if self.operator.type == TokenType.MINUS:
            return left - right
        if self.operator.type == TokenType.PLUS:
            return left + right
        if self.operator.type == TokenType.DIVIDE:
            return left / right
        if self.operator.type == TokenType.MULTIPLY:
            return left * right
        if self.operator.type == TokenType.EQUAL_EQUAL:
            return left == right
        if self.operator.type == TokenType.EQUAL_DIFFERENT:
            return left != right
        if self.operator.type == TokenType.LOWER:
            return left < right
        if self.operator.type == TokenType.LOWER_EQUAL:
            return left <= right
        if self.operator.type == TokenType.GREATER:
            return left > right
        if self.operator.type == TokenType.GREATER_EQUAL:
            return left >= right

    def __str__(self):
        return f"({self.left} {self.operator.text} {self.right})"


@dataclass
class Unary(Expression):
    operator: Token
    right: Expression

    def eval(self):
        if self.operator.type == TokenType.MINUS:
            return -self.right.eval()
        if self.operator.type == TokenType.EXCLAMATION:
            return not self.right.eval()

    def __str__(self):
        return f"({self.operator.text} {self.right})"


@dataclass
class Grouping(Expression):
    expression: Expression

    def eval(self):
        return self.expression.eval()

    def __str__(self):
        return f"({self.expression})"


@dataclass
class Literal(Expression):
    value: object

    def eval(self):
        return float(self.value)

    def __str__(self):
        return f"{self.value}"
