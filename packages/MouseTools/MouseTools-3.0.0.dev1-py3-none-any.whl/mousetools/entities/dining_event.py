from mousetools.entities.base import Entity


class DiningEvent(Entity):
    """Class for DiningEvent Entities."""

    def __repr__(self) -> str:
        return f"DiningEvent(id='{self.id}')"


class DinnerShow(Entity):
    """Class for DiningEvent Entities."""

    def __repr__(self) -> str:
        return f"DinnerShow(id='{self.id}')"
