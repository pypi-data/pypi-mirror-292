from typing import Any, List, Union

from mitypes import UserLite
from mitypes.user import AvatarDecorations
from pydantic import dataclasses
from pydantic.dataclasses import Field

from .federation import BadgeRoles, Emojis, Instance, field
from .note import Note
from .other import Achievements, Announcement, RolePolicies, SecurityKeysList
from .page import Page
from .role import RoleLite

@dataclasses.dataclass()
class DriveUsage:
    byte: int
    kilobyte: int
    megabyte: int
    gigabyte: int
    terabyte: int


@dataclasses.dataclass()
class UserStat:
    notesCount: int
    repliesCount: int
    renotesCount: int
    repliedCount: int
    renotedCount: int
    pollVotesCount: int
    pollVotedCount: int
    localFollowingCount: int
    remoteFollowingCount: int
    localFollowersCount: int
    remoteFollowersCount: int
    followingCount: int
    followersCount: int
    sentReactionsCount: int
    recivedReactionsCount: int
    noteFavoritesCount: int
    pageLikesCount: int
    pageLikedCount: int
    driveFilesCount: int
    driveUsage: DriveUsage


@dataclasses.dataclass()
class Relation:
    id: str
    isFollowing: bool
    hasPnedingFollowRequestFromYou: bool
    hasPendingFollowRequestToYou: bool
    isFollowed: bool
    isBlocking: bool
    isBlocked: bool
    isMuted: bool
    isRenoteMuted: bool


@dataclasses.dataclass()
class MeDetailed:
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
    badgeRoles: List[BadgeRoles]
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
    fields: List[field]
    verifiedLinks: List[str]
    followersCount: int
    followingCount: int
    notesCount: int
    pinnedNoteIds: List[str]
    pinnedNotes: List[Note]
    pinnedPageId: Union[str, None]
    pinnedPage: Page
    publicReactions: bool
    followingVisibility: str
    followersVisibility: str
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
    avatarId: Union[str, None]
    bannerId: Union[str, None]
    isModerator: Union[bool, None]
    isAdmin: Union[bool, None]
    injectFeaturedNote: bool
    receiveAnnouncementEmail: bool
    alwaysMarkNsfw: bool
    autoSensitive: bool
    carefulBot: bool
    autoAcceptFollowed: bool
    noCrawle: bool
    preventAiLearning: bool
    isExplorable: bool
    isDeleted: bool
    twoFactorBackupCodesStock: str
    hideOnlineStatus: bool
    hasUnreadSpecifiedNotes: bool
    hasUnreadMentions: bool
    hasUnreadAnnouncement: bool
    unreadAnnouncements: List[Announcement]
    hasUnreadAntenna: bool
    hasUnreadChannel: bool
    hasUnreadNotification: bool
    hasPendingReceivedFollowRequest: bool
    unreadNotificationsCount: int
    mutedWords: List[str]
    mutedInstances: List[Union[str, None]]
    notificationRecieveConfig: Any
    emailNotificationTypes: List[str]
    achievements: List[Achievements]
    loggedInDays: int
    policies: RolePolicies
    role: RoleLite
    email: Union[str, None]
    emailVerified: Union[bool, None]
    securityKeysList: List[SecurityKeysList]
    twoFactorEnabled: bool = False
    usePasswordLessLogin: bool = False
    securityKeys: bool = False


@dataclasses.dataclass()
class UserDetailedNotMe:
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
    badgeRoles: List[BadgeRoles]
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
    fields: List[field]
    verifiedLinks: List[str]
    followersCount: int
    followingCount: int
    notesCount: int
    pinnedNoteIds: List[str]
    pinnedNotes: List[Note]
    pinnedPageId: Union[str, None]
    pinnedPage: Page
    publicReactions: bool
    followingVisibility: str
    followersVisibility: str
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
    role: RoleLite
    twoFactorEnabled: bool = False
    usePasswordLessLogin: bool = False
    securityKeys: bool = False


@dataclasses.dataclass()
class followers:
    id: str
    createdAt: str
    followeeId: str
    followerId: str
    followee: UserDetailedNotMe
    follower: UserDetailedNotMe


