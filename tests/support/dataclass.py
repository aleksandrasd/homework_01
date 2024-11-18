from dataclasses import dataclass


@dataclass
class Person:
    name: str
    age: int
    surname: str | None = None