from abc import abstractmethod

from .base_classes import Environment
from .graph_environments import GraphEnvironment
from .vehicles import Vehicle, MapObject
import random
import heapq


class DistanceAndPathCalc:
    distances: {str: {str: int}}
    paths: {str: {str: str}}

    def __init__(self):
        self.distances = {}
        self.paths = {}

    def calc(self, env: GraphEnvironment):
        for place in env.get_places():
            self.distances[place] = self.calc_distances(place, env)
            self.paths[place] = self.calc_paths(place, env)

    @staticmethod
    def calc_distances(place: str, env: GraphEnvironment) -> {str: int}:
        distance = {vertex: float('infinity') for vertex in env.get_places()}
        distance[place] = 0

        pq = [(0, place)]
        while len(pq) > 0:
            current_distance, current_vertex = heapq.heappop(pq)
            if current_distance > distance[current_vertex]:
                continue

            for neighbor, weight in env.graph[current_vertex].items():
                new_distance = current_distance + weight

                if new_distance < distance[neighbor]:
                    distance[neighbor] = new_distance
                    heapq.heappush(pq, (new_distance, neighbor))
        return distance

    @staticmethod
    def calc_paths(place: str, env: GraphEnvironment) -> {str: int}:
        distance = {vertex: float('infinity') for vertex in env.get_places()}
        path = {vertex: "" for vertex in env.get_places()}
        distance[place] = 0

        pq = [(0, place, "")]
        while len(pq) > 0:
            current_distance, current_vertex, parent = heapq.heappop(pq)
            if current_distance > distance[current_vertex]:
                continue
            path[current_vertex] = parent

            for neighbor, weight in env.graph[current_vertex].items():
                new_distance = current_distance + weight

                if new_distance < distance[neighbor]:
                    distance[neighbor] = new_distance
                    heapq.heappush(pq, (new_distance, neighbor, current_vertex))
        return path

    @staticmethod
    def get_path(finish: str, path: {str: str}) -> [str]:
        final_path = [finish]
        while path[finish]:
            final_path.append(path[finish])
            finish = path[finish]
        final_path.reverse()
        return final_path


class HillClimbing:

    @staticmethod
    def random_solution(start: int, distances: [[int]]) -> [int]:
        cities = list(range(len(distances)))
        cities.remove(start)
        solution = [start]

        for i in range(len(distances)):
            if i == start:
                continue
            random_city = cities[random.randint(0, len(cities) - 1)]
            solution.append(random_city)
            cities.remove(random_city)

        solution.append(start)
        return solution

    @staticmethod
    def route_length(solution: [int], distances: [[int]]) -> int:
        route_length = 0
        for i in range(len(solution)):
            route_length += distances[solution[i - 1]][solution[i]]
        return route_length

    @staticmethod
    def get_neighbours(solution: [int]) -> [[int]]:
        neighbours = []
        for i in range(1, len(solution) - 1):
            for j in range(i + 1, len(solution) - 1):
                neighbour = solution.copy()
                neighbour[i] = solution[j]
                neighbour[j] = solution[i]
                neighbours.append(neighbour)
        return neighbours

    @staticmethod
    def get_best_neighbour(neighbours: [[int]], distances: [[int]]) -> [int]:
        best_route_length = HillClimbing.route_length(neighbours[0], distances)
        best_neighbour = neighbours[0]
        for neighbour in neighbours:
            current_route_length = HillClimbing.route_length(neighbour, distances)
            if current_route_length < best_route_length:
                best_route_length = current_route_length
                best_neighbour = neighbour
        return best_neighbour

    @staticmethod
    def hill_climbing(start: int, distances: [[int]]) -> [int]:
        current_solution = HillClimbing.random_solution(start, distances)
        if len(current_solution) <= 3:
            return current_solution
        current_route_length = HillClimbing.route_length(current_solution, distances)
        neighbours = HillClimbing.get_neighbours(current_solution)
        best_neighbour = HillClimbing.get_best_neighbour(neighbours, distances)
        best_neighbour_route_length = HillClimbing.route_length(best_neighbour, distances)

        while best_neighbour_route_length < current_route_length:
            current_solution = best_neighbour
            current_route_length = best_neighbour_route_length
            neighbours = HillClimbing.get_neighbours(current_solution)
            best_neighbour = HillClimbing.get_best_neighbour(neighbours, distances)
            best_neighbour_route_length = HillClimbing.route_length(best_neighbour, distances)

        return current_solution


class PickUpVehicle(Vehicle):
    origin: str
    calculator: DistanceAndPathCalc
    path_opt: HillClimbing

    def __init__(self, identifier: int, position: str):
        super().__init__(identifier, position)
        self.origin = position
        self.calculator = DistanceAndPathCalc()
        self.path_opt = HillClimbing()

    @abstractmethod
    def update_cargo(self, cargo: MapObject, env: GraphEnvironment) -> None:
        pass

    def get_destiny(self, cargo: MapObject, env: GraphEnvironment) -> str:
        return self.origin

    def get_objectives(self, env: Environment) -> [str]:
        places = []
        for place in env.get_places():
            for obj in env.get_all_objects(place):
                if not isinstance(obj, Vehicle):
                    places.append(place)
                    break
        return places

    def build_tour(self, objectives: [str], env: GraphEnvironment) -> None:
        places: [str] = env.get_places()
        self.calculator.calc(env)
        distance = self.calculator.distances
        paths = self.calculator.paths
        matrix = []
        for i, place in enumerate(places):
            if place in objectives or place == self.position:
                row = []
                for target in places:
                    if target in objectives or target == self.position:
                        row.append(distance[place][target])
                matrix.append(row)
        places = [place for place in places if place in objectives or place == self.position]
        hc = HillClimbing()
        temp = hc.hill_climbing(places.index(self.position), matrix)
        temp = [places[x] for x in temp]
        answer = [self.position]
        objectives = []
        current = self.position
        for i in temp[1:]:
            path = self.calculator.get_path(i, paths[current])
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
