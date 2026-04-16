from __future__ import annotations
from abc import ABC, abstractmethod

class MContext(ABC):
    def __init__(self):
        pass
    @abstractmethod
    def compute(self):
        pass

class State(ABC):
    def __init__(self):
        self.transitions = {}
    def check_change(self, context:MContext):
        for rule, state in self.transitions.items():
            if(rule.applies(context)):
                self.on_exit(context) 
                return state
        return None
    # Funcion para activar o desactivar o cosas
    @abstractmethod
    def on_init(self, context:MContext):
        pass
    @abstractmethod
    def on_exit(self, context:MContext):
        pass
    @abstractmethod
    def execute(self, context:MContext):
        pass
    def add_transition(self, rule:Rule, new_state:State):
        self.transitions[rule] = new_state

class Rule(ABC):
    @abstractmethod
    def applies(self, context:MContext) -> bool:
        pass

class Machine:
    def __init__(self, istate:State):
        self.istate:State = istate
        self.cstate:State = istate
    def reset(self):
        self.cstate = self.istate
    def run(self, context:MContext):
        # el contexto ejecuta tareas que pasan 
        # siempre por captura
        next = self.cstate.check_change(context)
        if next is not None:
            self.cstate = next
            self.cstate.on_init(context)
        self.cstate.execute(context)
    def add(self, s_from:State, s_to:State, rule: Rule):
        s_from.add_transition(rule, s_to)
