Place::Position{
    fun init(name: String, x: Int, y: Int): void{
        super.init(name);
        // Clase posicion.
        // Instanciamos la clase lugar, con el nombre.

        // Instanciamos las coordenadas.
        attr x = x;
        attr y = y;
    }
}


Cargo::Person{
    fun init(identifier: Int, position: Position, destiny: Position, payment: Int, final_time: Int): void{
        super.init(identifier, position);
        // Clase persona.
        // Instanciamos la clase carga (de la que hereda persona) con el identificador y la posicion.

        // Destino de la persona, o sea, a donde se dirige.
        attr destiny: Position = destiny;
        // Dinero que ofrece la persona por ser transportada.
        attr payment: Float = payment;
        // Identificador del vehiculo que reservo la persona.
        attr reserved_id: Int = 0;
        // Tiempo final hasta el que esperara la persona.
        attr final_time: Int = final_time;
    }

    fun update_state(env: Environment, event: Event): List<Event>{
        // Actualiza el estado de la persona.

        // Si la persona no ha reservado un vehiculo, y se le acabo el tiempo,
        // lanza un evento de eliminacion (la persona es retirada del entorno simulado).
        if(self.reserved_id == 0 && event.time >= final_time){
            // Le colocamos un valor de reserva absurdo, para que no vuelva a ser escogida
            // hasta su eliminacion.
            self.reserved_id = -1;
            // Lanzamos el evento de eliminacion.
            return [DeleteEvent(0, event.time + 1, self.identifier, self.position)];
        }
    }
}


Vehicle::Taxi
{
    fun init(identifier: Int, position: Place): void{
        super.init(identifier, position);
        // Clase vehiculo.
        // Instanciamos la clase vehiculo (de la que hereda taxi) con el identificador y la posicion.

        // Instanciamos la inteligencia artificial del taxi con AStarT (AStar para la clase Taxi).
        self.IA = AStarT();
    }

    fun something_to_charge(env: Environment): List<Person>{
        // Verifica si en la posicion actual hay objetos que cargar, y en caso positivo, devuelve una
        // lista de ellos.
        // En el caso del taxi, dado que carga una sola persona a la vez, la lista siempre sera unaria.

        // Obtenemos la lista de objetos en la posicion actual. Para este problema trivial, en cada
        // posicion del entorno habra solo un objeto, por lo que la lista sera unaria.
        var map_object: List<MapObject> = graph.get_objects(self.position)[0];

        // Comprobamos el objeto en la posicion actual.
        // Solo nos interesa si es una persona (el taxi solo carga personas).
        switch map_object:
            case Person{
                // Si esta persona reservo este taxi la montamos, y retornamos
                // dado que es la unica que montara este taxi.
                if(map_object.reserved_id == self.identifier){
                    return [map_object];
                }
            }

        // En cualquier otro caso devolvemos una lista vacia.
        return [];
    }

    fun next_objective(positions: List<Place>, env: Environment): List<Position>{
        // Encuentra el proximo objetivo del taxi en base a un comportamiento definido.

        // El proximo objetivo esta determinado por la IA del taxi.
        return self.IA.algorithm(positions, env);
    }
}


AStar::AStarT{
    fun measure(current: Position, person: Person, graph: GraphEnvironment): Float{
        // Calcula la medida que emplea la heuristica de AStarT.

        // Calculamos la distancia euclidiana entre la posicion actual y la posicion de la persona.
        var distance: Float = pow(current.x - person.position.x, 2) + pow(current.y - person.position.y, 2);
        // Calculamos la distancia euclidiana entre la posicion de la persona y su destino.
        var destiny_distance: Float = pow(pow(person.position.x - person.destiny.x, 2) +
                                      pow(person.position.y - person.destiny.y, 2), 1/2);
        // Devolvemos la suma de las distancias menos el precio a pagar.
        return distance + destiny_distance - person.payment;
    }

    fun h(current: Place, destinations: List<Place>, taxi: MapObject, taxis: List<MapObject>,
        graph: Environment): Float{
        // Heuristica de AStarT.

        // Comrpobamos que cada parametro recibido sea del tipo deseado.
        switch current:
            case Position{
                // Por cada posicion destino posible.
                for(var destiny : destinations){
                    // Obtenemos la lista de objetos en la posicion actual. Para este problema trivial, en cada
                    // posicion del entorno habra solo un objeto, por lo que la lista sera unaria.
                    var map_object: List<MapObject> = graph.get_objects(self.position)[0];

                    // Comprobamos si el destino es una posicion.
                    switch destiny:
                        case Position{
                            // Comprobamos el objeto en la posicion actual.
                            // Solo nos interesa si es una persona (el taxi solo carga personas).
                            switch map_object:
                                case Person{
                                    // Si esta persona no ha reservado taxi, calculamos el valor de la heuristica
                                    // para esta persona, y retornamos este valor, dado que es la unica persona en
                                    // esta posicion.
                                    if(map_object.reserved_id == 0){
                                        return measure(current, person);
                                    }
                                }
                        }

                }
            }

        // En cualquier otro caso devolvemos un valor absurdo (infinito).
        return infinity();
    }

    fun actualize(current: Place, taxi: MapObject, taxis: List<MapObject>, graph: Environment): void{
        // Metodo para actualizar la posicion objetivo del taxi en el entorno,
        // dado el taxi y la posicion afectada.

        // Obtenemos la lista de objetos en la posicion actual. Para este problema trivial, en cada
        // posicion del entorno habra solo un objeto, por lo que la lista sera unaria.
        var map_object: List<MapObject> = graph.get_objects(current)[0];

        // Comprobamos que el actor principal sea un taxi.
        switch taxi:
            case Taxi{
                // Comprobamos el objeto en la posicion actual.
                // Solo nos interesa si es una persona (el taxi solo carga personas).
                switch map_object:
                    case Person{
                        // Si esta persona no ha reservado taxi la marcamos como reservada para este,
                        // puesto que es la unica en esta posicion, y esta es la posicion objetivo
                        // del taxi.
                        if(map_object.reserved_id == 0){
                            map_object.reserved_id = taxis[0].identifier;
                        }
                    }
            }

        // Retornamos.
        return;
    }
}


fun main(): void{
    var places: List<Position> = [Position("Alamar", 10, 20), Position("Vedado", 20, 25),
                                Position("10 de Octubre", 30, 35)];

    var graph_places: dict<String, Place> = {places[0].name : places[0], places[1].name : places[1],
                                                places[2].name : places[2]};
    var graph_edges: dict<String, dict<String, Float>> = {"Alamar": {"Vedado" : 25, "10 de Octubre": 30},
                                                          "Vedado": {"10 de Octubre": 10},
                                                          "10 de Octubre": {"Vedado": 10}};
    var get_objects: dict<String, dict<Int, Float>> = {"Alamar": {1 : Person(1, places[0], places[1], 1000, 100)},
                                                       "Vedado": {2 : Person(2, places[1], places[2], 1000, 100)}};
    var env: GraphEnvironment = GraphEnvironment(graph_edges, graph_places, get_objects);
    var total_time: Int = 1000;
    var taxi_A = Taxi(3, places[0]);
    var taxi_B = Taxi(4, places[2]);
    var initial_events = [SetEvent(0, 0, taxi_A), SetEvent(0, 1, taxi_B)];
    simulate_environment(env, initial_events, total_time);
}





