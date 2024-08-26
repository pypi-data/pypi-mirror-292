from typing import List, Union

from mitypes import User, UserLite
from mitypes.drive import DriveFile

from ..core.http import AsyncHttpHandler, HttpHandler
from ..core.models.antennas import created_antnna, notes, show_antnna
from ..core.models.blocking import blocking_list
from ..core.models.clip import clips
from ..core.models.favorites import favorite
from ..core.models.following import RequestList
from ..core.models.likes import GalleryPost, Like
from ..core.models.mute import mute as mp_mute
from ..core.models.note import Note  # , Pin
from ..core.models.notifications import notifications as notify
from ..core.models.page import Page, likes
from ..core.models.users import (
    Follow,
    Frequently_replied,
    MeDetailed,
    Relation,
    UserDetailedNotMe,
    UserStat,
    followers,
    reactions,
)
from ..utils.internaltool import nonecheck


class i:
    def __init__(
        self,
        address: str,
        i: Union[str, None],
        ssl: bool,
        endpoints: List[str],
        handler: AsyncHttpHandler = None,
    ) -> None:
        self.i = i
        self.address = address
        self.ssl = ssl
        self.__http = handler

    async def get(self):
        r = await self.__http.send("i", {})
        return User(**r)

    async def favorites(self, limit=10, sinceId=None, untilId=None):
        base = {"limit": limit}
        if nonecheck(sinceId):
            base["sinceId"] = sinceId
        if nonecheck(untilId):
            base["untilId"] = untilId
        return [favorite(**fav) for fav in await self.__http.send("i/favorites", base)]

    async def gallery_likes(self, limit=10, sinceId=None, untilId=None):
        base = {"limit": limit}
        if nonecheck(sinceId):
            base["sinceId"] = sinceId
        if nonecheck(untilId):
            base["untilId"] = untilId
        resp = await self.__http.send("i/gallery/likes", base)
        likes = []
        for like in resp:
            like["post"]["files"] = [DriveFile(**fav) for fav in resp["files"]]
            likes.append(Like(**like))
        return likes

    async def gallery_posts(self, limit=10, sinceId=None, untilId=None):
        base = {"limit": limit}
        if nonecheck(sinceId):
            base["sinceId"] = sinceId
        if nonecheck(untilId):
            base["untilId"] = untilId
        resp = await self.__http.send("i/gallery/posts", base)
        posts = []
        for post in resp:
            post["files"] = [DriveFile(**fav) for fav in resp["files"]]
            posts.append(GalleryPost(**post))
        return posts

    async def notifications(
        self,
        limit=10,
        sinceId=None,
        untilId=None,
        following=False,
        unreadOnly=False,
        markAsRead=True,
        includeTypes=None,
        excludeTypes=None,
    ):
        base = {
            "limit": limit,
            "following": following,
            "unreadOnly": unreadOnly,
            "markAsRead": markAsRead,
        }
        if nonecheck(sinceId):
            base["sinceId"] = sinceId
        if nonecheck(untilId):
            base["untilId"] = untilId
        if nonecheck(includeTypes):
            base["includeTypes"] = includeTypes
        if nonecheck(excludeTypes):
            base["excludeTypes"] = excludeTypes
        return [
            notify(**notif) for notif in await self.__http.send("i/notifications", base)
        ]

    async def page_likes(self, limit=10, sinceId=None, untilId=None):
        base = {"limit": limit}
        if nonecheck(sinceId):
            base["sinceId"] = sinceId
        if nonecheck(untilId):
            base["untilId"] = untilId
        return [
            Page(**page_like)
            for page_like in await self.__http.send("i/page-likes", base)
        ]

    async def pages(self, limit=10, sinceId=None, untilId=None):
        base = {"limit": limit}
        if nonecheck(sinceId):
            base["sinceId"] = sinceId
        if nonecheck(untilId):
            base["untilId"] = untilId
        resp = await self.__http.send("i/page-likes", base)
        lks = []
        for page_like in resp:
            lks.append(likes(**page_like))
        return lks

    """
    async def pin(self, noteId):
        return Pin(**await self.__http.send("i/pin", {"noteId": noteId}))

    async def unpin(self, noteId):
        return Pin(**await self.__http.send("i/unpin", {"noteId": noteId}))

    async def update(self, params):
        return Pin(**await self.__http.send("i/update", params))
    """

    async def read_all_unread_notes(self):
        return await self.__http.send("i/read-all-unread-notes", {})

    async def read_announcement(self, announcementId):
        return await self.__http.send(
            "i/read-all-unread-notes",
            {"announcementId": announcementId},
        )


