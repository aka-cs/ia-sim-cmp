class MissingMainError(Exception):
    pass


class InvalidMain(Exception):

    def __init__(self, main):
        super().__init__(self)
        self.main = main


class InvalidTypeError(TypeError):

    def __init__(self, message, line):
        super().__init__(self)
        self.message = message
        self.line = line


class InvalidOperation(Exception):

    def __init__(self, message, token=None):
        super().__init__()
        self.message = message
        self.token = token


class OperatorNotFound(Exception):

    def __init__(self, message):
        super().__init__()
        self.message = message


class AttributeNotFound(Exception):

    def __init__(self, message):
        super().__init__()
        self.message = message


class TypeNotDefined(Exception):

    def __init__(self, message, token):
        super().__init__()
        self.message = message
        self.token = token


class NameNotInScope(Exception):

    def __init__(self, message, token):
        super().__init__()
        self.message = message
        self.token = token


class InvalidMethodDeclaration(Exception):

    def __init__(self, message, line):
        super().__init__()
        self.message = message
        self.line = line


class InvalidCall(Exception):
    def __init__(self, message, line):
        super().__init__()
        self.message = message
        self.line = line
