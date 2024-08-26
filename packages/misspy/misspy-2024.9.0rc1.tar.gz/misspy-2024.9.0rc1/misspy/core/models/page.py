from __future__ import annotations

from typing import List, Union

from mitypes.drive import DriveFile
from mitypes.user import UserLite
from pydantic import dataclasses


@dataclasses.dataclass()
class PageBlock:
    pass


@dataclasses.dataclass()
class Properties:
    width: int
    height: int
    orientation: int
    avgColor: str


@dataclasses.dataclass()
class Folder:
    id: str
    createdAt: str
    name: str
    parentId: Union[str, None]
    foldersCount: int
    filesCount: int
    parent: Folder


@dataclasses.dataclass()
class eyeCatchingImage:
    id: str
    createdAt: str
    name: str
    type: str
    md5: str
    size: int
    isSensitive: bool
    blurhash: Union[str, None]
    properties: Properties
    url: str
    thumbnailUrl: Union[str, None]
    comment: Union[str, None]
    folderId: Union[str, None]
    folder: Folder


@dataclasses.dataclass()
class Page:
    id: str
    createdAt: str
    updatedAt: str
    userId: str
    user: UserLite
    content: PageBlock
    variables: List[object]
    title: str
    name: str
    summary: Union[str, None]
    hideTitleWhenPinned: bool
    alignCenter: bool
    font: str
    script: str
    eyeCatchingImageId: Union[str, None]
    eyeCatchingImage: eyeCatchingImage
    attachedFiles: List[DriveFile]
    likedCount: int
    isLiked: bool


@dataclasses.dataclass()
class likes:
    id: str
    page: Page
