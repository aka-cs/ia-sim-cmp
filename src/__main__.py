import os

from pathlib import Path

from transpiler.transpiler import Transpiler
from builtin.builtin import get_code
from regex.regex_ import RegParser
from tokenizer.tokenizer import Tokenizer
from _parser import Parser
from checker import TypeChecker
from token_matchers import matches
from errors import UnexpectedToken, Error

if __name__ == '__main__':

    reg_parser = RegParser(path='binaries/reg_parser')

    tokenizer = Tokenizer(matches, path='binaries/tokenizer')

    with open('src/test/program.kt', 'r') as file:
        program = file.read()

    tokens = tokenizer.tokenize(program)

    parser = Parser(Path('binaries/grammar_parser').resolve())

    error = Error(program)
    ast = None
    try:
        ast = parser.parse(tokens)
    except UnexpectedToken as e:
        error(f"Unexpected token found \"{tokens[e.index].text}\"", token=tokens[e.index])

    checker = TypeChecker(error)
    transpiler = Transpiler()

    checker.start(ast)

    os.makedirs("out", exist_ok=True)
    code = get_code()

    python_code = [*[f"from {file.stem} import *" for file in code], '\n', *transpiler.transpile(ast)]
    with open('out/program.py', 'w') as f:
        f.write('\n'.join(python_code))

    for file in code:
        with open(f'out/{file.name}', 'w') as f:
            for line in code[file]:
                f.write(line)
