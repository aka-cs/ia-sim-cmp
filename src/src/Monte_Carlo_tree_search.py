from __future__ import annotations
from .base_classes import MapObject, Agent, Environment
from abc import abstractmethod
from random import shuffle
from math import inf


class MonteCarloTreeSearchNode:
    """
     Implementación del algoritmo Monte Carlo Tree Search para la selección del próximo objetivo de un agente.
     Recibe una lista de objetivos y, asumiendo que es aspiración del agente recogerlos todos, analiza varios
     ordenes a seguir para visitarlos todos y en base a esta información establece cuál es el mejor para elegir
     como próximo objetivo.
     Para ponderar los nodos hojas del árbol de decisiones que construye el algoritmo, la clase recibe una heurística
     (una instancia de MonteCarloHeuristic) que pondera en base a información pertinente al problema que se ataca.
     Por defecto la heurística no posee implementación, por lo que para usar la clase es necesario heredar de
     MonteCarloHeuristic e implementar una heurística consecuente.
    """
    def __init__(self, untried_positions: [MapObject], agent: Agent, env: Environment, heuristic: MonteCarloHeuristic,
                 parent: MonteCarloTreeSearchNode, parent_choice: MapObject):
        # Posiciones no probadas a tomar aún.
        self._untried_positions = untried_positions

        # Guardamos el entorno y los agentes a tener en cuenta.
        self._env = env
        self._agent = agent

        # Guardamos la heuristica.
        self._heuristic = heuristic

        # Padre del nodo actual.
        self._parent = parent
        # Hijos del nodo actual.
        self._children = []

        # Elección del padre, que conllevó a la génesis de este nodo.
        self._parent_choice = parent_choice

        # Peso del nodo.
        self._weight = 0

    # Devuelve, de una serie posible de acciones a tomar, la mejor.
    def best_action(self, n: int) -> MapObject:
        # Realizamos n simulaciones.
        for _ in range(n):
            # Explora el árbol de decisiones actual, expande si es necesario,
            # y obtiene el valor de solución para la rama explorada.
            v, reward = self._tree_policy()
            # Propaga la solución hacia arriba en la rama.
            v.back_propagate(reward)

        # Devolvemos la mejor elección desde la raíz.
        return self.best_child().parent_choice()

    # Explora el árbol de decisiones hasta que halla un nodo a expandir.
    # Al hallar uno, lo expande y devuelve el hijo que se genera.
    # Si todos los nodos del camino están expandidos, devuelve el último de estos (una hoja).
    # Si el parámetro 'rollout' es true, acompañado al nodo devuelve el valor de la simulación
    # a partir de él, en otro caso devuelve None.
    def _tree_policy(self, *, rollout: bool = True):
        # Establecemos este como el nodo actual.
        current_node = self

        # Declaramos el camino vacío.
        path = []

        # Mientras no hayamos llegado a un nodo terminal.
        while not current_node.is_terminal_node():
            # Si el nodo actual no está completamente expandido.
            if not current_node.is_fully_expanded():
                # Expandimos el nodo, y guardamos el hijo que se genera.
                current_node = current_node.expand()
                # Si hay que simular, actualizamos el camino.
                if rollout:
                    path.append(current_node.parent_choice())

                # Devolvemos el nodo correspondiente al nuevo estado y el valor de la simulación
                # a partir de él, si es requerido.
                return current_node, (current_node.rollout(path) if rollout else None)

            # Si el nodo está completamente expandido, nos movemos al mejor de sus hijos.
            else:
                current_node = current_node.best_child()
                # Si hay que simular, actualizamos el camino.
                if rollout:
                    path.append(current_node.parent_choice())

        # Al llegar a un nodo terminal, devolvemos este y el valor de la simulación a partir de él,
        # si es requerido.
        return current_node, (current_node.rollout(path) if rollout else None)

    # Devuelve verdadero si el nodo es terminal y falso en caso contrario.
    def is_terminal_node(self):
        # Un nodo es terminal solo si su estado es terminal (se ha construido un camino
        # de decisión completo y no quedan elecciones para tomar).
        # En consecuencia, un nodo es terminal si está completamente expandido y no tiene hijos.
        return self.is_fully_expanded() and not self._children

    # Devuelve verdadero si el nodo está completamente expandido y falso en caso contrario.
    def is_fully_expanded(self):
        # Un nodo está completamente expandido si y solo si ya fueron revisadas todas las
        # acciones posibles desde el estado que representa.
        return len(self._untried_positions) == 0

    # Expande un nodo
    def expand(self):
        # Extraemos una posición del listado de posiciones no probadas.
        position = self._untried_positions.pop()

        # Construimos la lista de posibles decisiones a tomar del hijo (todas aquellas tomadas
        # por otros hijos paralelos, sumado a las no tomadas aún por el padre).
        child_untried_positions = [child.parent_choice() for child in self._children]
        child_untried_positions.extend(self._untried_positions)

        # Obtenemos el nodo correspondiente al nuevo estado.
        child_node = MonteCarloTreeSearchNode(child_untried_positions, self._agent, self._env, self._heuristic,
                                              self, position)

        # Lo añadimos como hijo del nodo actual.
        self._children.append(child_node)
        # Lo devolvemos.
        return child_node

    # Simula un resultado aleatorio partiendo de un estado dado.
    def rollout(self, path: [MapObject]):
        # Para construir el resultado, permutamos la lista de opciones válidas desde el estado
        # actual y la concatenamos al camino construido.
        valid_options = [child.parent_choice for child in self._children]
        valid_options.extend(self._untried_positions)
        shuffle(valid_options)
        path.extend(valid_options)

        # Calculamos el valor de la heuristica para este estado.
        self._weight = self._heuristic.heuristic(path, self._agent, self._env)

        # Devolvemos el valor de esta solución.
        return self._weight

    # Devuelve el mejor hijo de este nodo.
    def best_child(self):
        # Si el nodo actual no tiene hijos, devolvemos None.
        if not self._children:
            return None

        # Variables para guardar el mejor hijo, y su peso asociado.
        best_child = self._children[0]
        best_weight = -inf

        # Visitamos cada uno de los hijos.
        for child in self._children:
            # Si mejora el actual, actualizamos este como mejor hijo, y guardamos su peso.
            if child.weight() > best_weight:
                best_weight = child.weight()
                best_child = child

        # Devolvemos el mejor de los hijos.
        return best_child

    # Devuelve el peso del nodo.
    def weight(self):
        return self._weight

    # Actualiza los pesos del árbol.
    def back_propagate(self, result: float):
        if self._children:
            self._weight = sum([child.weight() for child in self._children]) / len(self._children)
        if self._parent:
            self._parent.back_propagate(result)

    # Devuelve la elección del padre, que conllevó a la génesis de este nodo.
    def parent_choice(self):
        return self._parent_choice


class MonteCarloHeuristic:
    """
    Heurística de MonteCarloTreeSearch.
    """
    @staticmethod
    @abstractmethod
    def heuristic(path: [MapObject], agent: Agent, env: Environment) -> float:
        """
        Método para cálculo de la heurística.
        """
        pass
