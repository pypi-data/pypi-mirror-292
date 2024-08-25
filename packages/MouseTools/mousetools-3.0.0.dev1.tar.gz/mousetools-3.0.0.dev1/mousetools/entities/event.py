from mousetools.entities.base import Entity


class Event(Entity):
    """Class for Event Entities."""

    def __repr__(self) -> str:
        return f"Event(id='{self.id}')"
