from __future__ import annotations
from collections import deque


class Map:

    def __init__(self):
        pass


class Vehicle:

    def __init__(self):
        pass

    def move(self, interval: int):
        pass


def start(vehicle: Vehicle, _map: Map):
    events = deque()
    while len(events):
        next_event = events.popleft()
        vehicle.move(next_event.time)
    print("Done")