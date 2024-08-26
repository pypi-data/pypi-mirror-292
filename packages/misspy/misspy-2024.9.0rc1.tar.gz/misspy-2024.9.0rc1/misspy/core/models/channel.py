from __future__ import annotations

from typing import Union

from pydantic import dataclasses

@dataclasses.dataclass()
class Channel:
    id: str
    name: str
    color: str
    isSensitive: bool
    allowRenoteToExternal: bool
    userId: Union[str, None]
