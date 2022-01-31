from __future__ import annotations
from dataclasses import dataclass, field
from math import inf, pow
from abc import abstractmethod
import heapq


@dataclass
class Place:
    """
    Clase lugar. Define las diferentes localizaciones del entorno simulado.
    """
    # Nombre para identificar la localización.
    name: str


@dataclass
class MapObject:
    """
    Clase objeto de entorno. Engloba a los elementos posibles de un entorno simulado.
    """
    # Identificador para distinguir los elementos.
    identifier: int
    # Lugar del entorno simulado en el que se encuentra la carga.
    position: Place

    @abstractmethod
    def update_state(self, env: Environment, event: Event) -> [Event]:
        """
        Actualiza el estado del objeto según las caracteristicas de este.
        """
        pass


@dataclass
class Cargo(MapObject):
    """
    Clase carga. Engloba los objeto cargables/transportables por un vehículo.
    """

    @abstractmethod
    def update_state(self, env: Environment, event: Event) -> [Event]:
        pass


@dataclass
class Event:
    """
    Clase evento. Engloba los diferentes sucesos de un ambiente simulado.
    """
    # Identificador del emisor del evento.
    issuer_id: int
    # Momento en que debe ocurrir el evento.
    time: int


@dataclass
class SetEvent(Event):
    """
    Evento de eliminacion. Indica al entorno simulado que debe eliminar el objeto del id correspondiente,
    en la posicion dada.
    """
    object: MapObject


@dataclass
class DeleteEvent(Event):
    """
    Evento de eliminacion. Indica al entorno simulado que debe eliminar el objeto del id correspondiente,
    en la posicion dada.
    """
    object_id: int
    position: Place


@dataclass
class MovementEvent(Event):
    """
    Evento de movimiento. Indica al vehículo correspondiente que debe moverse.
    """
    pass


@dataclass
class LoadEvent(Event):
    """
    Evento de carga. Indica al vehículo correspondiente que debe cargar el objeto con el id especificado.
    """
    cargo_identifier: int


@dataclass
class DownloadEvent(Event):
    """
    Evento de carga. Indica al vehículo correspondiente que debe cargar el objeto con el id especificado.
    """
    cargo_identifier: int


@dataclass
class Environment:
    @abstractmethod
    def get_places(self) -> [Place]:
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
    def get_all_objects(self, position: Place) -> [MapObject]:
        """
        Devuelve el listado de objetos localizados en la posición dada del entorno simulado.
        """
        pass

    @abstractmethod
    def get_object(self, position: Place, identifier: int) -> MapObject:
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
    def remove_object(self, position: Place, identifier: int) -> None:
        """
        Remueve al elemento dado en la posición especificada del entorno simulado.
        """
        pass


