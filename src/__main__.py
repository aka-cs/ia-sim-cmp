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
    
    src_path = Path(__file__).parent.parent
    
    if os.getenv("FILE"):
        path = Path('run') / os.getenv("FILE")
    else:
        if len(sys.argv) > 1:
            path = Path(sys.argv[1])
            if not path.is_file():
                print(f"File \"{sys.argv[1]}\" not found", file=stderr)
                exit(1)
        else:
            path = src_path / Path('run/program.kt')
        
    if not path.exists():
        print(f"File \"{path}\" not found", file=stderr)
        exit(1)

    reg_parser = RegParser(path=src_path / 'binaries/reg_parser')

    tokenizer = Tokenizer(matches, path=src_path / 'binaries/tokenizer')

    with open(path, 'r') as f:
        program = f.read()

    tokens = tokenizer.tokenize(program)

    parser = Parser(Path(src_path / 'binaries/grammar_parser').resolve())

    error = Error(program)
    ast = None
    try:
        ast = parser.parse(tokens)
    except UnexpectedToken as e:
        error(f"Unexpected token found \"{tokens[e.index].text}\"", token=tokens[e.index])

    checker = TypeChecker(error)
    transpiler = Transpiler()

    checker.start(ast)

    if os.path.exists(src_path / "out"):
        shutil.rmtree(src_path / "out")
    os.makedirs(src_path / "out", exist_ok=True)
    code = get_code()

    python_code = [f"from builtin import *", '\n', *transpiler.transpile(ast)]
    with open(src_path / 'out/__main__.py', 'w') as f:
        f.write('\n'.join(python_code))

    os.makedirs(src_path / "out/builtin", exist_ok=True)
    for file in code:
        with open(src_path / f'out/builtin/{file.name}', 'w') as f:
            for line in code[file]:
                f.write(line)
