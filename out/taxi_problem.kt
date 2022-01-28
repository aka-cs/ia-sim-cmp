Person::Cargo {
    fun init(identifier: Int, position: String, destiny: String, payment: Int, actual_time: Float,
    waiting_time: Float) {
        self.super(identifier, position)
        attr destiny: Position = destiny
        attr payment: Float = payment
        attr marked_by: Int = 0
        attr final_time: Int = actual_time + waiting_time
    }

    fun update_state(env: Environment, event: Event): List<Event> {
        if(self.marked_by == 0 && event.time >= final_time) {
            self.marked_by = -1
            return [DeleteEvent(0, event.time + 1, self.position)]
        }
    }
}

Taxi::Vehicle
{
    fun init(identifier: Int, position: String) {
        self.super(identifier, position)
        self.IA = AStarT()
    }

    fun something_to_charge(env: GraphEnvironment){
        cargos: List<Cargo> = graph.get_objects(self.position)
        persons: List<Person> = []

        for(var cargo: cargos){
            switch cargo:
                case Person{
                    if(cargo.marked_by == self.identifier){
                        person.append(cargo)
                    }
                }
                default{}
        }
        return persons
    }

    fun next_objective(positions: [Position], env: GraphEnvironment) {
        return self.IA.algorithm(position, env)
    }
}

AStar::AStarT {
    fun measure(current: Position, person: Person, graph: GraphEnvironment): Float {
        distance: Float = pow(current.x - person.position.x, 2) + pow(current.y - person.position.y, 2)
        destiny_distance: Float = pow(pow(person.position.x - person.destiny.x, 2) +
                                      pow(person.position.y - person.destiny.y, 2), 1/2)
        return distance + destiny_distance - person.payment
    }

    fun h(current: Position, destinations: [Position], taxi: Taxi, graph: GraphEnvironment): Float {
        result: Float = get_inf()

        for(var destiny : destinations) {
            cargos: List<Cargo> = graph.get_objects(destiny)

            for(var cargo: cargos) {
                switch cargo:
                    case Person {
                        if(person.marked_by == 0){
                            result: Float = min(result, measure(current, person))
                        }
                    }
                    default {}
            }
        }
        return result
    }

    fun actualize(current: Position, taxi: Taxi, graph: GraphEnvironment): Float {
        min_cost: Float = get_inf()
        person: Person = null
        cargos: List<Cargo> = graph.get_objects(position)

        for(var cargo: cargos) {
            switch cargo:
                case Person {
                    if(person.marked_by == 0){
                        cost = measure(current, person)
                        if(min_cost > cost) {
                            min_cost = cost
                            person = cargo
                        }
                    }
                }
                default {}
        }

        if(person != null) {
            person.marked_by = taxi.identifier
        }
        return
    }
}

Event::MovementEvent {
    fun init(identifier: Int, time: Int) {
        self.super(identifier, time)
    }
}

Event::DeleteEvent {
    fun init(identifier: Int, time: Int, position: Position) {
        self.super(identifier, time)
        attr position = position
    }
}





