from pydantic import dataclasses

from .users import UserDetailedNotMe


@dataclasses.dataclass()
class blocking_list:
    id: str
    createdAt: str
    blockeeId: str
    blockee: UserDetailedNotMe
