import inspect
import src
import glob
from pathlib import Path

from src import *
from builtin.functions import Function
from builtin._types import Object, Null, Int, Float, Boolean, String, TypeList, TypeDict, Type, List
from builtin.classes import Class
from builtin.scope import Scope


type_map = {type: Type, int: Int, float: Float, object: Object, bool: Boolean, str: String, None: Null}


def get_type(_type: str | type):
    if isinstance(_type, str):
        _type = eval(_type)
    if isinstance(_type, list):
        return TypeList(get_type(_type[0]))
    if isinstance(_type, dict):
        dict_types = list(_type.items())[0]
        return TypeDict((get_type(dict_types[0]), get_type(dict_types[1])))
    return type_map.get(_type, _type)


def get_classes_in_module(module) -> [type]:
    classes = inspect.getmembers(module, inspect.isclass)
    result = []
    for _class in classes:
        result.append(_class)
    return result


def get_classes(module=src) -> [Class]:
    classes = get_classes_in_module(module)
    created = set()
    result = []
    while len(created) != len(classes):
        for _class in classes:
            if _class[1] not in created and (_class[1].__base__ == object or _class[1].__base__ in created):
                super_class = _class[1].__base__ if _class[1].__base__ != object else None
                scope = Scope()
                c_class = Class(_class[0], type_map[super_class] if super_class else None, scope)
                c_class.super_class = super_class
                type_map[_class[1]] = c_class
                result.append(c_class)
                created.add(_class[1])
    for _class in classes:
        c_class = type_map[_class[1]]
        for function in inspect.getmembers(_class[1], inspect.isfunction):
            function_name = function[0] if function[0] != "__init__" else "init"
            c_class.scope.declare(function_name, get_builtin_function(function))
        for var in _class[1].__annotations__:
            _type = get_type(_class[1].__annotations__[var])
            c_class.scope.declare(var, _type)
    return result


def get_builtin_function(function) -> Function:
    _annotations = inspect.get_annotations(function[1])
    params = [get_type(_annotations[var]) for var in _annotations if var != 'return']
    return Function(function[0], params, get_type(_annotations.get('return', None)))


def get_functions(module=src) -> [Function]:
    functions = inspect.getmembers(module, inspect.isfunction)
    result = []
    for function in functions:
        result.append(get_builtin_function(function))
    return result


def get_code() -> [str]:
    files_path = Path('src/src/')
    files = files_path.glob('*.py')
    result = {}
    for file in files:
        result[file] = open(file).readlines()
    return result


builtin_classes: [Class] = [*get_classes()]

builtin_functions: [Function] = [
    Function("print", [Object], Null),
    Function("len", [List], Int),
    Function("isinstance", [Object, Type], Boolean),
    Function("max", [Float, Float], Float),
    Function("min", [Float, Float], Float),
    Function("pow", [Float, Float], Float),
    *get_functions()
]
