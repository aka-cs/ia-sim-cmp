from typing import Optional


class Scope:
    def __init__(self, father: Optional['Scope'] = None):
        self.variables: {str: object} = {}
        self.father = father

    def declare(self, name: str, value: object) -> None:
        if name not in self.variables:
            self.variables[name] = value
        else:
            raise Exception(f"Variable {name} already exists")

    def get(self, name: str):
        if name in self.variables:
            return self.variables[name]
        if self.father:
            return self.father.get(name)
        raise Exception(f"Variable {name} not defined")

    def assign(self, name: str, value: object):
        if name in self.variables:
            self.variables[name] = value
        elif self.father:
            self.father.assign(name, value)
        else:
            raise Exception(f"Variable {name} not defined")
