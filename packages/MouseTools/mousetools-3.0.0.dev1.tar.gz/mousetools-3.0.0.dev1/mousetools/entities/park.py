from mousetools.entities.base import Entity


class Park(Entity):
    """Class for Park Entities."""

    def __repr__(self) -> str:
        return f"Park(id='{self.id}')"
