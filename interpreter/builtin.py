import inspect

from . import builtin_code
from .builtin_code import *
from .functions import BuiltinFunction
from ._types import Object, Null, Int, Float, Bool, String, TypeList, TypeDict
from .classes import Class
from .scope import Scope


type_map = {int: Int, float: Float, object: Object, bool: Bool, str: String, None: Null}


def get_type(_type: str | type):
    if isinstance(_type, str):
        if _type[0] == "[" and _type[-1] == "]":
            return TypeList(get_type(_type[1:-1]))
        if _type.startswith("dict"):
            _type = _type[5:-1]
            types = _type.split(", ")
            return TypeDict((get_type(types[0]), get_type(types[1])))
        _type = eval(_type)
    return type_map.get(_type, _type)


def get_classes_in_module(module) -> [type]:
    classes = inspect.getmembers(module, inspect.isclass)
    result = []
    for _class in classes:
        result.append(_class)
    return result


def get_classes(module=builtin_code) -> [Class]:
    classes = get_classes_in_module(module)
    result = []
    for _class in classes:
        scope = Scope()
        c_class = Class(_class[0], None, scope)
        type_map[_class[1]] = c_class
    for _class in classes:
        c_class = type_map[_class[1]]
        for function in inspect.getmembers(_class[1], inspect.isfunction):
            function_name = function[0] if function[0] != "__init__" else "init"
            c_class.scope.declare(function_name, get_builtin_function(function))
        for var in _class[1].__annotations__:
            _type = get_type(_class[1].__annotations__[var])
            c_class.scope.declare(var, _type)
        super_class = _class[1].__base__ if _class[1].__base__ != object else None
        c_class.super_class = super_class
        result.append(c_class)
    return result


def get_builtin_function(function) -> BuiltinFunction:
    _annotations = inspect.get_annotations(function[1])
    params = [get_type(_annotations[var]) for var in _annotations if var != 'return']
    return BuiltinFunction(function[0], params, get_type(_annotations.get('return', None)))


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


builtin_classes: [Class] = [*get_classes()]

builtin_functions: [BuiltinFunction] = [
    BuiltinFunction("print", [Object], Null),
    *get_functions()
]
