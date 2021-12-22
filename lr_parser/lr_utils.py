from lr_parser.shift_reduce_parser import Action
from automata.automata import Automata, Info

from lr_parser.grammar import Grammar, Terminal, NonTerminal, Symbol, Sentence, Item, AttributedProduction
from typing import Dict, Set, Iterable, Tuple


class MySet(set):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.contains_epsilon = False
            
    def hard_update(self, other: "MySet"):
        old_len = len(self)
        had_epsilon = self.contains_epsilon
        self.update(other)
        self.contains_epsilon = self.contains_epsilon or other.contains_epsilon
        return old_len != len(self) or had_epsilon != self.contains_epsilon
    
    def __repr__(self):
        return f"{set(self)} epsilon: {self.contains_epsilon}"


def get_local_firsts(firsts: Dict[Symbol | Sentence, MySet[Terminal]], alpha: Sentence):
    firsts_alpha = MySet()
    
    if alpha.IsEpsilon:
        firsts_alpha.contains_epsilon = True
    else:
        for x in alpha.symbols:
            firsts_alpha.hard_update(firsts[x])
            
            if not firsts[x].contains_epsilon:
                break
        else:
            firsts_alpha.contains_epsilon = True

    return firsts_alpha


def get_firsts(grammar: Grammar):
    firsts: Dict[Symbol | Sentence, MySet[Terminal]] = {}
    change = True
    
    for terminal in grammar.Terminals:
        firsts[terminal] = MySet([terminal])
        
    for non_terminal in grammar.NonTerminals:
        firsts[non_terminal] = MySet()

    while change:
        change = False
        for production in grammar.Productions:
            x = production.Left
            alpha = production.Right
            
            firsts[alpha] = firsts.get(alpha, MySet())
            
            local_first = get_local_firsts(firsts, alpha)
            
            change |= firsts[alpha].hard_update(local_first)
            change |= firsts[x].hard_update(local_first)
            
    return firsts


def expand(item: Item, firsts: Dict[Symbol | Sentence, MySet[Terminal]]):
    next_symbol = item.NextSymbol
    
    if next_symbol is None or not next_symbol.IsNonTerminal:
        return []
    
    assert isinstance(next_symbol, NonTerminal)
    
    lookaheads = MySet()
    
    for prev in item.Preview():
        lookaheads.update(get_local_firsts(firsts, prev))
    
    return frozenset(Item(prod, 0, lookaheads) for prod in next_symbol.productions)
    
    
def compress(items: Iterable[Item]):
    centers: Dict[Item, Set] = {}
    
    for item in items:
        center = item.Center()
        if center not in centers:
            centers[center] = lookaheads = MySet()
        else:
            lookaheads = centers[center]
            
        lookaheads.update(item.lookaheads)
    
    return set(Item(x.production, x.pos, lookahead) for x, lookahead in centers.items())


def closure_lr1(items: Iterable[Item], firsts):
    closure = MySet(items)

    changed = True
    while changed:
        
        new_items = MySet()
        
        for item in closure:
            new_items.update(expand(item, firsts))
            
        changed = closure.hard_update(new_items)
        
    return compress(closure)


def goto_lr1(items: Iterable[Item], symbol: Symbol, firsts=None, just_kernel=False):
    
    if firsts is None:
        firsts = {}
    
    items = frozenset(item.NextItem for item in items if item.NextSymbol == symbol)
    
    if just_kernel:
        return items
    
    return closure_lr1(items, firsts)


def build_lr1_automata(g: Grammar):
    assert g.IsAugmentedGrammar
    
    firsts = get_firsts(g)
    firsts[g.EOF] = MySet([g.EOF])

    start_production = g.Initial.productions[0]
    start_item = Item(start_production, 0, lookaheads=(g.EOF,))
    start = frozenset([start_item])

    closure_ = closure_lr1(start, firsts)
    
    pending = [start]
    visited = {start: 0}
    
    transitions: Dict[Tuple[int, str], Tuple[int]] = {}
    info = {0: Info(closure_)}

    count = 1

    while pending:
        current = pending.pop()
        current_state = visited[current]
        
        closure = closure_lr1(current, firsts)
        
        for symbol in g.Terminals + g.NonTerminals:
            new_items = frozenset(goto_lr1(closure, symbol, just_kernel=True))
            if not new_items:
                continue
            try:
                next_state = visited[new_items]
            except KeyError:
                pending.append(new_items)
                next_state = count
                info[next_state] = Info(frozenset(closure_lr1(new_items, firsts)))
                visited[new_items] = next_state
                count += 1
            transitions[(current_state, symbol.Name)] = (next_state,)
    
    return Automata(count, transitions, {i: [] for i in range(count)}, 0, info)


def evaluate_reverse_parser(right_parse, operations, tokens):
    
    right_parse = iter(right_parse)
    tokens = iter(tokens)
    stack = []

    for operation in operations:
        if operation == Action.SHIFT:
            token: NonTerminal = next(tokens)
            stack.append(token)
        if operation == Action.REDUCE:
            production: AttributedProduction = next(right_parse)
            synthesize = stack[-len(production.Right):]
            value = production.attribute(synthesize)
            stack[-len(production.Right):] = [value]
            
    assert len(stack) == 1
    
    return stack[0]
