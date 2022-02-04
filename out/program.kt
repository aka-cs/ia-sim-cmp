// Clase posicion.
class Position{
    fun init(x: Int, y: Int): void{
        // Instanciamos las coordenadas.
        attr x = x;
        attr y = y;
    }
}


// Clase mapa.
GraphEnvironment::Map{
    fun init(edges: dict<String, dict<String, Float>>, objects: dict<String, dict<Int, MapObject>>,
            positions: dict<String, Position>): void{
        // Instanciamos la clase GraphEnvironment (de la que hereda mapa) con los arcos y objetos del entorno.
        super.init(edges, objects);

        // Guardamos el listado de posiciones.
        attr positions: dict<String, Position> = positions;
    }
}


// Clase agente.
Agent::Person{
    fun init(identifier: Int, position: String, destiny: String, payment: Int, final_time: Int): void{
        // Instanciamos la clase agente (de la que hereda persona) con el identificador y la localizacion.
        super.init(identifier, position);

        // Destino de la persona, o sea, a donde se dirige.
        attr destiny: String = destiny;
        // Dinero que ofrece la persona por ser transportada.
        attr payment: Float = payment;
        // Tiempo final hasta el que esperara la persona.
        attr final_time: Int = final_time;
        // Identificador del vehiculo que reservo la persona.
        attr reserved_id: Int = 0;
    }

    // Actualiza el estado de la persona.
    fun update_state(event: Event, env: Environment): list<Event>{
        // Si la persona no ha reservado un vehiculo, y se le acabo el tiempo,
        // lanza un evento de eliminacion (la persona es retirada del entorno simulado).
        if(self.reserved_id == 0 && event.time >= self.final_time){
            // Le colocamos un valor de reserva absurdo, para que no vuelva a ser escogida
            // hasta su eliminacion.
            self.reserved_id = -1;
            // Lanzamos el evento de eliminacion.
            return [DeleteEvent(event.time + 1, 0, self.identifier, self.position)];
        }

        // En caso contrario, devolvemos una lista de eventos vacia.
        return [];
    }
}


// Clase taxi.
Vehicle::Taxi
{
    fun init(identifier: Int, position: String): void{
        // Instanciamos la clase vehiculo (de la que hereda taxi) con el identificador y la localizacion.
        super.init(identifier, position);

        // Inteligencia artificial del taxi. La instanciamos con AStarT (AStar para la clase Taxi).
        attr IA: AStarT = AStarT();
    }

    // Localiza los posibles objetivos del taxi en el entorno.
    fun get_objectives(env: Environment): list<String>{
        // Localizaciones del entorno.
        var places: list<String> = env.places();
        // Lista de localizaciones objetivo.
        var objective_localizations: list<String> = [];

        // Por cada localizacion del entorno.
        for(var place: places){
            // Obtenemos la lista de objetos en la posicion actual.
            var map_objects: list<MapObject> = env.get_all_objects(place);

            // Recorremos la lista de objetos.
            for(var map_object: map_objects){
                // Comprobamos el objeto en la posicion actual.
                // Solo nos interesa si es una persona (el taxi solo carga personas).
                switch map_object:
                    case Person{
                        // Si es una persona, y esta pendiente a reserva, adicionamos su localizacion a la lista.
                        // Salimos del ciclo para analizar la proxima localizacion.
                        if(map_object.reserved_id == 0){
                            objective_localizations.append(map_object.position);
                            break;
                        }
                    }
            }
        }

        // Devolvemos la lista de localizaciones.
        return objective_localizations;
    }

    // Encuentra el proximo objetivo del taxi en base a un comportamiento definido.
    fun build_tour(positions: list<String>, map: Environment): dict<String, list<Int>>{
        // Si el entorno es un mapa.
        switch map:
            case Map{
                // El proximo objetivo esta determinado por la IA del taxi.
                return self.IA.algorithm(self.position, positions, [], map);
            }

        // En cualquier otro caso devolvemos un diccionario vacio.
        return {};
    }

    fun actualize_cargo(cargo: MapObject, map: Environment): void{
       // Comprobamos si la carga es una persona (el taxi solo carga personas).
        switch cargo:
            case Person{
                // Si la persona no ha reservado, entonces actualize se llamo para reservar.
                // Actualizamos el identificador de reserva de la persona con el identificador
                // del taxi.
                if(cargo.reserved_id == 0){
                    cargo.reserved_id == self.identifier;
                }

                // Si la persona reservo este vehiculo, entonces actualizamos su identificador
                // de reserva con -1 (despues de la reserva, actualize solo se llama para una persona
                // si la persona en efecto ya esta en el vehiculo).
                if(cargo.reserved_id == self.identifier){
                    cargo.reserved_id = -1;
                }
            }
    }
    
    fun get_destiny(cargo: MapObject, map: Environment): String{
       // Comprobamos si la carga es una persona (el taxi solo carga personas).
       switch cargo:
            case Person{
                return cargo.destiny;
            }
        // En otro caso devolvemos un string vacio.
        return "";
    }
}


