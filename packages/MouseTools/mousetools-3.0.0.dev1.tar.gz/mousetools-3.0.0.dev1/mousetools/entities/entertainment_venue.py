from mousetools.entities.base import Entity


class EntertainmentVenue(Entity):
    """Class for EntertainmentVenue Entities."""

    def __repr__(self) -> str:
        return f"EntertainmentVenue(id='{self.id}')"
