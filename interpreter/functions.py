from dataclasses import dataclass
from typing import Callable
from _parser.statement import Function
from .scope import Scope


@dataclass
class BuiltinFunction:
    function: Callable
    number_arguments: int

    def __call__(self, interpreter, arguments):
        return self.function(*arguments)


@dataclass
class UserDefinedFunction:
    declaration: Function
    number_arguments: int

    def __call__(self, interpreter, arguments):
        scope = Scope(interpreter.globals)
        for i, arg in enumerate(arguments):
            scope.declare(self.declaration.params[i].text, arg)
        try:
            interpreter.execute_block(self.declaration.body, scope)
        except ReturnCall as value:
            return value.value


@dataclass
class ReturnCall(Exception):
    value: object


builtin_print = BuiltinFunction(print, 1)
