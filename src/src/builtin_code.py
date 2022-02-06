from __future__ import annotations
from .vehicles import *
from math import inf
import heapq


def infinity() -> float:
    return inf


def simulate_environment(env: Environment, initial_events: [Event], total_time: int) -> None:
    """
    Simula el entorno, evento a evento.
    """
    actual_event = None
    events = [event for event in initial_events]
    while events and (actual_event := heapq.heappop(events)) and actual_event.time <= total_time:
        for event in env.update_state(actual_event):
            heapq.heappush(events, event)

        # Imprimimos los resultados de cada evento en la simulación.
        print(f"\nTime: {actual_event.time}")
        for place in env.get_places():
            for map_object in env.get_all_objects(place):
                print(f"{map_object.position}: {type(map_object).__name__} {map_object.identifier} "
                      f"{[cargo.identifier for cargo in map_object.get_cargos()] if isinstance(map_object, Vehicle) else ''}")

