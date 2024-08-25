from mousetools.entities.base import Entity


class Resort(Entity):
    """Class for Resort Entities."""

    def __repr__(self) -> str:
        return f"Resort(id='{self.id}')"
