from sys import stderr

from .parsing import UnexpectedToken
from .static_checks import *


def print_code_error(code: str, token):
    print_code_line(code, token.line)
    spaces = " " * (1 + len(str(token.line)) + token.column)
    pointer = "^" * len(token.text)
    print(f"{spaces}{pointer}", file=stderr)


def print_code_line(code: str, line: int):
    code_line = code.split('\n')[line - 1]
    print(f"{line}|{code_line}", file=stderr)
