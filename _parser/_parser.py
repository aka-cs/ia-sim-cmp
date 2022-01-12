from lr_parser.lr1_parser import LR1Parser
from lr_parser.grammar import Grammar, CreateTerminals, CreateNonTerminals, Terminal, Epsilon
from lr_parser.lr_utils import evaluate_reverse_parser
from .nodes import *
from tokenizer.token_ import Token, TokenType
from tools import Singleton


class Parser(metaclass=Singleton):

    def __init__(self, path=None):
        symbol = Terminal("symbol")
        operators = equals, plus, minus, mul, div, exclamation = CreateTerminals("= + - * / !".split())
        comparison = equals_equals, different, greater, greaterequal, less, lessequal = CreateTerminals(
            "== != > >= < <=".split())
        logic = and_operator, or_operator = CreateTerminals("and or".split())
        statements = if_s, else_s, while_s, fun_s, var_s, return_s, class_s, attr \
            = CreateTerminals("if else while fun var return class attr".split())
        specials = integer, _float, identifier, string, _self, _super \
            = CreateTerminals("int float identifier string self super".split())
        grouping = open_p, close_p, open_b, close_b, open_br, close_br = CreateTerminals("( ) { } [ ]".split())
        punctuation = comma, dot, semicolon, colon = CreateTerminals(", . ; :".split())
        boolean = true_i, false_i, null_i = CreateTerminals("true false null".split())

        terminals = [symbol, *operators, *comparison, *logic, *statements, *specials, *grouping, *punctuation, *boolean]

        non_terminals \
            = p_program, p_functions, p_statements, p_statement, p_if, p_else, p_while, p_fun_declaration, p_return, p_return_arg, \
              p_params, p_more_params, p_var_declaration, p_var_type, p_assign, p_expression_s, p_expression, p_logic, p_logic_op, \
              p_equality, p_equality_op, p_comparison, p_comparison_op, p_term, p_term_op, \
              p_factor, p_factor_op, p_unary, p_unary_op, p_index, p_call, p_arguments, p_more_arguments, p_primary, \
              p_array, p_array_elem, p_more_array_elem, p_type, p_class, p_class_members, p_get, p_set, p_attr, p_superclass \
            = CreateNonTerminals("Program Functions Statements Statement If Else While FunDeclaration Return ReturnArg "
                                 "Params MoreParams VarDeclaration VarType Assign ExpressionS Expression Logic Logic_op "
                                 "Equality Equality_op Comparison Comparison_op Term Term_op "
                                 "Factor Factor_op Unary Unary_op Index Call Arguments MoreArguments Primary "
                                 "Array ArrayElem MoreArrayElem Type Class ClassMembers Get Set Attribute SuperClass".split())

        e = Epsilon()

        productions = [
            p_program > (p_class + p_program | p_functions,
                         lambda x: [Statement(x[0]), *x[1]], lambda x: x[0], lambda x: []),
            p_functions > (p_fun_declaration + p_functions | e,
                           lambda x: [Statement(x[0]), *x[1]], lambda x: []),
            p_statements > (p_statements + p_statement | e, lambda x: [*x[0], x[1]], lambda x: []),
            p_statement > (p_if | p_while | p_var_declaration | p_assign | p_return | p_expression_s | p_attr,
                           lambda x: Statement(x[0]),
                           lambda x: Statement(x[0]),
                           lambda x: Statement(x[0]),
                           lambda x: Statement(x[0]),
                           lambda x: Statement(x[0]),
                           lambda x: Statement(x[0]),
                           lambda x: Statement(x[0])),

            p_class > (class_s + identifier + p_superclass + open_b + p_class_members + close_b,
                       lambda x: ClassNode(x[1], x[2], x[4])),
            p_superclass > (colon + identifier | e, lambda x: x[1], lambda x: None),
            p_class_members > (p_fun_declaration + p_class_members | e, lambda x: [x[0], *x[1]], lambda x: []),

            p_if > (if_s + open_p + p_expression + close_p + open_b + p_statements + close_b + p_else,
                    lambda x: If(x[2], x[5], x[7])),
            p_else > (else_s + open_b + p_statements + close_b | e,
                      lambda x: x[2],
                      lambda x: []),

            p_while > (while_s + open_p + p_expression + close_p + open_b + p_statements + close_b,
                       lambda x: While(x[2], x[5])),

            p_var_declaration > (var_s + identifier + p_var_type + equals + p_equality + semicolon,
                                 lambda x: VarDeclaration(x[1], x[2], x[4])),
            p_attr > (attr + identifier + p_var_type + equals + p_equality + semicolon,
                      lambda x: AttrDeclaration(x[1], x[2], x[4])),
            p_var_type > (colon + p_type | e, lambda x: x[1], lambda x: None),
            p_type > (
                identifier + less + p_type + greater | identifier, lambda x: VarType(x[0], x[2]),
                lambda x: VarType(x[0])),
            p_assign > (p_set + equals + p_equality + semicolon, lambda x: Assignment(x[0], x[2])),
            p_fun_declaration > (
                fun_s + identifier + open_p + p_params + colon + p_type + open_b + p_statements + close_b,
                lambda x: FunctionNode(x[1], x[3], x[5], x[7])),

            p_params > (identifier + colon + p_type + p_more_params | close_p,
                        lambda x: [(x[0], x[2]), *x[3]], lambda x: []),
            p_more_params > (comma + identifier + colon + p_type + p_more_params | close_p,
                             lambda x: [(x[1], x[3]), *x[4]], lambda x: []),

            p_return > (return_s + p_return_arg, lambda x: Return(x[1])),
            p_return_arg > (p_expression + semicolon | semicolon, lambda x: x[0], lambda x: None),

            p_expression_s > (p_expression + semicolon, lambda x: x[0]),
            p_expression > (p_logic, lambda x: x[0]),
            p_logic > (p_logic + p_logic_op + p_equality | p_equality, lambda x: Binary(*x), lambda x: x[0]),
            p_equality > (
                p_equality + p_equality_op + p_comparison | p_comparison, lambda x: Binary(*x), lambda x: x[0]),
            p_comparison > (p_comparison + p_comparison_op + p_term | p_term, lambda x: Binary(*x), lambda x: x[0]),
            p_term > (p_term + p_term_op + p_factor | p_factor, lambda x: Binary(*x), lambda x: x[0]),
            p_factor > (p_factor + p_factor_op + p_unary | p_unary, lambda x: Binary(*x), lambda x: x[0]),
            p_unary > (p_unary_op + p_unary | p_call, lambda x: Unary(*x), lambda x: x[0]),
            p_call > (p_primary | p_get,
                      lambda x: x[0],
                      lambda x: x[0]),
            p_primary > (integer | _float | string | true_i | false_i | null_i | open_p + p_logic + close_p | p_array,
                         lambda x: Literal(int(x[0].text)),
                         lambda x: Literal(float(x[0].text)),
                         lambda x: Literal(x[0].text),
                         lambda x: Literal(True),
                         lambda x: Literal(False),
                         lambda x: Literal(None),
                         lambda x: Grouping(x[1]),
                         lambda x: x[0]),

            p_set > (p_get + dot + identifier | identifier | p_index,
                     lambda x: GetNode(x[0], x[2]), lambda x: Variable(x[0]), lambda x: x[0]),
            p_get > (p_get + dot + identifier | p_get + open_p + p_arguments + close_p | identifier | _self | _super | p_index,
                     lambda x: GetNode(x[0], x[2]), lambda x: Call(x[0], x[2]),
                     lambda x: Variable(x[0]), lambda x: SelfNode(), lambda x: SuperNode(), lambda x: x[0]),
            p_index > (p_call + open_br + p_expression + close_br, lambda x: Index(x[0], x[2])),

            p_arguments > (p_expression + p_more_arguments | e, lambda x: [x[0], *x[1]], lambda x: []),
            p_more_arguments > (comma + p_expression + p_more_arguments | e, lambda x: [x[1], *x[2]], lambda x: []),

            p_array > (open_br + p_array_elem + close_br, lambda x: ArrayNode(x[1])),
            p_array_elem > (p_expression + p_more_array_elem | e, lambda x: [x[0], *x[1]], lambda x: []),
            p_more_array_elem > (comma + p_expression + p_more_array_elem | e, lambda x: [x[1], *x[2]], lambda x: []),

            p_logic_op > (and_operator | or_operator, lambda x: x[0], lambda x: x[0]),
            p_equality_op > (equals_equals | different, lambda x: x[0], lambda x: x[0]),
            p_comparison_op > (greater | greaterequal | less | lessequal,
                               lambda x: x[0], lambda x: x[0], lambda x: x[0], lambda x: x[0]),
            p_term_op > (plus | minus, lambda x: x[0], lambda x: x[0]),
            p_factor_op > (mul | div, lambda x: x[0], lambda x: x[0]),
            p_unary_op > (exclamation | minus, lambda x: x[0], lambda x: x[0])
        ]

        grammar = Grammar(non_terminals, terminals, p_program, productions)

        self.parser = LR1Parser(grammar, path=path)
        self.mapping = {
            TokenType.SELF: _self,
            TokenType.SUPER: _super,
            TokenType.IDENTIFIER: identifier,
            TokenType.INTEGER: integer,
            TokenType.FLOAT: _float,
            TokenType.STRING: string,
            TokenType.EQUAL: equals,
            TokenType.EQUAL_EQUAL: equals_equals,
            TokenType.EQUAL_DIFFERENT: different,
            TokenType.GREATER: greater,
            TokenType.GREATER_EQUAL: greaterequal,
            TokenType.LESS: less,
            TokenType.LESS_EQUAL: lessequal,
            TokenType.IF: if_s,
            TokenType.ELSE: else_s,
            TokenType.WHILE: while_s,
            TokenType.CLASS: class_s,
            TokenType.FUN: fun_s,
            TokenType.RETURN: return_s,
            TokenType.VAR: var_s,
            TokenType.ATTR: attr,
            TokenType.OPEN_PARENTHESIS: open_p,
            TokenType.CLOSE_PARENTHESIS: close_p,
            TokenType.OPEN_BRACES: open_b,
            TokenType.CLOSE_BRACES: close_b,
            TokenType.OPEN_BRACKETS: open_br,
            TokenType.CLOSE_BRACKETS: close_br,
            TokenType.AND: and_operator,
            TokenType.OR: or_operator,
            TokenType.TRUE: true_i,
            TokenType.FALSE: false_i,
            TokenType.NULL: null_i,
            TokenType.PLUS: plus,
            TokenType.MINUS: minus,
            TokenType.MULTIPLY: mul,
            TokenType.DIVIDE: div,
            TokenType.EXCLAMATION: exclamation,
            TokenType.COMMA: comma,
            TokenType.DOT: dot,
            TokenType.COLON: colon,
            TokenType.SEMICOLON: semicolon,
            TokenType.EOF: self.parser.G.EOF
        }

    def _map_tokens_to_terminals(self, tokens: [Token]):
        mapped_tokens = []
        for token in tokens:
            mapped_tokens.append(self.mapping.get(token.type, self.parser.G.Terminals[0]))
        return mapped_tokens

    def parse(self, tokens: [Token]):
        mapped_tokens = self._map_tokens_to_terminals(tokens)
        parsed, operations = self.parser(mapped_tokens)
        ast = evaluate_reverse_parser(parsed, operations, tokens + [self.parser.G.EOF])
        return ast
