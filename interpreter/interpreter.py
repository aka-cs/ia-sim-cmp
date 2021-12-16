from _parser.expression import Literal, Grouping, Unary, Binary, Expression, Variable, Assignment
from _parser.statement import ExpressionStatement, VarDeclaration
from tokenizer import TokenType
from .scope import Scope
from .visitor import visitor


class Interpreter:

    def __init__(self):
        self.scope = Scope()

    def interpret(self, expressions: [Expression]):
        for expression in expressions:
            print(expression.eval(self))

    @visitor(Literal)
    def eval(self, literal: Literal):
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

    @visitor(Variable)
    def eval(self, variable: Variable):
        return self.scope.get(variable.name.text)

    @visitor(VarDeclaration)
    def eval(self, declaration: VarDeclaration):
        self.scope.declare(declaration.name.text, declaration.expression.eval(self))

    @visitor(Assignment)
    def eval(self, assignment: Assignment):
        self.scope.assign(assignment.var_name.text, assignment.value.eval(self))

    @visitor(ExpressionStatement)
    def eval(self, expression: ExpressionStatement):
        return expression.expression.eval(self)

    def execute_block(self, statements, scope: Scope):
        previous = self.scope
        try:
            self.scope = scope
            for statement in statements:
                self.eval(statement)
        finally:
            self.scope = previous