class blocking:
    def __init__(
        self,
        address: str,
        i: Union[str, None],
        ssl: bool,
        endpoints: List[str],
        handler: AsyncHttpHandler = None,
    ) -> None:
        self.__http = handler

    async def create(self, userId: str):
        params = {"userId": userId}
        r = await self.__http.send("blocking/create", params)
        return UserDetailedNotMe(**r)

    async def delete(self, userId: str):
        params = {"userId": userId}
        r = await self.__http.send("blocking/delete", params)
        return r

    async def list(self, limit: int = 30, sinceId: str = None, untilId: str = None):
        params = {
            "limit": limit,
        }
        if sinceId is not None:
            params["sinceId"] = sinceId
        if untilId is not None:
            params["untilId"] = untilId
        r = await self.__http.send("blocking/list", params)
        return [blocking_list(**page_like) for page_like in r]


class antennas:
    def __init__(
        self,
        address: str,
        i: Union[str, None],
        ssl: bool,
        endpoints: List[str],
        handler: AsyncHttpHandler = None,
    ) -> None:
        self.i = i
        self.address = address
        self.__http = handler
        self.endpoints = endpoints

    async def create(
        self,
        name,
        src,
        keywords,
        excludeKeywords,
        users,
        caseSensitive,
        withReplies,
        withFile,
        notify,
        userListId=None,
    ):
        base = {
            "name": name,
            "src": src,
            "keywords": keywords,
            "excludeKeywords": excludeKeywords,
            "users": users,
            "caseSensitive": caseSensitive,
            "withReplies": withReplies,
            "withFile": withFile,
            "notify": notify,
        }
        if nonecheck(userListId):
            base["userListId"] = userListId
        return created_antnna(**await self.__http.send("antennas/create", base))

    async def update(
        self,
        name,
        src,
        keywords,
        excludeKeywords,
        users,
        caseSensitive,
        withReplies,
        withFile,
        notify,
        userListId=None,
    ):
        base = {
            "name": name,
            "src": src,
            "keywords": keywords,
            "excludeKeywords": excludeKeywords,
            "users": users,
            "caseSensitive": caseSensitive,
            "withReplies": withReplies,
            "withFile": withFile,
            "notify": notify,
        }
        if nonecheck(userListId):
            base["userListId"] = userListId
        return created_antnna(**self.__http.send("antennas/update", base))

    async def delete(self, antennaId):
        return self.__http.send("antennas/delete", {"antennaId": antennaId})

    async def show(self, antennaId):
        return show_antnna(
            **self.__http.send("antennas/show", {"antennaId": antennaId})
        )

    async def list(self):
        return [show_antnna(**r) for r in await self.__http.send("antennas/list", {})]

    async def notes(
        self,
        antennaId,
        limit=10,
        sinceId=None,
        untilId=None,
        sinceDate=None,
        untilDate=None,
    ):
        base = {"antennaId": antennaId, "limit": limit}
        if nonecheck(sinceId):
            base["sinceId"] = sinceId
        if nonecheck(untilId):
            base["untilId"] = untilId
        if nonecheck(sinceDate):
            base["sinceDate"] = sinceDate
        if nonecheck(untilDate):
            base["untilDate"] = untilDate
        return [notes(**r) for r in await self.__http.send("antennas/notes", base)]


class mute:
    def __init__(
        self,
        address: str,
        i: Union[str, None],
        ssl: bool,
        endpoints: List[str],
        handler: AsyncHttpHandler = None,
    ) -> None:
        self.__http = handler

    async def create(self, userId, expiresAt=None):
        return await self.__http.send(
            "mute/create",
            {"userId": userId, "expiresAt": expiresAt},
        )

    async def list(self, limit=30, sinceId=None, untilId=None):
        base = {"limit": limit}
        if nonecheck(sinceId):
            base["sinceId"] = sinceId
        if nonecheck(untilId):
            base["untilId"] = untilId
        return [mp_mute(**r) for r in await self.__http.send("mute/list", base)]

    async def delete(self, userId):
        return await self.__http.send("mute/delete", {"userId": userId})


