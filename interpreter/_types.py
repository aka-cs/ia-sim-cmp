class Type(type):

    def __add__(self, other):
        raise TypeError(f"+ operator not supported for types {self} and {other}")

    def __sub__(self, other):
        raise TypeError(f"- operator not supported for types {self} and {other}")

    def __mul__(self, other):
        raise TypeError(f"* operator not supported for types {self} and {other}")

    def __truediv__(self, other):
        raise TypeError(f"/ operator not supported for types {self} and {other}")

    def __neg__(self):
        raise TypeError(f"- operator not supported for type {self}")

    def __eq__(self, other):
        raise TypeError(f"== operator not supported for types {self} and {other}")

    def __ne__(self, other):
        raise TypeError(f"!= operator not supported for types {self} and {other}")

    def __lt__(self, other):
        raise TypeError(f"< operator not supported for types {self} and {other}")

    def __gt__(self, other):
        raise TypeError(f"> operator not supported for types {self} and {other}")

    def __le__(self, other):
        raise TypeError(f"<= operator not supported for types {self} and {other}")

    def __ge__(self, other):
        raise TypeError(f">= operator not supported for types {self} and {other}")

    def __str__(self):
        return self.__qualname__.lower()


class Object(metaclass=Type):

    def __init__(self):
        self.parent = super()


class TypeNumber(Type):

    def __add__(self, other):
        if issubclass(self, other):
            return other
        if issubclass(other, self):
            return self
        raise TypeError()

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
            return Bool
        raise TypeError()

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
        return Bool(self.value == other.value)

    def __ne__(self, other):
        return Bool(self.value != other.value)

    def __lt__(self, other):
        return Bool(self.value < other.value)

    def __gt__(self, other):
        return Bool(self.value > other.value)

    def __le__(self, other):
        return Bool(self.value <= other.value)

    def __ge__(self, other):
        return Bool(self.value >= other.value)

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
        raise TypeError()

    def __eq__(self, other):
        if issubclass(self, other) or issubclass(other, self):
            return Bool
        raise TypeError()

    def __ne__(self, other):
        return self == other


class String(Object, metaclass=TypeString):

    def __init__(self, value):
        Object.__init__(self)
        self.value = value

    def __add__(self, other):
        return String(self.value + other.value)

    def __eq__(self, other):
        return Bool(self.value == other.value)

    def __ne__(self, other):
        return Bool(self.value != other.value)

    def __str__(self):
        return self.value


class TypeBool(Type):
    pass


class Bool(Object, metaclass=TypeBool):

    def __init__(self, value):
        Object.__init__(self)
        self.value = value

    def __bool__(self):
        return self.value

    def __str__(self):
        return str(self.value).lower()


class TypeArray(Type):

    def __new__(mcs, array_type):
        mcs.array_type = array_type
        return super().__new__(mcs, "Array", (Array,), {'array_type': array_type})

    def __getitem__(cls, item):
        if not issubclass(item, Int):
            raise TypeError("Index must be an integer")
        return cls.array_type

    def __str__(self):
        return f"array<{self.array_type}>"


class Array(Object):

    def __init__(self, value):
        super().__init__()
        self.value = value

    def __getitem__(self, item):
        return self.value[item.value]

    def __setitem__(self, key, value):
        self.value[key] = value

    def __str__(self):
        return "[" + ", ".join(list(map(str, self.value))) + "]"


class Null(metaclass=Type):

    def __str__(self):
        return str(self.__class__).lower()
