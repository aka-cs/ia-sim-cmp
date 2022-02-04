from __future__ import annotations
from dataclasses import dataclass
from abc import abstractmethod
from typing import Union
from math import inf
import heapq


@dataclass
class MapObject:
    """
    Clase objeto de entorno. Engloba a los elementos posibles de un entorno simulado.
    """
    # Identificador para distinguir los elementos.
    identifier: int
    # Lugar del entorno simulado en el que se encuentra la carga.
    position: str


@dataclass
class Agent(MapObject):
    """
    Clase agente. Engloba a los elementos que pueden actuar en el entorno.
    """

    @abstractmethod
    def update_state(self, event: Event, env: Environment) -> [Event]:
        """
        Actualiza el estado del objeto según las caracteristicas de este.
        """
        pass


@dataclass
class Event:
    """
    Clase evento. Engloba los diferentes sucesos de un ambiente simulado.
    """
    # Momento en que debe ocurrir el evento.
    time: int
    # Identificador del emisor del evento.
    issuer_id: int

    # Comparador de eventos. Los eventos se comparan por el tiempo de emisión.
    def __le__(self, other: Event):
        return self.time <= other.time

    def __lt__(self, other: Event):
        return self.time < other.time

    def __ge__(self, other: Event):
        return self.time >= other.time

    def __gt__(self, other: Event):
        return self.time > other.time

    def __eq__(self, other: Event):
        return self.time == other.time


@dataclass
class SetEvent(Event):
    """
    Evento de adición. Indica al entorno simulado que debe añadir el objeto correspondiente,
    en la posicion que este especifica.
    """
    object: MapObject


@dataclass
class DeleteEvent(Event):
    """
    Evento de eliminacion. Indica al entorno simulado que debe eliminar el objeto del id correspondiente,
    en la posicion dada.
    """
    object_id: int
    position: str


@dataclass
class MovementEvent(Event):
    """
    Evento de movimiento. Indica al objeto con el id correspondiente que debe moverse.
    """
    pass


@dataclass
class LoadEvent(Event):
    """
    Evento de carga. Indica al vehículo correspondiente que debe cargar el objeto con el id especificado,
    en la posición actual del vehiculo.
    """
    cargo_identifier: int


@dataclass
class DownloadEvent(Event):
    """
    Evento de descarga. Indica al vehículo correspondiente que debe descargar el objeto con el id especificado,
    en la posición actual del vehiculo.
    """
    cargo_identifier: int


@dataclass
class Environment:
    @abstractmethod
    def get_places(self) -> [str]:
        """
        Devuelve las localizaciones del entorno simulado.
        """
        pass

    @abstractmethod
    def update_state(self, event: Event) -> [Event]:
        """
        Dado un evento, actualiza el entorno simulado.
        """
        pass

    @abstractmethod
    def get_all_objects(self, position: str) -> [MapObject]:
        """
        Devuelve el listado de objetos localizados en la posición dada del entorno simulado.
        """
        pass

    @abstractmethod
    def get_object(self, position: str, identifier: int) -> MapObject:
        """
        Devuelve el elemento del entorno simulado con el id especificado.
        """
        pass

    @abstractmethod
    def set_object(self, element: MapObject) -> None:
        """
        Coloca al elemento dado en la posición especificada del entorno simulado.
        """
        pass

    @abstractmethod
    def remove_object(self, position: str, identifier: int) -> None:
        """
        Remueve al elemento del id especificado de la posición dada en el entorno simulado.
        """
        pass


