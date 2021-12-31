from .functions import BuiltinFunction
from ._types import Object, Null

builtin_functions = [
    BuiltinFunction("print", print, [Object], Null)
]