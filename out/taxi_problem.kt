AStar::AStarT {
    fun h(current: Position, destinations: [Position], graph: GraphEnvironment): Float {
        result: Float = get_inf()
        i: Int = 0
        while(i < len(destinations)) {
            destiny: Position = destinations[i]
            person: Person = graph.get_object_in(destiny)
            distance: Float = pow(current.x - destiny.x, 2) + pow(current.y - destiny.y, 2)
            destiny_distance: Float = pow(pow(destiny.x - person.destiny.x, 2) +
                                        pow(destiny.y - person.destiny.y, 2), 1/2)
            result: Float = min(result, distance + destiny_distance - person.payment)
        }
        return result
    }
}

Event::CancelEvent {
    fun init(id: Int, time: Int) {
        self.super(id, time)
    }
}

Event::MovementEvent {
    fun init(id: Int, time: Int) {
        self.super(id, time)
    }
}

Event::DeleteEvent {
    fun init(id: Int, time: Int, position: Position) {
        self.super(id, time)
        attr position = position
    }
}

Person::Cargo {
    fun init(position, destiny, payment, actual_time, waiting_time) {
        self.super(position)
        attr destiny: Position = destiny
        attr payment: Float = payment
        attr final_time: Int = actual_time + waiting_time
        attr marked_by: Int = 0
    }

    fun update_state(env: Environment, event: Event): List<Event> {
        if(self.final_time > 0 && event.time >= final_time) {
            result: List<Event> = [DeleteEvent(0, event.time + 1, self.position)]
            if (self.marked_by > 0) {
                result.append(CancelEvent(self.marked_by, event.time + 1))
            }
            return result
        }
    }
}



