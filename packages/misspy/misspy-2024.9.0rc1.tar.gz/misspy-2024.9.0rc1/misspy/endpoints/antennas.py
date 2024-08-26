from typing import List, Union

from mitypes import channel

from ..core.http import AsyncHttpHandler
from ..core.models.antennas import created_antnna, show_antnna


class Antennas:
    def __init__(
        self,
        address: str,
        i: Union[str, None],
        ssl: bool,
        endpoints: List[str],
        handler: AsyncHttpHandler = None,
    ) -> None:
        self.http = handler
        if handler is None:
            self.http = AsyncHttpHandler(address, i, ssl)
        self.endpoints = endpoints

    async def create(
        self,
        name: str,
        src: str,
        userListId: Union[str, None],
        keywords: List[List],
        excludeKeywords: List[List],
        users: List[str],
        caseSensitive: bool=False,
        localOnly: bool=False,
        execludeBots: bool=False,
        withReplies: bool=False,
        withFile: bool=False,
    ):
        resp = await self.http.send(
            "antennas/create",
            {
                "name": name,
                "src": src,
                "userListId": userListId,
                "keywords": keywords,
                "excludeKeywords": excludeKeywords,
                "users": users,
                "caseSensitive": caseSensitive,
                "localOnly": localOnly,
                "execludeBots": execludeBots,
                "withReplies": withReplies,
                "withFile": withFile,
            },
        )
        return created_antnna(
            **resp
        )
