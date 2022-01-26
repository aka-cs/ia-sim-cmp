from tokenizer.tokenizer import TokenMatcher
from tokenizer.token_type import TokenType

matches = [
    TokenMatcher(r'self', TokenType.SELF),
    TokenMatcher(r'super', TokenType.SUPER),
    TokenMatcher(r'\d+', TokenType.INTEGER),
    TokenMatcher(r'\d+(.\d+)?', TokenType.FLOAT),
    TokenMatcher(r'"([^"]|\\")*[^\\]?"', TokenType.STRING),  # Regex is not prepared for strings yet
    TokenMatcher(r'\+', TokenType.PLUS),
    TokenMatcher(r'\-', TokenType.MINUS),
    TokenMatcher(r'!', TokenType.EXCLAMATION),
    TokenMatcher(r'\*', TokenType.MULTIPLY),
    TokenMatcher(r'\/', TokenType.DIVIDE),
    TokenMatcher(r'\(', TokenType.OPEN_PARENTHESIS),
    TokenMatcher(r'\)', TokenType.CLOSE_PARENTHESIS),
    TokenMatcher(r'\{', TokenType.OPEN_BRACES),
    TokenMatcher(r'\}', TokenType.CLOSE_BRACES),
    TokenMatcher(r'\[', TokenType.OPEN_BRACKETS),
    TokenMatcher(r'\]', TokenType.CLOSE_BRACKETS),
    TokenMatcher(r'var', TokenType.VAR),
    TokenMatcher(r'attr', TokenType.ATTR),
    TokenMatcher(r'class', TokenType.CLASS),
    TokenMatcher(r'fun', TokenType.FUN),
    TokenMatcher(r'if', TokenType.IF),
    TokenMatcher(r'else', TokenType.ELSE),
    TokenMatcher(r'while', TokenType.WHILE),
    TokenMatcher(r'null', TokenType.NULL),
    TokenMatcher(r'true', TokenType.TRUE),
    TokenMatcher(r'false', TokenType.FALSE),
    TokenMatcher(r'return', TokenType.RETURN),
    TokenMatcher(r'and', TokenType.AND),
    TokenMatcher(r'or', TokenType.OR),
    TokenMatcher('switch', TokenType.SWITCH),
    TokenMatcher('case', TokenType.CASE),
    TokenMatcher('default', TokenType.DEFAULT),
    TokenMatcher(r'>=', TokenType.GREATER_EQUAL),
    TokenMatcher(r'<=', TokenType.LESS_EQUAL),
    TokenMatcher(r'>', TokenType.GREATER),
    TokenMatcher(r'<', TokenType.LESS),
    TokenMatcher(r'==', TokenType.EQUAL_EQUAL),
    TokenMatcher(r'=', TokenType.EQUAL),
    TokenMatcher(r'[a-zA-Z_]+(\w|_)*', TokenType.IDENTIFIER),
    TokenMatcher(r'\.', TokenType.DOT),
    TokenMatcher(r',', TokenType.COMMA),
    TokenMatcher(r';', TokenType.SEMICOLON),
    TokenMatcher(r':', TokenType.COLON),
    TokenMatcher(' ', TokenType.SPACE),
    TokenMatcher('\n|\r|\n\r', TokenType.LINEBREAK)
]
