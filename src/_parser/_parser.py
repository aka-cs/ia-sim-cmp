from lr_parser.lr1_parser import LR1Parser
from lr_parser.grammar import Grammar, CreateTerminals, CreateNonTerminals, Terminal, Epsilon
from lr_parser.lr_utils import evaluate_reverse_parser
from .nodes import *
from tokenizer.token_ import Token, TokenType
from tools import Singleton


class Parser(metaclass=Singleton):

    def __init__(self, path=None):
        symbol = Terminal("symbol")
        operators = equals, plus, minus, mul, div, mod, exclamation = CreateTerminals("= + - * / % !".split())
        comparison = equals_equals, different, greater, greaterequal, less, lessequal = CreateTerminals(
            "== != > >= < <=".split())
        logic = and_operator, or_operator = CreateTerminals("and or".split())
        statements = if_s, else_s, while_s, fun_s, var_s, return_s, class_s, for_s, attr, switch, case, default,\
            continue_s, break_s\
            = CreateTerminals("if else while fun var return class for attr switch case default continue break".split())
        specials = integer, _float, identifier, string, _self, _super \
            = CreateTerminals("int float identifier string self super".split())
        grouping = open_p, close_p, open_b, close_b, open_br, close_br = CreateTerminals("( ) { } [ ]".split())
        punctuation = comma, dot, semicolon, colon = CreateTerminals(", . ; :".split())
        boolean = true_i, false_i, null_i = CreateTerminals("true false null".split())
        comment = Terminal("comment")
        
        terminals = [symbol, *operators, *comparison, *logic, *statements,
                     *specials, *grouping, *punctuation, *boolean, comment]

        non_terminals \
            = p_program, p_functions, p_statements, p_statement, p_if, p_else, p_while, p_fun_declaration, p_return, p_return_arg, \
              p_params, p_more_params, p_var_declaration, p_var_type, p_assign, p_expression_s, p_expression, p_logic, p_logic_op, \
              p_equality, p_equality_op, p_comparison, p_comparison_op, p_term, p_term_op, \
              p_factor, p_factor_op, p_unary, p_unary_op, p_index, p_call, p_arguments, p_more_arguments, p_primary, \
              p_array, p_array_elem, p_more_array_elem, p_dict, p_dict_elem, p_more_dict_elem, \
              p_types, p_type, p_class, p_class_members, p_get, p_set, p_attr, p_superclass, \
              p_switch, p_cases, p_default, p_comment, p_for, p_continue, p_break \
            = CreateNonTerminals("Program Functions Statements Statement If Else While FunDeclaration Return ReturnArg "
                                 "Params MoreParams VarDeclaration VarType Assign ExpressionS Expression Logic Logic_op "
                                 "Equality Equality_op Comparison Comparison_op Term Term_op "
                                 "Factor Factor_op Unary Unary_op Index Call Arguments MoreArguments Primary "
                                 "Array ArrayElem MoreArrayElem Dict DictElem MoreDictElem Types Type Class "
                                 "ClassMembers Get Set Attribute SuperClass Switch Cases Default Comment For Continue Break".split())

        e = Epsilon()

        productions = [
            p_program > (p_class + p_program | p_functions,
                         lambda x: [Statement(x[0]), *x[1]], lambda x: x[0], lambda x: []),
            p_functions > (p_fun_declaration + p_functions | e,
                           lambda x: [Statement(x[0]), *x[1]], lambda x: []),
            p_statements > (p_statements + p_statement | e, lambda x: [*x[0], x[1]], lambda x: []),
            p_statement > (p_if | p_while | p_var_declaration | p_assign | p_return | p_expression_s | p_attr
                           | p_switch | p_comment | p_for | p_continue | p_break,
                           lambda x: Statement(x[0]),
                           lambda x: Statement(x[0]),
                           lambda x: Statement(x[0]),
                           lambda x: Statement(x[0]),
                           lambda x: Statement(x[0]),
                           lambda x: Statement(x[0]),
                           lambda x: Statement(x[0]),
                           lambda x: Statement(x[0]),
                           lambda x: Statement(x[0]),
                           lambda x: Statement(x[0]),
                           lambda x: Statement(x[0]),
                           lambda x: Statement(x[0])),

            p_continue > (continue_s + semicolon, lambda x: ContinueNode(x[0])),
            p_break > (break_s + semicolon, lambda x: BreakNode(x[0])),

            p_for > (for_s + open_p + var_s + identifier + colon + p_expression + close_p + open_b + p_statements + close_b,
                     lambda x: ForNode(x[0], x[3], x[5], x[8])),
            
            p_comment > (comment, lambda x: CommentNode(x[0].text)),

            p_switch > (switch + identifier + colon + case + identifier + open_b + p_statements + close_b + p_cases + p_default,
                        lambda x: SwitchNode(x[1], {x[4]: x[6], **x[8]}, x[9])),
            p_cases > (case + identifier + open_b + p_statements + close_b + p_cases | e,
                       lambda x: {x[1]: x[3], **x[5]}, lambda x: dict()),
            p_default > (default + open_b + p_statements + close_b | e, lambda x: x[2], lambda x: []),

            p_class > (class_s + identifier + p_superclass + open_b + p_class_members + close_b |
                       identifier + colon + colon + identifier + open_b + p_class_members + close_b,
                       lambda x: ClassNode(x[1], x[2], x[4]),
                       lambda x: ClassNode(x[3], x[0], x[5])),
            p_superclass > (colon + identifier | e, lambda x: x[1], lambda x: None),
            p_class_members > (p_fun_declaration + p_class_members | e, lambda x: [x[0], *x[1]], lambda x: []),

            p_if > (if_s + open_p + p_expression + close_p + open_b + p_statements + close_b + p_else,
                    lambda x: If(x[0], x[2], x[5], x[7])),
            p_else > (else_s + open_b + p_statements + close_b | e,
                      lambda x: x[2],
                      lambda x: []),

            p_while > (while_s + open_p + p_expression + close_p + open_b + p_statements + close_b,
                       lambda x: While(x[0], x[2], x[5])),

            p_var_declaration > (var_s + identifier + p_var_type + equals + p_equality + semicolon,
                                 lambda x: VarDeclaration(x[1], x[2], x[4])),
            p_attr > (attr + identifier + colon + p_type + equals + p_equality + semicolon,
                      lambda x: AttrDeclaration(x[1], x[3], x[5])),
            p_var_type > (colon + p_type | e, lambda x: x[1], lambda x: None),
            p_type > (
                identifier + less + p_types + greater | identifier, lambda x: VarType(x[0], *x[2]),
                lambda x: VarType(x[0])),
            p_types > (p_type | p_type + comma + p_type, lambda x: [x[0]], lambda x: [x[0], x[2]]),
            p_assign > (p_set + equals + p_equality + semicolon, lambda x: Assignment(x[0], x[2], x[1].line)),
            p_fun_declaration > (
                fun_s + identifier + open_p + p_params + colon + p_type + open_b + p_statements + close_b,
                lambda x: FunctionNode(x[1], x[3], x[5], x[7])),

            p_params > (identifier + colon + p_type + p_more_params | close_p,
                        lambda x: [(x[0], x[2]), *x[3]], lambda x: []),
            p_more_params > (comma + identifier + colon + p_type + p_more_params | close_p,
                             lambda x: [(x[1], x[3]), *x[4]], lambda x: []),

            p_return > (return_s + p_return_arg, lambda x: Return(x[0], x[1])),
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
            p_primary > (
                integer | _float | string | true_i | false_i | null_i | open_p + p_logic + close_p | p_array | p_dict,
                lambda x: Literal(int(x[0].text)),
                lambda x: Literal(float(x[0].text)),
                lambda x: Literal(x[0].text),
                lambda x: Literal(True),
                lambda x: Literal(False),
                lambda x: Literal(None),
                lambda x: Grouping(x[1]),
                lambda x: x[0],
                lambda x: x[0]),

            p_set > (p_get + dot + identifier | identifier | p_index,
                     lambda x: GetNode(x[0], x[2]), lambda x: Variable(x[0]), lambda x: x[0]),
            p_get > (
                p_get + dot + identifier | p_get + open_p + p_arguments + close_p | identifier | _self | _super | p_index,
                lambda x: GetNode(x[0], x[2]), lambda x: Call(x[0], x[2], x[1].line),
                lambda x: Variable(x[0]), lambda x: SelfNode(x[0]), lambda x: SuperNode(x[0]), lambda x: x[0]),
            p_index > (p_call + open_br + p_expression + close_br, lambda x: Index(x[0], x[2])),

            p_arguments > (p_expression + p_more_arguments | e, lambda x: [x[0], *x[1]], lambda x: []),
            p_more_arguments > (comma + p_expression + p_more_arguments | e, lambda x: [x[1], *x[2]], lambda x: []),

            p_array > (open_br + p_array_elem + close_br, lambda x: ArrayNode(x[0], x[1])),
            p_array_elem > (p_expression + p_more_array_elem | e, lambda x: [x[0], *x[1]], lambda x: []),
            p_more_array_elem > (comma + p_expression + p_more_array_elem | e, lambda x: [x[1], *x[2]], lambda x: []),

            p_dict > (open_b + p_dict_elem + close_b, lambda x: DictionaryNode(x[0], *x[1])),
            p_dict_elem > (p_expression + colon + p_expression + p_more_dict_elem | e,
                           lambda x: [[x[0], *x[3][0]], [x[2], *x[3][1]]], lambda x: [[], []]),
            p_more_dict_elem > (comma + p_expression + colon + p_expression + p_more_dict_elem | e,
                                lambda x: [[x[1], *x[4][0]], [x[3], *x[4][1]]], lambda x: [[], []]),

            p_logic_op > (and_operator | or_operator, lambda x: x[0], lambda x: x[0]),
            p_equality_op > (equals_equals | different, lambda x: x[0], lambda x: x[0]),
            p_comparison_op > (greater | greaterequal | less | lessequal,
                               lambda x: x[0], lambda x: x[0], lambda x: x[0], lambda x: x[0]),
            p_term_op > (plus | minus, lambda x: x[0], lambda x: x[0]),
            p_factor_op > (mul | div | mod, lambda x: x[0], lambda x: x[0], lambda x:x[0]),
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
            TokenType.FOR: for_s,
            TokenType.WHILE: while_s,
            TokenType.BREAK: break_s,
            TokenType.CONTINUE: continue_s,
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
            TokenType.MODULO: mod,
            TokenType.EXCLAMATION: exclamation,
            TokenType.COMMA: comma,
            TokenType.DOT: dot,
            TokenType.COLON: colon,
            TokenType.SEMICOLON: semicolon,
            TokenType.SWITCH: switch,
            TokenType.CASE: case,
            TokenType.DEFAULT: default,
            TokenType.COMMENT: comment,
            TokenType.EOF: self.parser.G.EOF
        }

    def _map_tokens_to_terminals(self, tokens: [Token]):
        mapped_tokens = []
        for token in tokens:
            terminal = self.mapping.get(token.type, self.parser.G.Terminals[0])
            mapped_tokens.append(terminal)
        return mapped_tokens

    def parse(self, tokens: [Token]):
        mapped_tokens = self._map_tokens_to_terminals(tokens)
        parsed, operations = self.parser(mapped_tokens)
        ast = evaluate_reverse_parser(parsed, operations, tokens + [self.parser.G.EOF])
        return ast
