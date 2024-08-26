from .note import Note

from pydantic import dataclasses

@dataclasses.dataclass()
class favorite:
    id: str
    createdAt: str
    note: Note
    noteId: str
