from lr_parser.grammar import Item
from lr_parser.lr_utils import build_lr1_automata
from lr_parser.shift_reduce_parser import ShiftReduceParser, Action


class LR1Parser(ShiftReduceParser):
    
    def _build_parsing_table(self):
        G = self.G.AugmentedGrammar()
        
        automata = build_lr1_automata(G)
        
        if self.logs:
            for i in range(automata.states):
                print(i, '\t', '\n\t '.join(str(x) for x in automata.get_info(i)), '\n')
        
        for state in range(automata.states):
            for item in automata.get_info(state):  # type: Item
                prod = item.production
                if item.IsReduceItem:
                    if prod.Left == G.Initial:
                        self._register(self.action, (state, G.EOF), (Action.OK, 0))
                    else:
                        for symbol in item.lookaheads:
                            self._register(self.action, (state, symbol), (Action.REDUCE, prod))
                else:
                    next_symbol = item.NextSymbol
                    if next_symbol.IsTerminal:
                        self._register(self.action, (state, next_symbol),
                                       (Action.SHIFT, automata.transitions[(state, next_symbol.Name)][0]))
                    else:
                        self._register(self.goto, (state, next_symbol),
                                       automata.transitions[(state, next_symbol.Name)][0])
    
    @staticmethod
    def _register(table, key, value):
        assert key not in table or table[key] == value, 'Shift-Reduce or Reduce-Reduce conflict!!!'
        table[key] = value
