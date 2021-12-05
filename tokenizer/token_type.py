from enum import Enum


class TokenType(Enum):
    number = 0
    string = 1
    plus = 2
    minus = 3
    multiply = 4
    divide = 5
    left_parenthesis = 6
    right_parenthesis = 7
    left_bracket = 8
    right_bracket = 9
    let = 10
    fun = 11
    vehicle = 12
    cargo = 13
    place = 14
    while_ = 15
    if_ = 16
    else_ = 17
    gt = 18
    gte = 19
    lw = 20
    lwe = 21
    colon = 22
    coma = 23
    literal = 1000