class users:
    def __init__(
        self,
        address: str,
        i: Union[str, None],
        ssl: bool,
        endpoints: List[str],
        handler: AsyncHttpHandler = None,
    ) -> None:
        self.i = i
        self.address = address
        self.__http = handler
        self.__http_sync = HttpHandler(address, i, ssl)

    async def get(
        self, limit=10, offset=0, sort=None, state="all", origin="local", hostname=None
    ):
        base = {
            "limit": limit,
            "offset": offset,
            "state": state,
            "origin": origin,
            "hostname": hostname,
        }
        if nonecheck(sort):
            base["sort"] = sort
        resp = await self.__http.send("users", base)
        rl = []
        for r in resp:
            if r.get("loggedInDays") is None:
                rl.append(MeDetailed(**r))
            else:
                rl.append(UserDetailedNotMe(**r))
        return rl

    async def clips(self, userId, limit=10, sinceId=None, untilId=None):
        base = {"userId": userId, "limit": limit}
        if nonecheck(sinceId):
            base["sinceId"] = sinceId
        if nonecheck(untilId):
            base["untilId"] = untilId
        return [clips(**r) for r in await self.__http.send("users/clips", base)]

    async def followers(self, limit=10, sinceId=None, untilId=None):
        base = {"limit": limit}
        if nonecheck(sinceId):
            base["sinceId"] = sinceId
        if nonecheck(untilId):
            base["untilId"] = untilId
        return [followers(**r) for r in await self.__http.send("users/followers", base)]

    async def following(self, limit=10, sinceId=None, untilId=None):
        base = {"limit": limit}
        if nonecheck(sinceId):
            base["sinceId"] = sinceId
        if nonecheck(untilId):
            base["untilId"] = untilId
        return [followers(**r) for r in await self.__http.send("users/following", base)]

    async def gallery_posts(self, userId, limit=10, sinceId=None, untilId=None):
        base = {"userId": userId, "limit": limit}
        if nonecheck(sinceId):
            base["sinceId"] = sinceId
        if nonecheck(untilId):
            base["untilId"] = untilId
        return [
            GalleryPost(**r)
            for r in await self.__http.send("users/gallery/posts", base)
        ]

    async def pages(self, userId, limit=10, sinceId=None, untilId=None):
        base = {"userId": userId, "limit": limit}
        if nonecheck(sinceId):
            base["sinceId"] = sinceId
        if nonecheck(untilId):
            base["untilId"] = untilId
        return [Page(**r) for r in await self.__http.send("users/pages", base)]

    async def reactions(
        self,
        userId,
        limit=10,
        sinceId=None,
        untilId=None,
        sinceDate=None,
        untilDate=None,
    ):
        base = {"userId": userId, "limit": limit}
        if nonecheck(sinceId):
            base["sinceId"] = sinceId
        if nonecheck(untilId):
            base["untilId"] = untilId
        if nonecheck(sinceDate):
            base["sinceDate"] = sinceDate
        if nonecheck(untilDate):
            base["untilDate"] = untilDate
        return [reactions(**r) for r in await self.__http.send("users/reactions", base)]

    async def recommendation(
        self,
        limit=10,
        offset=0,
    ):
        base = {"limit": limit, "offset": offset}
        r = await self.__http.send("users/recommendation", base)
        ret = r
        if not isinstance(r, bool):
            ret = []
            for res in r:
                if res.get("loggedInDays"):
                    ret.append(MeDetailed(res))
                else:
                    ret.append(UserDetailedNotMe(res))
        return ret

    async def relation(self, userId):
        r = await self.__http.send("users/relation", {"userId": userId})
        if isinstance(r, dict):
            return Relation(**r)
        elif isinstance(r, list):
            return [Relation(**res) for res in r]

    async def report_abuse(self, userId, comment):
        return await self.__http.send(
            "users/report-abuse",
            {"userId": userId, "comment": comment},
        )

    async def search_by_username_and_host(
        self, username=None, host=None, limit=10, detail=True
    ) -> Union[UserLite, MeDetailed, UserDetailedNotMe]:
        r = await self.__http.send(
            "users/search-by-username-and-host",
            {"username": username, "host": host, "limit": limit, "detail": detail},
        )
        if r.get("alsoKnownAs") is None:
            return UserLite(**r)
        elif r.get("alsoKnownAs"):
            if r.get("loggedInDays"):
                return MeDetailed(**r)
            elif r.get("loggedInDays") is None:
                return UserDetailedNotMe(**r)

    async def search(
        self, query, offset=0, limit=10, origin="combined", detail=True
    ) -> Union[UserLite, MeDetailed, UserDetailedNotMe]:
        r = await self.__http.send(
            "users/search",
            {
                "query": query,
                "offset": offset,
                "limit": limit,
                "origin": origin,
                "detail": detail,
            },
        )
        if r.get("alsoKnownAs") is None:
            return UserLite(**r)
        else:
            if r.get("loggedInDays") is None:
                return UserDetailedNotMe(**r)
            return MeDetailed(**r)

    def show(
        self, username, host=None
    ) -> Union[
        UserLite,
        MeDetailed,
        UserDetailedNotMe,
        List[UserLite],
        List[MeDetailed],
        List[UserDetailedNotMe],
    ]:
        r = self.__http.send("users/show", {"username": username, "host": None})
        if isinstance(r, dict):
            if r.get("alsoKnownAs") is None:
                return UserLite(**r)
            else:
                if r.get("loggedInDays") is None:
                    return UserDetailedNotMe(**r)
                return MeDetailed(**r)
        elif isinstance(r, list):
            rl = []
            for res in r:
                if res.get("alsoKnownAs") is None:
                    rl.append(UserLite(**r))
                else:
                    if res.get("loggedInDays") is None:
                        rl.append(UserDetailedNotMe(**r))
                    rl.append(MeDetailed(**r))
            return rl

    async def stats(self, userId):
        r = await self.__http.send("users/stats", {"userId": userId})
        usage = r["driveUsage"]
        r["driveUsage"] = {
            "byte": usage,
            "kilobyte": usage * 1024,
            "megabyte": (usage * 1024) * 1024,
            "gigabyte": ((usage * 1024) * 1024) * 1024,
            "terabyte": (((usage * 1024) * 1024) * 1024) * 1024,
        }
        return UserStat(**r)

    async def get_frequently_replied_users(
        self,
        userId,
        limit=10,
    ):
        base = {"userId": userId, "limit": limit}
        return [
            Frequently_replied(**r)
            for r in await self.__http.send("users/get-frequently-replied-users", base)
        ]

    async def notes(
        self,
        userId,
        includeReplies=True,
        limit=10,
        sinceId=None,
        untilId=None,
        sinceDate=None,
        untilDate=None,
        includeMyRenotes=True,
        withFiles=False,
        fileType=None,
        excludeNsfw=False,
    ):
        base = {
            "userId": userId,
            "includeReplies": includeReplies,
            "limit": limit,
            "includeMyRenotes": includeMyRenotes,
            "withFiles": withFiles,
            "excludeNsfw": excludeNsfw,
        }
        if nonecheck(sinceDate):
            base["sinceDate"] = sinceDate
        if nonecheck(untilDate):
            base["untilDate"] = untilDate
        if nonecheck(withFiles):
            base["withFiles"] = withFiles
        if nonecheck(fileType):
            base["fileType"] = fileType
        if nonecheck(sinceId):
            base["sinceId"] = sinceId
        if nonecheck(untilId):
            base["untilId"] = untilId
        return [Note(**r) for r in await self.__http.send("users/notes", base)]


class following:
    def __init__(
        self,
        address: str,
        i: Union[str, None],
        ssl: bool,
        endpoints: List[str],
        handler: AsyncHttpHandler = None,
    ) -> None:
        self.__http = handler

    async def create(self, userId) -> Follow:
        return Follow(**await self.__http.send("following/create", {"userId": userId}))

    async def delete(self, userId) -> Follow:
        return Follow(**await self.__http.send("following/delete", {"userId": userId}))

    async def invalidate(self, userId) -> Follow:
        return Follow(
            await self.__http.send("following/invalidate", {"userId": userId})
        )

    async def requests_accept(self, userId) -> bool:
        return await self.__http.send("following/requests/accept", {"userId": userId})

    async def requests_cancel(self, userId) -> Follow:
        return Follow(
            await self.__http.send("following/requests/cancel", {"userId": userId})
        )

    async def requests_list(self) -> List[RequestList]:
        return [
            RequestList(**r)
            for r in await self.__http.send("following/requests/list", {})
        ]

    async def requests_reject(self, userId) -> bool:
        return await self.__http.send("following/requests/reject", {"userId": userId})
