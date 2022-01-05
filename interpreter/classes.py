from ._types import Type, Object
from typing import Tuple
from .scope import Scope


class Class(Type):

    def __new__(mcs, name: str, super_classes: Tuple['Class'] | None, scope: Scope):
        mcs.name = name
        if super_classes:
            mcs.super_classes = super_classes
        else:
            mcs.super_classes = (Object, )
        mcs.scope = scope
        return super().__new__(mcs, mcs.name, mcs.super_classes, {})

    def __str__(self):
        return f'{self.name}'

    def __getattr__(self, item):
        if item not in self.scope.variables:
            raise TypeError(f"{self.name} type has no property or method {item}")
        return self.scope.get(item)
