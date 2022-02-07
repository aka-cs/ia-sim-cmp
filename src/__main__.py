import os
import shutil
import sys

from pathlib import Path

from transpiler.transpiler import Transpiler
from builtin.builtin import get_code
from regex.regex_ import RegParser
from tokenizer.tokenizer import Tokenizer
from _parser import Parser
from checker import TypeChecker
from tokenizer.token_matchers import matches
from errors import UnexpectedToken, Error
from sys import stderr


if __name__ == '__main__':

    if len(sys.argv) > 1:
        if not Path(sys.argv[1]).is_file():
            print(f"File \"{sys.argv[1]}\" not found", file=stderr)
            exit(1)
        path = sys.argv[1]
    else:
        path = 'src/test/program.kt'

    reg_parser = RegParser(path='binaries/reg_parser')

    tokenizer = Tokenizer(matches, path='binaries/tokenizer')

    with open(path, 'r') as f:
        program = f.read()

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

    if os.path.exists("out"):
        shutil.rmtree("out")
    os.makedirs("out", exist_ok=True)
    code = get_code()

    python_code = [f"from builtin import *", '\n', *transpiler.transpile(ast)]
    with open('out/__main__.py', 'w') as f:
        f.write('\n'.join(python_code))

    os.makedirs("out/builtin", exist_ok=True)
    for file in code:
        with open(f'out/builtin/{file.name}', 'w') as f:
            for line in code[file]:
                f.write(line)
