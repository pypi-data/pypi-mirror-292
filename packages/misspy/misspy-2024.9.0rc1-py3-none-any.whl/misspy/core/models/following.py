from mitypes import UserLite

from pydantic import dataclasses

@dataclasses.dataclass()
class RequestList:
    id: str
    follower: UserLite
    followee: UserLite
