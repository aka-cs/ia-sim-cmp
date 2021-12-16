from dataclasses import dataclass
from .expression import Expression
from tokenizer.token_ import Token


class Statement:
    def eval(self, interpreter):
        return interpreter.eval(self)


@dataclass
class VarDeclaration(Statement):
    name: Token
    expression: Expression


@dataclass
class ExpressionStatement(Statement):
    expression: Expression
