import string
from dataclasses import dataclass
from abc import abstractmethod
from typing import Optional

from tokenizer.token_ import Token
from tokenizer.token_type import TokenType


class Scope:
    def __init__(self, father: Optional['Scope']):
        self.variables = {}
        self.father = father

    def declaration(self, name):
        if not self.exists_scoped_variable(name):
            self.variables[name] = None
            return True
        return False

    def obtain_value(self, name):
        if name in self.variables:
            return self.variables[name], True
        return self.obtain_value(self.father) if self.father else None, False

    def exists_scoped_variable(self, name):
        return name in self.variables

    def exists_variable(self, name):
        return self.obtain_value(name)[1]


class Expression:

    @abstractmethod
    def eval(self):
        pass


@dataclass
class Assignment(Expression):
    var_name: string
    value: Expression
    variables: dict

    def eval(self):
        """
        Evaluates the node of the syntax tree by evaluating right expression and assign its value
        to the corresponding variable
        """
        self.variables[self.var_name] = self.value.eval()
        return self.variables[self.var_name]

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

    def eval(self):
        """
        Evaluates the node of the syntax tree by evaluating left and right expressions and then applying the operator
        """
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
    """
    Unary expressions representation
    Every unary representation has an operator and an operand
    """
    operator: Token
    right: Expression

    def eval(self):
        """
        Evaluates the node by evaluating the expression on the right and applying the unary operator
        """
        if self.operator.type == TokenType.MINUS:
            return -self.right.eval()
        if self.operator.type == TokenType.EXCLAMATION:
            return not self.right.eval()

    def __str__(self):
        return f"({self.operator.text} {self.right})"


@dataclass
class Grouping(Expression):
    """
    Grouping expressions representation
    Stores the expression inside the grouping tokens
    """
    expression: Expression

    def eval(self):
        """
        Evaluates the grouping node by simply evaluating the expression it contains
        """
        return self.expression.eval()

    def __str__(self):
        return f"({self.expression})"


@dataclass
class Literal(Expression):
    """
    Literal representation
    Stores the value for a literal
    """
    value: object

    def eval(self):
        """
        Evaluates a literal by returning it's corresponding value
        """
        return self.value

    def __str__(self):
        return f"{self.value}"
