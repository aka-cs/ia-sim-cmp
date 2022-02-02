from ._types import Type, Object, Null
from typing import Optional
from .scope import Scope
from .functions import Function


class Class(Type):

    def __new__(mcs, name: str, super_class: Optional['Class'], scope: Scope):
        if super_class:
            scope.father = super_class.scope
            super_class = (super_class, )
        else:
            super_class = (Object,)
        class_to_return = super().__new__(mcs, name, super_class, {})
        class_to_return.name = name
        class_to_return.scope = scope
        return class_to_return

    def get_constructor(cls):
        params = []
        if "init" in cls.scope.variables:
            params = cls.scope.get("init").param_types
        return Function(cls.name, params, cls)

    def __str__(self):
        return self.__qualname__

    def getattr(self, item):
        try:
            return self.scope.get(item)
        except:
            raise TypeError(f"{self.name} type has no property or method {item}")
