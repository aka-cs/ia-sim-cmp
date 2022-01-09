from pathlib import Path

from interpreter.transpiler import Transpiler
from interpreter.builtin import get_classes_code, get_functions_code
from regex.regex_ import RegParser
from tokenizer.tokenizer import Tokenizer
from _parser import Parser
from interpreter import Interpreter, TypeChecker
from token_matchers import matches

if __name__ == '__main__':

    reg_parser = RegParser(path='binaries/reg_parser')

    tokenizer = Tokenizer(matches, path='binaries/tokenizer')

    with open('test/program.kt', 'r') as file:
        program = file.read()

    tokens = tokenizer.tokenize(program)

    parser = Parser(Path('binaries/grammar_parser').resolve())

    ast = parser.parse(tokens)
    interpreter = Interpreter()
    checker = TypeChecker()
    transpiler = Transpiler()

    checker.start(ast)
    # interpreter.interpret(ast)
    python_code = ["from builtin_code import *\n\n", *transpiler.transpile(ast)]
    with open('out/program.py', 'w') as f:
        f.write('\n'.join(python_code))

    with open('out/builtin_code.py', 'w') as f:
        for lines, _ in get_classes_code():
            f.write("".join(lines))
            f.write("\n")
        for lines, _ in get_functions_code():
            f.write("".join(lines))
            f.write("\n")
