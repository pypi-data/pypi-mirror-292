from typing import Union, List

from pydantic import dataclasses
from mitypes.user import AvatarDecorations

from .note import Note
from .page import Page
from .role import RoleLite

@dataclasses.dataclass
class Emojis:
    ""


@dataclasses.dataclass
class Instance:
    name: Union[str, None]
    softwareName: Union[str, None]
    softwareVersion: Union[str, None]
    iconUrl: Union[str, None]
    faviconUrl: Union[str, None]
    themeColor: Union[str, None]


@dataclasses.dataclass
class BadgeRoles:
    name: str
    iconUrl: Union[str, None]
    displayOrder: int
    behavior: str


@dataclasses.dataclass
class field:
    name: str
    value: str

@dataclasses.dataclass
class users:
    id: str
    name: Union[str, None]
    username: str
    host: Union[str, None]
    avatarUrl: Union[str, None]
    avatarBlurhash: Union[str, None]
    avatarDecorations: AvatarDecorations
    isBot: bool
    isCat: bool
    instance: Instance
    emojis: Emojis
    onlineStatus: str
    badgeRoles: BadgeRoles
    url: Union[str, None]
    uri: Union[str, None]
    movedTo: Union[str, None]
    alsoKnownAs: List[Union[str, None]]
    createdAt: str
    updatedAt: Union[str, None]
    lastFetchedAt: Union[str, None]
    bannerUrl: Union[str, None]
    bannerBlurhash: Union[str, None]
    isLocked: bool
    isSilenced: bool
    isLimited: bool
    isSuspended: bool
    description: Union[str, None]
    location: Union[str, None]
    birthday: Union[str, None]
    lang: Union[str, None]
    fields: field
    verifiedLinks: List[str]
    followersCount: int
    followingCount: int
    notesCount: int
    pinnedNoteIds: List[str]
    pinnedNotes: List[Note]
    pinnedPageId: str
    pinnedPage: Page
    publicReactions: bool
    followingVisibility: str
    followersVisibility: str
    roles: RoleLite
    memo: Union[str, None]
    moderationNote: str
    isFollowing: bool
    isFollowed: bool
    hasPendingFollowRequestFromYou: bool
    hasPendingFollowRequestToYou: bool
    isBlocking: bool
    isBlocked: bool
    isMuted: bool
    isRenoteMuted: bool
    notify: str
    withReplies: bool
    twoFactorEnabled: bool = False
    usePasswordLessLogin: bool = False
    securityKeys: bool = False