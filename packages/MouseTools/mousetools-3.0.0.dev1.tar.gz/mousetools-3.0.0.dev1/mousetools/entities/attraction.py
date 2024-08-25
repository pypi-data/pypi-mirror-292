from mousetools.entities.base import Entity


class Attraction(Entity):
    """Class for Attraction Entities."""

    def __repr__(self) -> str:
        return f"Attraction(id='{self.id}')"
