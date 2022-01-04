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
        return self.lines
    
    @visitor(Literal)
    def eval(self, literal: Literal):
        return str(literal.value)
    
    @visitor(ArrayNode)
    def eval(self, expression: ArrayNode):
        result = []
        for elem in expression.expressions:
            result.append(elem.eval(self))
        return '[' + ', '.join(result) + ']'
    
    @visitor(Index)
    def eval(self, expression: Index):
        left = expression.expression.eval(self)
        index = expression.index.eval(self)
        return f'{left}[{index}]'
    
    @visitor(Grouping)
    def eval(self, grouping: Grouping):
        return f'({grouping.expression.eval(self)})'
    
    @visitor(Unary)
    def eval(self, unary: Unary):
        right = unary.right.eval(self)
        if unary.operator.type == TokenType.MINUS:
            return f'-{right}'
        elif unary.operator.type == TokenType.EXCLAMATION:
            return f'not {right}'
        return ''
    
    @visitor(Binary)
    def eval(self, binary: Binary):
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
    def eval(self, variable: Variable):
        return variable.name.text
    
    @visitor(VarDeclaration)
    def eval(self, declaration: VarDeclaration, tabs: int = 0):
        tabs_str = '\t' * tabs
        self.lines.append(f"{tabs_str}{declaration.name.text} = {declaration.expression.eval(self)}")
    
    @visitor(Assignment)
    def eval(self, assignment: Assignment, tabs: int = 0):
        tabs_str = '\t' * tabs
        self.lines.append(f"{tabs_str}{assignment.var_name.text} = {assignment.value.eval(self)}")
        # self.scope.assign(assignment.var_name.text, assignment.value.eval(self))
    
    @visitor(ExpressionStatement)
    def eval(self, expression: ExpressionStatement, tabs: int = 0):
        return expression.expression.eval(self, tabs=tabs)
    
    @visitor(Call)
    def eval(self, expression: Call, tabs=0):
        tabs_str = '\t' * tabs
        called = expression.called.eval(self)
        arguments = []
        for arg in expression.arguments:
            arguments.append(arg.eval(self))
        if tabs > 0:
            self.lines.append(f'{tabs_str}{called}({", ".join(arguments)})')
        else:
            return f'{called}({", ".join(arguments)})'
    
    @visitor(FunctionNode)
    def eval(self, expression: FunctionNode, tabs: int = 0):
        params = map(lambda x: x[0].text, expression.params)
        self.lines.append(f'def {expression.name.text}({", ".join(params)}):')
        self.eval_block(expression.body, tabs + 1)
        # self.scope.declare(expression.name.text, UserDefinedFunction(expression))
    
    @visitor(Return)
    def eval(self, expression: Return, tabs=0):
        tabs_str = '\t' * tabs
        value = None
        if expression.expression:
            value = expression.expression.eval(self)
        self.lines.append(f'{tabs_str}return {value}')
    
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
