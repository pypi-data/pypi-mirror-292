from typing import List, Union

from pydantic import dataclasses

@dataclasses.dataclass()
class App:
    id: str
    name: str
    callbackUrl: str
    permission: List[str]
    secret: str


@dataclasses.dataclass()
class SecurityKeysList:
    id: str
    name: str
    lastUsed: str


@dataclasses.dataclass()
class RolePolicies:
    gtlAvailable: bool
    ltlAvailable: bool
    canPublicNote: bool
    canInitiateConversation: bool
    canCreateContent: bool
    canUpdateContent: bool
    canDeleteContent: bool
    canPurgeAccount: bool
    canUpdateAvatar: bool
    canUpdateBanner: bool
    mentionLimit: int
    canInvite: bool
    inviteLimit: int
    inviteLimitCycle: int
    inviteExpirationTime: int
    canManageCustomEmojis: bool
    canManageAvatarDecorations: bool
    canSearchNotes: bool
    canUseTranslator: bool
    canUseDriveFileInSoundSettings: bool
    canHideAds: bool
    driveCapacityMb: int
    alwaysMarkNsfw: bool
    skipNsfwDetection: bool
    pinLimit: int
    antennaLimit: int
    antennaNotesLimit: int
    wordMuteLimit: int
    webhookLimit: int
    clipLimit: int
    noteEachClipsLimit: int
    userListLimit: int
    userEachUserListsLimit: int
    rateLimitFactor: int
    avatarDecorationLimit: int


@dataclasses.dataclass()
class Achievements:
    name: str
    unlockedAt: int


@dataclasses.dataclass()
class Announcement:
    id: str
    createdAt: str
    updatedAt: Union[str, None]
    text: str
    title: str
    imageUrl: Union[str, None]
    icon: str
    display: str
    needConfirmationToRead: bool
    forYou: bool
    closeDuration: int
    displayOrder: int
    silence: bool
    isRead: bool
