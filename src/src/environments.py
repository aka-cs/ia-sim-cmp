from base_classes import *


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


@dataclass
class MapEnvironment(GraphEnvironment):
    positions: {str: Position}

    def get_position(self, name: str) -> Position:
        return self.positions.get(name, None)
