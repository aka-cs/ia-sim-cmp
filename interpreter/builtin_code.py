from .builtin_base_classes import *


def infinity() -> float:
    return inf


def simulate_environment(env: Environment, initial_events: [Event], total_time: int):
    """
    Simula el entorno, evento a evento.
    """
    i = 0
    actual_event = None
    events = [event for event in initial_events]
    while events and (actual_event := heapq.heappop(events)) and actual_event.time <= total_time:
        for event in env.update_state(actual_event):
            heapq.heappush(events, event)

        i += 1
        print(f"\nIteración: {i}")
        for place in env.get_places():
            for map_object in env.get_all_objects(place):
                print(f"{map_object.position.place_name}: {type(map_object).__name__} {map_object.identifier} "
                      f"{[cargo.identifier for cargo in map_object.cargos] if isinstance(map_object, Vehicle) else ''}")