@dataclass
class Vehicle(MapObject):
    """
    Clase vehículo. Define los diferentes transportes del entorno simulado.
    """
    # Carga que actualmente desplaza el vehículo.
    cargos: [Cargo]
    # Recorrido del vehículo.
    tour: [str]

    def update_state(self, env: Environment, event: Event) -> [Event]:
        """
        Actualiza el estado del vehículo, dígase, moverse a la proxima posición,
        cargar un objeto, entre otras acciones.
        """
        # Si el evento afecta a este vehículo.
        if event.issuer_id == self.identifier:
            # Si queda recorrido, y el evento es un evento de movimiento.
            if len(self.tour) > 0 and isinstance(event, MovementEvent):
                # Desplazamos el vehículo una casilla.
                self.position = self.tour.pop()

                # Si el recorrido terminó, y hay carga.
                if len(self.tour) == 0:
                    if len(self.cargos) > 0:
                        # Emitimos la cantidad correspondiente de eventos de descarga.
                        return [DownloadEvent(self.identifier, cargo.identifier, event.time + 1)
                                for cargo in self.cargos]

                # En otro caso, varificamos si hay algo que cargar en la nueva posición.
                else:
                    cargos = self.something_to_charge(env)

                    # Si hay cargas, emitimos la cantidad correspondiente de eventos de carga,
                    # y un evento extra de movimiento.
                    if len(cargos) > 0:
                        events: [Event] = [LoadEvent(self.identifier, cargo.identifier, event.time + i + 1)
                                           for i, cargo in enumerate(cargos)]
                        # noinspection PyTypeChecker
                        events.append(MovementEvent(self.identifier, event.time + len(events) + 1))
                        return events

            # Si es un evento de carga, llamamos al método de carga.
            if isinstance(event, LoadEvent):
                self.load(event.cargo_identifier, env)

            # Si es un evento de descarga, llamamos al método de carga.
            if isinstance(event, DownloadEvent):
                self.download(event.cargo_identifier, env)

        # Si el vehículo está inactivo, busca un nuevo objetivo.
        if len(self.tour) == 0 and len(self.cargos) == 0:
            # Revisa los objetivos en el mapa.
            places = self.get_objectives(env)
            # Calcula el nuevo recorrido.
            self.tour = self.next_objective(places, env)

        # Mientras haya camino que recorrer, lanzamos un evento de movimiento, en caso contrario
        # no lanzamos nada.
        return [MovementEvent(self.identifier, event.time + 1)] if len(self.tour) != 0 else []

    @abstractmethod
    def something_to_charge(self, env: Environment) -> [Cargo]:
        """
        Indica si hay elementos de carga en la posición actual del vehículo dentro del ambiente
        simulado. En caso afirmativo devuelve una lista con los elementos cargables.
        """
        pass

    def load(self, cargo_id: int, env: Environment) -> None:
        """
        Carga el elemento en la posición actual con el identificador especificado.
        """
        # Obtenemos el elemento.
        element = env.get_object(self.position, cargo_id)
        # Si es una carga, lo montamos.
        if isinstance(element, Cargo):
            env.remove_object(self.position, cargo_id)
            self.cargos.append(element)

    def download(self, cargo_id, env: Environment) -> None:
        """
        Descarga el elemento con el identificador especificado en la posición actual.
        """
        # Obtenemos el elemento.
        for i in range(len(self.cargos)):
            # Obtenemos la carga.
            cargo = self.cargos[i]
            # Si el id de la carga es el especificado, encontramos la carga deseada.
            if cargo.identifier == cargo_id:
                env.set_object(cargo)
                self.cargos[i], self.cargos[-1] = self.cargos[-1], self.cargos[i]
                self.cargos.pop()
                break

    @abstractmethod
    def get_objectives(self, env: Environment) -> [Place]:
        """
        Localiza en el mapa los posibles recorridos del taxi.
        """
        pass

    @abstractmethod
    def next_objective(self, places: [Place], env: Environment) -> [Place]:
        """
        Escoge, entre una serie de localizaciones, la del próximo objetivo.
        """
        pass

    def get_pos(self) -> Place:
        """
        Devuelve la posición actual del vehiculo.
        """
        return self.position


@dataclass
class GraphEnvironment(Environment):
    edges: {str: {str: float}}
    places: {str: Place}
    objects: {str: {int: MapObject}}

    def get_places(self) -> [Place]:
        """
        Devuelve las localizaciones del entorno simulado.
        """
        return [place for place in self.places.value()]

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

    def get_all_objects(self, position: Place) -> [MapObject]:
        """
        Devuelve el listado de objetos localizados en la posición dada del entorno simulado.
        """
        return [element for element in self.objects.get(position.name, {}).values()]

    def get_object(self, position: Place, identifier: int) -> MapObject:
        """
        Devuelve el elemento del entorno simulado con el id especificado.
        """
        if position in self.objects and identifier in self.objects[position]:
            return self.objects[position.name][identifier]

    def set_object(self, element: MapObject) -> None:
        """
        Coloca al elemento dado en la posición especificada del entorno simulado.
        """
        if element.position.name in self.objects:
            self.objects[element.position.name][element.identifier] = element

    def remove_object(self, position: Place, identifier: int) -> None:
        """
        Remueve al elemento dado en la posición especificada del entorno simulado.
        """
        if position.name in self.objects and identifier in self.objects[position.name]:
            del self.objects[position.name][identifier]


