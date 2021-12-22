from typing import List, Dict, Tuple, Any
import itertools as it


class MySet(set):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.id = -1
        self.is_final = False
        self.tags = []
        self.info = None


class Info:
    
    def __init__(self, info=None):
        self.info = info
    
    def __hash__(self):
        return hash(self.info)
    
    def __eq__(self, other):
        return self.info == other.info
    
    def __repr__(self):
        return f"Info: {self.info}"

    def __str__(self):
        return f"Info: {self.info}"


class Automata:
    
    def __init__(self,
                 states: int,
                 transitions: Dict[Tuple[int, str], Tuple[int]],
                 final_states: Dict[int, List[Tuple[Any, int]]],
                 initial_state: int = 0,
                 states_info: Dict[int, Info] = None):
        self.states = states
        self.transitions = transitions
        self.final_states = final_states
        self.states_info = states_info or {}
        self.initial_state = initial_state
        self.current = initial_state
        
        # Vocabulary
        self.vocabulary = set()
        for (_, symbol) in transitions.keys():
            if symbol:
                self.vocabulary.add(symbol)
    
    def reset(self):
        self.current = self.initial_state
    
    def recognize(self, program, start_index=0):
        self.reset()
        i = start_index
        for i in range(start_index, len(program)):
            if not self.next(program[i]):
                return False, i - start_index
        if start_index != len(program):
            i += 1
        return self.current in self.final_states.keys(), i - start_index
    
    def next(self, c: str):
        current = self.transitions.get((self.current, c), [None])[0]
        if current is not None:
            self.current = current
        return current is not None
    
    def get_type(self, state):
        types = self.final_states.get(state)
        if not types:
            return
        types.sort(key=lambda x: x[1])
        return types[0][0]
    
    def add_type(self, type: Tuple[Any, int]):
        transitions = dict(self.transitions)
        finals = {k: value + [type] for k, value in self.final_states.items()}
        
        return Automata(self.states, transitions, finals, self.initial_state, dict(self.states_info))
        
    
    def get_info(self, state):
        return self.states_info.get(state, Info(None)).info
    
    def move(self, states, symbol):
        n_states = set()
        for state in states:
            if p_states := self.transitions.get((state, symbol)):
                n_states.update(set(p_states))
        return list(n_states)
    
    def e_closure(self, states):
        visited = set(states)
        n_states = MySet(states)
        stack = list(visited)
        while stack:
            state = stack.pop()
            if p_states := self.transitions.get((state, "")):
                n_states.update(p_states)
                for n_state in p_states:
                    if n_state not in visited:
                        stack.append(n_state)
                visited.update(p_states)
        return n_states
    
    def dfa(self):
        transitions = {}
        
        start = self.e_closure([self.initial_state])
        start.id = 0
        start.is_final = any(s in self.final_states for s in start)
        start.tags = set()
        for tags in (self.final_states.get(s) for s in start if s in self.final_states):
            start.tags.update(tags)
        start.info = list(it.chain(*[self.states_info.get(s, []) for s in start]))
        
        states = [start]
        pending = [start]
        
        while pending:
            state = pending.pop()
            for symbol in self.vocabulary:
                q = self.e_closure(self.move(state, symbol))
                if not q:
                    continue
                
                if q not in states:
                    q.id = len(states)
                    q.is_final = any(s in self.final_states for s in q)
                    q.tags = set()
                    for tags in (self.final_states.get(s) for s in q if s in self.final_states):
                        q.tags.update(tags)
                    q.info = set(it.chain(*[self.states_info.get(s, []) for s in q]))
                    states.append(q)
                    pending.append(q)
                else:
                    for s in states:
                        if q == s:
                            q = s
                
                transitions[(state.id, symbol)] = (q.id,)
        
        finals = {s.id: list(s.tags) for s in states if s.is_final}
        info = {s.id: s.info for s in states}
        
        return Automata(len(states), transitions, finals, start.id, info)
    
    def concat(self, other: "Automata"):
        l1 = self.states
        l2 = other.states
        states = l1 + l2
        initial = self.initial_state
        transitions = dict(self.transitions)
        states_info = dict(self.states_info)
        
        # Epsilon transitions
        for state in self.final_states:
            transitions[(state, "")] = transitions.get((state, ''), ()) + (other.initial_state + l1,)
        
        for (state, c), new_states in other.transitions.items():
            transitions[(state + l1, c)] = tuple([s + l1 for s in new_states])
        
        for state, info in other.states_info.items():
            states_info[state + l1] = info
        
        finals = {s + l1: list(tags) for s, tags in other.final_states.items()}
        
        return Automata(states, transitions, finals, initial, states_info)
    
    def union(self, other: "Automata"):
        transitions = {}
        start = 0
        offset = self.states + 1
        
        transitions[(start, '')] = (self.initial_state + 1, other.initial_state + offset)
        
        for (state, c), new_state in self.transitions.items():
            transitions[(state + 1, c)] = tuple(ns + 1 for ns in new_state)
        for (state, c), new_state in other.transitions.items():
            transitions[(state + offset, c)] = tuple(ns + offset for ns in new_state)
        
        state_info = {state + 1: info for state, info in self.states_info.items()}
        state_info.update({state + offset: info for state, info in other.states_info.items()})
        
        finals = {s + 1: list(tags) for s, tags in self.final_states.items()}
        finals.update({s + offset: list(tags) for s, tags in other.final_states.items()})
        
        return Automata(self.states + other.states + 1, transitions, finals, start, state_info)
    
    def star(self):
        transitions = dict(self.transitions)
        
        for state in self.final_states:
            transitions[(state, '')] = transitions.get((state, ''), ()) + (self.initial_state,)
        
        finals = {k: list(tags) for k, tags in self.final_states.items()}
        
        all_tags = set()
        for tags in finals.values():
            all_tags.update(tags)
        
        finals.update({self.initial_state: list(all_tags)})
        
        return Automata(self.states, transitions, finals, self.initial_state, dict(self.states_info))
