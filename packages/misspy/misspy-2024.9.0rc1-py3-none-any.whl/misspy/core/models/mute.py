from typing import Union

from .users import UserDetailedNotMe
from pydantic import dataclasses


@dataclasses.dataclass()
class mute:
    id: str
    createdAt: str
    expiresAt: Union[str, None]
    muteeId: str
    mutee: UserDetailedNotMe