@dataclasses.dataclass()
class reactions:
    id: str
    createdAt: str
    user: UserLite
    type: str


@dataclasses.dataclass()
class Frequently_replied:
    user: Union[UserDetailedNotMe, MeDetailed]
    weight: int


@dataclasses.dataclass()
class Follow:
    id: str
    name: Union[str, None]
    username: str
    host: Union[str, None]
    avatarUrl: Union[str, None]
    avatarBlurhash: Union[str, None]
    avatarDecorations: List[AvatarDecorations]
    isBot: bool
    isCat: bool
    instance: Instance
    emojis: Emojis
    onlineStatus: str
    badgeRoles: BadgeRoles

"""
@dataclasses.dataclass()
class Pin:
    id: str
    createdAt: str
    isLocked: bool
    isSilenced: bool
    isLimited: bool
    isSuspended: bool
    followersCount: int
    followingCount: int
    notesCount: int
    pinnedPage: Page
    publicReactions: bool
    followingVisibility: str
    followersVisibility: str
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
    injectFeaturedNote: bool
    receiveAnnouncementEmail: bool
    alwaysMarkNsfw: bool
    autoSensitive: bool
    carefulBot: bool
    autoAcceptFollowed: bool
    noCrawle: bool
    preventAiLearning: bool
    isExplorable: bool
    isDeleted: bool
    twoFactorBackupCodesStock: str
    hideOnlineStatus: bool
    hasUnreadSpecifiedNotes: bool
    hasUnreadMentions: bool
    hasUnreadAnnouncement: bool
    unreadAnnouncements: List[Announcement]
    hasUnreadAntenna: bool
    hasUnreadChannel: bool
    hasUnreadNotification: bool
    hasPendingReceivedFollowRequest: bool
    unreadNotificationsCount: int
    notificationRecieveConfig: Any
    loggedInDays: int
    policies: RolePolicies
    role: RoleLite
    name: Union[str, None] = None
    username: Union[str, None] = None
    host: Union[str, None] = None
    avatarUrl: Union[str, None] = None
    avatarBlurhash: Union[str, None] = None
    avatarDecorations: List[AvatarDecorations] = Field(default_factory=list)
    isBot: Union[bool, None] = None
    isCat: Union[bool, None] = None
    instance: Union[Instance, None] = None
    emojis: Emojis = Field(default_factory=list)
    onlineStatus: str = Field(default_factory="unknown")
    badgeRoles: List[BadgeRoles] = Field(default_factory=list)
    url: Union[str, None] = None
    uri: Union[str, None] = None
    movedTo: Union[str, None] = None
    alsoKnownAs: List[Union[str, None]] = None
    updatedAt: Union[str, None] = None
    lastFetchedAt: Union[str, None] = None
    bannerUrl: Union[str, None] = None
    bannerBlurhash: Union[str, None] = None
    description: Union[str, None] = None
    location: Union[str, None] = None
    birthday: Union[str, None] = None
    lang: Union[str, None] = None
    Fields: List[Field] = Field(default_factory=list)
    verifiedLinks: List[str] = Field(default_factory=list)
    pinnedNoteIds: List[str] = Field(default_factory=list)
    pinnedNotes: List[Note] = Field(default_factory=list)
    pinnedPageId: Union[str, None] = None
    memo: Union[str, None] = None

    avatarId: Union[str, None] = None
    bannerId: Union[str, None] = None
    isModerator: Union[bool, None] = None
    isAdmin: Union[bool, None] = None

    mutedWords: List[str] = Field(default_factory=list)
    mutedInstances: List[Union[str, None]] = None
    emailNotificationTypes: List[str] = Field(default_factory=list)
    achievements: List[Achievements] = Field(default_factory=list)

    email: Union[str, None] = None
    emailVerified: Union[bool, None] = None
    securityKeysList: List[SecurityKeysList] = Field(default_factory=list)
    twoFactorEnabled: bool = False
    usePasswordLessLogin: bool = False
    securityKeys: bool = False
"""