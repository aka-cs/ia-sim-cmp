from dataclasses import dataclass
from typing import Callable
from _parser.nodes import Function
from interpreter.scope import Scope
from .types import Type


@dataclass
class BuiltinFunction:
    name: str
    function: Callable
    param_type: [Type]
    return_type: Type

    def __call__(self, interpreter, arguments):
        return self.function(*arguments)

    def __str__(self):
        return f"<builtin function {self.name}>"


class UserDefinedFunction:
    declaration: Function

    def __init__(self, function: Function):
        self.declaration = function
        self.param_type: [str] = []
        self.return_type: str = function.return_type.text
        for param in function.params:
            self.param_type.append(param[1].text)

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

