from mousetools.entities.base import Entity


class Entertainment(Entity):
    """Class for Entertainment Entities."""

    def __repr__(self) -> str:
        return f"Entertainment(id='{self.id}')"
