from mousetools.entities.base import Entity


class Restaurant(Entity):
    """Class for Restaurant Entities."""

    def __repr__(self) -> str:
        return f"Restaurant(id='{self.id}')"
