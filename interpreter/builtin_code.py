from __future__ import annotations
from dataclasses import dataclass, field
from math import inf, pow
from abc import abstractmethod
import heapq


@dataclass
class MapObject:
    """
    Clase objeto de entorno. Engloba a los elementos posibles de un entorno simulado.
    """
    # Identificador para distinguir los elementos.
    identifier: int


@dataclass
class Place:
    """
    Clase lugar. Define las diferentes localizaciones del entorno simulado.
    """
    # Nombre para identificar la localización.
    name: str


@dataclass
class Cargo:
    """
    Clase carga. Engloba los objeto cargables/transportables por un vehículo.
    """
    # Identificador para distinguir las cargas.
    identifier: int
    # Lugar del entorno simulado en el que se encuentra la carga.
    position: Place


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
class DeleteEvent(Event):
    """
    Evento de eliminacion. Indica al entorno simulado que debe eliminar el objeto del id correspondiente,
    en la posicion dada.
    """
    object_id: str
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
    def places(self) -> [Place]:
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
    def set_object(self, position: Place, element: MapObject) -> None:
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
    # Lugar del entorno simulado en el que se encuentra el vehículo.
    position: Place
    # Carga que actualmente desplaza el vehículo.
    cargos: [Cargo] = field(default_factory=list)
    # Recorrido del vehículo.
    tour: [str] = field(default_factory=list)

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
            self.tour = self.next_objective(places, env).reverse()

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
                env.set_object(self.position, cargo)
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
    def next_objective(self, places: str, env: Environment) -> [Place]:
        """
        Escoge, entre una serie de localizaciones, la del próximo objetivo.
        """
        pass

    def get_pos(self) -> Place:
        """
        Devuelve la posición actual del vehiculo.
        """
        return self.position

    def report_state(self) -> (Place, [Place], [Cargo]):
        """
        Devuelve la posición actual y recorrido del vehículo, y si lleva carga o no.
        """
        return self.position, self.tour, self.cargos


@dataclass
class GraphEnvironment(Environment):
    edges: dict[Place, [Place]]
    objects: dict[Place, dict[int, MapObject]]

    def places(self) -> [Place]:
        """
        Devuelve las localizaciones del entorno simulado.
        """
        return [place for place in self.objects.keys()]

    def update_state(self, event: Event) -> [Event]:
        """
        Dado un evento, actualiza el entorno simulado.
        """
        pass

    def get_all_objects(self, position: Place) -> [MapObject]:
        """
        Devuelve el listado de objetos localizados en la posición dada del entorno simulado.
        """
        return [element for element in self.objects.get(position, {}).values()]

    def get_object(self, position: Place, identifier: int) -> MapObject:
        """
        Devuelve el elemento del entorno simulado con el id especificado.
        """
        if position in self.objects and identifier in self.objects[position]:
            return self.objects[position][identifier]

    def set_object(self, position: Place, element: MapObject) -> None:
        """
        Coloca al elemento dado en la posición especificada del entorno simulado.
        """
        if position in self.objects:
            self.objects[position][element.identifier] = element

    def remove_object(self, position: Place, identifier: int) -> None:
        """
        Remueve al elemento dado en la posición especificada del entorno simulado.
        """
        if position in self.objects and identifier in self.objects[position]:
            del self.objects[position][identifier]


class AStar:
    @staticmethod
    @abstractmethod
    def h(current: str, destinations: [Place], actor: MapObject, graph: GraphEnvironment) -> float:
        pass

    @staticmethod
    @abstractmethod
    def actualize(place: str, actor: MapObject, graph: GraphEnvironment):
        pass

    def algorithm(self, origin: str, stop: [str], actor: MapObject, graph: GraphEnvironment) -> [str]:
        open_lst = {origin}
        closed_lst = set()

        distances = dict()
        distances[origin] = 0

        par = dict()
        par[origin] = origin

        while len(open_lst) > 0:
            n = None

            for v in open_lst:
                if n is None or distances[v] + self.h(v, stop, actor, graph) \
                        < distances[n] + self.h(n, stop, actor, graph):
                    n = v

            if n is None:
                return []

            if n in stop:
                path = []

                while par[n] != n:
                    path.append(n)
                    self.actualize(n, actor, graph)
                    n = par[n]

                path.reverse()
                return path

            for (m, weight) in graph.edges[n]:
                if m not in open_lst and m not in closed_lst:
                    open_lst.add(m)
                    par[m] = n
                    distances[m] = distances[n] + weight
                else:
                    if distances[m] > distances[n] + weight:
                        distances[m] = distances[n] + weight
                        par[m] = n

                        if m in closed_lst:
                            closed_lst.remove(m)
                            open_lst.add(m)

            open_lst.remove(n)
            closed_lst.add(n)

        return []


def get_inf():
    return inf


def start(vehicle: Vehicle, env: Environment, total_time: int):
    time = 0
    events = [Event(0, 0)]
    while events and (time := heapq.heappop(events).time) and time <= total_time:
        for event in env.update_state(time):
            heapq.heappush(events, event)
        for event in vehicle.update_state(env, time):
            heapq.heappush(events, event)
        vehicle.report_state()
