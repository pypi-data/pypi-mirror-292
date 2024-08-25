import typing
import logging
import requests
from mousetools.ids import DestinationIds, ThemeParkAPIIds
from mousetools.urls import THEMEPARK_BASE_URL
from mousetools.exceptions import AncestorDestinationMissing, EntityIDNotFound

logger = logging.getLogger(__name__)


class ThemeParkAPIMixin:
    _tp_entity_id = None
    # Should be set in subclass
    id = ""
    ancestor_destination_id: typing.Optional[str] = None

    @staticmethod
    def _send_tp_request(url: str) -> dict:
        """
        Send a GET request to ThemeParks.Wiki

        Args:
            url (str): The url to send the request to

        Returns:
            (dict): The response, parsed as JSON

        Raises:
            (requests.exceptions.RequestException): If the request fails
        """
        logger.debug("Sending request to %s", url)
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    @property
    def tp_entity_id(self) -> str:
        """
        The id of this entity on the ThemeParks.Wiki API.

        Returns:
            (str): The id of this entity on the ThemeParks.Wiki API

        Raises:
            (AncestorDestinationMissing): If the ancestor destination id is not
                either Walt Disney World or Disneyland Resort
            (EntityIDNotFound): If no ThemeParks.Wiki API id is found for this entity
        """

        if self._tp_entity_id is not None:
            return self._tp_entity_id

        if self.ancestor_destination_id == DestinationIds.WALT_DISNEY_WORLD:
            tp_destination_id = ThemeParkAPIIds.WALT_DISNEY_WORLD
        elif self.ancestor_destination_id == DestinationIds.DISNEYLAND_RESORT:
            tp_destination_id = ThemeParkAPIIds.DISNEYLAND_RESORT
        else:
            raise AncestorDestinationMissing

        request_url = f"{THEMEPARK_BASE_URL}/entity/{tp_destination_id}/children"
        children = self._send_tp_request(request_url)["children"]

        for i in children:
            if i["externalId"] == self.id:
                self._tp_entity_id = i["id"]
                return i["id"]

        raise EntityIDNotFound

    def get_entity_tp(self) -> dict:
        """
        Get an entity details from the ThemeParks.Wiki API.

        Returns:
            (dict): The response, parsed as JSON
        """
        request_url = f"{THEMEPARK_BASE_URL}/entity/{self.tp_entity_id}"
        return self._send_tp_request(request_url)

    def get_entity_children_tp(self) -> dict:
        """
        Get the children entities of an entity from the ThemeParks.Wiki API.

        Returns:
            (dict): The response, parsed as JSON
        """
        request_url = f"{THEMEPARK_BASE_URL}/entity/{self.tp_entity_id}/children"
        return self._send_tp_request(request_url)

    def get_entity_live_tp(self) -> dict:
        """
        Get the live data for an entity from the ThemeParks.Wiki API.

        Returns:
            (dict): The response, parsed as JSON
        """
        request_url = f"{THEMEPARK_BASE_URL}/entity/{self.tp_entity_id}/live"
        return self._send_tp_request(request_url)

    def get_entity_schedule_tp(
        self,
        year: typing.Optional[typing.Union[int, str]] = None,
        month: typing.Optional[typing.Union[int, str]] = None,
    ) -> dict:
        """
        Get the schedule for an entity from the ThemeParks.Wiki API.

        Args:
            year (Optional[Union[int, str]], optional): The year for which to get the schedule. Defaults to None.
            month (Optional[Union[int, str]], optional): The month for which to get the schedule. Defaults to None.

        Returns:
            (dict): The response, parsed as JSON
        """
        request_url = f"{THEMEPARK_BASE_URL}/entity/{self.tp_entity_id}/schedule"
        if year is not None and month is not None:
            request_url = f"{request_url}/{year}/{month}"
        else:
            raise UserWarning(
                "Missing year or month. Both must be passed to be used in request."
            )
        return self._send_tp_request(request_url)
