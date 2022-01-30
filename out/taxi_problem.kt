Position::Place{
    fun init(name: String, x: Int, y: Int){
        // Clase posición.

        // Instanciamos la clase lugar, con el nombre.
        self.super(name)

        // Instanciamos las coordenadas.
        attr x = x
        attr y = y
    }
}


Person::Cargo{
    fun init(identifier: Int, position: Position, destiny: Position, payment: Int, actual_time: Int,
    waiting_time: Int){
        // Clase persona.

        // Instanciamos la clase carga (de la que hereda persona) con el identificador y la posición.
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

    fun update_state(env: Environment, event: Event): List<Event>{
        // Actualiza el estado de la persona.

        // Si la persona no ha reservado un vehículo, y se le acabó el tiempo,
        // lanza un evento de eliminación (la persona es retirada del entorno simulado).
        if(self.reserved_id == 0 && event.time >= final_time){
            // Le colocamos un valor de reserva absurdo, para que no vuelva a ser escogida
            // hasta su eliminacion.
            self.reserved_id = -1
            // Lanzamos el evento de eliminación.
            return [DeleteEvent(0, event.time + 1, self.identifier, self.position)]
        }
    }
}


Taxi::Vehicle
{
    fun init(identifier: Int, position: String){
        // Clase vehiculo.

        // Instanciamos la clase vehículo (de la que hereda taxi) con el identificador y la posición.
        self.super(identifier, position)
        // Instanciamos la inteligencia artificial del taxi con AStarT (AStar para la clase Taxi).
        self.IA = AStarT()
    }

    fun something_to_charge(env: GraphEnvironment): List<Person>{
        // Verifica si en la posicion actual hay objetos que cargar, y en caso positivo, devuelve una
        // lista de ellos.
        // En el caso del taxi, dado que carga una sola persona a la vez, la lista siempre será unaria.

        // Obtenemos la lista de objetos en la posicion actual. Para este problema trivial, en cada
        // posicion del entorno habrá solo un objeto, por lo que la lista será unaria.
        map_object: List<MapObject> = graph.get_objects(self.position)[0]

        // Comprobamos el objeto en la posicion actual.
        switch map_object:
            // Solo nos interesa si es una persona (el taxi solo carga personas).
            case Person{
                // Si esta persona reservo este taxi la montamos, y retornamos
                // dado que es la única que montara este taxi.
                if(map_object.reserved_id == self.identifier){
                    return [map_object]
                }
            }

        // En cualquier otro caso devolvemos una lista vacía.
        return []
    }

    fun next_objective(positions: [Position], env: GraphEnvironment): List<Position>{
        // Encuentra el proximo objetivo del taxi en base a un comportamiento definido.

        // El proximo objetivo esta determinado por la IA del taxi.
        return self.IA.algorithm(position, env)
    }
}


AStar::AStarT{
    fun measure(current: Position, person: Person, graph: GraphEnvironment): Float{
        // Calcula la medida que emplea la heuristica de AStarT.

        // Calculamos la distancia euclidiana entre la posicion actual y la posicion de la persona.
        distance: Float = pow(current.x - person.position.x, 2) + pow(current.y - person.position.y, 2)
        // Calculamos la distancia euclidiana entre la posicion de la persona y su destino.
        destiny_distance: Float = pow(pow(person.position.x - person.destiny.x, 2) +
                                      pow(person.position.y - person.destiny.y, 2), 1/2)
        // Devolvemos la suma de las distancias menos el precio a pagar.
        return distance + destiny_distance - person.payment
    }

    fun h(current: Position, destinations: [Position], taxi: Taxi, graph: GraphEnvironment): Float{
        // Heuristica de AStarT.

        // Por cada posicion destino posible.
        for(var destiny : destinations){
            // Obtenemos la lista de objetos en la posicion actual. Para este problema trivial, en cada
            // posicion del entorno habrá solo un objeto, por lo que la lista será unaria.
            map_object: List<MapObject> = graph.get_objects(self.position)[0]

            // Comprobamos el objeto en la posicion actual.
            switch map_object:
                // Solo nos interesa si es una persona (el taxi solo carga personas).
                case Person{
                    // Si esta persona no ha reservado taxi, calculamos el valor de la heuristica para esta
                    // persona, y retornamos este valor, dado que es la unica persona en esta posicion.
                    if(map_object.reserved_id == 0){
                        return measure(current, person)
                    }
                }
        }

        // En cualquier otro caso devolvemos un valor absurdo (infinito).
        return infinity()
    }

    fun actualize(current: Position, taxi: Taxi, graph: GraphEnvironment): Float{
        // Metodo para actualizar la posicion objetivo del taxi en el entorno,
        // dado el taxi y la posicion afectada.

        // Obtenemos la lista de objetos en la posicion actual. Para este problema trivial, en cada
        // posicion del entorno habrá solo un objeto, por lo que la lista será unaria.
        map_object: List<MapObject> = graph.get_objects(self.position)[0]

        // Comprobamos el objeto en la posicion actual.
        switch map_object:
            // Solo nos interesa si es una persona (el taxi solo carga personas).
            case Person{
                // Si esta persona no ha reservado taxi la marcamos como reservada para este,
                // puesto que es la unica en esta posicion, y esta es la posicion objetivo
                // del taxi.
                if(map_object.reserved_id == 0){
                    map_object.reserved_id = self.identifier
                }
            }

        // Retornamos.
        return
    }
}