class AStar:
    @staticmethod
    @abstractmethod
    def h(current: Place, destinations: [Place], principal_actor: MapObject, actors: [MapObject],
          graph: GraphEnvironment) -> float:
        """
        Heuristica de AStar, recibe todos los objetos de los cuales pudiera ser necesaria información
        para la heuristica, dígase, la posición actual, las posiciones destino, un agente distinguido
        (potencialmente el actor al que pertenece la IA), una lista de actores tener en cuenta y el
        entorno simulado.
        """
        pass

    @staticmethod
    @abstractmethod
    def actualize_objective(objective: Place, principal_actor: MapObject, actors: [MapObject],
                            graph: GraphEnvironment) -> None:
        """
        Método de actualizacion adyacente, recibe todos los objetos de los cuales pudiera ser necesaria
        información para actualizar el objetivo devuelto por AStar, dígase, la posición objetivo,
        un actor distinguido (potencialmente el actor al que pertenece la IA), una lista de actores
        tener en cuenta y el entorno simulado.
        """
        pass

    def algorithm(self, origin: Place, objectives: [Place], principal_actor: MapObject, actors: [MapObject],
                  graph: GraphEnvironment) -> [str]:
        """
        Algoritmo AStar.
        """

        # Conjunto salida.
        open_lst = {origin}

        # Conjunto llegada.
        closed_lst = set()

        # Lista de distancias.
        distances = dict()
        # La distancia del origen al origen es 0.
        distances[origin] = 0

        # Lista de padres (es una forma de representar el ast asociado al recorrido que
        # realiza AStar sobre el grafo).
        parents = dict()
        # El origen es su propio padre (es el inicio del camino).
        parents[origin] = origin

        # Mientras en el conjunto de salida queden elementos.
        while len(open_lst) > 0:
            # Instanciamos el vertice actual con el valor por defecto None.
            v = None

            # Por cada vértice w del conjunto salida.
            for w in open_lst:
                # Si aun no hemos instanciado v o bien el vértice w está más cerca
                # del conjunto llegada (según la heurística) que v, actualizamos v con w.
                if v is None or distances[w] + self.h(w, objectives, principal_actor, actors, graph) \
                        < distances[v] + self.h(v, objectives, principal_actor, actors, graph):
                    v = w

            # Si v esta directamente en el conjunto objetivo.
            if v in objectives:
                # Actualizamos la posición destino como objetivo del actor principal.
                self.actualize_objective(v, principal_actor, actors, graph)

                # Variable para guardar el camino.
                path = []

                # Mientras quede camino (mientras no encontremos un nodo que sea su propio padre, o sea,
                # no encontremos el origen).
                while parents[v] != v:
                    # Añadimos el vertice al camino.
                    path.append(v)
                    # Nos movemos al vertice padre.
                    v = parents[v]

                # Devolvemos el camino.
                return path

            # En caso de que v no sea del conjunto objetivo, visitamos cada adyacente w de v.
            for w in graph.edges[v]:
                # Obtenemos el peso del arco que los une.
                weight = graph.edges[v][w]
                # Si w no pertenece al conjunto origen ni al conjunto objetivo.
                if w not in open_lst and w not in closed_lst:
                    # Lo añadimos al conjunto origen ahora que fue visitado.
                    open_lst.add(w)
                    # Asignamos a v como su padre.
                    parents[w] = v
                    # Actualizamos el array de distancias consecuentemente.
                    distances[w] = distances[w] + weight
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

            open_lst.remove(v)
            closed_lst.add(v)

        return []


def infinity():
    return inf


def simulate_environment(env: Environment, initial_events: [Event], total_time: int):
    """
    Simula el entorno, evento a evento.
    """
    actual_event = None
    events = [event for event in initial_events]
    while len(events) > 0 and (actual_event := heapq.heappop(events)) and actual_event.time <= total_time:
        for event in env.update_state(actual_event):
            heapq.heappush(events, event)
        # Actualizamos cada objeto del entorno.
        for place in env.get_places():
            for map_object in env.get_all_objects(place):
                for event in env.get_object(place, map_object.identifier).update_state(env, actual_event):
                    heapq.heappush(events, event)
        # vehicle.report_state()
