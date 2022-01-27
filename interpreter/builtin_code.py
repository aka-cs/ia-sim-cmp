from __future__ import annotations
from dataclasses import dataclass, field
from math import inf, pow
from abc import abstractmethod
import heapq


@dataclass
class Environment:

    def get_state(self):
        pass

    def update_state(self, event: Event) -> [Event]:
        pass


@dataclass
class GraphEnvironment(Environment):
    edges: [[int]]
    objects: dict[Position, object]

    def __getitem__(self, position: Position):
        return self.objects.get(position, None)

    @property
    def positions(self):
        return self.objects.keys()

    def get_vehicles(self):
        return {position: self.objects[position] for position in self.positions
                if isinstance(self.objects[position], Vehicle)}

    def get_cargos(self):
        return {position: self.objects[position] for position in self.positions
                if isinstance(self.objects[position], Cargo)}


class AStar:
    @staticmethod
    def h(current: Position, destinations: [Position], graph: GraphEnvironment) -> float:
        result: float = inf
        for destiny in destinations:
            result = min(result, (current.x - destiny.x)**2 + (current.y - destiny.y)**2)
        return result

    def a_star_algorithm(self, origin: Position, stop: [Position], graph: GraphEnvironment) -> [Position]:
        open_lst = {origin}
        closed_lst = set()

        distances = dict()
        distances[origin] = 0

        par = dict()
        par[origin] = origin

        while len(open_lst) > 0:
            n = None

            for v in open_lst:
                if n is None or distances[v] + self.h(v, stop, graph) < distances[n] + self.h(n, stop, graph):
                    n = v

            if n is None:
                return []

            if n in stop:
                path = []

                while par[n] != n:
                    path.append(n)
                    n = par[n]

                path.append(start)
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


@dataclass
class Position:
    x: int
    y: int


@dataclass
class Event:
    identifier: int
    time: int


@dataclass
class MovementEvent(Event):
    pass


@dataclass
class ChargeEvent(Event):
    cargo_identifier: int


@dataclass
class Cargo:
    identifier: int
    position: str
    disponible: bool = True


@dataclass
class Vehicle:
    identifier: int
    position: str
    cargo: [Cargo] = field(default_factory=list)
    path: [str] = field(default_factory=list)

    def update_state(self, env: Environment, event: Event) -> [Event]:
        """
        Actualiza el estado del vehículo, dígase, se mueve a la proxima posición y
        realiza el resto de acciones consecuentes.
        """
        if event.identifier == self.identifier:
            if len(self.path) > 0 and isinstance(event, MovementEvent):
                self.position = self.path.pop()

                if len(self.path) == 0:
                    if self.cargo:
                        self.cargo = None
                        return []

                cargos = self.something_to_charge()
                if len(cargos) > 0:
                    return [ChargeEvent(identifier=self.identifier, cargo_identifier=cargo.identifier,
                                        time=event.time + 1) for cargo in cargos]

            if isinstance(event, ChargeEvent):
                self.charge(event.cargo_identifier)

            return [MovementEvent(self.identifier, event.time + 1)]

        elif not self.cargo:
            positions = self.get_objetives(env)
            self.path = self.next_objetive(positions, env).reverse()
            return [MovementEvent(self.identifier, event.time + 1)]

    @abstractmethod
    def something_to_charge(self) -> [Cargo]:
        pass

    @abstractmethod
    def charge(self, cargo_id):
        pass

    @abstractmethod
    def get_objetives(self, env: Environment):
        pass

    @abstractmethod
    def next_objetive(self, positions, env: Environment):
        pass

    def get_pos(self):
        """
        Devuelve la posición actual del vehiculo.
        """
        return self.position

    def report_state(self):
        """
        Devuelve la posición a la que va el vehículo, y si lleva carga o no.
        """
        return self.position, self.path[0] if len(self.path) != 0 else None, self.cargo


def get_inf():
    return inf


def start(vehicle: Vehicle, env: Environment, total_time: int):
    time = 0
    events = [Event(0)]
    while events and (time := heapq.heappop(events).time) and time <= total_time:
        for event in env.update_state(time):
            heapq.heappush(events, event)
        for event in vehicle.update_state(env, time):
            heapq.heappush(events, event)
        vehicle.report_state()

