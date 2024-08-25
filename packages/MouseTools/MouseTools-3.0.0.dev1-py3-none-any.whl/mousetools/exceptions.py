class MouseToolsException(Exception):
    """Base class for all MouseTools exceptions."""


class EntityIDNotFound(MouseToolsException):
    """Raised when an enity id could not be found."""

    # TODO add id to message
    def __init__(self, message="Entity ID not found."):
        super().__init__(message)


class AncestorDestinationMissing(MouseToolsException):
    """Raised for entities missing ancestor destination."""

    def __init__(self, message="Entity missing ancestor destination id."):
        super().__init__(message)
