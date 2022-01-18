from __future__ import annotations
from dataclasses import dataclass

import heapq


@dataclass
class Event:
    time: int


@dataclass
class Position:
    x: int
    y: int


@dataclass
class Cargo:
    position: Position


@dataclass
class Environment:

    def get_state(self):
        pass

    def update_state(self, event: Event) -> [Event]:
        pass


@dataclass
class Vehicle:
    position: Position
    path: [Position]

    def update_state(self, env: Environment, time: int) -> Event:
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
        heapq.heappush(events, vehicle.update_state(env, time))
