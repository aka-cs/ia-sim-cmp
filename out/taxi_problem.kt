Person::Cargo {
    fun init(identifier: Int, position: String, destiny: String, payment: Int, actual_time: Float,
    waiting_time: Float) {
        // Clase persona.

        // Instanciamos la clase carga (de la que hereda persona) con el identificador y la posicion.
        self.super(identifier, position)
        // Destino de la persona, o sea, a donde se dirige.
        attr destiny: Position = destiny
        // Dinero que ofrece la persona por ser transportada.
        attr payment: Float = payment
        // Identificador del vehiculo que reservó la persona.
        attr reserved_id: Int = 0
        // Tiempo final hasta el que esperará la persona.
        attr final_time: Int = actual_time + waiting_time
    }

    fun update_state(env: Environment, event: Event): List<Event> {
        // Actualiza el estado de la persona.

        // Si la persona no ha reservado un vehículo, y se le acabó el tiempo,
        // lanza un evento de eliminacion (la persona se retira del entorno simulado).
        if(self.reserved_id == 0 && event.time >= final_time) {
            // Le colocamos un valor de reserva absurdo, para que no vuelva a ser escogida
            // hasta su eliminacion.
            self.reserved_id = -1
            // Lanzamos el evento de eliminacion.
            return [DeleteEvent(0, event.time + 1, self.identifier, self.position)]
        }
    }
}


Taxi::Vehicle
{
    fun init(identifier: Int, position: String) {
        // Clase vehiculo.

        // Instanciamos la clase vehículo (de la que hereda taxi) con el identificador y la posicion.
        self.super(identifier, position)
        // Instanciamos la inteligencia artificial del taxi con AStarT (AStar para la clase Taxi).
        self.IA = AStarT()
    }

    fun something_to_charge(env: GraphEnvironment){
        // Verifica si en la posicion actual hay objetos que cargar, y en caso positivo, devuelve una
        // lista de ellos.

        // Lista de objetos en la posicion actual.
        map_objects: List<MapObject> = graph.get_objects(self.position)
        // Listado de personas en la posicion actual, que han reservado este vehiculo.
        persons: List<Person> = []

        // Por cada objeto en el listado de objetos de la posicion actual.
        for(var map_object: map_objects){
            // Comprobamos el tipo de objeto.
            switch map_object:
                // Solo nos interesa si es una persona (el taxi solo carga personas).
                case Person{
                    // Si esta persona reservo este taxi, la montamos.
                    if(map_object.reserved_id == self.identifier){
                        person.append(map_object)
                    }
                }
                // En cualquier otro caso, ignoramos el objeto.
                default{}
        }

        // Devolvemos el listado de personas en la posicion actual, que han reservado este vehiculo.
        return persons
    }

    fun next_objective(positions: [Position], env: GraphEnvironment) {
        // El proximo objetivo esta determinado por la IA del taxi.
        return self.IA.algorithm(position, env)
    }
}


AStar::AStarT {
    fun measure(current: Position, person: Person, graph: GraphEnvironment): Float {
        // Calcula la medida que emplea la heuristica de AStarT.

        // Calculamos la distancia euclidiana entre la posicion actual y la posicion de la persona.
        distance: Float = pow(current.x - person.position.x, 2) + pow(current.y - person.position.y, 2)
        // Calculamos la distancia euclidiana entre la posicion de la persona y su destino.
        destiny_distance: Float = pow(pow(person.position.x - person.destiny.x, 2) +
                                      pow(person.position.y - person.destiny.y, 2), 1/2)
        // Devolvemos la suma de las distancias menos el precio a pagar.
        return distance + destiny_distance - person.payment
    }

    fun h(current: Position, destinations: [Position], taxi: Taxi, graph: GraphEnvironment): Float {
        // Heuristica de AStarT.

        // Instanciamos el mejor valor con un valor absurdo (infinito).
        result: Float = get_inf()

        // Por cada posicion destino posible.
        for(var destiny : destinations) {
            // Obtenemos la lista de objetos en la posicion actual.
            map_objects: List<MapObject> = graph.get_objects(destiny)

            // Por cada objeto en el listado de objetos de la posicion actual.
            for(var map_object: map_objects) {
                // Comprobamos el tipo de objeto.
                switch map_object:
                    // Solo nos interesa si es una persona (el taxi solo carga personas).
                    case Person {
                        // Calculamos el valor de la heuristica para esta persona y actualizamos el minimo.
                        if(map_object.reserved_id == 0){
                            result: Float = min(result, measure(current, person))
                        }
                    }
                    // En cualquier otro caso, ignoramos el objeto.
                    default {}
            }
        }
        // Devolvemos el minimo valor alcanzado.
        return result
    }

    fun actualize(current: Position, taxi: Taxi, graph: GraphEnvironment): Float {
        // Metodo para actualizar una posicion del entorno, dado un taxi y la posicion afectada.

        // Instanciamos el mejor valor con un valor absurdo (infinito).
        min_cost: Float = get_inf()
        // Instanciamos la persona vacia.
        person: Person = null
        // Obtenemos la lista de objetos en la posicion actual.
        map_objects: List<MapObject> = graph.get_objects(destiny)

        // Por cada objeto en el listado de objetos de la posicion actual.
        for(var map_object: map_objects) {
            // Comprobamos el tipo de objeto.
            switch map_object:
                // Solo nos interesa si es una persona (el taxi solo carga personas).
                case Person {
                    // Si esta persona no ha reservado este taxi.
                    if(map_object.reserved_id == 0){
                        // Calculamos el valor de la heuristica para ella.
                        cost = measure(current, person)
                        // Si mejora la obtenida hasta el momento.
                        if(min_cost > cost) {
                            // Actualizamos el mejor valor.
                            min_cost = cost
                            // Guardamos la persona.
                            person = map_object
                        }
                    }
                }
                // En cualquier otro caso, ignoramos el objeto.
                default {}
        }

        // Si encontramos la persona a montar, marcamos la reserva.
        if(person != null) {
            person.reserved_id = taxi.identifier
        }

        // Retornamos.
        return
    }
}







