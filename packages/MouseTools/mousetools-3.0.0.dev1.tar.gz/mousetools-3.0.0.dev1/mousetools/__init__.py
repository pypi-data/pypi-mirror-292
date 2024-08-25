import logging
from mousetools.ids import ancestor_entities, DestinationIds

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

__version__ = "3.0.0-dev.1"  # will be set at runtime
logger.info(f"MouseTools version: {__version__}")

WALT_DISNEY_WORLD_ENTITIES = ancestor_entities(DestinationIds.WALT_DISNEY_WORLD)
logger.debug("%s Walt Disney World Entities", len(WALT_DISNEY_WORLD_ENTITIES))
DISNEYLAND_RESORT_ENTITIES = ancestor_entities(DestinationIds.DISNEYLAND_RESORT)
logger.debug("%s Disneyland Resort Entities", len(DISNEYLAND_RESORT_ENTITIES))
