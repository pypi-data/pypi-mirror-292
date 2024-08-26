import asyncio
import inspect
import logging
import traceback
from enum import Enum
from functools import partial, reduce

from importlib import import_module
from typing import Union

from mitypes.user import User

from .core.exception import (
    ClientException,
    MisskeyAPIError,
)

#     NotExtensionError
from .core.http import AsyncHttpHandler, HttpHandler
from .core.models.internal import error
from .core.models.note import Context
from .core.websocket import MiWS_V2
from .core.experimental.aiows import MSC

# from .core.models.note import Context
from .endpoints.drive import drive
from .endpoints.i import antennas, blocking, following, mute, users
from .endpoints.i import i as ep_i
from .endpoints.notes import notes
from .endpoints.reaction import reactions


class Timeline(Enum):
    HOME = "homeTimeline"
    LOCAL = "localTimeline"
    SOCIAL = "hybridTimeline"
    HYBRID = "hybridTimeline"
    GLOBAL = "globalTimeline"


class Bot:
    def __init__(self, address: str, i: Union[str, None], use_ws_aio: bool=False) -> None:
        self.apierrors = []
        self.logger = logging.getLogger("misspy")
        self.address = address
        self._i = i
        self.engine = MiWS_V2 if not use_ws_aio else MSC
        self.ssl = True
        self.http = AsyncHttpHandler(
            self.address, self._i, self.ssl, logger=self.logger
        )
        self.http_sync = HttpHandler(self.address, self._i, self.ssl)
        self.user: User = User(**self.__i())
        self.__funcs: dict = {}
        self.cls = []
        self.endpoint_list = self.endpoints()
        args = {
            "address": self.address,
            "i": self._i,
            "ssl": self.ssl,
            "endpoints": self.endpoint_list,
            "handler": self.http,
        }
        # ---------- endpoints ------------
        self.antennas = antennas(**args)
        self.notes = notes(**args)
        self.drive = drive(**args)
        self.reactions = reactions(**args)
        self.i = ep_i(**args)
        self.blocking = blocking(**args)
        self.mute = mute(**args)
        self.users = users(**args)
        self.following = following(**args)
        # ---------------------------------
        self.reconnectionCoolDown: int = 3

        self.__connected_channels: list = []

    def __i(self):
        return self.http_sync.send("i", data={})

    def endpoints(self):
        return self.http_sync.send("endpoints", data={})

    def run(self, reconnect=False, log_handler: logging.Logger="INTERNAL"):
        asyncio.run(self.start())

    async def __reconnecter(self):
        for channel in self.__connected_channels:
            await self.connect(channel["channel"], channel["id"])
        self.__funcs["on_ready"].pop(0)

    async def start(self, reconnect=False):
        self.ws = self.engine(self.address, self._i, self.handler, reconnect, self.ssl)
        await self.handler({"type": "__internal", "body": {"type": "setup_hook"}})
        try:
            await self.ws.start()
        except Exception as e:
            if isinstance(e, self.ws.ConnectionClosedError):
                if reconnect:
                    if isinstance(self.reconnectionCoolDown, int):
                        await asyncio.sleep(self.reconnectionCoolDown)
                    else:
                        await asyncio.sleep(3)
                    if self.__funcs.get("on_ready"):
                        self.__funcs["on_ready"].insert(0, self.__reconnecter)
                    else:
                        self.__funcs["on_ready"] = [self.__reconnecter]
                    await self.start(reconnect)

                else:
                    await self.handler(
                        {
                            "type": "__internal",
                            "body": {
                                "type": "exception",
                                "errorType": e.__class__.__name__,
                                "exc": traceback.format_exc(),
                                "exc_obj": e,
                            },
                        }
                    )
            await self.handler(
                {
                    "type": "__internal",
                    "body": {
                        "type": "exception",
                        "errorType": e.__class__.__name__,
                        "exc": traceback.format_exc(),
                        "exc_obj": e,
                    },
                }
            )

    async def include_gear(self, package):
        module = import_module(package).gear
        self.__funcs = reduce(lambda d1, d2: {key: d1.get(key, []) + d2.get(key, []) for key in set(d1) | set(d2)}, [module._funcs, self.__funcs])

    def event(self, event=""):
        """A decorator that can listen for events in Discord.py-like notation.

        For a list of events, see [documentation](https://docs.misspy.xyz/rewrite/events).

        ## Examples:
        ```python
        @bot.event()
        async def on_ready():
            print("ready!")
        ```

        ↓ Put the event name in the decorator argument.
        ```python
        @bot.event("ready")
        async def ready():
            print("ready!")
        ```

        Args:
            event (str): Name of the event to listen for.
        """

        def decorator(func):
            if event == "":
                ev = func.__name__
            else:
                ev = event
            func.__event_type = ev
            if isinstance(func, staticmethod):
                func = func.__func__
            if not inspect.iscoroutinefunction(func):
                raise TypeError("Functions that listen for events must be coroutines.")
            if self.__funcs.get(ev) and isinstance(self.__funcs.get(ev), list):
                ev: list = self.__funcs.get(ev)
                ev.append(func)
            else:
                self.__funcs[ev] = [func]
            return func

        return decorator

    """
    async def load_extension(self, module: str):
        module = import_module(module)
        try:
            await module.setup(self)
        except AttributeError:
            raise NotExtensionError(
                "Module loading failed because the setup function does not exist in the module."
            )
    """

    async def connect(self, channel: Union[str, Timeline], id=None):
        if isinstance(channel, Timeline):
            channel = channel.value
        await self.ws.connect_channel(channel, id)
        self.__connected_channels.append({"channel": channel, "id": id})

    async def handler(self, json: dict):
        try:
            if json["type"] == "channel":
                if json["body"]["type"] == "note":
                    if self.__funcs.get("on_note") is None:
                        return
                    json["body"]["body"]["api"] = {}
                    json["body"]["body"]["api"]["reactions"] = {}
                    json["body"]["body"]["api"]["reactions"]["create"] = partial(
                        self.reactions.create, noteId=json["body"]["body"]["id"]
                    )
                    json["body"]["body"]["api"]["reactions"]["delete"] = partial(
                        self.reactions.delete, noteId=json["body"]["body"]["id"]
                    )
                    json["body"]["body"]["api"]["reply"] = partial(
                        self.notes.create, replyId=json["body"]["body"]["id"]
                    )
                    json["body"]["body"]["api"]["renote"] = partial(
                        self.notes.create, renoteId=json["body"]["body"]["id"]
                    )
                    pnote = Context(**json["body"]["body"])

                    for func in self.__funcs["on_note"]:
                        await func(pnote)
                if json["body"]["type"] == "followed":
                    if self.__funcs.get("on_followed") is None:
                        return
                    for func in self.__funcs["on_followed"]:
                        await func()
        except Exception as e:
            await self.handler(
                {
                    "type": "__internal",
                    "body": {
                        "type": "exception",
                        "errorType": e.__class__.__name__,
                        "exc": traceback.format_exc(),
                        "exc_obj": e,
                    },
                }
            )
        if json["type"] == "__internal":
            if json["body"]["type"] == "setup_hook":
                if self.__funcs.get("setup_hook") is None:
                    return
                for func in self.__funcs["setup_hook"]:
                    await func()
            if json["body"]["type"] == "ready":
                if self.__funcs.get("on_ready") is None:
                    return
                for func in self.__funcs["on_ready"]:
                    await func()
            elif json["body"]["type"] == "exception":
                if self.__funcs.get("on_error"):
                    eb = {
                        "type": json["body"]["errorType"],
                        "exc": json["body"]["exc"],
                        "exc_obj": json["body"]["exc_obj"],
                    }
                    for func in self.__funcs["on_error"]:
                        await func(error(**eb))
                else:
                    if json["body"]["errorType"] in self.apierrors:
                        raise MisskeyAPIError(json["body"]["exc"])
                    else:
                        raise ClientException(json["body"]["exc"])
