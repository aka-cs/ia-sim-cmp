from tools import Singleton, visitor
from builtin.scope import Scope
from _parser.nodes import *
from tokenizer.token_type import TokenType
from builtin._types import Float, Int, String, Boolean, Null, TypeList, Object, TypeDict, Type
from builtin.functions import Function
from builtin.builtin import builtin_functions, builtin_classes
from builtin.classes import Class
from errors import Error


class TypeChecker(metaclass=Singleton):

    def __init__(self, error: Error):
        self.error = error
        self.globals = Scope()
        self.scope = self.globals
        self.types = [Object, Float, Int, String, Boolean, *builtin_classes]
        self.current_function: Function | None = None
        self.current_class: Class | None = None
        self.current_loops = 0
        for fun in builtin_functions:
            self.scope.declare(fun.name, Function(fun.name, fun.param_types, fun.return_type))
        for cls in builtin_classes:
            self.scope.declare(cls.name, cls.get_constructor())

    def start(self, expressions: [Node]):
        self.check_classes_in_scope(expressions)
        self.check_functions_in_scope(self.scope, expressions)
        if "main" not in self.scope.variables:
            self.error("Program must contain a main method")
        main: Function = self.scope.get("main")
        if len(main.param_types) != 0 or not issubclass(main.return_type, Null):
            self.error("Main method must receive no arguments and return void", line=main.line)
        for expression in expressions:
            expression.check(self)
        return

    @visitor(Statement)
    def check(self, expression: Statement):
        return expression.code.check(self)

    @visitor(ContinueNode)
    def check(self, expression: ContinueNode):
        if self.current_loops <= 0:
            self.error("continue must be inside a for or while loop body", token=expression.token)

    @visitor(BreakNode)
    def check(self, expression: BreakNode):
        if self.current_loops <= 0:
            self.error("break must be inside a for or while loop body", token=expression.token)

    @visitor(Literal)
    def check(self, expression: Literal):
        if isinstance(expression.value, bool):
            return Boolean
        if isinstance(expression.value, float):
            return Float
        if isinstance(expression.value, int):
            return Int
        if isinstance(expression.value, str):
            return String
        if expression.value is None:
            return Null
        return None

    @visitor(ForNode)
    def check(self, expression: ForNode):
        scope = Scope(self.scope)
        iterable = expression.iterable.check(self)
        if isinstance(iterable, TypeDict):
            scope.declare(expression.variable.text, iterable.key_type)
        elif isinstance(iterable, TypeList):
            scope.declare(expression.variable.text, iterable.list_type)
        else:
            self.error("For can only iterate over a list or a dictionary", line=expression.start.line)
        self.current_loops += 1
        self.check_block(expression.statements, scope)
        self.current_loops -= 1

    @visitor(ArrayNode)
    def check(self, expression: ArrayNode):
        result = [elem.check(self) for elem in expression.expressions]
        list_type = self.common_type(result)
        return TypeList(list_type)

    @visitor(DictionaryNode)
    def check(self, expression: DictionaryNode):
        keys = [elem.check(self) for elem in expression.keys]
        values = [elem.check(self) for elem in expression.values]
        keys_types = self.common_type(keys)
        values_types = self.common_type(values)
        if keys_types is None or values_types is None:
            return TypeDict((keys_types, values_types))
        if issubclass(Object, keys_types):
            self.error("Dictionary keys are not of the same type", line=expression.start.line)
        if not issubclass(keys_types, Float) and not issubclass(keys_types, String):
            self.error("Dictionary keys are not immutable", line=expression.start.line)
        return TypeDict((keys_types, values_types))

    @visitor(Index)
    def check(self, expression: Index):
        left = expression.expression.check(self)
        index = expression.index.check(self)
        return left[index]

    @visitor(Grouping)
    def check(self, expression: Grouping):
        return expression.expression.check(self)

    @visitor(Unary)
    def check(self, expression: Unary):
        right = expression.right.check(self)
        if expression.operator.type == TokenType.MINUS:
            return -right
        elif expression.operator.type == TokenType.EXCLAMATION:
            if not issubclass(right, Boolean):
                self.error(f"Operator ! not supported for {right}", token=expression.operator)
            return Boolean
        return None

    @visitor(Binary)
    def check(self, expression: Binary):
        left = expression.left.check(self)
        right = expression.right.check(self)
        try:
            if expression.operator.type == TokenType.EQUAL_EQUAL:
                return left == right
            if expression.operator.type == TokenType.EQUAL_DIFFERENT:
                return left != right
            if expression.operator.type in [TokenType.AND, TokenType.OR]:
                if not issubclass(left, Boolean) or not issubclass(right, Boolean):
                    self.error(f"Operator not supported for types {left} and {right}", token=expression.operator)
                return Boolean
            if expression.operator.type == TokenType.PLUS:
                return left + right
            if expression.operator.type == TokenType.MINUS:
                return left - right
            if expression.operator.type == TokenType.DIVIDE:
                return left / right
            if expression.operator.type == TokenType.MULTIPLY:
                return left * right
            if expression.operator.type == TokenType.LESS:
                return left < right
            if expression.operator.type == TokenType.LESS_EQUAL:
                return left <= right
            if expression.operator.type == TokenType.GREATER:
                return left > right
            if expression.operator.type == TokenType.GREATER_EQUAL:
                return left >= right
        except TypeError as e:
            self.error(e.args[0], token=expression.operator)
        return None

    @visitor(Variable)
    def check(self, expression: Variable):
        try:
            return self.check_scope(expression.name.text)
        except:
            self.error(f"{expression.name.text} not defined in current scope", token=expression.name)

    @visitor(VarDeclaration)
    def check(self, expression: VarDeclaration):
        expression_type = expression.expression.check(self)
        if expression.type:
            variable_type = expression.type.check(self)
            if not self.can_assign(expression_type, variable_type):
                self.error(
                    f"Variable {expression.name.text} of type {variable_type} can't be assigned {expression_type}",
                    line=expression.name.line)
            expression_type = variable_type
        else:
            if isinstance(expression_type, Function):
                self.error(
                    f"Variable {expression.name.text} can't be assigned {expression_type}", line=expression.name.line)
            if not self.can_infer(expression_type):
                self.error("Can't infer type from expression", line=expression.name.line)
        if self.scope.exists(expression.name.text):
            self.error(f"Variable {expression.name.text} already exists", line=expression.name.line)
        self.scope.declare(expression.name.text, expression_type)

    @visitor(VarType)
    def check(self, expression: VarType):
        if expression.type.text == "list":
            return TypeList(expression.nested.check(self))
        if expression.type.text == "dict":
            return TypeDict((expression.nested.check(self), expression.s_nested.check(self)))
        for t in self.types:
            if expression.type.text == str(t):
                return t
        self.error(f"Type {expression.type.text} is not defined in current scope", token=expression.type)

    @visitor(Assignment)
    def check(self, expression: Assignment):
        expression_type = expression.value.check(self)
        left_type = expression.left.check(self)
        if not self.can_assign(expression_type, left_type):
            self.error(
                f"Can't assign {expression_type} to {left_type} object", line=expression.line)

    @visitor(ExpressionStatement)
    def check(self, expression: ExpressionStatement):
        return expression.expression.check(self)

    @visitor(Call)
    def check(self, expression: Call):
        called: Function = expression.called.check(self)
        if not isinstance(called, Function):
            self.error(f"Calls must be made to functions and methods", line=expression.line)
        if len(expression.arguments) != len(called.param_types):
            self.error("Invalid number of arguments", line=expression.line)
        for arg, param in zip(expression.arguments, called.param_types):
            arg_type = arg.check(self)
            if param is Type and isinstance(arg_type, Function):
                continue
            if not self.can_assign(arg_type, param):
                self.error(f"Function with argument type {param} can't receive {arg_type}", line=expression.line)
        return called.return_type

    @visitor(FunctionNode)
    def check(self, expression: FunctionNode):
        if self.current_class and expression.name.text == "init":
            if not issubclass(Object, self.current_class.__bases__[0]):
                line = None
                for statement in expression.body:
                    if not isinstance(statement.code, CommentNode):
                        line = statement.code
                        break
                if not expression.body or not isinstance(line, Call):
                    self.error("init method must call super's init in first statement", line=expression.name.line)
                if not isinstance(line.called, GetNode):
                    self.error("init method must call super's init in first statement", line=expression.name.line)
                if not isinstance(line.called.left, SuperNode) or line.called.right.text != "init":
                    self.error("init method must call super's init in first statement", line=expression.name.line)
        scope = Scope(self.globals)
        for param in expression.params:
            scope.declare(param[0].text, param[1].check(self))
        self.current_function = self.check_scope(expression.name.text)
        self.check_block(expression.body, scope)
        if not issubclass(self.current_function.return_type, Null) and not self.check_return_paths(expression.body):
            self.error("All code paths don't return a value", line=expression.name.line)
        self.current_function = None

    @visitor(Return)
    def check(self, expression: Return):
        if not self.current_function:
            self.error("return statement should be inside a function", token=expression.start)
        if expression.expression:
            return_type = expression.expression.check(self)
        else:
            return_type = Null
        expected = self.current_function.return_type
        if not self.can_assign(return_type, expected):
            self.error(
                f"Function expects {expected} return type, got {return_type} instead", line=expression.start.line)

    @visitor(If)
    def check(self, expression: If):
        if not issubclass(expression.condition.check(self), Boolean):
            self.error(f"if condition is not a boolean value", line=expression.start.line)
        self.check_block(expression.code, Scope(self.scope))
        self.check_block(expression.else_code, Scope(self.scope))

    @visitor(While)
    def check(self, expression: While):
        if not issubclass(expression.condition.check(self), Boolean):
            self.error(f"while condition is not a boolean value", line=expression.start.line)
        self.current_loops += 1
        self.check_block(expression.code, Scope(self.scope))
        self.current_loops -= 1

    @visitor(ClassNode)
    def check(self, expression: ClassNode):
        created = self.get_class(expression.name)
        self.current_class = created
        expression.methods.sort(key=lambda x: {"init": 0}.get(x.name.text, 1))
        self.check_block(expression.methods, created.scope)
        self.current_class = None

    @visitor(SelfNode)
    def check(self, expression: SelfNode):
        if not self.current_class:
            self.error("self must be contained in a class", token=expression.token)
        return self.current_class

    @visitor(SuperNode)
    def check(self, expression: SuperNode):
        if not self.current_class:
            self.error("super must be contained in a class", token=expression.token)
        return self.current_class.__bases__[0]

    @visitor(GetNode)
    def check(self, expression: GetNode):
        left: Class = expression.left.check(self)
        try:
            return left.getattr(expression.right.text)
        except AttributeError as e:
            self.error(e.args[0], line=expression.right.line)

    @visitor(AttrDeclaration)
    def check(self, expression: AttrDeclaration):
        if not self.current_class:
            self.error("Attributes can only be created inside classes", line=expression.name.line)
        if self.current_function.name != "init":
            self.error("Attributes can only be declared in init class method", line=expression.name.line)
        expression_type = expression.expression.check(self)
        if expression.type:
            attr_type = expression.type.check(self)
            if not self.can_assign(expression_type, attr_type):
                self.error(
                    f"Attribute {expression.name.text} of type {expression.type.type.text} can't be assigned {expression_type}",
                    line=expression.name.line)
            expression_type = attr_type
        else:
            if not self.can_infer(expression_type):
                self.error("Can't infer type from expression", line=expression.name.line)
        self.current_class.scope.declare(expression.name.text, expression_type)

    @visitor(SwitchNode)
    def check(self, expression: SwitchNode):
        var = expression.variable.text
        var_type = self.scope.get(var)
        for _case in expression.switch_cases:
            c_type = self.get_class(_case)
            if not isinstance(c_type, Class):
                self.error(f"Can't cast to type {c_type}", line=_case.line)
            if not self.can_assign(var_type, c_type) and not self.can_assign(c_type, var_type):
                self.error(f"Can't cast {var_type} to {c_type}", line=_case.line)
            scope = Scope(self.scope)
            scope.declare(var, c_type)
            self.check_block(expression.switch_cases[_case], scope)
        self.check_block(expression.default, self.scope)
        
    @visitor(CommentNode)
    def check(self, expression: CommentNode):
        pass

    def check_block(self, statements, scope: Scope):
        previous = self.scope
        try:
            self.scope = scope
            for statement in statements:
                self.check(statement)
        finally:
            self.scope = previous

    def check_functions_in_scope(self, scope: Scope, nodes: [Node]):
        for _node in nodes:
            node = _node
            if isinstance(_node, Statement):
                node = _node.code
            if isinstance(node, FunctionNode):
                params = []
                for param in node.params:
                    params.append(param[1].check(self))
                if node.return_type.type.text == "void" and not node.return_type.nested:
                    return_type = Null
                else:
                    return_type = node.return_type.check(self)
                scope.declare(node.name.text, Function(node.name.text, params, return_type, node.name.line))

    def check_classes_in_scope(self, nodes: [Node]):
        for _node in nodes:
            node = _node
            if isinstance(_node, Statement):
                node = _node.code
            if isinstance(node, ClassNode):
                scope = Scope(self.scope)
                if node.superclass:
                    super_class = self.get_class(node.superclass)
                else:
                    super_class = None
                created = Class(node.name.text, super_class, scope)
                self.types.append(created)
        for _node in nodes:
            node = _node
            if isinstance(_node, Statement):
                node = _node.code
            if isinstance(node, ClassNode):
                c_class = self.get_class(node.name)
                self.check_functions_in_scope(c_class.scope, node.methods)
                self.check_class_inheritance(c_class)
                params = []
                try:
                    init = c_class.getattr("init")
                    if not issubclass(init.return_type, Null):
                        self.error("init method must have void return type", line=init.line)
                    params = init.param_types
                except TypeError:
                    pass
                self.scope.declare(node.name.text, Function(c_class.name, params, c_class))

    def get_class(self, name: Token):
        for t in self.types:
            if str(t) == name.text:
                return t
        self.error(f"Class {name.text} not defined in scope", line=name.line)

    def check_scope(self, name: str):
        try:
            return self.scope.get(name)
        except:
            return self.globals.get(name)

    def check_class_inheritance(self, cls):
        if not isinstance(cls.__base__, Class):
            return
        for member in cls.scope.variables:
            current = cls.scope.variables[member]
            if isinstance(current, Function):
                try:
                    function = cls.scope.father.get(member)
                except:
                    continue
                if current.name == "init":
                    continue
                if len(function.param_types) != len(current.param_types):
                    self.error("Function must have same number of arguments as in parent class", line=current.line)
                for i, j in zip(current.param_types, function.param_types):
                    if not self.can_assign(j, i):
                        self.error(f"Parameter in {member} defined in parent class as {j} "
                                   f"type, can't be of type {i} in class {cls}", line=current.line)
                if not self.can_assign(current.return_type, function.return_type):
                    self.error(
                        f"Return type defined in parent class as {function.return_type} type, not {current.return_type}",
                        line=current.line)
            else:
                try:
                    variable = cls.scope.father.get(member)
                except:
                    continue
                if not TypeChecker.can_assign(current, variable):
                    self.error(f"Variable {member} defined in parent class as {variable} type, not {current}",
                               line=member.line)

    @staticmethod
    def check_return_paths(body: [Node]):
        for node in body:
            if isinstance(node.code, Return):
                return True
            if isinstance(node.code, If):
                if TypeChecker.check_return_paths(node.code.code) and TypeChecker.check_return_paths(
                        node.code.else_code):
                    return True
        return False

    def can_assign(self, type1, type2):
        if isinstance(type1, Function) or isinstance(type2, Function):
            return False
        if isinstance(type1, TypeList) and isinstance(type2, TypeList):
            if type1.list_type is None:
                return True
            if type2.list_type is None:
                return False
            return self.can_assign(type1.list_type, type2.list_type)
        if isinstance(type1, TypeDict) and isinstance(type2, TypeDict):
            if type1.key_type is None:
                return True
            if type2.key_type is None:
                return False
            return self.can_assign(type1.key_type, type2.key_type) and \
                   self.can_assign(type1.value_type, type2.value_type)
        if issubclass(type1, Null) and isinstance(type2, Class):
            return True
        return issubclass(type1, type2)
    
    def can_infer(self, type: Type):
        if type is None or issubclass(type, Null):
            return False
        if isinstance(type, TypeList):
            return self.can_infer(type.list_type)
        if isinstance(type, TypeDict):
            return self.can_infer(type.key_type) and self.can_infer(type.value_type)
        return True

    def common_type(self, types):
        if not types:
            return None
        _type = types[0]
        for elem in types:
            if self.can_assign(elem, _type):
                continue
            elif self.can_assign(_type, elem):
                _type = elem
            else:
                while not issubclass(Object, elem):
                    if self.can_assign(_type, elem):
                        break
                    elem = elem.__base__
                _type = elem
        return _type
