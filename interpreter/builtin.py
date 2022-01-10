import inspect

from . import builtin_code
from .functions import BuiltinFunction
from ._types import Object, Null, Int, Float, Bool, String, TypeArray
from .classes import Class
from .scope import Scope


def get_type(_type: str | type):
    if isinstance(_type, str):
        if _type[0] == "[" and _type[-1] == "]":
            return TypeArray(get_type(_type[1:-1]))
        _type = eval(_type)
    type_map = {int: Int, float: Float, object: Object, bool: Bool, str: String, None: Null}
    return type_map.get(_type, _type)


def get_classes(module=builtin_code) -> [Class]:
    classes = inspect.getmembers(module, inspect.isclass)
    result = []
    for _class in classes:
        if _class[1].__module__ != module.__name__:
            continue
        scope = Scope()
        for function in inspect.getmembers(_class[1], inspect.isfunction):
            function_name = function[0] if function[0] != "__init__" else "init"
            scope.declare(function_name, get_builtin_function(function))
        for var in _class[1].__annotations__:
            _type = get_type(_class[1].__annotations__[var])
            scope.declare(var, _type)
        super_class = _class[1].__base__ if _class[1].__base__ != object else None
        result.append(Class(_class[0], super_class, scope))
    return result


def get_builtin_function(function) -> BuiltinFunction:
    annotations = inspect.get_annotations(function[1])
    params = [get_type(annotations[var]) for var in annotations if var != 'return']
    return BuiltinFunction(function[0], params, get_type(annotations.get('return', None)))


def get_functions(module=builtin_code) -> [BuiltinFunction]:
    functions = inspect.getmembers(module, inspect.isfunction)
    result = []
    for function in functions:
        if function[1].__module__ != module.__name__:
            continue
        result.append(get_builtin_function(function))
    return result


def get_code(file: str) -> [str]:
    file = open(file)
    lines = file.readlines()
    file.close()
    return lines


builtin_functions: [BuiltinFunction] = [
    BuiltinFunction("print", [Object], Null),
    *get_functions()
]

builtin_classes: [Class] = [*get_classes()]
