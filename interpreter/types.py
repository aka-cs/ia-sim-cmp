from typing import Optional
from dataclasses import dataclass


@dataclass
class Type:
    name: str
    parent: Optional['Type'] = None

    def __str__(self):
        return self.name

    def __eq__(self, other):
        if isinstance(other, Type):
            return self.name == other.name
        if isinstance(other, str):
            return self.name == other
        raise TypeError()

    def __ge__(self, other: 'Type'):
        if not isinstance(other, Type):
            raise TypeError()
        if self == other:
            return True
        if other.parent:
            return self >= other.parent
        return False
