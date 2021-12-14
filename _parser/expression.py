from dataclasses import dataclass
from abc import abstractmethod
from tokenizer.token_ import Token


class Expression:

    @abstractmethod
    def eval(self, interpreter):
        pass


@dataclass
class Assignment(Expression):
    var_name: str
    value: Expression
    variables: dict

    def eval(self, interpreter):
        """
        Evaluates the node of the syntax tree by evaluating right expression and assign its value
        to the corresponding variable
        """
        self.variables[self.var_name] = self.value.eval(interpreter)
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

    def eval(self, interpreter):
        """
        Evaluates the node of the syntax tree by evaluating left and right expressions and then applying the operator
        """
        return interpreter.eval_binary(self)

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

    def eval(self, interpreter):
        """
        Evaluates the node by evaluating the expression on the right and applying the unary operator
        """
        return interpreter.eval_unary(self)

    def __str__(self):
        return f"({self.operator.text} {self.right})"


@dataclass
class Grouping(Expression):
    """
    Grouping expressions representation
    Stores the expression inside the grouping tokens
    """
    expression: Expression

    def eval(self, interpreter):
        """
        Evaluates the grouping node by simply evaluating the expression it contains
        """
        return interpreter.eval_grouping(self)

    def __str__(self):
        return f"({self.expression})"


@dataclass
class Literal(Expression):
    """
    Literal representation
    Stores the value for a literal
    """
    value: object

    def eval(self, interpreter):
        """
        Evaluates a literal by returning it's corresponding value
        """
        return interpreter.eval_literal(self)

    def __str__(self):
        return f"{self.value}"
