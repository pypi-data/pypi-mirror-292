import inspect


class Gear:
    def __init__(self) -> None:
        self._funcs: dict = {}
    
    def listen(self, event=""):
        """A decorator that can listen for events in Discord.py-like notation.

        For a list of events, see [documentation](https://misspy.github.io/docs/events).

        ## Examples:
        ```python
        gear = misspy.Gear()
        
        @gear.listen()
        async def on_ready():
            print("ready!")
        ```

        ↓ Put the event name in the decorator argument.
        ```python
        gear = misspy.Gear()
        
        @gear.listen("ready")
        async def ready():
            print("ready!")
        ```

        Args:
            event (str): Name of the event to listen for.
        """

        def decorator(func):
            if not hasattr(self, "_funcs"):
                self._funcs = {}
            if event == "":
                ev = func.__name__ 
            else:
                ev = event
            func.__event_type = ev
            if isinstance(func, staticmethod):
                func = func.__func__
            if not inspect.iscoroutinefunction(func):
                raise TypeError("Functions that listen for events must be coroutines.")
            if self._funcs.get(ev) and isinstance(self._funcs.get(ev), list):
                ev: list = self._funcs.get(ev)
                ev.append(func)
            else:
                self._funcs[ev] = [func]
            return func
        return decorator