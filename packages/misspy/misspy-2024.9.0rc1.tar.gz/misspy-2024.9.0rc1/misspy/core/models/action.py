from typing import Any

from pydantic import dataclasses


@dataclasses.dataclass
class reactions:
    create: Any
    delete: Any


@dataclasses.dataclass
class APIAction:
    reply: Any
    renote: Any
    reactions: reactions
