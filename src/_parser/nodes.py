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
class ArrayNode(Node):
    start: Token
    expressions: [Node]


@dataclass
class DictionaryNode(Node):
    start: Token
    keys: [Node]
    values: [Node]


@dataclass
class Index(Node):
    expression: Node
    index: Node


@dataclass
class VarType(Node):
    type: Token
    nested: Optional['VarType'] = None
    s_nested: Optional['VarType'] = None


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
    line: int


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
    start: Token
    expression: Node


@dataclass
class If(Node):
    start: Token
    condition: Node
    code: [Node]
    else_code: [Node]


@dataclass
class While(Node):
    start: Token
    condition: Node
    code: [Node]


@dataclass
class GetNode(Node):
    left: Node
    right: Token


@dataclass
class Statement(Node):
    code: Node


@dataclass
class ClassNode(Node):
    name: Token
    superclass: Token
    methods: [FunctionNode]


@dataclass
class Assignment(Node):
    left: Variable | GetNode
    value: Node
    line: int


@dataclass
class SelfNode(Node):
    token: Token


@dataclass
class SuperNode(Node):
    token: Token


@dataclass
class BreakNode(Node):
    token: Token


@dataclass
class ContinueNode(Node):
    token: Token


@dataclass
class AttrDeclaration(Node):
    name: Token
    type: VarType
    expression: Node


@dataclass
class SwitchNode(Node):
    variable: Token
    switch_cases: {Token: [Node]}
    default: [Node]


@dataclass
class CommentNode(Node):
    text: str


@dataclass
class ForNode(Node):
    start: Token
    variable: Token
    iterable: Node
    statements: [Node]
