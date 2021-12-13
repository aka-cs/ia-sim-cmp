from enum import Enum, auto


class TokenType(Enum):
    # single character
    LEFT_PARENTHESIS = auto()
    RIGHT_PARENTHESIS = auto()
    LEFT_BRACKET = auto()
    RIGHT_BRACKET = auto()
    COMMA = auto()
    DOT = auto()
    SEMICOLON = auto()
    LINEBREAK = auto()
    PLUS = auto()
    MINUS = auto()
    MULTIPLY = auto()
    DIVIDE = auto()
    EXCLAMATION = auto()

    # one or two characters
    GREATER = auto()
    GREATER_EQUAL = auto()
    LOWER = auto()
    LOWER_EQUAL = auto()
    EQUAL = auto()
    EQUAL_EQUAL = auto()
    EQUAL_DIFFERENT = auto()

    # literals
    NUMBER = auto()
    STRING = auto()
    IDENTIFIER = auto()

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
    TRUE = auto()
    FALSE = auto()

    # End of File
    EOF = auto()
