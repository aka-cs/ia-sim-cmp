from dataclasses import dataclass
from typing import Callable
from _parser.nodes import FunctionNode
from interpreter.scope import Scope
from ._types import Type


class Function:

    def __init__(self, name, param_types: [Type], return_type: Type):
        self.name = name
        self.param_types = param_types
        self.return_type = return_type


class BuiltinFunction:

    def __init__(self, name: str, function: Callable, param_type: [Type], return_type: Type):
        self.name = name
        self.function = function
        self.param_type = param_type
        self.return_type = return_type

    def __call__(self, interpreter, arguments):
        return self.function(*arguments)

    def __str__(self):
        return f"<builtin function {self.name}>"


class UserDefinedFunction:

    def __init__(self, function: FunctionNode):
        self.declaration = function

    def __call__(self, interpreter, arguments):
        scope = Scope(interpreter.globals)
        for i, arg in enumerate(arguments):
            scope.declare(self.declaration.params[i][0].text, arg)
        try:
            interpreter.execute_block(self.declaration.body, scope)
        except ReturnCall as value:
            return value.value

    def __str__(self):
        return f"<function {self.declaration.name}>"


@dataclass
class ReturnCall(Exception):
    value: object
