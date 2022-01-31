from pathlib import Path

from interpreter.transpiler import Transpiler
from interpreter.builtin import get_code
from regex.regex_ import RegParser
from tokenizer.tokenizer import Tokenizer
from _parser import Parser
from interpreter import TypeChecker
from token_matchers import matches
from errors import *

if __name__ == '__main__':

    reg_parser = RegParser(path='binaries/reg_parser')

    tokenizer = Tokenizer(matches, path='binaries/tokenizer')

    with open('test/program.kt', 'r') as file:
        program = file.read()

    tokens = tokenizer.tokenize(program)

    parser = Parser(Path('binaries/grammar_parser').resolve())

    try:
        ast = parser.parse(tokens)
    except UnexpectedToken as e:
        print(f"Unexpected token found \"{tokens[e.index].text}\"", file=stderr)
        print_code_error(program, tokens[e.index])
        exit(1)

    checker = TypeChecker()
    transpiler = Transpiler()

    try:
        checker.start(ast)
    except MissingMainError:
        print(f"Program must define a main function", file=stderr)
        exit(1)
    except InvalidMain as e:
        print(f"Main function must have void return type and no arguments", file=stderr)
        print_code_line(program, e.main.line)
        exit(1)
    except InvalidTypeError as e:
        print(e.message, file=stderr)
        print_code_line(program, e.line)
        exit(1)
    except InvalidOperation as e:
        print(e.message, file=stderr)
        print_code_error(program, e.token)
        exit(1)
    except TypeNotDefined as e:
        print(e.message, file=stderr)
        print_code_error(program, e.token)
        exit(1)
    except InvalidMethodDeclaration as e:
        print(e.message, file=stderr)
        print_code_line(program, e.line)
        exit(1)
    except InvalidCall as e:
        print(e.message, file=stderr)
        print_code_line(program, e.line)
        exit(1)

    python_code = ["from builtin_code import *\n\n", *transpiler.transpile(ast)]
    with open('out/program.py', 'w') as f:
        f.write('\n'.join(python_code))

    with open('out/builtin_code.py', 'w') as f:
        for line in get_code("interpreter/builtin_code.py"):
            f.write(line)
