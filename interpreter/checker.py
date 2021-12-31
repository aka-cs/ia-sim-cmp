from tools import Singleton, visitor
from .scope import Scope
from _parser.nodes import *
from tokenizer.token_type import TokenType
from ._types import Float, Int, String, Bool, Null, TypeArray, Array
from .functions import Function
from .builtin import builtin_functions


class TypeChecker(metaclass=Singleton):

    def __init__(self):
        self.globals = Scope()
        self.scope = self.globals
        self.types = [Float, Int, String, Bool]
        self.current_function = None
        for fun in builtin_functions:
            self.scope.declare(fun.name, Function(fun.param_type, fun.return_type))

    def start(self, expressions: [Node]):
        for expression in expressions:
            if isinstance(expression, FunctionNode):
                params = []
                for param in expression.params:
                    params.append(param[1].check(self))
                if expression.return_type.type.text == "void" and not expression.return_type.nested:
                    return_type = Null
                else:
                    return_type = expression.return_type.check(self)
                self.scope.declare(expression.name.text, Function(params, return_type))
        for expression in expressions:
            expression.check(self)

    @visitor(Literal)
    def check(self, expression: Literal):
        if isinstance(expression.value, float):
            return Float
        if isinstance(expression.value, int):
            return Int
        if isinstance(expression.value, str):
            return String
        if isinstance(expression.value, bool):
            return Bool
        if expression.value is None:
            return Null
        return None

    @visitor(ArrayNode)
    def check(self, expression: ArrayNode):
        result = []
        for elem in expression.expressions:
            result.append(elem.check(self))
        if not result:
            return TypeArray(None)
        array_type = result[0]
        for elem in result:
            if self.can_assign(elem, array_type):
                continue
            elif self.can_assign(array_type, elem):
                array_type = elem
            else:
                raise TypeError(f"Array elements are not of the same type")
        return TypeArray(array_type)

    @visitor(Index)
    def check(self, expression: Index):
        left = expression.expression.check(self)
        index = expression.index.check(self)
        return left[index]

    @visitor(Grouping)
    def check(self, expression: Grouping):
        return expression.expression.check(self)

    @visitor(Unary)
    def check(self, expression: Unary):
        right = expression.right.check(self)
        if expression.operator.type == TokenType.MINUS:
            return -right
        elif expression.operator.type == TokenType.EXCLAMATION:
            if not issubclass(right, Bool):
                raise TypeError()
            return Bool
        return None

    @visitor(Binary)
    def check(self, expression: Binary):
        left = expression.left.check(self)
        right = expression.right.check(self)
        if expression.operator.type == TokenType.EQUAL_EQUAL:
            return left == right
        if expression.operator.type == TokenType.EQUAL_DIFFERENT:
            return left != right
        if expression.operator.type in [TokenType.AND, TokenType.OR]:
            if not issubclass(left, Bool) or not issubclass(right, Bool):
                raise TypeError()
            return Bool
        if expression.operator.type == TokenType.PLUS:
            return left + right
        if expression.operator.type == TokenType.MINUS:
            return left - right
        if expression.operator.type == TokenType.DIVIDE:
            return left / right
        if expression.operator.type == TokenType.MULTIPLY:
            return left * right
        if expression.operator.type == TokenType.LESS:
            return left < right
        if expression.operator.type == TokenType.LESS_EQUAL:
            return left <= right
        if expression.operator.type == TokenType.GREATER:
            return left > right
        if expression.operator.type == TokenType.GREATER_EQUAL:
            return left >= right
        return None

    @visitor(Variable)
    def check(self, expression: Variable):
        return self.scope.get(expression.name.text)

    @visitor(VarDeclaration)
    def check(self, expression: VarDeclaration):
        expression_type = expression.expression.check(self)
        if expression.type:
            variable_type = expression.type.check(self)
            if not self.can_assign(expression_type, variable_type):
                raise TypeError(
                    f"Variable {expression.name.text} of type {expression.type.type.text} can't be assigned {expression_type}")
            expression_type = variable_type
        else:
            if issubclass(expression_type, Null):
                raise TypeError("Can't infer type of null")
        self.scope.declare(expression.name.text, expression_type)

    @visitor(VarType)
    def check(self, expression: VarType):
        if expression.type.text == "array":
            return TypeArray(expression.nested.check(self))
        for t in self.types:
            if expression.type.text == str(t):
                return t
        raise TypeError(f"{expression.type.text} is not defined in current scope")

    @visitor(Assignment)
    def check(self, expression: Assignment):
        expression_type = expression.value.check(self)
        variable_type = self.scope.get(expression.var_name.text)
        if not self.can_assign(expression_type, variable_type):
            raise TypeError(
                f"Variable {expression.var_name.text} of type {variable_type} can't be assigned {expression_type}")
        self.scope.assign(expression.var_name.text, expression_type)

    @visitor(ExpressionStatement)
    def check(self, expression: ExpressionStatement):
        return expression.expression.check(self)

    @visitor(Call)
    def check(self, expression: Call):
        called: Function = expression.called.check(self)
        if len(expression.arguments) != len(called.params_types):
            raise Exception("Invalid number of arguments")
        for arg, param in zip(expression.arguments, called.params_types):
            arg_type = arg.check(self)
            if not self.can_assign(arg_type, param):
                raise TypeError(f"Function with argument type {param} can't receive {arg_type}")
        return called.return_type

    @visitor(FunctionNode)
    def check(self, expression: FunctionNode):
        scope = Scope(self.scope)
        for param in expression.params:
            scope.declare(param[0].text, param[1].check(self))
        self.current_function = self.scope.get(expression.name.text)
        self.check_block(expression.body, scope)
        self.current_function = None

    @visitor(Return)
    def check(self, expression: Return):
        if not self.current_function:
            raise Exception("return statement should be inside a function")
        if expression.expression:
            return_type = expression.expression.check(self)
        else:
            return_type = Null
        expected = self.current_function.return_type
        if not self.can_assign(return_type, expected):
            raise TypeError(
                f"Function expects {expected} return type, got {return_type} instead")

    @visitor(If)
    def check(self, expression: If):
        if not issubclass(expression.condition.check(self), Bool):
            raise TypeError(f"if condition is not a boolean value")
        self.check_block(expression.code, Scope(self.scope))
        self.check_block(expression.else_code, Scope(self.scope))

    @visitor(While)
    def check(self, expression: While):
        if not issubclass(expression.condition.check(self), Bool):
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

    @staticmethod
    def can_assign(type1, type2):
        if isinstance(type1, Function) or isinstance(type2, Function):
            raise TypeError()
        if isinstance(type1, TypeArray) and isinstance(type2, TypeArray):
            if type1.array_type is None:
                return True
            return TypeChecker.can_assign(type1.array_type, type2.array_type)
        return issubclass(type1, type2)
