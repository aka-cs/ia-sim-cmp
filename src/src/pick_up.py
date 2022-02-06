from abc import abstractmethod
from dataclasses import dataclass

from .base_classes import Environment
from .graph_environments import GraphEnvironment
from .vehicles import Vehicle, MapObject
from .AStar import AStar
import random
import heapq


def distances(place: str, env: GraphEnvironment) -> {str: int}:
    distance = {vertex: float('infinity') for vertex in env.get_places()}
    distance[place] = 0

    pq = [(0, place)]
    while len(pq) > 0:
        current_distance, current_vertex = heapq.heappop(pq)
        if current_distance > distance[current_vertex]:
            continue

        for neighbor, weight in env.edges[current_vertex].items():
            new_distance = current_distance + weight

            if new_distance < distance[neighbor]:
                distance[neighbor] = new_distance
                heapq.heappush(pq, (new_distance, neighbor))

    return distance


def shortest_paths(place: str, env: GraphEnvironment) -> {str: str}:
    distance = {vertex: float('infinity') for vertex in env.get_places()}
    path = {vertex: "" for vertex in env.get_places()}
    distance[place] = 0

    pq = [(0, place, "")]
    while len(pq) > 0:
        current_distance, current_vertex, parent = heapq.heappop(pq)
        if current_distance > distance[current_vertex]:
            continue
        path[current_vertex] = parent

        for neighbor, weight in env.edges[current_vertex].items():
            new_distance = current_distance + weight

            if new_distance < distance[neighbor]:
                distance[neighbor] = new_distance
                heapq.heappush(pq, (new_distance, neighbor, current_vertex))

    return path


def extract_path(finish: str, tree: {str: str}) -> [str]:
    path = [finish]
    while tree[finish]:
        path.append(tree[finish])
        finish = tree[finish]
    path.reverse()
    return path


class PickUpVehicle(Vehicle):
    origin: str

    def __init__(self, identifier: int, position: str):
        super().__init__(identifier, position)
        self.origin = position

    @abstractmethod
    def update_cargo(self, cargo: MapObject, env: Environment) -> None:
        pass

    def get_destiny(self, cargo: MapObject, env: Environment) -> str:
        return self.origin

    def get_objectives(self, env: Environment) -> [str]:
        places = []
        for place in env.get_places():
            for obj in env.get_all_objects(place):
                if not isinstance(obj, Vehicle):
                    places.append(place)
                    break
        return places

    def build_tour(self, objectives: [str], env: Environment) -> None:
        places: [str] = env.get_places()
        distance = {place: distances(place, env) for place in places}
        paths = {place: shortest_paths(place, env) for place in places}
        matrix = []
        for i, place in enumerate(places):
            if place in objectives or place == self.position:
                row = []
                for target in places:
                    if target in objectives or target == self.position:
                        row.append(distance[place][target])
                matrix.append(row)
        places = [place for place in places if place in objectives or place == self.position]
        hc = HillClimbing(matrix)
        temp = hc.hill_climbing(places.index(self.position))
        temp = [places[x] for x in temp]
        answer = [self.position]
        objectives = []
        current = self.position
        for i in temp[1:]:
            path = extract_path(i, paths[current])
            path = path[1:]
            answer.extend(path)
            for j in range(1, len(path)):
                objectives.append([])
            objectives.append([y.identifier for y in env.get_all_objects(i) if y.identifier != self.identifier])
            current = i
        answer = answer[1:]
        answer.reverse()
        objectives.reverse()
        self.tour.extend(answer)
        self.objectives.extend(objectives)


@dataclass
class HillClimbing:
    distances: [[int]]

    def random_solution(self, start: int) -> [int]:
        cities = list(range(len(self.distances)))
        cities.remove(start)
        solution = [start]

        for i in range(len(self.distances)):
            if i == start:
                continue
            random_city = cities[random.randint(0, len(cities) - 1)]
            solution.append(random_city)
            cities.remove(random_city)

        solution.append(start)
        return solution

    def route_length(self, solution: [int]) -> int:
        route_length = 0
        for i in range(len(solution)):
            route_length += self.distances[solution[i - 1]][solution[i]]
        return route_length

    def get_neighbours(self, solution: [int]) -> [[int]]:
        neighbours = []
        for i in range(1, len(solution) - 1):
            for j in range(i + 1, len(solution) - 1):
                neighbour = solution.copy()
                neighbour[i] = solution[j]
                neighbour[j] = solution[i]
                neighbours.append(neighbour)
        return neighbours

    def get_best_neighbour(self, neighbours: [[int]]) -> [int]:
        best_route_length = self.route_length(neighbours[0])
        best_neighbour = neighbours[0]
        for neighbour in neighbours:
            current_route_length = self.route_length(neighbour)
            if current_route_length < best_route_length:
                best_route_length = current_route_length
                best_neighbour = neighbour
        return best_neighbour

    def hill_climbing(self, start: int) -> [int]:
        current_solution = self.random_solution(start)
        if len(current_solution) <= 3:
            return current_solution
        current_route_length = self.route_length(current_solution)
        neighbours = self.get_neighbours(current_solution)
        best_neighbour = self.get_best_neighbour(neighbours)
        best_neighbour_route_length = self.route_length(best_neighbour)

        while best_neighbour_route_length < current_route_length:
            current_solution = best_neighbour
            current_route_length = best_neighbour_route_length
            neighbours = self.get_neighbours(current_solution)
            best_neighbour = self.get_best_neighbour(neighbours)
            best_neighbour_route_length = self.route_length(best_neighbour)

        return current_solution
