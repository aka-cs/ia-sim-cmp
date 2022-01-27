from builtin_code import *


class AStarT(AStar):
    @staticmethod
    def h(current: Position, destinations: [Position], graph: GraphEnvironment) -> float:
        result: float = inf
        for destiny in destinations:
            person = graph[destiny]
            distance = (current.x - destiny.x)**2 + (current.y - destiny.y)**2
            destiny_distance = (destiny.x - person.destiny.x)**2 + (destiny.y - person.destiny.y)**2
            result = min(result, distance + destiny_distance - person.payment)
        return result


@dataclass
class Person(Cargo):
    marked_by: int
    destiny: Position
    payment: float


@dataclass
class MovementEvent(Event):
    pass


@dataclass
class CargoEvent(Event):
    pass


@dataclass
class CancelEvent(Event):
    pass


class Taxi(Vehicle):
    path: [Position] = []
    heuristic = AStarT
    gps = AStar
    identifier: int

    def update_state(self, env: GraphEnvironment, event: Event) -> [Event]:
        if event.identifier == self.identifier:
            if isinstance(event, MovementEvent):
                self.position = self.path.pop()

                if len(self.path) == 0:
                    if self.cargo:
                        self.cargo = None
                        return []

                    elif isinstance(env[self.position], Person) and env[self.position].marked:
                        self.cargo = env[self.position]
                        self.path = self.gps.a_star_algorithm(self.position, [self.cargo.destiny], env).reverse()
                        return [MovementEvent(self.identifier, event.time + 1)]

            if isinstance(event, CancelEvent):
                self.path = []
                return []

        elif not self.cargo:
            persons = env.get_cargos()
            self.path = self.heuristic.a_star_algorithm(self.position, persons.keys(), env).reverse()
            destiny = self.path[0]
            env[destiny].marked = self.identifier
            return [MovementEvent(self.identifier, event.time + 1)]

    def get_pos(self):
        return self.position

    def report_state(self):
        return self.position, self.path[0] if len(self.path) != 0 else None, self.cargo



