from typing import Union

from pydantic import dataclasses

@dataclasses.dataclass()
class RoleLite:
    id: str
    name: str
    color: Union[str, None]
    iconUrl: Union[str, None]
    description: str
    isModerator: bool
    isAdminstrator: bool
    displayOrder: int
