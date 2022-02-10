MonteCarloHeuristic::TaxiHeuristic{
    fun heuristic(objectives: List<MapObject>, agent: Agent, env: Environment): Float{
        if(len(objectives) == 0){
            return -infinity();
        }

        var value: Float = 0;
        var position: Position = null;
        var constant: Float = golden() / 2;
        var i: Int = 0;

        switch env:
            case MapEnvironment{

                switch agent:
                    case Taxi{
                        position = env.get_position(agent.position);
                    }
                    default{ return -infinity(); }

                for(var map_object: objectives){
                    switch map_object:
                        case Person{
                            var step: Position = env.get_position(map_object.position);
                            var destiny: Position = env.get_position(map_object.destiny);

                            if(step == null || destiny == null){
                                return -infinity();
                            }

                            var distance: Float = pow(pow(position.x - step.x, 2) + pow(position.y - step.y, 2), 1/2);
                            distance = distance + pow(pow(destiny.x - step.x, 2) + pow(destiny.y - step.y, 2), 1/2);
                            if (distance == 0){
                                value = infinity();
                            }
                            else{
                                value = value + pow(constant, i) * map_object.payment / distance;
                            }
                            position = destiny;
                            i = i + 1;
                        }
                }

            }
            default{ return -infinity(); }

        return value;
    }
}


// Clase agente.
Agent::Person{
    fun init(identifier: Int, position: String, destiny: String, payment: Int, final_time: Int): Void{
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
    fun update_state(event: Event, env: Environment): List<Event>{
        // Si la persona no ha reservado un vehiculo, y se le acabo el tiempo,
        // lanza un evento de eliminacion (la persona es retirada del entorno simulado).
        if(this.reserved_id == 0 && event.time >= this.final_time){
            // Le colocamos un valor de reserva absurdo, para que no vuelva a ser escogida
            // hasta su eliminacion.
            this.reserved_id = -1;
            // Lanzamos el evento de eliminacion.
            return [DeleteEvent(event.time + 1, 0, this.identifier, this.position)];
        }

        // En caso contrario, devolvemos una lista de eventos vacia.
        return [];
    }
}


// Clase taxi.
MapVehicle::Taxi
{
    fun update_cargo(cargo: MapObject, map: MapEnvironment): Void{
       // Comprobamos si la carga es una persona (el taxi solo carga personas).
        switch cargo:
            case Person{
                // Si la persona reservo este vehiculo, entonces actualizamos su identificador
                // de reserva con -1 (despues de la reserva, update solo se llama para una persona
                // si la persona en efecto ya esta en el vehiculo).
                if(cargo.reserved_id == this.identifier && cargo.destiny == this.position){
                    cargo.reserved_id = -1;
                }

                // Si la persona no ha reservado, entonces update se llamo para reservar.
                // Actualizamos el identificador de reserva de la persona con el identificador
                // del taxi.
                if(cargo.reserved_id == 0){
                    cargo.reserved_id = this.identifier;
                }
            }
    }

    fun get_objectives_in(position: String, env: MapEnvironment): List<MapObject>{
        // Obtenemos la lista de objetos en la posicion actual.
        var map_objects: List<MapObject> = env.get_all_objects(position);
        // Lista de objetos en la posicion actual que le interesan al taxi.
        var objectives: List<MapObject> = [];

        // Recorremos la lista de objetos.
        for(var map_object: map_objects){
            // Comprobamos el objeto en la posicion actual.
            // Solo nos interesa si es una persona (el taxi solo carga personas).
            switch map_object:
                case Person{
                    // Si es una persona, y esta pendiente a reserva, adicionamos su localizacion a la lista.
                    // Salimos del ciclo para analizar la proxima localizacion.
                    if(map_object.reserved_id == 0){
                        objectives.append(map_object);
                    }
                }
        }

        return objectives;
    }

    // Localiza los posibles objetivos del taxi en el entorno.
    fun get_objectives(env: MapEnvironment): List<String>{
        // Localizaciones del entorno.
        var places: List<String> = env.get_places();
        // Lista de localizaciones objetivo.
        var objective_localizations: List<String> = [];

        // Por cada localizacion del entorno.
        for(var place: places){
            if(len(this.get_objectives_in(place, env)) > 0){
                objective_localizations.append(place);
            }
        }

        // Devolvemos la lista de localizaciones.
        return objective_localizations;
    }

    fun get_destiny(cargo: MapObject, map: MapEnvironment): String{
       // Comprobamos si la carga es una persona (el taxi solo carga personas).
       switch cargo:
            case Person{
                return cargo.destiny;
            }
        // En otro caso devolvemos un string vacio.
        return "";
    }

    fun select_objective(objectives: List<MapObject>, env: MapEnvironment): MapObject{
        if(len(objectives) == 0){
            return null;
        }

        return MonteCarloTreeSearchNode(objectives, this, env, TaxiHeuristic(), null, null).best_action(100);
    }
}

Generator::PersonGenerator
{
    fun init(amount: Int): Void{
        super.init();

        attr amount: Int = amount + 1;
    }

    fun generate(places: List<String>): MapObject{
        var place: String = places[uniformly_discrete(0, len(places) - 1)];
        var destiny: String = places[uniformly_discrete(0, len(places) - 1)];
        var payment: Int = uniformly_discrete(1, 1000);
        var time: Int = uniformly_discrete(1, 1000);
        var person: Person = Person(0, place, destiny, payment, time);

        return person;
    }

    fun next(time: Int): Int{
        this.amount = this.amount - 1;

        if(this.amount == 0){
            return 0;
        }

        return time + uniformly_discrete(0, 20);
    }
}


fun main(): Void{
    var graph_places: Dict<String, Position> = {"Alamar": Position(0, 0), "La Habana Vieja": Position(5, 5),
                                                "Centro Habana": Position(10, 5), "Vedado": Position(15, 5),
                                                "La Vibora": Position(20, 15),"10 de Octubre": Position(20, 20),
                                                "China": Position(100, 100)};

    var graph_edges: Dict<String, Dict<String, Float>> = {"Alamar": {"La Habana Vieja" : 5},
                                                          "La Habana Vieja": {"Centro Habana" : 5, "Alamar": 5},
                                                          "Centro Habana": {"La Habana Vieja" : 5, "Vedado" : 5,
                                                                            "La Vibora": 5},
                                                          "Vedado": {"Centro Habana": 5},
                                                          "La Vibora": {"Centro Habana": 5, "10 de Octubre": 10},
                                                          "10 de Octubre": {"Vedado": 5, "China": 100},
                                                          "China": {"10 de Octubre": 100, "Japon": 50}};

    var graph_objects: Dict<String, Dict<Int, MapObject>> = {
                                                        "Alamar": {1 : Person(1, "Alamar", "10 de Octubre", 15, 100)},
                                                        "Vedado": {2 : Person(2, "Vedado", "10 de Octubre", 20, 100)},
                                                        "La Vibora": {3 : Person(3, "La Vibora", "China", 1000, 5)}
                                                       };
    var generators:  Dict<String, Generator> = {"Person" : PersonGenerator(5)};
    var env: MapEnvironment = MapEnvironment(graph_edges, graph_objects, graph_places, generators);
    var total_time: Int = 1000;
    var taxi_A = Taxi(3, "Alamar");
    var taxi_B = Taxi(4, "10 de Octubre");
    var initial_events = [SetEvent(1, 0, taxi_A), SetEvent(0, 0, taxi_B), GenerateEvent(2, 0, "Person")];
    simulate_environment(env, initial_events, total_time);
}





