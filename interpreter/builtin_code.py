from __future__ import annotations
from dataclasses import dataclass


@dataclass
class A:
    a: [int]
    b: {int: str}