class Vehicle(Agent):
    """
    Clase vehículo. Define los diferentes transportes del entorno simulado.
    """

    def __init__(self, identifier: int, position: str):
        super().__init__(identifier, position)
        # Cargas que actualmente desplaza el vehículo.
        self.cargos: {str: [MapObject]} = {}
        # Objetivos del taxi.
        self.objectives: [[int]] = []
        # Recorrido del vehículo.
        self.tour: [str] = []

    def update_state(self, event: Event, env: Environment) -> [Event]:
        """
        Actualiza el estado del vehículo, dígase, moverse a la proxima posición,
        cargar un objeto, entre otras acciones.
        """

        # Si el evento afecta a este vehiculo.
        if event.issuer_id == self.identifier:
            # Si queda recorrido, y el evento es un evento de movimiento.
            if self.tour and isinstance(event, MovementEvent):
                # Movemos el vehiculo de posición.
                # Lo borramos de la casilla anterior.
                env.remove_object(self.position, self.identifier)
                # Actualizamos la posición.
                self.position = self.tour.pop()
                # Lo colocamos en la nueva casilla.
                env.set_object(self)

                # Obtenemos los objetivos a cargar en la posición actual.
                cargos: [int] = self.objectives.pop()

                # Lista de eventos a devolver.
                events: [Event] = []

                # Si llegamos a una de las posiciones destino.
                if self.position in self.cargos:
                    # Emitimos la cantidad correspondiente de eventos de descarga (una por cada objeto a descargar
                    # en esta posición).
                    events.extend([DownloadEvent(event.time + 1, self.identifier, cargo.identifier)
                                   for i, cargo in enumerate(self.cargos[self.position])])

                # Si hay cargas, emitimos la cantidad correspondiente de eventos de carga.
                if cargos:
                    events.extend([LoadEvent(event.time + i + 1, self.identifier, cargo_id)
                                   for i, cargo_id in enumerate(cargos) if env.get_object(self.position, cargo_id)])

                # Si queda camino por recorrer.
                if self.tour:
                    # Añadimos un evento de movimiento.
                    events.append(MovementEvent((events[-1].time if events else event.time) + 1, self.identifier))

                # Lanzamos el listado de eventos.
                return events

            # Si es un evento de carga, llamamos al método de carga.
            if isinstance(event, LoadEvent):
                self.load(event.cargo_identifier, env)
                return []

            # Si es un evento de descarga, llamamos al método de carga.
            if isinstance(event, DownloadEvent):
                self.download(event.cargo_identifier, env)
                return []

        # Si el vehículo está inactivo, busca un nuevo objetivo.
        if not self.tour and not self.cargos:
            # Revisa los objetivos en el mapa.
            places = self.get_objectives(env)

            # Calcula el nuevo recorrido.
            tour = self.build_tour(places, env)
            # Por cada localizacion del recorrido.
            for place in tour:
                # Añadimos la localizacion al tour del vehículo.
                self.tour.append(place)
                # Añadimos los objetivos en esta posición a la lista de objetivos.
                self.objectives.append(tour[place])

                # Actualizamos el estado de cada objeto objetivo.
                for objective_id in tour[place]:
                    self.actualize_cargo(env.get_object(place, objective_id), env)

            # Si queda camino por recorrer, emitimos un evento de movimiento.
            return [MovementEvent(event.time + 1, self.identifier)] if self.tour else []

        # En caso que el evento no afecte a este vehículo, devolvemos una lista de eventos vacía.
        return []

    def load(self, cargo_id: int, env: Environment) -> None:
        """
        Carga el elemento en la posición actual con el identificador especificado.
        """

        # Obtenemos el elemento.
        element = env.get_object(self.position, cargo_id)
        # Obtenemos el destino del elemento.
        destiny = self.get_destiny(element, env)

        # Si obtenemos un destino correcto.
        if destiny:
            # Lo removemos del entorno.
            env.remove_object(self.position, cargo_id)

            # Si el destino no está en el diccionario de cargas, lo añadimos.
            if destiny not in self.cargos:
                self.cargos[destiny] = []

            # Lo guardamos en el diccionario de cargas, asociado a su destino.
            self.cargos[destiny].append(element)

    def download(self, cargo_id: int, env: Environment) -> None:
        """
        Descarga el elemento con el identificador especificado en la posición actual.
        """
        # Obtenemos la lista de cargas del taxi asociadas a este destino.
        cargos: [MapObject] = self.cargos[self.position]

        # Por cada carga.
        for i in range(len(cargos)):
            # Si el id de la carga es el especificado, encontramos la carga deseada.
            if cargos[i].identifier == cargo_id:
                # Actualizamos el estado de la carga.
                cargos[i].position = self.position
                self.actualize_cargo(cargos[i], env)

                # La colocamos en la posición actual del entorno.
                env.set_object(cargos[i])

                # La bajamos del vehiculo.
                cargos[i], cargos[-1] = cargos[-1], cargos[i]
                cargos.pop()

                # Si no hay mas cargas para este destino, lo borramos del diccionario de cargas.
                if not cargos:
                    del self.cargos[self.position]
                break

    def get_cargos(self):
        """
        Devuelve las cargas del vehículo.
        """
        # Lista para guardar las cargas del vehículo.
        cargos = []
        # Por cada destino del vehículo.
        for destiny in self.cargos:
            # Añadimos las cargas asociadas a este destino.
            cargos.extend(self.cargos[destiny])
        # Devolvemos el listado de cargas.
        return cargos

    @abstractmethod
    def actualize_cargo(self, cargo: MapObject, env: Environment) -> None:
        """
        Actualiza el estado de una carga.
        """
        pass

    @abstractmethod
    def get_destiny(self, cargo: MapObject, env: Environment) -> str:
        """
        Obtiene el destino del elemento especificado.
        """
        pass

    @abstractmethod
    def get_objectives(self, env: Environment) -> [str]:
        """
        Localiza en el mapa los posibles objetivos del taxi.
        """
        pass

    @abstractmethod
    def build_tour(self, objectives: [str], env: Environment) -> {str: [int]}:
        """
        Escoge, entre una serie de localizaciones, la del próximo objetivo.
        """
        pass


