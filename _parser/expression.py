from dataclasses import dataclass
from tokenizer.token_ import Token


class Expression:
    def eval(self, interpreter):
        return interpreter.eval(self)


@dataclass
class Assignment(Expression):
    var_name: Token
    value: Expression

    def __str__(self):
        return f"({self.var_name} = {self.value})"


@dataclass
class Binary(Expression):
    """
    Binary expression representation
    Every binary operation has a left expression, an operand and a right expression
    """
    left: Expression
    operator: Token
    right: Expression

    def __str__(self):
        return f"({self.left} {self.operator.text} {self.right})"


@dataclass
class Unary(Expression):
    """
    Unary expressions representation
    Every unary representation has an operator and an operand
    """
    operator: Token
    right: Expression

    def __str__(self):
        return f"({self.operator.text} {self.right})"


@dataclass
class Grouping(Expression):
    """
    Grouping expressions representation
    Stores the expression inside the grouping tokens
    """
    expression: Expression

    def __str__(self):
        return f"({self.expression})"


@dataclass
class Call(Expression):
    called: Expression
    arguments: [Expression]


@dataclass
class Literal(Expression):
    """
    Literal representation
    Stores the value for a literal
    """
    value: object

    def __str__(self):
        return f"{self.value}"


@dataclass
class Variable(Expression):
    name: Token

    def __str__(self):
        return f"{self.name}"
