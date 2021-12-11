from enum import Enum, auto


class TokenType(Enum):
    # single character
    LEFT_PARENTHESIS = auto()
    RIGHT_PARENTHESIS = auto()
    LEFT_BRACKET = auto()
    RIGHT_BRACKET = auto()
    COMMA = auto()
    DOT = auto()
    PLUS = auto()
    MINUS = auto()
    MULTIPLY = auto()
    DIVIDE = auto()

    # one or two characters
    GREATER = auto()
    GREATER_EQUAL = auto()
    LOWER = auto()
    LOWER_EQUAL = auto()

    # literals
    NUMBER = auto()
    STRING = auto()
    LITERAL = auto()

    # keywords
    LET = auto()
    FUN = auto()
    VEHICLE = auto()
    CARGO = auto()
    PLACE = auto()
    WHILE = auto()
    IF = auto()
    ELSE = auto()
    NULL = auto()

    # End of File
    EOF = auto()