@dataclass
class GraphEnvironment(Environment):
    edges: {str: {str: float}}
    objects: {str: {int: MapObject}}

    def get_places(self) -> [str]:
        """
        Devuelve las localizaciones del entorno simulado.
        """
        return [place for place in self.edges]

    def get_objects(self):
        """
        Devuelve las objetos del entorno.
        """
        # Lista para guardar las objetos del entorno.
        map_objects = []
        # Por cada destino del vehículo.
        for place in self.objects:
            # Añadimos las cargas asociadas a este destino.
            map_objects.extend(self.get_all_objects(place))
        # Devolvemos el listado de objetos.
        return map_objects

    def update_state(self, event: Event) -> [Event]:
        """
        Dado un evento, actualiza el entorno simulado.
        """

        # Si es un evento de borrado, borramos el elemento correspondiente en la posición dada.
        if isinstance(event, DeleteEvent):
            self.remove_object(event.position, event.object_id)

        # Si es un evento de adición, añadimos el elemento correspondiente.
        elif isinstance(event, SetEvent):
            self.set_object(event.object)

        events = []

        # Actualizamos cada objeto del entorno.
        for map_object in self.get_objects():
            # Si es un agente, actualizamos su estado.
            if isinstance(map_object, Agent):
                events.extend(map_object.update_state(event, self))

        # Lanzamos los eventos obtenidos.
        return events

    def get_all_objects(self, position: str) -> [MapObject]:
        """
        Devuelve el listado de objetos localizados en la posición dada del entorno simulado.
        """
        return [element for element in self.objects.get(position, {}).values()]

    def get_object(self, position: str, identifier: int) -> MapObject:
        """
        Devuelve el elemento del entorno simulado con el id especificado.
        """
        if position in self.objects and identifier in self.objects[position]:
            return self.objects[position][identifier]

    def set_object(self, element: MapObject) -> None:
        """
        Coloca al elemento dado en la posición especificada del entorno simulado.
        """
        if element.position in self.edges:
            if element.position not in self.objects:
                self.objects[element.position] = {}
            self.objects[element.position][element.identifier] = element

    def remove_object(self, position: str, identifier: int) -> None:
        """
        Remueve al elemento dado en la posición especificada del entorno simulado.
        """
        if position in self.objects and identifier in self.objects[position]:
            del self.objects[position][identifier]


