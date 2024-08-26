import sys
from datetime import datetime
from typing import Any, List, Union

from mitypes.drive import DriveFile
from mitypes.user import AvatarDecorations, UserLite
from pydantic.dataclasses import dataclass, Field

from .action import APIAction
from .channel import Channel
# from .federation import BadgeRoles, Emojis, Instance
from .internal import mspy


@dataclass()
class Context:
    id: str
    createdAt: str
    userId: str
    user: UserLite
    localOnly: bool
    renoteCount: int
    repliesCount: int
    clippedCount: int
    reactionCount: int
    reactionEmojis: dict
    reactionAndUserPairCache: List[str]
    replyId: Union[str, None] = None
    renoteId: Union[str, None] = None
    visibility: str = None
    reactions: Union[dict, None] = None
    uri: Union[str, None] = None
    url: Union[str, None] = None
    isHidden: Union[bool, None] = None
    deletedAt: Union[str, None] = None
    text: Union[str, None] = None
    cw: Union[str, None] = None
    reply: Union[dict, None] = None
    renote: Union[dict, None] = None
    mentions: List[str] = Field(default_factory=list)
    visibleUserIds: List[str] = Field(default_factory=list)
    fileIds: List[str] = Field(default_factory=list)
    files: List[DriveFile] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    poll: Union[dict, None] = None
    channelId: Union[str, None] = None
    channel: Union[dict, None] = None
    reactionAcceptance: Union[str, None] = None
    reactionAndUserPairCache: List[str] = Field(default_factory=list)
    misspy: Union[mspy, None] = None
    api: Union[APIAction, None] = None


@dataclass()
class Note:
    id: str
    createdAt: str
    userId: str
    user: UserLite
    visibility: str
    localOnly: bool
    uri: str
    url: str
    reactions: dict
    renoteCount: int
    repliesCount: int
    reactionCount: int
    clippedCount: int
    reactionEmojis: dict
    reactionAndUserPairCache: List[str]
    replyId: Union[str, None] = None
    renoteId: Union[str, None] = None
    myReaction: Union[dict, None] = None

    isHidden: Union[bool, None] = None
    deletedAt: Union[str, None] = None
    text: Union[str, None] = None
    cw: Union[str, None] = None
    reply: Union[dict, None] = None
    renote: Union[dict, None] = None
    mentions: List[str] = Field(default_factory=list)
    visibleUserIds: List[str] = Field(default_factory=list)
    fileIds: List[str] = Field(default_factory=list)
    files: List[DriveFile] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    poll: Union[dict, None] = None
    channelId: Union[str, None] = None
    channel: Union[Channel, None] = None
    reactionAcceptance: Union[str, None] = None
    reactionAndUserPairCache: List[str] = Field(default_factory=list)
    misspy: Union[mspy, None] = None

    def __post_init__(self):
        verinf = sys.version_info
        if not verinf.major + verinf.minor >= 311:
            self.createdAt = datetime.fromisoformat(
                self.createdAt.replace("Z", "+00:00")
            )
            if self.deletedAt:
                self.deletedAt = datetime.fromisoformat(
                    self.deletedAt.replace("Z", "+00:00")
                )
        else:
            self.createdAt = datetime.fromisoformat(self.createdAt)
            if self.deletedAt:
                self.deletedAt = datetime.fromisoformat(self.deletedAt)