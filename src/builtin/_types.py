from .functions import Function


class Type(type):

    def __add__(self, other):
        raise TypeError(f"Operator not supported for types {self} and {other}")

    def __sub__(self, other):
        raise TypeError(f"Operator not supported for types {self} and {other}")

    def __mul__(self, other):
        raise TypeError(f"Operator not supported for types {self} and {other}")

    def __truediv__(self, other):
        raise TypeError(f"Operator not supported for types {self} and {other}")

    def __neg__(self):
        raise TypeError(f"Operator not supported for type {self}")

    def __eq__(self, other):
        raise TypeError(f"Operator not supported for types {self} and {other}")

    def __ne__(self, other):
        raise TypeError(f"Operator not supported for types {self} and {other}")

    def __lt__(self, other):
        raise TypeError(f"Operator not supported for types {self} and {other}")

    def __gt__(self, other):
        raise TypeError(f"Operator not supported for types {self} and {other}")

    def __le__(self, other):
        raise TypeError(f"Operator not supported for types {self} and {other}")

    def __ge__(self, other):
        raise TypeError(f"Operator not supported for types {self} and {other}")

    def __getattr__(self, item):
        raise AttributeError(f"{self} has no attribute {item}")

    def getattr(cls, name):
        return getattr(cls, name)

    def __str__(self):
        return self.__qualname__


class Object(metaclass=Type):

    def __init__(self):
        self.parent = super()


class TypeNumber(Type):

    def __add__(self, other):
        if issubclass(self, other):
            return other
        if issubclass(other, self):
            return self
        raise TypeError(f"Operator not supported for types {self} and {other}")

    def __sub__(self, other):
        return self + other

    def __mul__(self, other):
        return self + other

    def __truediv__(self, other):
        return self + other

    def __neg__(self):
        return self

    def __eq__(self, other):
        if issubclass(self, other) or issubclass(other, self):
            return Boolean
        raise TypeError(f"Operator not supported for types {self} and {other}")

    def __ne__(self, other):
        return self == other

    def __lt__(self, other):
        return self == other

    def __gt__(self, other):
        return self == other

    def __le__(self, other):
        return self == other

    def __ge__(self, other):
        return self == other


class Float(Object, metaclass=TypeNumber):

    def __init__(self, value):
        Object.__init__(self)
        self.value = float(value)

    def __add__(self, other):
        return Float(self.value + other.value)

    def __sub__(self, other):
        return Float(self.value - other.value)

    def __mul__(self, other):
        return Float(self.value * other.value)

    def __truediv__(self, other):
        return Float(self.value / other.value)

    def __neg__(self):
        return Float(-self.value)

    def __eq__(self, other):
        return Boolean(self.value == other.value)

    def __ne__(self, other):
        return Boolean(self.value != other.value)

    def __lt__(self, other):
        return Boolean(self.value < other.value)

    def __gt__(self, other):
        return Boolean(self.value > other.value)

    def __le__(self, other):
        return Boolean(self.value <= other.value)

    def __ge__(self, other):
        return Boolean(self.value >= other.value)

    def __str__(self):
        return str(self.value)


class Int(Float, metaclass=TypeNumber):

    def __init__(self, value):
        Object.__init__(self)
        self.value = value

    def __add__(self, other):
        if isinstance(other, Int):
            return Int(self.value + other.value)
        return Float(self.value + other.value)

    def __sub__(self, other):
        if isinstance(other, Int):
            return Int(self.value - other.value)
        return Float(self.value - other.value)

    def __mul__(self, other):
        if isinstance(other, Int):
            return Int(self.value * other.value)
        return Float(self.value * other.value)

    def __truediv__(self, other):
        if isinstance(other, Int):
            return Int(self.value / other.value)
        return Float(self.value / other.value)

    def __neg__(self):
        return Int(-self.value)

    def __str__(self):
        return str(self.value)


class TypeString(Type):

    def __add__(self, other):
        if issubclass(self, other):
            return other
        if issubclass(other, self):
            return self
        raise TypeError(f"Operator not supported for types {self} and {other}")

    def __eq__(self, other):
        if issubclass(self, other) or issubclass(other, self):
            return Boolean
        raise TypeError(f"Operator not supported for types {self} and {other}")

    def __ne__(self, other):
        return self == other


class String(Object, metaclass=TypeString):

    def __init__(self, value: str):
        Object.__init__(self)
        self.value = value

    def __add__(self, other):
        return String(self.value + other.value)

    def __eq__(self, other):
        return Boolean(self.value == other.value)

    def __ne__(self, other):
        return Boolean(self.value != other.value)

    def __str__(self):
        return self.value


class TypeBool(Type):
    pass


class Boolean(Object, metaclass=TypeBool):

    def __init__(self, value):
        Object.__init__(self)
        self.value = value

    def __bool__(self):
        return self.value

    def __str__(self):
        return str(self.value).lower()


class TypeList(Type):

    def __new__(mcs, list_type):
        created = super().__new__(mcs, "List", (List,), {'list_type': list_type})
        created.list_type = list_type
        created.append = Function("append", [list_type], Null)
        created.remove = Function("remove", [list_type], Null)
        return created

    def __getitem__(cls, item):
        if not issubclass(item, Int):
            raise TypeError("Index must be an integer")
        return cls.list_type

    def __str__(self):
        return f"list<{self.list_type}>"


class List(Object):

    def __init__(self, value):
        super().__init__()
        self.value = value

    def __getitem__(self, item):
        return self.value[item.value]

    def __setitem__(self, key, value):
        self.value[key] = value

    def __str__(self):
        return str(self.value)


class TypeDict(Type):

    def __new__(mcs, types):
        created = super().__new__(mcs, "Dict", (Dict,), {'key_type': types[0], 'value_type': types[1]})
        created.key_type = types[0]
        created.value_type = types[1]
        created.keys = Function("keys", [], TypeList(created.key_type))
        return created

    def __getitem__(cls, item):
        if not issubclass(item, cls.key_type) and not issubclass(cls.key_type, item):
            raise TypeError(f"Index must be of type {cls.key_type}")
        return cls.value_type

    def __str__(self):
        return f"dict<{self.key_type}, {self.value_type}>"


class Dict(Object):

    def __init__(self, value):
        super().__init__()
        self.value = value

    def __getitem__(self, item):
        return self.value[item]

    def __setitem__(self, key, value):
        self.value[key] = value

    def __str__(self):
        return str(self.value)


class Null(metaclass=Type):

    def __str__(self):
        return str(self.__class__).lower()
