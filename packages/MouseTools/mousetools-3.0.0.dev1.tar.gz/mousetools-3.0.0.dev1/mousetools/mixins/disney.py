import logging
import requests
from mousetools.auth import auth_obj
from mousetools import WALT_DISNEY_WORLD_ENTITIES, DISNEYLAND_RESORT_ENTITIES
from mousetools.ids import DestinationIds
from mousetools.exceptions import EntityIDNotFound

logger = logging.getLogger(__name__)


class DisneyAPIMixin:
    _ancestor_destination_id = None
    # should be set in subclass
    id = ""

    def get_disney_data(self):
        """
        Finds the entity in the Disney data and stores it in the
        disney_data attribute. Also stores the ancestor destination id in
        the _ancenstor_destination_id attribute.

        Returns:
            (dict): The disney data.

        Raises:
            (EntityIDNotFound): If the entity is not found in the Disney data.
        """
        for i in WALT_DISNEY_WORLD_ENTITIES:
            if self.id == i["id"]:
                self._ancestor_destination_id = DestinationIds.WALT_DISNEY_WORLD
                logger.info("Entity %s found in Walt Disney World", self.id)
                return i

        for i in DISNEYLAND_RESORT_ENTITIES:
            if self.id == i["id"]:
                self._ancestor_destination_id = DestinationIds.DISNEYLAND_RESORT
                logger.info("Entity %s found in Disneyland Resort", self.id)
                return i

        raise EntityIDNotFound

    def get_extended_disney_data(self):
        """
        Gets the extended disney data for this entity from the Disney API.

        The extended data is the data returned by the simple details API endpoint.

        Returns:
            (dict): The extended disney data.

        Raises:
            (requests.exceptions.RequestException): If there is an error getting the data.
        """

        headers = auth_obj.get_headers()

        try:
            response = requests.get(self.details_simple_url(), headers=headers)

            response.raise_for_status()
            return response.json()

        except Exception as e:
            logger.debug("Error getting extended disney data: %s", e)
