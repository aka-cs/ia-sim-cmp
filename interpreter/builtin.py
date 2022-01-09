import inspect

from . import builtin_code
from .functions import BuiltinFunction
from ._types import Object, Null
from .classes import Class
from .scope import Scope


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
            scope.declare(var, _class[1].__annotations__[var])
        super_class = _class[1].__base__ if _class[1].__base__ != object else None
        result.append(Class(_class[0], super_class, scope))
    return result


def get_classes_code(module=builtin_code):
    classes = inspect.getmembers(module, inspect.isclass)
    result = []
    for _class in classes:
        if _class[1].__module__ != module.__name__:
            continue
        result.append(inspect.getsourcelines(_class[1]))
    return result


def get_builtin_function(function) -> BuiltinFunction:
    annotations = inspect.get_annotations(function[1])
    params = [annotations[var] for var in annotations if var != 'return']
    return BuiltinFunction(function[0], params, annotations.get('return', Null))


def get_functions(module=builtin_code) -> [BuiltinFunction]:
    functions = inspect.getmembers(module, inspect.isfunction)
    result = []
    for function in functions:
        if function[1].__module__ != module.__name__:
            continue
        result.append(get_builtin_function(function))
    return result


def get_functions_code(module=builtin_code) -> [str]:
    functions = inspect.getmembers(module, inspect.isfunction)
    result = []
    for function in functions:
        if function[1].__module__ != module.__name__:
            continue
        result.append(inspect.getsourcelines(function[1]))
    return result


builtin_functions: [BuiltinFunction] = [
    BuiltinFunction("print", [Object], Null),
    *get_functions()
]

builtin_classes: [Class] = [*get_classes()]

