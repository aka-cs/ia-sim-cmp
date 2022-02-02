from dataclasses import dataclass
from _parser.nodes import FunctionNode
from interpreter.scope import Scope


class Function:

    def __init__(self, name, param_types, return_type, line=0):
        self.name = name
        self.param_types = param_types
        self.return_type = return_type
        self.line = line

    def __str__(self):
        return Function.__qualname__

