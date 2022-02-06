from .base_classes import *
from .AStar import AStarM
from .environments import MapEnvironment
from random import choice


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
                    self.update_cargo(env.get_object(place, objective_id), env)

            # Si queda camino por recorrer, emitimos un evento de movimiento.
            return [MovementEvent(event.time + 1, self.identifier)] if self.tour else []

        # En caso que el evento no afecte a este vehículo, devolvemos una lista de eventos vacía.
        return []

    def load(self, cargo_id: int, env: Environment) -> None:
        """
        Carga el elemento en la posición actual con el identificador especificado.
        """

        # Obtenemos el elemento.
        cargo = env.get_object(self.position, cargo_id)
        # Obtenemos el destino del elemento.
        destiny = self.get_destiny(cargo, env)

        # Si obtenemos un destino correcto.
        if destiny:
            # Lo removemos del entorno.
            env.remove_object(self.position, cargo_id)

            # Si el destino no está en el diccionario de cargas, lo añadimos.
            if destiny not in self.cargos:
                self.cargos[destiny] = []

            # Lo guardamos en el diccionario de cargas, asociado a su destino.
            self.cargos[destiny].append(cargo)
            # Actualizamos el estado de la carga.
            self.update_cargo(cargo, env)

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
                self.update_cargo(cargos[i], env)

                # La colocamos en la posición actual del entorno.
                env.set_object(cargos[i])

                # La bajamos del vehiculo.
                cargos[i], cargos[-1] = cargos[-1], cargos[i]
                cargos.pop()

                # Si no hay mas cargas para este destino, lo borramos del diccionario de cargas.
                if not cargos:
                    del self.cargos[self.position]
                break

    def in_cargo(self, cargo_id: int) -> bool:
        for destiny in self.cargos:
            if cargo_id in self.cargos[destiny]:
                return True
        return False

    def get_cargos(self) -> [MapObject]:
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
    def update_cargo(self, cargo: MapObject, env: Environment) -> None:
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


class VehicleM(Vehicle):
    def __init__(self, identifier: int, position: str):
        super().__init__(identifier, position)
        self.IA = AStarM()

    @abstractmethod
    def update_cargo(self, cargo: MapObject, env: MapEnvironment) -> None:
        pass

    @abstractmethod
    def get_objectives_in(self, position: str, env: MapEnvironment) -> [MapObject]:
        pass

    @abstractmethod
    def get_objectives(self, env: MapEnvironment) -> [str]:
        pass

    @abstractmethod
    def get_destiny(self, cargo: MapObject, env: MapEnvironment) -> str:
        pass

    @staticmethod
    def select_objective(objectives: [MapObject], env: MapEnvironment) -> MapObject:
        return choice(objectives)

    def build_tour(self, objectives_positions: [str], env: MapEnvironment) -> {str: [int]}:
        objectives = []
        for position in objectives_positions:
            objectives.extend(self.get_objectives_in(position, env))
        objective = self.select_objective(objectives, env)
        destiny = self.get_destiny(objective, env)

        first_path = self.IA.algorithm(self.position, objective.position, [], env)
        second_path = self.IA.algorithm(objective.position, destiny, [], env)

        path = {position: [] for position in first_path}
        path.update({position: [] for position in second_path})
        path[destiny] = [objective.identifier]
        return path
