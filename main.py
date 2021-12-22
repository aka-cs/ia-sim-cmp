from tokenizer.tokenizer import Tokenizer
from _parser import Parser
from interpreter import Interpreter
from token_matchers import matches

if __name__ == '__main__':

    tokenizer = Tokenizer(matches)

    with open('test/program.kt', 'r') as file:
        program = file.read()

    tokens = tokenizer.tokenize(program)

    parser = Parser(tokens)
    result = (parser.parse())
    # print(result)
    interpreter = Interpreter()
    interpreter.interpret(result)
