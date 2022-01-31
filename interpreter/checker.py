from tools import Singleton, visitor
from .scope import Scope
from _parser.nodes import *
from tokenizer.token_type import TokenType
from ._types import Float, Int, String, Boolean, Null, TypeList, Object, TypeDict, Type
from .functions import Function
from .builtin import builtin_functions, builtin_classes
from .classes import Class
from errors import *


class TypeChecker(metaclass=Singleton):

    def __init__(self):
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
        self.check_functions_in_scope(self.scope, expressions)
        if "main" not in self.scope.variables:
            raise MissingMainError()
        main: Function = self.scope.get("main")
        if len(main.param_types) != 0 or not issubclass(main.return_type, Null):
            raise InvalidMain(main)
        for expression in expressions:
            expression.check(self)
        return

    @visitor(Statement)
    def check(self, expression: Statement):
        return expression.code.check(self)

    @visitor(ContinueNode)
    def check(self, expression: ContinueNode):
        if self.current_loops <= 0:
            raise Exception("continue must be inside a for or while loop body")

    @visitor(BreakNode)
    def check(self, expression: BreakNode):
        if self.current_loops <= 0:
            raise Exception("break must be inside a for or while loop body")

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
            raise TypeError("For can only iterate over a list or a dictionary")
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
        if issubclass(Object, keys_types):
            raise InvalidTypeError("Dictionary keys are not of the same type", expression.start.line)
        if not issubclass(keys_types, Float) and not issubclass(keys_types, String):
            raise InvalidTypeError("Dictionary keys are not immutable", expression.start.line)
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
                raise InvalidOperation(f"Operator ! not supported for {right}", expression.operator)
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
                    raise InvalidOperation(f"Operator not supported for types {left} and {right}")
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
        except InvalidOperation as e:
            e.token = expression.operator
            raise e
        return None

    @visitor(Variable)
    def check(self, expression: Variable):
        return self.check_scope(expression.name.text)

    @visitor(VarDeclaration)
    def check(self, expression: VarDeclaration):
        expression_type = expression.expression.check(self)
        if expression.type:
            variable_type = expression.type.check(self)
            if not self.can_assign(expression_type, variable_type):
                raise TypeError(
                    f"Variable {expression.name.text} of type {variable_type} can't be assigned {expression_type}")
            expression_type = variable_type
        else:
            if isinstance(expression_type, Function):
                raise TypeError(
                    f"Variable {expression.name.text} can't be assigned {expression_type}")
            if issubclass(expression_type, Null):
                raise TypeError("Can't infer type of null")
        if self.scope.exists(expression.name.text):
            raise Exception(f"Variable {expression.name.text} already exists")
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
        raise TypeNotDefined(f"Type {expression.type.text} is not defined in current scope", expression.type)

    @visitor(Assignment)
    def check(self, expression: Assignment):
        expression_type = expression.value.check(self)
        left_type = expression.left.check(self)
        if not self.can_assign(expression_type, left_type):
            raise TypeError(
                f"Can't assign {expression_type} to {left_type} object")

    @visitor(ExpressionStatement)
    def check(self, expression: ExpressionStatement):
        return expression.expression.check(self)

    @visitor(Call)
    def check(self, expression: Call):
        called: Function = expression.called.check(self)
        if not isinstance(called, Function):
            raise TypeError()
        if len(expression.arguments) != len(called.param_types):
            raise Exception("Invalid number of arguments")
        for arg, param in zip(expression.arguments, called.param_types):
            arg_type = arg.check(self)
            if param is Type and isinstance(arg_type, Function):
                continue
            if not self.can_assign(arg_type, param):
                raise TypeError(f"Function with argument type {param} can't receive {arg_type}")
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
                    raise Exception("init method must call super's init in first statement")
                if not isinstance(line.called, GetNode):
                    raise Exception("init method must call super's init in first statement")
                if not isinstance(line.called.left, SuperNode) or line.called.right.text != "init":
                    raise Exception("init method must call super's init in first statement")
        scope = Scope(self.scope)
        for param in expression.params:
            scope.declare(param[0].text, param[1].check(self))
        self.current_function = self.check_scope(expression.name.text)
        self.check_block(expression.body, scope)
        if not issubclass(self.current_function.return_type, Null) and not self.check_return_paths(expression.body):
            raise Exception("All code paths don't return a value")
        self.current_function = None

    @visitor(Return)
    def check(self, expression: Return):
        if not self.current_function:
            raise Exception("return statement should be inside a function")
        if expression.expression:
            return_type = expression.expression.check(self)
        else:
            return_type = Null
        expected = self.current_function.return_type
        if not self.can_assign(return_type, expected):
            raise TypeError(
                f"Function expects {expected} return type, got {return_type} instead")

    @visitor(If)
    def check(self, expression: If):
        if not issubclass(expression.condition.check(self), Boolean):
            raise TypeError(f"if condition is not a boolean value")
        self.check_block(expression.code, Scope(self.scope))
        self.check_block(expression.else_code, Scope(self.scope))

    @visitor(While)
    def check(self, expression: While):
        if not issubclass(expression.condition.check(self), Boolean):
            raise TypeError(f"while condition is not a boolean value")
        self.current_loops += 1
        self.check_block(expression.code, Scope(self.scope))
        self.current_loops -= 1

    @visitor(ClassNode)
    def check(self, expression: ClassNode):
        scope = Scope(self.scope)
        if expression.superclass:
            super_class = self.get_class(expression.superclass.text)
        else:
            super_class = None
        created = Class(expression.name.text, super_class, scope)
        self.types.append(created)
        self.check_functions_in_scope(scope, expression.methods)
        params = []
        try:
            init = getattr(created, "init")
            if not issubclass(init.return_type, Null):
                raise Exception("init method must have void return type")
            params = init.param_types
        except TypeError:
            pass
        self.current_class = created
        self.scope.declare(expression.name.text, Function(created.name, params, created))
        expression.methods.sort(key=lambda x: {"init": 0}.get(x.name.text, 1))
        self.check_block(expression.methods, scope)
        self.current_class = None
        self.check_class_inheritance(created)

    @visitor(SelfNode)
    def check(self, _):
        if not self.current_class:
            raise Exception("self must be contained in a class")
        return self.current_class

    @visitor(SuperNode)
    def check(self, _):
        if not self.current_class:
            raise Exception("self must be contained in a class")
        return self.current_class.__bases__[0]

    @visitor(GetNode)
    def check(self, expression: GetNode):
        left: Class = expression.left.check(self)
        return getattr(left, expression.right.text)

    @visitor(AttrDeclaration)
    def check(self, expression: AttrDeclaration):
        if not self.current_class:
            raise Exception("Attributes can only be created inside classes")
        if self.current_function.name != "init":
            raise Exception("Attributes can only be declared in init class method")
        expression_type = expression.expression.check(self)
        if expression.type:
            attr_type = expression.type.check(self)
            if not self.can_assign(expression_type, attr_type):
                raise TypeError(
                    f"Attribute {expression.name.text} of type {expression.type.type.text} can't be assigned {expression_type}")
            expression_type = attr_type
        else:
            if issubclass(expression_type, Null):
                raise TypeError("Can't infer type of null")
        self.current_class.scope.declare(expression.name.text, expression_type)

    @visitor(SwitchNode)
    def check(self, expression: SwitchNode):
        var = expression.variable.text
        var_type = self.scope.get(var)
        for _case in expression.switch_cases:
            c_type = self.get_class(_case.text)
            if not isinstance(c_type, Class):
                raise TypeError()
            if not self.can_assign(var_type, c_type) and not self.can_assign(c_type, var_type):
                raise TypeError(f"Can't cast {var_type} to {c_type}")
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

    def get_class(self, name: str):
        for t in self.types:
            if str(t) == name:
                return t
        raise Exception(f"Class {name} not defined in scope")

    def check_scope(self, name: str):
        try:
            return self.scope.get(name)
        except:
            return self.globals.get(name)

    @staticmethod
    def check_class_inheritance(cls):
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
                    raise InvalidMethodDeclaration("Function must have same number of arguments as in parent class",
                                                   current.line)
                for i, j in zip(current.param_types, function.param_types):
                    if not TypeChecker.can_assign(j, i):
                        raise InvalidMethodDeclaration(f"Parameter in {member} defined in parent class as {j} "
                                                       f"type, can't be of type {i} in class {cls}", current.line)
                if not TypeChecker.can_assign(current.return_type, function.return_type):
                    raise InvalidMethodDeclaration(
                        f"Return type defined in parent class as {function.return_type} type, not {current.return_type}",
                        current.line)
            else:
                try:
                    variable = cls.scope.father.get(member)
                except:
                    continue
                if not TypeChecker.can_assign(current, variable):
                    raise TypeError(f"Variable {member} defined in parent class as {variable} type, not {current}")

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

    @staticmethod
    def can_assign(type1, type2):
        if isinstance(type1, Function) or isinstance(type2, Function):
            raise TypeError()
        if isinstance(type1, TypeList) and isinstance(type2, TypeList):
            if type1.list_type is None:
                return True
            return TypeChecker.can_assign(type1.list_type, type2.list_type)
        if isinstance(type1, TypeDict) and isinstance(type2, TypeDict):
            if type1.key_type is None:
                return True
            return TypeChecker.can_assign(type1.key_type, type2.key_type) and \
                   TypeChecker.can_assign(type1.value_type, type2.value_type)
        if issubclass(type1, Null) and isinstance(type2, Class):
            return True
        return issubclass(type1, type2)

    @staticmethod
    def common_type(types):
        if not types:
            return None
        _type = types[0]
        for elem in types:
            if TypeChecker.can_assign(elem, _type):
                continue
            elif TypeChecker.can_assign(_type, elem):
                _type = elem
            else:
                while not issubclass(Object, elem):
                    if TypeChecker.can_assign(_type, elem):
                        break
                    elem = elem.__base__
                _type = elem
        return _type
