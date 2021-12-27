from dataclasses import dataclass
from tokenizer.token_ import Token


class Node:
    def eval(self, interpreter):
        return interpreter.eval(self)

    def check(self, checker):
        return checker.check(self)


@dataclass
class Assignment(Node):
    var_name: Token
    value: Node


@dataclass
class Binary(Node):
    left: Node
    operator: Token
    right: Node


@dataclass
class Unary(Node):
    operator: Token
    right: Node


@dataclass
class Grouping(Node):
    expression: Node


@dataclass
class Call(Node):
    called: Node
    arguments: [Node]


@dataclass
class Literal(Node):
    value: object


@dataclass
class Variable(Node):
    name: Token


@dataclass
class VarDeclaration(Node):
    name: Token
    type: Token
    expression: Node


@dataclass
class ExpressionStatement(Node):
    expression: Node


@dataclass
class Function(Node):
    name: Token
    params: [(Token, Token)]
    return_type: Token
    body: [Node]


@dataclass
class Return(Node):
    expression: Node


@dataclass
class If(Node):
    condition: Node
    code: [Node]
    else_code: [Node]


@dataclass
class While(Node):
    condition: Node
    code: [Node]
