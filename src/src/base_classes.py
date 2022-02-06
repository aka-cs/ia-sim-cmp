from __future__ import annotations
from abc import abstractmethod
from dataclasses import dataclass
from .environments import Environment


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
class Position:
    x: int
    y: int
