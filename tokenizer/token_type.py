from enum import Enum, auto


class TokenType(Enum):
    # single character
    OPEN_PARENTHESIS = auto()
    CLOSE_PARENTHESIS = auto()
    OPEN_BRACES = auto()
    CLOSE_BRACES = auto()
    OPEN_BRACKETS = auto()
    CLOSE_BRACKETS = auto()
    COMMA = auto()
    DOT = auto()
    SEMICOLON = auto()
    COLON = auto()
    LINEBREAK = auto()
    SPACE = auto()
    PLUS = auto()
    MINUS = auto()
    MULTIPLY = auto()
    DIVIDE = auto()
    EXCLAMATION = auto()

    # one or two characters
    GREATER = auto()
    GREATER_EQUAL = auto()
    LESS = auto()
    LESS_EQUAL = auto()
    EQUAL = auto()
    EQUAL_EQUAL = auto()
    EQUAL_DIFFERENT = auto()

    # literals
    INTEGER = auto()
    FLOAT = auto()
    STRING = auto()
    IDENTIFIER = auto()

    # keywords
    VAR = auto()
    CLASS = auto()
    FUN = auto()
    VEHICLE = auto()
    CARGO = auto()
    PLACE = auto()
    WHILE = auto()
    IF = auto()
    ELSE = auto()
    NULL = auto()
    TRUE = auto()
    FALSE = auto()
    RETURN = auto()
    AND = auto()
    OR = auto()

    # End of File
    EOF = auto()