class AStar:
    @staticmethod
    @abstractmethod
    def h(current: str, destinations: [str], actors: [MapObject], graph: GraphEnvironment) -> float:
        """
        Heuristica de AStar, recibe todos los objetos de los cuales pudiera ser necesaria información
        para calcular la heuristica, dígase, la posición actual, las posiciones destino, un agente
        distinguido (potencialmente el actor al que pertenece la IA), una lista de actores tener en
        cuenta y el entorno simulado.
        """
        pass

    @staticmethod
    @abstractmethod
    def get_objectives(objective: str, actors: [MapObject], graph: GraphEnvironment) -> [int]:
        """
        Método de para obtener el destino final luego de alcanzar el objetivo, recibe todos los
        objetos de los cuales pudiera ser necesaria información para ello, dígase, la posición
        objetivo, un actor distinguido (potencialmente el actor al que pertenece la IA), una lista
        de actores tener en cuenta y el entorno simulado.
        """
        pass

    @staticmethod
    @abstractmethod
    def actualize_destiny(objective: str, objective_ids: [int], actors: [MapObject], graph: GraphEnvironment) -> str:
        """
        Método de para obtener el destino final luego de alcanzar el objetivo, recibe todos los
        objetos de los cuales pudiera ser necesaria información para ello, dígase, la posición
        objetivo, el id del objetivo, un actor distinguido (potencialmente el actor al que pertenece
        la IA), una lista de actores tener en cuenta y el entorno simulado.
        """
        pass

    def algorithm(self, origin: str, objective_positions: [str], actors: [MapObject],
                  graph: GraphEnvironment) -> {str: [int]}:
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

        # Objetivos encontrados.
        objectives_found: [int] = []

        # Variable para guardar el primer fragmento del recorrido total.
        objective_path: [str] = []

        # Variable para guardar el camino.
        path: [str] = []

        # Mientras en el conjunto de salida queden elementos.
        while open_lst:
            # Instanciamos el vertice actual con el valor por defecto None.
            v: Union[str, None] = None

            # Por cada vértice w del conjunto salida.
            for w in open_lst:
                # Si aun no hemos instanciado v o bien el vértice w está más cerca
                # del conjunto llegada (según la heurística) que v, actualizamos v con w.
                if v is None or distances[w] + (self.h(w, objective_positions, actors, graph)
                                                if not objectives_found else 0) < \
                                distances[v] + (self.h(v, objective_positions, actors, graph)
                                                if not objectives_found else 0):
                    v = w

            # Si v esta directamente en el conjunto objetivo.
            if v in objective_positions:
                # Mientras quede camino (mientras no encontremos un nodo que sea su propio padre, o sea,
                # no encontremos el origen).
                while parents[v] != v:
                    # Añadimos el vertice al camino.
                    path.append(v)
                    # Nos movemos al vertice padre.
                    v = parents[v]
                path.append(v)

                if objectives_found:
                    # Unimos las mitades y devolvemos el camino.
                    tour: {str: [int]} = {place: [] for place in path}
                    tour.update({place: [] for place in objective_path})
                    tour[objective_path[0]] = objectives_found
                    return tour

                else:
                    # Establecemos el nuevo origen.
                    new_origin = path[0] if path else origin

                    # Guardamos el camino construido y reiniciamos el camino.
                    objective_path = path
                    path = []

                    # Encontramos el objetivo.
                    objectives_found = self.get_objectives(new_origin, actors, graph)

                    # Reiniciamos las variables, para hallar ahora el camino del objetivo a su destino.
                    objective_positions = [self.actualize_destiny(new_origin, objectives_found, actors, graph)]

                    # Conjunto salida.
                    open_lst: {str} = {new_origin}

                    # Conjunto llegada.
                    closed_lst: {str} = set()

                    # Lista de distancias.
                    distances: {str: float} = dict()
                    # La distancia del origen al origen es 0.
                    distances[new_origin] = 0

                    # Lista de padres (es una forma de representar el ast asociado al recorrido que
                    # realiza AStar sobre el grafo).
                    parents: {str, str} = dict()
                    # El origen es su propio padre (es el inicio del camino).
                    parents[new_origin] = new_origin

                    # Regresamos al inicio del ciclo para computar el problema del nuevo inicio al nuevo objetivo.
                    continue

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

        # Devolvemos un diccionario vacio en caso de no hallar solución.
        return {}


def infinity() -> float:
    return inf


def simulate_environment(env: Environment, initial_events: [Event], total_time: int) -> None:
    """
    Simula el entorno, evento a evento.
    """
    actual_event = None
    events = [event for event in initial_events]
    while events and (actual_event := heapq.heappop(events)) and actual_event.time <= total_time:
        for event in env.update_state(actual_event):
            heapq.heappush(events, event)

        # Imprimimos los resultados de cada evento en la simulación.
        print(f"\nTime: {actual_event.time}")
        for place in env.get_places():
            for map_object in env.get_all_objects(place):
                print(f"{map_object.position}: {type(map_object).__name__} {map_object.identifier} "
                      f"{[cargo.identifier for cargo in map_object.get_cargos()] if isinstance(map_object, Vehicle) else ''}")

