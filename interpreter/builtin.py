from .functions import BuiltinFunction
from .types import Type

objects = Type("object")
numbers = Type("number", objects)
strings = Type("string", objects)
boolean = Type("bool", objects)
null = Type("null")

builtin_types = [numbers, strings, boolean]

builtin_functions = [
    BuiltinFunction("print", print, [objects], null)
]