from .environments import *
from typing import Union
from math import sqrt, inf


class AStar:
    @staticmethod
    @abstractmethod
    def heuristic(current: str, objective: str, actors: [MapObject], graph: GraphEnvironment) -> float:
        """
        Heuristica de AStar, recibe todos los objetos de los cuales pudiera ser necesaria información
        para calcular la heuristica, dígase, la posición actual, la posicion objetivo, una lista de
        actores tener en cuenta y el entorno simulado.
        """
        pass

    def algorithm(self, origin: str, destiny: str, actors: [MapObject], graph: GraphEnvironment) -> [str]:
        """
        Algoritmo AStar.
        """
        # Conjunto salida.
        open_lst: {str} = {origin}
        # Conjunto llegada.
        closed_lst: {str} = set()

        # Lista de distancias.
        distances: {str: float} = dict()
        # La distancia del origen al origen es 0.
        distances[origin] = 0

        # Lista de padres (es una forma de representar el ast asociado al recorrido que
        # realiza AStar sobre el grafo).
        parents: {str, str} = dict()
        # El origen es su propio padre (es el inicio del camino).
        parents[origin] = origin

        # Mientras en el conjunto de salida queden elementos.
        while open_lst:
            # Instanciamos el vertice actual con el valor por defecto None.
            v: Union[str, None] = None

            # Por cada vértice w del conjunto salida.
            for w in open_lst:
                # Si aun no hemos instanciado v o bien el vértice w está más cerca
                # del conjunto llegada (según la heurística) que v, actualizamos v con w.
                if v is None or distances[w] + self.heuristic(w, destiny, actors, graph) < \
                                distances[v] + self.heuristic(v, destiny, actors, graph):
                    v = w

            # Si v es el destino.
            if v == destiny:
                # Variable para guardar el camino.
                path: [str] = []

                # Mientras quede camino (mientras no encontremos un nodo que sea su propio padre, o sea,
                # no encontremos el origen).
                while parents[v] != v:
                    # Añadimos el vertice al camino.
                    path.append(v)
                    # Nos movemos al vertice padre.
                    v = parents[v]
                path.append(v)

                # Devolvemos el camino.
                return path

            # En caso de que v no sea del conjunto objetivo, visitamos cada adyacente w de v.
            for w in graph.edges[v]:
                # Obtenemos el peso del arco que los une.
                weight: float = graph.edges[v][w]
                # Si w no pertenece al conjunto origen ni al conjunto objetivo.
                if w not in open_lst and w not in closed_lst:
                    # Lo añadimos al conjunto origen ahora que fue visitado.
                    open_lst.add(w)
                    # Asignamos a v como su padre.
                    parents[w] = v
                    # Actualizamos el array de distancias consecuentemente.
                    distances[w] = distances[v] + weight
                # Si está en alguno de los dos conjuntos.
                else:
                    # Si pasar por v mejora el camino de costo minimo del origen a w,
                    # entonces pasamos por v.
                    if distances[w] > distances[v] + weight:
                        # Actualizamos la distancia.
                        distances[w] = distances[v] + weight
                        # Colocamos a v como padre de w.
                        parents[w] = v

                        # Si el vértice está en el conjunto de llegada.
                        if w in closed_lst:
                            closed_lst.remove(w)
                            open_lst.add(w)

            # Removemos el vertice del conjunto de salida y lo añadimos al de llegada.
            open_lst.remove(v)
            closed_lst.add(v)

        # Devolvemos un camino vacío en caso de que no haya solución.
        return []


class AStarM(AStar):
    @staticmethod
    def heuristic(current: str, objective: str, actors: [MapObject], map_env: MapEnvironment) -> float:
        if current not in map_env.positions or objective not in map_env.positions:
            return inf
        current_position: Position = map_env.positions[current]
        objective_position: Position = map_env.positions[objective]
        return sqrt((current_position.x - objective_position.x)**2
                    + (current_position.y - objective_position.y)**2)
