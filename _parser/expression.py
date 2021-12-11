from dataclasses import dataclass
from abc import abstractmethod
from tokenizer.token_ import Token


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
        pass

    def __str__(self):
        return f"({self.left} {self.operator.text} {self.right})"


@dataclass
class Unary(Expression):
    operator: Token
    right: Expression

    def eval(self):
        pass

    def __str__(self):
        return f"({self.operator.text} {self.right})"


@dataclass
class Grouping(Expression):
    expression: Expression

    def eval(self):
        pass

    def __str__(self):
        return f"({self.expression})"


@dataclass
class Literal(Expression):
    value: object

    def eval(self):
        pass

    def __str__(self):
        return f"{self.value}"
