from __future__ import annotations
from .AStar import *
from .base_classes import *
from .graph_environments import *
from .Monte_Carlo_tree_search import *
from .vehicles import *
from math import inf
from random import randint
import heapq


def golden() -> float:
    return (1 + 5 ** 0.5) / 2


def infinity() -> float:
    return inf


def uniformly_discrete(a: int, b: int) -> int:
    return randint(a, b)


def simulate_environment(env: Environment, initial_events: [Event], total_time: int) -> None:
    """
    Simula el entorno, evento a evento.
    """
    actual_event = None
    events = [event for event in initial_events]
    events.sort()
    while events and (actual_event := heapq.heappop(events)) and actual_event.time <= total_time:
        for event in env.update_state(actual_event):
            heapq.heappush(events, event)

        # Imprimimos los resultados de cada evento en la simulación.
        print(f"\nTime: {actual_event.time}")
        map_objects = []
        for place in env.get_places():
            map_objects.extend(env.get_all_objects(place))
        for map_object in map_objects:
            if isinstance(map_object, Vehicle):
                print(f"{map_object.position}: {type(map_object).__name__} {map_object.identifier} "
                      f"{[cargo.identifier for cargo in map_object.get_cargos()]}")
        for map_object in map_objects:
            if not isinstance(map_object, Vehicle):
                print(f"{map_object.position}{'->' + map_object.destiny if hasattr(map_object, 'destiny') else ''}:"
                      f" {type(map_object).__name__} {map_object.identifier} "
                      f" {'Payment ' + str(map_object.payment) if hasattr(map_object, 'payment') else ''}"
                      f" {'Final time ' + str(map_object.final_time) if hasattr(map_object, 'final_time') else ''}")

