from enum import Enum
from typing import Union

from mitypes.user import UserLite
from pydantic import dataclasses

from .note import Note

class AnnounceIconEnum(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"

class AnnounceDisplayEnum(str, Enum):
    DIALOG = "dialog"
    NORMAL = "normal"
    BANNER = "banner"

@dataclasses.dataclass()
class Announce:
    id: str
    createdAt: str
    updatedAt: Union[str, None]
    text: str
    title: str
    imageUrl: Union[str, None]
    icon: AnnounceIconEnum
    display: AnnounceDisplayEnum
    needConfirmationToRead: bool
    silence: bool
    forYou: bool
    isRead: bool

@dataclasses.dataclass()
class notifications:
    id: str
    createdAt: str
    type: str
    user: UserLite
    userId: str
    note: Note