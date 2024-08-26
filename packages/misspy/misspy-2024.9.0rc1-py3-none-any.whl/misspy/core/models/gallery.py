from typing import List, Union

from mitypes import DriveFile, UserLite
from pydantic import dataclasses


@dataclasses.dataclass()
class posts:
    id: str
    createdAt: str
    updatedAt: str
    userId: str
    user: UserLite
    title: str
    description: Union[str, None]
    fileIds: List[str]
    files: DriveFile
    tags: List[str]
    isSensitive: bool
    likedCount: int
    isLikes: bool
