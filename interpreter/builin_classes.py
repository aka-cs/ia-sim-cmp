from builtin_base_classes import *


@dataclass
class Vehicle(Agent):
    """
    Clase vehículo. Define los diferentes transportes del entorno simulado.
    """
    # Cargas que actualmente desplaza el vehículo.
    cargos: {str: [MapObject]}
    # Recorrido del vehículo.
    tour: [str]

    def update_state(self, env: Environment, event: Event) -> [Event]:
        """
        Actualiza el estado del vehículo, dígase, moverse a la proxima posición,
        cargar un objeto, entre otras acciones.
        """
        # Verificamos si hay algo que cargar en la posición actual.
        cargos = self.something_to_charge(env)

        # Si hay cargas, emitimos la cantidad correspondiente de eventos de carga,
        # y un evento extra de movimiento.
        if cargos:
            events: [Event] = [LoadEvent(self.identifier, event.time + i + 1, cargo.identifier)
                               for i, cargo in enumerate(cargos)]
            # noinspection PyTypeChecker
            events.append(MovementEvent(self.identifier, self.identifier, event.time + len(events) + 1))
            return events

        # Si queda recorrido, y el evento es un evento de movimiento.
        if self.tour and isinstance(event, MovementEvent):
            # Movemos el vehiculo de posición.
            # Lo borramos de la casilla anterior.
            env.remove_object(self.position, self.identifier)
            # Actualizamos la posición.
            self.position = self.tour.pop()
            # Lo colocamos en la nueva casilla.
            env.set_object(self)

            # Si llegamos a una de las posiciones destino.
            if self.position.name in self.cargos:
                # Emitimos la cantidad correspondiente de eventos de descarga (una por cada objeto a descargar
                # en esta posición).
                events: [Event] = [DownloadEvent(self.identifier, event.time + 1, cargo.identifier)
                                   for cargo in self.cargos[self.position.name]]
                # noinspection PyTypeChecker
                events.append(MovementEvent(self.identifier, self.identifier, event.time + len(events) + 1))
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
            self.tour = self.build_tour(places, env)

        # Retornamos un evento de movimiento si hay camino, en caso contrario no lanzamos evento.
        return [MovementEvent(self.identifier, self.identifier, event.time + 1)] if self.tour else []

    def load(self, cargo_id: int, env: Environment) -> None:
        """
        Carga el elemento en la posición actual con el identificador especificado.
        """
        # Obtenemos el elemento.
        element = env.get_object(self.position, cargo_id)
        # Lo removemos del entorno.
        env.remove_object(self.position, cargo_id)
        # Obtenemos el destino del elemento.
        destiny = self.get_destiny(element, env)

        # Lo añadimos al listado de cargas, asociado a su destino.
        if destiny.name not in self.cargos:
            self.cargos[destiny.name] = []

        # Lo guardamos en el diccionario de cargas, asociado a su destino.
        self.cargos[destiny.name].append(element)

    def download(self, cargo_id: int, env: Environment) -> None:
        """
        Descarga el elemento con el identificador especificado en la posición actual.
        """
        # Por cada destino del taxi.
        for destiny in self.cargos:
            # Obtenemos la lista de cargas del taxi asociadas a este destino.
            cargos: [MapObject] = self.cargos[destiny]

            # Por cada carga.
            for i in range(len(cargos)):
                # Si el id de la carga es el especificado, encontramos la carga deseada.
                if cargos[i].identifier == cargo_id:
                    # Actualizamos el estado de la carga.
                    self.actualize_cargo(cargos[i], env)
                    # La colocamos en la posición actual del entorno.
                    env.set_object(cargos[i])
                    # La bajamos del vehiculo.
                    cargos[i], cargos[-1] = cargos[-1], cargos[i]
                    cargos.pop()
                    # Si no hay mas cargas para este destino, lo borramos del diccionario de cargas.
                    if not cargos:
                        del self.cargos[destiny]
                    break

    def get_destiny(self, cargo: MapObject, env: Environment) -> Place:
        """
        Obtiene el destino del elemento especificado.
        """
        pass

    def actualize_cargo(self, cargo: MapObject, env: Environment) -> None:
        """
        Actualiza el estado de una carga.
        """
        cargo.position = self.position

    @abstractmethod
    def something_to_charge(self, env: Environment) -> [MapObject]:
        """
        Indica si hay elementos de carga en la posición actual del vehículo dentro del ambiente
        simulado. En caso afirmativo devuelve una lista con los elementos cargables.
        """
        pass

    @abstractmethod
    def get_objectives(self, env: Environment) -> [Place]:
        """
        Localiza en el mapa los posibles objetivos del taxi.
        """
        pass

    @abstractmethod
    def build_tour(self, objectives: [Place], env: Environment) -> [Place]:
        """
        Escoge, entre una serie de localizaciones, la del próximo objetivo.
        """
        pass


