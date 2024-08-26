import inspect


class Cog:
    @classmethod
    def listener(cls, event=""):
        """A decorator that can listen for events in Discord.py-like notation.

        Examples:
        ```python
        @misspy.Cog.listen("ready")
        async def ready():
            print("ready!")
        ```

        Args:
            event (str): Name of the event to listen for.
        """
        if event == "":
            raise TypeError("Error in Cog.listener: event name is Missing.")

        def decorator(func):
            if isinstance(func, staticmethod):
                func = func.__func__
            if not inspect.iscoroutinefunction(func):
                raise TypeError("Functions that listen for events must be coroutines.")
            func._event = event
            return classmethod(func)

        return decorator


