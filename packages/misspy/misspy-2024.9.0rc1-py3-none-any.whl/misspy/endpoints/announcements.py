from typing import List, Union


from ..core.exception import NotFound
from ..core.http import AsyncHttpHandler
from ..core.models.notifications import Announce

class Announcements:
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

    async def announce(
        self,
        limit: int = 10,
        sinceId: str = None,
        untilId: str = None,
        isActive: bool = True,
    ) -> List[Announce]:
        """Obtains a list of files in the specified folder or root hierarchy under the logged-in user's drive.

        Args:
            limit (int, optional): Maximum number of announcement to retrieve. Defaults to 10.
            sinceId (str, optional): If specified, returns announcement whose id is greater than that value. Defaults to None.
            untilId (str, optional): If specified, returns announcement whose id is less than that value. Defaults to None.
            isActive (Union[str, None], optional): If the id of the parent folder is null (default), files in the root hierarchy are retrieved. Defaults to None.

        Returns:
            List[Announce]: Announcements
        """
        endpoint = "announcements"
        if endpoint not in self.endpoints:
            raise NotFound('endpoint "announcements" is not found.')
        data = {"limit": limit, "isActive": isActive}
        if sinceId:
            data["sinceId"] = sinceId
        if untilId:
            data["untilId"] = untilId
        resp = await self.http.send(endpoint, data=data)
        anmts = []
        for res in resp:
            anmts.append(Announce(**res))
        return anmts

    async def show(self, announcementId: str) -> Announce:
        """Show announcements

        Args:
            announcementId (str): announcement id.

        Returns:
            Announce: announce body
        """
        endpoint = "announcements/show"
        if endpoint not in self.endpoints:
            raise NotFound('endpoint "announcements/show" is not found.')
        return Announce(**await self.http.send(endpoint, data={"announcementId": announcementId}))
