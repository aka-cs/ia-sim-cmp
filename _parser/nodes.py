from dataclasses import dataclass
from tokenizer.token_ import Token
from typing import Optional


class Node:
    def exec(self, interpreter):
        return interpreter.exec(self)

    def check(self, checker):
        return checker.check(self)
    
    def eval(self, transpiler, **kwargs):
        return transpiler.eval(self, **kwargs)


@dataclass
class Assignment(Node):
    var_name: Token
    value: Node


@dataclass
class ArrayNode(Node):
    expressions: [Node]


@dataclass
class Index(Node):
    expression: Node
    index: Node


@dataclass
class VarType(Node):
    type: Token
    nested: Optional['VarType'] = None


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
    type: VarType
    expression: Node


@dataclass
class ExpressionStatement(Node):
    expression: Node


@dataclass
class FunctionNode(Node):
    name: Token
    params: [(Token, VarType)]
    return_type: VarType
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


@dataclass
class GetNode(Node):
    left: Node
    right: Token


@dataclass
class Statement(Node):
    code: Node