@dataclass
class GraphEnvironment(Environment):
    edges: {str: {str: float}}
    places: {str: Place}
    objects: {str: {int: MapObject}}

    def get_place(self, name) -> Place:
        """
        Devuelve las localizaciones del entorno simulado.
        """
        return self.places.get(name, None)

    def get_places(self) -> [Place]:
        """
        Devuelve las localizaciones del entorno simulado.
        """
        return [place for place in self.places.values()]

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
        for place in self.places:
            for map_object in self.objects[place]:
                if isinstance(map_object, Agent):
                    events.extend(map_object.update_state(event, self))

        # Lanzamos los eventos obtenidos.
        return events

    def get_all_objects(self, position: Place) -> [MapObject]:
        """
        Devuelve el listado de objetos localizados en la posición dada del entorno simulado.
        """
        return [element for element in self.objects.get(position.name, {}).values()]

    def get_object(self, position: Place, identifier: int) -> MapObject:
        """
        Devuelve el elemento del entorno simulado con el id especificado.
        """
        if position.name in self.objects and identifier in self.objects[position.name]:
            return self.objects[position.name][identifier]

    def set_object(self, element: MapObject) -> None:
        """
        Coloca al elemento dado en la posición especificada del entorno simulado.
        """
        if element.position.name in self.places:
            if element.position.name not in self.objects:
                self.objects[element.position.name] = {}
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
    def actualize_destiny(objective: Place, principal_actor: MapObject, actors: [MapObject],
                          graph: GraphEnvironment) -> Place:
        """
        Método de para obtener el destino final luego de alcanzar el objetivo, recibe todos los
        objetos de los cuales pudiera ser necesaria información para actualizar el objetivo devuelto
        por AStar, dígase, la posición objetivo, un actor distinguido (potencialmente el actor al que
        pertenece la IA), una lista de actores tener en cuenta y el entorno simulado.
        """
        pass

    def algorithm(self, origin: Place, objectives: [Place], principal_actor: MapObject, actors: [MapObject],
                  graph: GraphEnvironment) -> [Place]:
        """
        Algoritmo AStar.
        """
        # Conjunto salida.
        open_lst: {str} = {origin.name}

        # Conjunto llegada.
        closed_lst: {str} = set()

        # Lista de distancias.
        distances: {str: float} = dict()
        # La distancia del origen al origen es 0.
        distances[origin.name] = 0

        # Lista de padres (es una forma de representar el ast asociado al recorrido que
        # realiza AStar sobre el grafo).
        parents: {str, str} = dict()
        # El origen es su propio padre (es el inicio del camino).
        parents[origin.name] = origin.name

        # Variable que determina si ya se encontró el objetivo.
        objective_found: bool = False

        # Variable para guardar el primer fragmento del recorrido total.
        objective_path: [Place] = []

        # Variable para guardar el camino.
        path: [Place] = []

        # Mientras en el conjunto de salida queden elementos.
        while len(open_lst) > 0:
            # Instanciamos el vertice actual con el valor por defecto None.
            v: Union[str, None] = None

            # Por cada vértice w del conjunto salida.
            for w in open_lst:
                # Si aun no hemos instanciado v o bien el vértice w está más cerca
                # del conjunto llegada (según la heurística) que v, actualizamos v con w.
                if v is None or distances[w] + (self.h(graph.get_place(w), objectives, principal_actor, actors, graph)
                                                if not objective_found else 0) < \
                                distances[v] + (self.h(graph.get_place(v), objectives, principal_actor, actors, graph)
                                                if not objective_found else 0):
                    v = w

            # Si v esta directamente en el conjunto objetivo.
            if graph.get_place(v) in objectives:
                # Mientras quede camino (mientras no encontremos un nodo que sea su propio padre, o sea,
                # no encontremos el origen).
                while parents[v] != v:
                    # Añadimos el vertice al camino.
                    path.append(graph.get_place(v))
                    # Nos movemos al vertice padre.
                    v = parents[v]

                if objective_found:
                    # Unimos las mitades y devolvemos el camino.
                    path.extend(objective_path)
                    return path

                else:
                    # Establecemos el nuevo origen.
                    new_origin = path[-1] if path else origin

                    # Guardamos el camino construido y reiniciamos el camino.
                    objective_path = path
                    path = []

                    # Encontramos el objetivo.
                    objective_found = True

                    # Reiniciamos las variables, para hallar ahora el camino del objetivo a su destino.
                    objectives = [self.actualize_destiny(new_origin, principal_actor, actors, graph)]

                    # Conjunto salida.
                    open_lst: {str} = {new_origin.name}

                    # Conjunto llegada.
                    closed_lst: {str} = set()

                    # Lista de distancias.
                    distances: {str: float} = dict()
                    # La distancia del origen al origen es 0.
                    distances[new_origin.name] = 0

                    # Lista de padres (es una forma de representar el ast asociado al recorrido que
                    # realiza AStar sobre el grafo).
                    parents: {str, str} = dict()
                    # El origen es su propio padre (es el inicio del camino).
                    parents[new_origin.name] = new_origin.name

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

            open_lst.remove(v)
            closed_lst.add(v)

        return []
