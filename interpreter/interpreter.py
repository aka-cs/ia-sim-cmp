from _parser.nodes import *
from tokenizer.token_type import TokenType
from tools import visitor
from .functions import UserDefinedFunction, ReturnCall
from .scope import Scope
from .builtin import builtin_functions
from ._types import Float, Int, String, Bool, Null, Array


class Interpreter:

    def __init__(self):
        self.globals: Scope = Scope()
        self.scope: Scope = self.globals
        for fun in builtin_functions:
            self.globals.declare(fun.name, fun)

    def interpret(self, expressions: [Node]):
        for expression in expressions:
            expression.eval(self)

    @visitor(Literal)
    def eval(self, literal: Literal):
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
    def eval(self, expression: ArrayNode):
        result = []
        for elem in expression.expressions:
            result.append(elem.eval(self))
        return Array(result)

    @visitor(Index)
    def eval(self, expression: Index):
        left = expression.expression.eval(self)
        index = expression.index.eval(self)
        return left[index]

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

    @visitor(Call)
    def eval(self, expression: Call):
        called = expression.called.eval(self)
        arguments = []
        for arg in expression.arguments:
            arguments.append(arg.eval(self))
        return called(self, arguments)

    @visitor(FunctionNode)
    def eval(self, expression: FunctionNode):
        self.scope.declare(expression.name.text, UserDefinedFunction(expression))

    @visitor(Return)
    def eval(self, expression: Return):
        value = None
        if expression.expression:
            value = expression.expression.eval(self)
        raise ReturnCall(value)

    @visitor(If)
    def eval(self, expression: If):
        if expression.condition.eval(self):
            self.execute_block(expression.code, Scope(self.scope))
        else:
            self.execute_block(expression.else_code, Scope(self.scope))

    @visitor(While)
    def eval(self, expression: While):
        while expression.condition.eval(self):
            self.execute_block(expression.code, Scope(self.scope))

    def execute_block(self, statements, scope: Scope):
        previous = self.scope
        try:
            self.scope = scope
            for statement in statements:
                self.eval(statement)
        finally:
            self.scope = previous
