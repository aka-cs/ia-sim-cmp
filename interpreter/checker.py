from tools import Singleton, visitor
from .scope import Scope
from _parser.nodes import *
from tokenizer.token_type import TokenType
from .types import Type
from .functions import UserDefinedFunction
from .builtin import builtin_functions, builtin_types, objects, numbers, boolean, strings, null


class TypeChecker(metaclass=Singleton):

    def __init__(self):
        self.globals = Scope()
        self.scope = self.globals
        self.types = builtin_types[:]
        self.current_function = None
        for fun in builtin_functions:
            self.scope.declare(fun.name, fun)

    def start(self, expressions: [Node]):
        for expression in expressions:
            if isinstance(expression, Function):
                for param in expression.params:
                    if param[1].text not in self.types:
                        raise TypeError(f"Type {param[1].text} not defined in current scope")

                self.scope.declare(expression.name.text, UserDefinedFunction(expression))
        for expression in expressions:
            expression.check(self)

    @visitor(Literal)
    def check(self, expression: Literal):
        if isinstance(expression.value, float):
            return numbers
        if isinstance(expression.value, str):
            return strings
        if isinstance(expression.value, bool):
            return boolean
        return None

    @visitor(Grouping)
    def check(self, expression: Grouping):
        return expression.expression.check(self)

    @visitor(Unary)
    def check(self, expression: Unary):
        right = expression.right.check(self)
        if expression.operator.type == TokenType.MINUS:
            if right != "number":
                raise TypeError(f"{right} type doesn't support - unary operator")
            return right
        elif expression.operator.type == TokenType.EXCLAMATION:
            return boolean
        return None

    @visitor(Binary)
    def check(self, expression: Binary):
        left = expression.left.check(self)
        right = expression.right.check(self)
        if left != right:
            raise TypeError(f"{left} and {right} types don't support {expression.operator.text} operator")
        if left not in builtin_types:
            raise TypeError(f"{left} type doesn't support {expression.operator.text} operator")
        if expression.operator.type == TokenType.EQUAL_EQUAL:
            return boolean
        if expression.operator.type == TokenType.EQUAL_DIFFERENT:
            return boolean
        if left == "bool" and expression.operator.type in [TokenType.AND, TokenType.OR]:
            return boolean
        if left != "string" and left != "number":
            raise TypeError(f"{left} type doesn't support {expression.operator.text} operator")
        if expression.operator.type == TokenType.PLUS:
            return left
        if left != "number":
            raise TypeError(f"{left} type doesn't support {expression.operator.text} operator")
        if expression.operator.type == TokenType.MINUS:
            return numbers
        if expression.operator.type == TokenType.DIVIDE:
            return numbers
        if expression.operator.type == TokenType.MULTIPLY:
            return numbers
        if expression.operator.type == TokenType.LESS:
            return boolean
        if expression.operator.type == TokenType.LESS_EQUAL:
            return boolean
        if expression.operator.type == TokenType.GREATER:
            return boolean
        if expression.operator.type == TokenType.GREATER_EQUAL:
            return boolean
        return None

    @visitor(Variable)
    def check(self, expression: Variable):
        return self.scope.get(expression.name.text)

    @visitor(VarDeclaration)
    def check(self, expression: VarDeclaration):
        expression_type = expression.expression.check(self)
        if expression.name.text in self.types:
            raise Exception("Variable name can't be the same as a type's name")
        if expression.type:
            variable_type = self.get_type(expression.type.text)
            if not variable_type:
                raise TypeError(f"Type {expression.type.text} is not defined in current scope")
            if not variable_type >= expression_type:
                raise TypeError(f"Variable {expression.name.text} of type {expression.type.text} can't be assigned {expression_type}")
            expression_type = variable_type
        if expression_type == "null":
            raise TypeError(f"Can't assign null type value to a variable")
        self.scope.declare(expression.name.text, expression_type)

    @visitor(Assignment)
    def check(self, expression: Assignment):
        expression_type = expression.value.check(self)
        variable_type = self.scope.get(expression.var_name.text)
        if not variable_type >= expression_type:
            raise TypeError(f"Variable {expression.var_name.text} of type {variable_type} can't be assigned {expression_type}")
        self.scope.assign(expression.var_name.text, expression_type)

    @visitor(ExpressionStatement)
    def check(self, expression: ExpressionStatement):
        return expression.expression.check(self)

    @visitor(Call)
    def check(self, expression: Call):
        called = expression.called.check(self)
        if len(expression.arguments) != len(called.param_type):
            raise Exception("Invalid number of arguments")
        for arg, param in zip(expression.arguments, called.param_type):
            arg_type = arg.check(self)
            if not self.get_type(param) >= arg_type:
                raise TypeError(f"Function with argument type {param} can't receive {arg_type}")
        return self.get_type(called.return_type)

    @visitor(Function)
    def check(self, expression: Function):
        scope = Scope(self.scope)
        for param in expression.params:
            scope.declare(param[0].text, self.get_type(param[1].text))
        self.current_function = expression
        self.check_block(expression.body, scope)
        self.current_function = None

    @visitor(Return)
    def check(self, expression: Return):
        if not self.current_function:
            raise Exception("return statement should be inside a function")
        if expression.expression:
            return_type = expression.expression.check(self)
        else:
            return_type = null
        expected = self.get_type(self.current_function.return_type.text)
        if not expected >= return_type:
            raise TypeError(f"{self.current_function.name.text} expects {expected} return type, got {return_type} instead")

    @visitor(If)
    def check(self, expression: If):
        if expression.condition.check(self) != "bool":
            raise TypeError(f"if condition is not a boolean value")
        self.check_block(expression.code, Scope(self.scope))
        self.check_block(expression.else_code, Scope(self.scope))

    @visitor(While)
    def check(self, expression: While):
        if expression.condition.check(self) != "bool":
            raise TypeError(f"while condition is not a boolean value")
        self.check_block(expression.code, Scope(self.scope))

    def check_block(self, statements, scope: Scope):
        previous = self.scope
        try:
            self.scope = scope
            for statement in statements:
                self.check(statement)
        finally:
            self.scope = previous

    def get_type(self, name):
        if isinstance(name, str):
            if name == "object":
                return objects
            if name == "void" or name == "null":
                return null
            for t in self.types:
                if t == name:
                    return t
        if isinstance(name, Type):
            return name
        return None
