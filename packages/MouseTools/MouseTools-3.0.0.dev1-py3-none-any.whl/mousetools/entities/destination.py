from mousetools.entities.base import Entity


class Destination(Entity):
    """Class for Destination Entities."""

    def __repr__(self) -> str:
        return f"Destination(id='{self.id}')"
