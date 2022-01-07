from _parser.nodes import *
from tokenizer.token_type import TokenType
from tools import visitor
from .functions import UserDefinedFunction, ReturnCall
from .scope import Scope
from .builtin import builtin_functions
from ._types import Float, Int, String, Bool, Null, Array


class Transpiler:

    def __init__(self):
        self.lines: [str] = []
        self.globals: Scope = Scope()
        self.scope: Scope = self.globals
        for fun in builtin_functions:
            self.globals.declare(fun.name, fun)

    def transpile(self, expressions: [Node]):
        self.lines = []
        for expression in expressions:
            expression.eval(self)
            self.lines.append('')
        self.lines.append("if __name__ == '__main__':\n\tmain()")
        return self.lines

    @visitor(Statement)
    def eval(self, statement: Statement, tabs: int = 0):
        tabs_str = '\t' * tabs
        result = statement.code.eval(self, tabs=tabs)
        if result:
            self.lines.append(f"{tabs_str}{result}")

    @visitor(Literal)
    def eval(self, literal: Literal, tabs: int = 0):
        return str(literal.value)

    @visitor(ArrayNode)
    def eval(self, expression: ArrayNode, tabs: int = 0):
        result = []
        for elem in expression.expressions:
            result.append(elem.eval(self))
        return '[' + ', '.join(result) + ']'

    @visitor(Index)
    def eval(self, expression: Index, tabs: int = 0):
        left = expression.expression.eval(self)
        index = expression.index.eval(self)
        return f'{left}[{index}]'

    @visitor(Grouping)
    def eval(self, grouping: Grouping, tabs: int = 0):
        return f'({grouping.expression.eval(self)})'

    @visitor(Unary)
    def eval(self, unary: Unary, tabs: int = 0):
        right = unary.right.eval(self)
        if unary.operator.type == TokenType.MINUS:
            return f'-{right}'
        elif unary.operator.type == TokenType.EXCLAMATION:
            return f'not {right}'
        return ''

    @visitor(Binary)
    def eval(self, binary: Binary, tabs: int = 0):
        left = binary.left.eval(self)
        right = binary.right.eval(self)
        if binary.operator.type == TokenType.MINUS:
            return f'{left} - {right}'
        if binary.operator.type == TokenType.PLUS:
            return f'{left} + {right}'
        if binary.operator.type == TokenType.DIVIDE:
            return f'{left} / {right}'
        if binary.operator.type == TokenType.MULTIPLY:
            return f'{left} * {right}'
        if binary.operator.type == TokenType.EQUAL_EQUAL:
            return f'{left} == {right}'
        if binary.operator.type == TokenType.EQUAL_DIFFERENT:
            return f'{left} != {right}'
        if binary.operator.type == TokenType.LESS:
            return f'{left} < {right}'
        if binary.operator.type == TokenType.LESS_EQUAL:
            return f'{left} <= {right}'
        if binary.operator.type == TokenType.GREATER:
            return f'{left} > {right}'
        if binary.operator.type == TokenType.GREATER_EQUAL:
            return f'{left} >= {right}'
        if binary.operator.type == TokenType.AND:
            return f'{left} and {right}'
        if binary.operator.type == TokenType.OR:
            return f'{left} or {right}'

    @visitor(Variable)
    def eval(self, variable: Variable, tabs: int = 0):
        return variable.name.text

    @visitor(VarDeclaration)
    def eval(self, declaration: VarDeclaration, tabs: int = 0):
        return f"{declaration.name.text} = {declaration.expression.eval(self)}"

    @visitor(Assignment)
    def eval(self, assignment: Assignment, tabs: int = 0):
        return f"{assignment.left.eval(self)} = {assignment.value.eval(self)}"

    @visitor(ExpressionStatement)
    def eval(self, expression: ExpressionStatement, tabs: int = 0):
        return expression.expression.eval(self, tabs=tabs)

    @visitor(Call)
    def eval(self, expression: Call, tabs: int = 0):
        called: str = expression.called.eval(self)
        if called.endswith("init"):
            called = called[:-4] + "__init__"
        arguments = []
        for arg in expression.arguments:
            arguments.append(arg.eval(self))
        return f'{called}({", ".join(arguments)})'

    @visitor(GetNode)
    def eval(self, expression: GetNode, tabs: int = 0):
        return f'{expression.left.eval(self)}.{expression.right.text}'

    @visitor(ClassNode)
    def eval(self, expression: ClassNode, tabs: int = 0):
        text = f"class {expression.name.text}:\n"
        if expression.superclass:
            text = f"class {expression.name.text}({expression.superclass.text}):\n"
        if not expression.methods:
            text += "\tpass\n"
            return text
        self.lines.append(text)
        for method in expression.methods:
            method.eval(self, tabs=tabs + 1)

    @visitor(SelfNode)
    def eval(self, expression: SelfNode, tabs: int = 0):
        return "self"

    @visitor(SuperNode)
    def eval(self, expression: SuperNode, tabs: int = 0):
        return "super()"

    @visitor(AttrDeclaration)
    def eval(self, expression: AttrDeclaration, tabs: int = 0):
        return f"self.{expression.name.text} = {expression.expression.eval(self)}"

    @visitor(FunctionNode)
    def eval(self, expression: FunctionNode, tabs: int = 0):
        params = map(lambda x: x[0].text, expression.params)
        tabs_str = '\t' * tabs
        function_name = expression.name.text
        if tabs > 0:
            params = ["self", *list(params)]
            if expression.name.text == "init":
                function_name = "__init__"
        self.lines.append(f'{tabs_str}def {function_name}({", ".join(params)}):')
        self.eval_block(expression.body, tabs + 1)
        if not expression.body:
            self.lines.append(f'{tabs_str}\tpass')
        self.lines.append("")

    @visitor(Return)
    def eval(self, expression: Return, tabs=0):
        value = None
        if expression.expression:
            value = expression.expression.eval(self)
        return f'return {value}'

    @visitor(If)
    def eval(self, expression: If, tabs: int = 0):
        tabs_str = '\t' * tabs
        self.lines.append(f'{tabs_str}if {expression.condition.eval(self)}:')
        self.eval_block(expression.code, tabs + 1)
        if expression.else_code:
            self.lines.append(f'{tabs_str}else:')
            self.eval_block(expression.else_code, tabs + 1)

    @visitor(While)
    def eval(self, expression: While, tabs: int = 0):
        tabs_str = '\t' * tabs
        self.lines.append(f'{tabs_str}while {expression.condition.eval(self)}:')
        self.eval_block(expression.code, tabs + 1)

    def eval_block(self, statements, tabs: int = 0):
        for statement in statements:
            self.eval(statement, tabs=tabs)
