from tokenizer import Tokenizer, TokenMatcher, TokenType

if __name__ == '__main__':

    matches = [
        TokenMatcher(r'-?\d+(?:\.\d+)?', TokenType.number),
        TokenMatcher(r'"[^"]+"', TokenType.string),
        TokenMatcher(r'\+', TokenType.plus),
        TokenMatcher(r'\-', TokenType.minus),
        TokenMatcher(r'\*', TokenType.multiply),
        TokenMatcher(r'\/', TokenType.divide),
        TokenMatcher(r'\(', TokenType.left_parenthesis),
        TokenMatcher(r'\)', TokenType.right_parenthesis),
        TokenMatcher(r'\{', TokenType.left_bracket),
        TokenMatcher(r'\}', TokenType.right_bracket),
        TokenMatcher(r'let', TokenType.let),
        TokenMatcher(r'fun', TokenType.fun),
        TokenMatcher(r'if', TokenType.if_),
        TokenMatcher(r'else', TokenType.else_),
        TokenMatcher(r'while', TokenType.while_),
        TokenMatcher(r'>', TokenType.gt),
        TokenMatcher(r'<', TokenType.lw),
        TokenMatcher(r'>=', TokenType.gte),
        TokenMatcher(r'<=', TokenType.lwe),
        TokenMatcher(r'\w[\w\d_]+', TokenType.literal),
        TokenMatcher(r';', TokenType.colon),
        TokenMatcher(r',', TokenType.coma)
    ]

    tokenizer = Tokenizer(matches)

    with open('test/program.txt', 'r') as file:
        program = file.read()

    print('\n'.join(map(str, tokenizer.analyze(program))))
