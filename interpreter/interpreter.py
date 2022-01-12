from _parser.nodes import *
from tokenizer.token_type import TokenType
from tools import visitor
from .functions import UserDefinedFunction, ReturnCall
from .scope import Scope
from .builtin import builtin_functions
from ._types import Float, Int, String, Bool, Null, List


class Interpreter:

    def __init__(self):
        self.globals: Scope = Scope()
        self.scope: Scope = self.globals
        for fun in builtin_functions:
            self.globals.declare(fun.name, fun)

    def interpret(self, expressions: [Node]):
        for expression in expressions:
            expression.exec(self)

    @visitor(Literal)
    def exec(self, literal: Literal):
        if isinstance(literal.value, float):
            return Float(literal.value)
        if isinstance(literal.value, int):
            return Int(literal.value)
        if isinstance(literal.value, str):
            return String(literal.value)
        if isinstance(literal.value, bool):
            return Bool(literal.value)
        if literal.value is None:
            return Null()

    @visitor(ArrayNode)
    def exec(self, expression: ArrayNode):
        result = []
        for elem in expression.expressions:
            result.append(elem.exec(self))
        return List(result)

    @visitor(Index)
    def exec(self, expression: Index):
        left = expression.expression.exec(self)
        index = expression.index.exec(self)
        return left[index]

    @visitor(Grouping)
    def exec(self, grouping: Grouping):
        return grouping.expression.exec(self)

    @visitor(Unary)
    def exec(self, unary: Unary):
        right = unary.right.exec(self)
        if unary.operator.type == TokenType.MINUS:
            return -right
        elif unary.operator.type == TokenType.EXCLAMATION:
            return not right
        return None

    @visitor(Binary)
    def exec(self, binary: Binary):
        left = binary.left.exec(self)
        right = binary.right.exec(self)
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
        if binary.operator.type == TokenType.LESS:
            return left < right
        if binary.operator.type == TokenType.LESS_EQUAL:
            return left <= right
        if binary.operator.type == TokenType.GREATER:
            return left > right
        if binary.operator.type == TokenType.GREATER_EQUAL:
            return left >= right
        if binary.operator.type == TokenType.AND:
            return left and right
        if binary.operator.type == TokenType.OR:
            return left or right

    @visitor(Variable)
    def exec(self, variable: Variable):
        return self.scope.get(variable.name.text)

    @visitor(VarDeclaration)
    def exec(self, declaration: VarDeclaration):
        self.scope.declare(declaration.name.text, declaration.expression.exec(self))

    @visitor(Assignment)
    def exec(self, assignment: Assignment):
        self.scope.assign(assignment.left.text, assignment.value.exec(self))

    @visitor(Statement)
    def exec(self, expression: Statement):
        return expression.code.exec(self)

    @visitor(Call)
    def exec(self, expression: Call):
        called = expression.called.exec(self)
        arguments = []
        for arg in expression.arguments:
            arguments.append(arg.exec(self))
        return called(self, arguments)

    @visitor(FunctionNode)
    def exec(self, expression: FunctionNode):
        self.scope.declare(expression.name.text, UserDefinedFunction(expression))

    @visitor(Return)
    def exec(self, expression: Return):
        value = None
        if expression.expression:
            value = expression.expression.exec(self)
        raise ReturnCall(value)

    @visitor(If)
    def exec(self, expression: If):
        if expression.condition.exec(self):
            self.execute_block(expression.code, Scope(self.scope))
        else:
            self.execute_block(expression.else_code, Scope(self.scope))

    @visitor(While)
    def exec(self, expression: While):
        while expression.condition.exec(self):
            self.execute_block(expression.code, Scope(self.scope))

    def execute_block(self, statements, scope: Scope):
        previous = self.scope
        try:
            self.scope = scope
            for statement in statements:
                self.exec(statement)
        finally:
            self.scope = previous