// Calcula la medida que emplea la heuristica de AStarT.
AStar::AStarT{
    fun measure(current: Position, objective: Position, destiny: Position, payment: Float): Float{
        // Calculamos la distancia euclidiana entre la posicion actual y la posicion de la persona.
        var distance: Float = pow(current.x - objective.x, 2) + pow(current.y - objective.y, 2);
        // Calculamos la distancia euclidiana entre la posicion de la persona y su destino.
        var destiny_distance: Float = pow(pow(objective.x - destiny.x, 2) + pow(objective.y - destiny.y, 2), 1/2);
        // Devolvemos la suma de las distancias sobre el precio a pagar.
        return (distance + destiny_distance) / payment;
    }

    // Obtiene los objetivos en una posicion dada.
    fun get_objectives(objective: String, actors: list<MapObject>, map: GraphEnvironment): list<Int>{
        // Variable para guardar el resultado.
        var min_value: Float = infinity();
        var result: Int = 0;

        // Si el entorno es un mapa.
        switch map:
            case Map{
                // Obtenemos la lista de objetos en la localizacion actual.
                var map_objects: list<MapObject> = map.get_all_objects(objective);

                // Recorremos la lista de objetos.
                for(var map_object: map_objects){
                    // Solo nos interesa si el objeto es una persona (el taxi solo carga personas).
                    switch map_object:
                        case Person{
                            // Si esta persona no ha reservado taxi, calculamos el valor de la heuristica
                            // para esta persona.
                            if(map_object.reserved_id == 0){
                                var value: Float = self.measure(map.positions[objective],
                                                                map.positions[map_object.position],
                                                                map.positions[map_object.destiny], map_object.payment);

                                // Actualizamos el que ya tenemos con el minimo de ambos.
                                // Si minimiza, guardamos su id.
                                if(value < min_value){
                                    min_value = value;
                                    result = map_object.identifier;
                                }
                            }
                        }
                }
            }

        // Devolvemos el id resultante.
        return [result];
    }

    // Heuristica de AStarT.
    fun h(current: String, destinations: list<String>, agents: list<MapObject>, map: GraphEnvironment): Float{
        // Variable para guardar el resultado de la heuristica.
        var result: Float = infinity();

        // Si el entorno es un mapa.
        switch map:
            case Map{
                // Por cada localizacion destino posible.
                for(var destiny : destinations){
                    // Obtenemos la lista de objetos en la localizacion actual.
                    var map_objects: list<MapObject> = map.get_all_objects(destiny);

                    // Recorremos la lista de objetos.
                    for(var map_object: map_objects){
                        // Solo nos interesa si el objeto es una persona (el taxi solo carga personas).
                        switch map_object:
                            case Person{
                                // Si esta persona no ha reservado taxi, calculamos el valor de la heuristica
                                // para esta persona, y actualizamos el que ya tenemos con el minimo de ambos.
                                if(map_object.reserved_id == 0){
                                    var value: Float = self.measure(map.positions[current],
                                                        map.positions[map_object.position],
                                                        map.positions[map_object.destiny], map_object.payment);
                                    result = min(result, value);
                                }
                            }
                    }
                }
            }

        // Devolvemos el minimo valor obtenido.
        return result;
    }


    // Metodo para encontrar el nuevo destino del taxi despues de hallar la posicion objetivo,
    // dado el taxi, la posicion afectada y una serie de ids objetivo.
    fun actualize_destiny(current: String, objective_ids: list<Int>, taxis: list<MapObject>,
        graph: GraphEnvironment): String{
        // Si hay objetivos en la lista de objetivos.
        if(len(objective_ids) > 0){
            // Obtenemos la lista de objetos en la posicion actual.
            var map_objects: list<MapObject> = graph.get_all_objects(current);

            // El taxi solo carga una persona, asi que solo nos importa el primer objetivo.
            var objective_id = objective_ids[0];

            // Recorremos la lista de objetos.
            for(var map_object: map_objects){
                // Comprobamos el objeto en la posicion actual.
                // Solo nos interesa si es una persona (el taxi solo carga personas).
                switch map_object:
                    case Person{
                        // Si la persona es objetivo, devolvemos el destino de la persona.
                        if(map_object.identifier == objective_id){
                            return map_object.destiny;
                        }
                    }
            }
        }

        // Si no hay personas en esta posicion, devolvemos un string vacio.
        return "";
    }
}


fun main(): void{
    var graph_places: dict<String, Position> = {"Alamar": Position(10, 20), "Vedado": Position(20, 25),
                                            "10 de Octubre": Position(30, 35)};

    var graph_edges: dict<String, dict<String, Float>> = {"Alamar": {"Vedado" : 25},
                                                          "Vedado": {"10 de Octubre": 10},
                                                          "10 de Octubre": {"Vedado": 10}};

    var graph_objects: dict<String, dict<Int, MapObject>> = {
                                                       "Alamar": {1 : Person(1, "Alamar", "10 de Octubre", 1000, 100)},
                                                       "Vedado": {2 : Person(2, "Vedado", "10 de Octubre", 1000, 100)},
                                                       "10 de Octubre": {}
                                                       };
    var env: Map = Map(graph_edges, graph_objects, graph_places);
    var total_time: Int = 1000;
    var taxi_A = Taxi(3, "Alamar");
    var taxi_B = Taxi(4, "Vedado");
    var initial_events = [SetEvent(0, 0, taxi_A), SetEvent(0, 1, taxi_B)];
    simulate_environment(env, initial_events, total_time);
}





