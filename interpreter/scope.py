from typing import Optional
from dataclasses import dataclass


@dataclass
class Type:
    name: str
    parent: 'Type'


@dataclass
class Object:
    value: object
    type: Type


class Scope:
    def __init__(self, father: Optional['Scope']):
        self.variables: {str: Object} = {}
        self.father = father

    def declaration(self, name: str) -> bool:
        if not self.exists_scoped_variable(name):
            self.variables[name] = None
            return True
        return False

    def obtain_value(self, name: str) -> (Object, bool):
        if name in self.variables:
            return self.variables[name], True
        return self.father.obtain_value(name) if self.father else None, False

    def exists_scoped_variable(self, name) -> bool:
        return name in self.variables

    def exists_variable(self, name) -> bool:
        return self.obtain_value(name)[1]
