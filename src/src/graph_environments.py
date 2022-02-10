from __future__ import annotations
from .base_classes import Event, SetEvent, DeleteEvent, GenerateEvent, MapObject, Agent, Position, Generator, \
    Environment


class GraphEnvironment(Environment):
    """
     Implementación particular de entorno, en el que hay noción de localizaciones y adyacencias entre estas.
     Está representado sobre un grafo.
    """
    graph: {str: {str: float}}
    objects: {str: {int: MapObject}}
    generators: {str: Generator}

    def __init__(self, graph: {str: {str: float}}, objects: {str: {int: MapObject}}, generators: {str: Generator}):
        # Guardamos el grafo y los objetos del entorno.
        self.graph = graph
        self.objects = objects
        self.generators = generators
        self.counter = 0

        # Nos aseguramos que la lista de objetos tenga el formato correcto.
        # Por cada localización del grafo.
        for place in graph:
            # Si en el listado de objetos no existe esta localización, la añadimos sin objetos.
            if place not in objects:
                self.objects[place] = {}

        # Si existe al menos una localización en la lista de objetos que no existe en el entorno,
        # lanzamos excepción.
        for place in objects:
            for object_id in self.objects[place]:
                self.counter = max(self.counter, object_id)
            if place not in graph:
                raise Exception("Invalid objects list.")

    def next(self):
        self.counter += 1
        return self.counter

    def get_places(self) -> [str]:
        """
        Devuelve las localizaciones del entorno simulado.
        """
        # Construimos una lista de localizaciones y la devolvemos.
        return [place for place in self.graph]

    def get_objects(self):
        """
        Devuelve los objetos del entorno.
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

        events = []

        # Si es un evento de borrado, borramos el elemento correspondiente en la posición dada.
        if isinstance(event, DeleteEvent):
            self.remove_object(event.position, event.object_id)

        # Si es un evento de adición, añadimos el elemento correspondiente.
        elif isinstance(event, SetEvent):
            event.object.identifier = self.next()
            self.set_object(event.object)

        elif isinstance(event, GenerateEvent) and event.generator_name in self.generators:
            map_object = self.generators[event.generator_name].generate(self.get_places())
            map_object.identifier = self.next()
            self.set_object(map_object)
            next_genesis = self.generators[event.generator_name].next(event.time)
            if next_genesis > event.time:
                events.append(GenerateEvent(next_genesis, event.issuer_id, event.generator_name))

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
        # Construimos una lista con los objetos en la posición dadda y la devolvemos.
        return [element for element in self.objects.get(position, {}).values()]

    def get_object(self, position: str, identifier: int) -> MapObject:
        """
        Devuelve el elemento del entorno simulado con el id especificado.
        """
        # Si en la posición dada existe un objeto con el id especificado, lo devolvemos.
        # En caso contrario devolvemos None.
        if position in self.objects and identifier in self.objects[position]:
            return self.objects[position][identifier]

    def set_object(self, element: MapObject) -> None:
        """
        Coloca al elemento dado en la posición especificada del entorno simulado.
        """
        # Si la posición especificada existe.
        if element.position in self.graph:
            # Guardamos el objeto dado en la posición especificada.
            self.objects[element.position][element.identifier] = element

    def remove_object(self, position: str, identifier: int) -> None:
        """
        Remueve al elemento dado en la posición especificada del entorno simulado.
        """
        # Si en la posición dada existe un objeto con el id especificado, lo eliminamos.
        if position in self.objects and identifier in self.objects[position]:
            del self.objects[position][identifier]


class MapEnvironment(GraphEnvironment):
    positions: {str: Position}

    def __init__(self, graph: {str: {str: float}}, objects: {str: {int: MapObject}}, positions: {str: Position},
                 generators: {str: Generator}):
        # Guardamos el grafo y los objetos del entorno.
        super().__init__(graph, objects, generators)

        # Guardamos las posiciones.
        self.positions = positions

        # Si existe al menos una localización en la lista de posiciones que no existe en el entorno,
        # lanzamos excepción.
        for place in positions:
            if place not in graph:
                raise Exception("Invalid positions list.")

        # Si existe al menos una localización en la lista de objetos que no existe en el entorno,
        # lanzamos excepción.
        for place in graph:
            if place not in positions:
                raise Exception("Invalid positions list.")

    def get_position(self, name: str) -> Position:
        """
        Devuelve la posición asociada a la localización que recibe como argumento.
        """
        return self.positions.get(name, None)
