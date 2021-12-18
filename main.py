from tokenizer import Tokenizer, TokenMatcher, TokenType
from _parser import Parser
from interpreter import Interpreter, Scope

if __name__ == '__main__':

    matches = [
        TokenMatcher(r'(-?\d+(?:\.\d+)?)[^\w]', TokenType.NUMBER),
        TokenMatcher(r'"(.+?[^\\])"', TokenType.STRING),
        TokenMatcher(r'\+', TokenType.PLUS),
        TokenMatcher(r'\-', TokenType.MINUS),
        TokenMatcher(r'\*', TokenType.MULTIPLY),
        TokenMatcher(r'\/', TokenType.DIVIDE),
        TokenMatcher(r'\(', TokenType.LEFT_PARENTHESIS),
        TokenMatcher(r'\)', TokenType.RIGHT_PARENTHESIS),
        TokenMatcher(r'\{', TokenType.LEFT_BRACKET),
        TokenMatcher(r'\}', TokenType.RIGHT_BRACKET),
        TokenMatcher(r'(let) ', TokenType.LET),
        TokenMatcher(r'(fun) ', TokenType.FUN),
        TokenMatcher(r'(if)[^\w]', TokenType.IF),
        TokenMatcher(r'(else)[^\w]', TokenType.ELSE),
        TokenMatcher(r'(while)[^\w]', TokenType.WHILE),
        TokenMatcher(r'(null)[^\w]', TokenType.NULL),
        TokenMatcher(r'(true)[^\w]', TokenType.TRUE),
        TokenMatcher(r'(false)[^\w]', TokenType.FALSE),
        TokenMatcher(r'(return)[^\w]', TokenType.RETURN),
        TokenMatcher(r'>=', TokenType.GREATER_EQUAL),
        TokenMatcher(r'<=', TokenType.LOWER_EQUAL),
        TokenMatcher(r'>', TokenType.GREATER),
        TokenMatcher(r'<', TokenType.LOWER),
        TokenMatcher(r'==', TokenType.EQUAL_EQUAL),
        TokenMatcher(r'=', TokenType.EQUAL),
        TokenMatcher(r'[a-zA-Z_][\w\d_]*', TokenType.IDENTIFIER),
        TokenMatcher(r'\.', TokenType.DOT),
        TokenMatcher(r',', TokenType.COMMA),
        TokenMatcher(r';', TokenType.SEMICOLON),
        TokenMatcher(r'\n|\r|\n\r', TokenType.LINEBREAK)
    ]

    tokenizer = Tokenizer(matches)

    with open('test/program.txt', 'r') as file:
        program = file.read()

    tokens = tokenizer.analyze(program)

    parser = Parser(tokens)
    result = (parser.parse())
    # print(result)
    interpreter = Interpreter()
    interpreter.interpret(result)
