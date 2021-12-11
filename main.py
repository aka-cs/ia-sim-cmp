from tokenizer import Tokenizer, TokenMatcher, TokenType
from _parser import Parser

if __name__ == '__main__':

    matches = [
        TokenMatcher(r'-?\d+(?:\.\d+)?', TokenType.NUMBER),
        TokenMatcher(r'"[^"]+"', TokenType.STRING),
        TokenMatcher(r'\+', TokenType.PLUS),
        TokenMatcher(r'\-', TokenType.MINUS),
        TokenMatcher(r'\*', TokenType.MULTIPLY),
        TokenMatcher(r'\/', TokenType.DIVIDE),
        TokenMatcher(r'\(', TokenType.LEFT_PARENTHESIS),
        TokenMatcher(r'\)', TokenType.RIGHT_PARENTHESIS),
        TokenMatcher(r'\{', TokenType.LEFT_BRACKET),
        TokenMatcher(r'\}', TokenType.RIGHT_BRACKET),
        TokenMatcher(r'let', TokenType.LET),
        TokenMatcher(r'fun', TokenType.FUN),
        TokenMatcher(r'if', TokenType.IF),
        TokenMatcher(r'else', TokenType.ELSE),
        TokenMatcher(r'while', TokenType.WHILE),
        TokenMatcher(r'null', TokenType.NULL),
        TokenMatcher(r'>', TokenType.GREATER),
        TokenMatcher(r'<', TokenType.LOWER),
        TokenMatcher(r'>=', TokenType.GREATER_EQUAL),
        TokenMatcher(r'<=', TokenType.LOWER_EQUAL),
        TokenMatcher(r'\w[\w\d_]+', TokenType.LITERAL),
        TokenMatcher(r'.', TokenType.DOT),
        TokenMatcher(r',', TokenType.COMMA)
    ]

    tokenizer = Tokenizer(matches)

    with open('test/program.txt', 'r') as file:
        program = file.read()

    tokens = tokenizer.analyze(program)
    parser = Parser(tokens)
    result = (parser.parse())
    print(result)
    print(result.eval())
