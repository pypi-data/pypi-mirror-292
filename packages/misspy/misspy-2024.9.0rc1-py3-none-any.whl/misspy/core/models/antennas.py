from __future__ import annotations

from typing import Any, List, Union

from mitypes import UserLite
from mitypes.drive import DriveFile
from mitypes.poll import Poll
from pydantic import dataclasses

from .channel import Channel
from .federation import Emojis


@dataclasses.dataclass()
class notes:
    id: str
    createdAt: str
    deletedAt: Union[str, None]
    text: Union[str, None]
    cw: Union[str, None]
    userId: str
    user: UserLite
    replyId: Union[str, None]
    renoteId: Union[str, None]
    reply: notes
    renote: notes
    isHidden: bool
    visibility: str
    mentions: List[str]
    visibleUserIds: List[str]
    fileIds: List[str]
    files: List[DriveFile]
    tags: List[str]
    poll: Poll
    emojis: Emojis
    channelId: Union[str, None]
    channel: Channel
    localOnly: bool
    reactionAcceptance: Union[str, None]
    reactionEmojis: Emojis
    reactions: Any
    reactionCount: int
    renoteCount: int
    renoteCount: int
    repliesCount: int
    uri: str
    url: str
    reactionAndUserPairCache: List[str]
    clippedCount: int
    myReaction: Union[str, None]


@dataclasses.dataclass()
class created_antnna:
    id: str
    createdAt: str
    name: str
    keywords: List[str]
    excludeKeywords: List[str]
    src: str
    userListId: Union[str, None]
    users: List[str]
    notify: bool
    withFile: bool
    isActive: bool
    caseSensitive: bool = False
    localOnly: bool = False
    excludeBots: bool = False
    withReplies: bool = False
    hasUnreadNote: bool = False


@dataclasses.dataclass()
class show_antnna:
    id: str
    createdAt: str
    name: str
    keywords: List[str]
    excludeKeywords: List[str]
    src: str
    userListId: Union[str, None]
    users: List[str]
    notify: bool
    withFile: bool
    isActive: bool
    caseSensitive: bool = False
    localOnly: bool = False
    excludeBots: bool = False
    withReplies: bool = False
    hasUnreadNote: bool = False
