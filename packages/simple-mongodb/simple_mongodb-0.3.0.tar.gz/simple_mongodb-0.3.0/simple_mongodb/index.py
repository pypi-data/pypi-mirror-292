from dataclasses import dataclass
from typing import Any, Literal


class Index:

    @dataclass
    class SimpleIndex:
        index: str
        name: str
        sort: Literal[1, -1] = 1
        unique: bool = False
        sparse: bool = True
        partialFilterExpression: None | dict[str, Any] = None

    @dataclass
    class CompoundIndex:
        indexes: list[tuple[str, Literal[1, -1]]]
        name: str
        unique: bool = False
        sparse: bool = True
        partialFilterExpression: None | dict[str, Any] = None

    @dataclass
    class TTLIndex:
        index: str
        name: str
        expireAfterSeconds: int
        sort: Literal[1, -1] = 1
        sparse: bool = True
        partialFilterExpression: None | dict[str, Any] = None
