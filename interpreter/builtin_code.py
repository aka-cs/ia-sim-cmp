from __future__ import annotations
from collections import deque


class Map:
    pass


class Vehicle:

    def move(self, interval: int):
        pass


def start(vehicle: Vehicle, _map: Map):
    events = deque()
    while len(events):
        next_event = events.popleft()
        vehicle.move(next_event.time)
    print("Done")