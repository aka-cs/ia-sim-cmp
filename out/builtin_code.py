from __future__ import annotations
from dataclasses import dataclass

import heapq


@dataclass
class Event:
    time: int


class Environment:

    def __init__(self):
        pass

    def get_state(self):
        pass

    def update_state(self, time: int) -> [Event]:
        return []


class Vehicle:

    def __init__(self):
        pass

    def move(self, env: Environment, time: int) -> Event:
        pass

    def get_pos(self):
        pass

    def report_state(self):
        pass


def start(vehicle: Vehicle, env: Environment, total_time: int):
    time = 0
    events = [Event(0)]
    while events and (time := heapq.heappop(events).time) and time <= total_time:
        for event in env.update_state(time):
            heapq.heappush(events, event)
        vehicle.report_state()
        heapq.heappush(events, vehicle.move(env, time))
