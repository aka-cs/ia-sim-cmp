from dataclasses import dataclass
from _parser.nodes import FunctionNode
from interpreter.scope import Scope


class Function:

    def __init__(self, name, param_types, return_type, line=0):
        self.name = name
        self.param_types = param_types
        self.return_type = return_type
        self.line = line


class BuiltinFunction:

    def __init__(self, name: str, param_types, return_type):
        self.name = name
        self.param_types = param_types
        self.return_type = return_type

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
