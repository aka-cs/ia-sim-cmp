from tokenizer.tokenizer import TokenMatcher
from tokenizer.token_type import TokenType

matches = [
    TokenMatcher(r'-?\d+(.\d+)?', TokenType.NUMBER),
    # TokenMatcher(r'""', TokenType.STRING), # Regex is not prepared for strings yet
    TokenMatcher(r'\+', TokenType.PLUS),
    TokenMatcher(r'\-', TokenType.MINUS),
    TokenMatcher(r'\*', TokenType.MULTIPLY),
    TokenMatcher(r'\/', TokenType.DIVIDE),
    TokenMatcher(r'\(', TokenType.LEFT_PARENTHESIS),
    TokenMatcher(r'\)', TokenType.RIGHT_PARENTHESIS),
    TokenMatcher(r'\{', TokenType.LEFT_BRACKET),
    TokenMatcher(r'\}', TokenType.RIGHT_BRACKET),
    TokenMatcher(r'var', TokenType.VAR),
    TokenMatcher(r'fun', TokenType.FUN),
    TokenMatcher(r'if', TokenType.IF),
    TokenMatcher(r'else', TokenType.ELSE),
    TokenMatcher(r'while', TokenType.WHILE),
    TokenMatcher(r'null', TokenType.NULL),
    TokenMatcher(r'true', TokenType.TRUE),
    TokenMatcher(r'false', TokenType.FALSE),
    TokenMatcher(r'return', TokenType.RETURN),
    TokenMatcher(r'>=', TokenType.GREATER_EQUAL),
    TokenMatcher(r'<=', TokenType.LOWER_EQUAL),
    TokenMatcher(r'>', TokenType.GREATER),
    TokenMatcher(r'<', TokenType.LOWER),
    TokenMatcher(r'==', TokenType.EQUAL_EQUAL),
    TokenMatcher(r'=', TokenType.EQUAL),
    TokenMatcher(r'(\l|_)+(\w|_)*', TokenType.IDENTIFIER),
    TokenMatcher(r'\.', TokenType.DOT),
    TokenMatcher(r',', TokenType.COMMA),
    TokenMatcher(r';', TokenType.SEMICOLON),
    TokenMatcher(' ', TokenType.SPACE),
    TokenMatcher('\n|\r|\n\r', TokenType.LINEBREAK)
]
