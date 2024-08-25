import logging
import typing
from datetime import datetime
from zoneinfo import ZoneInfo
from mousetools.mixins.disney import DisneyAPIMixin
from mousetools.mixins.themeparksapi import ThemeParkAPIMixin
from mousetools.ids import DestinationIds
from mousetools.urls import ENTITY_DETAILS_SIMPLE_BASE_URL
from mousetools.exceptions import AncestorDestinationMissing


logger = logging.getLogger(__name__)


class Entity(DisneyAPIMixin, ThemeParkAPIMixin):
    def __init__(self, id: str):
        self.id: str = id
        self.disney_data: typing.Optional[dict] = None

    @property
    def name(self) -> typing.Optional[str]:
        """
        The name of the entity.

        Returns:
            (typing.Optional[str]): The name of the entity, or None if it was not found.
        """

        if self.disney_data is None:
            self.disney_data = self.get_disney_data()
        try:
            return self.disney_data["name"]
        except KeyError:
            logger.debug("No name found for %s", self.id)
            return None

    @property
    def entity_type(self) -> typing.Optional[str]:
        """
        The type of entity this is.

        Returns:
            (typing.Optional[str]): The type of entity this is, or None if it was not found.
        """

        if self.disney_data is None:
            self.disney_data = self.get_disney_data()
        try:
            return self.disney_data["entityType"]
        except KeyError:
            logger.debug("No entity type found for %s", self.id)
            return None

    @property
    def entity_type_name(self) -> typing.Optional[str]:
        """
        The name of the type of entity.

        Returns:
            (typing.Optional[str]): The name of the type of entity, or None if it was not found.
        """
        if self.disney_data is None:
            self.disney_data = self.get_disney_data()
        try:
            return self.disney_data["entityTypeName"]
        except KeyError:
            logger.debug("No entity type name found for %s", self.id)
            return None

    @property
    def url_friendly_id(self) -> typing.Optional[str]:
        """
        The url friendly id of the entity.

        Returns:
            (typing.Optional[str]): The url friendly id of the entity, or None if not found.
        """
        if self.disney_data is None:
            self.disney_data = self.get_disney_data()
        try:
            id = self.disney_data["urlFriendlyId"]
            # for some reason pirates in wdw has a -wdw and its wrong
            id = id.replace("-wdw", "").replace("-dlr", "")
            return id
        except KeyError:
            logger.debug("No url friendly id found for %s", self.id)
            return None

    @property
    def coordinates(self) -> typing.Optional[dict[str, float]]:
        """
        The coordinates of this entity

        Returns:
            (typing.Optional[dict[str, float]]): A dict with "lat" and "lng" keys containing the coordinates of this entity as floats, or None if no coordinates are found
        """
        if self.disney_data is None:
            self.disney_data = self.get_disney_data()
        try:
            return {
                "lat": float(self.disney_data["marker"]["lat"]),
                "lng": float(self.disney_data["marker"]["lng"]),
            }
        except KeyError:
            logger.debug("No coordinates found for %s", self.id)
            return None

    @property
    def ancestor_destination_id(self) -> typing.Optional[str]:
        """
        The id of the ancestor destination of this entity.

        Returns:
            (typing.Optional[str]): The id of the ancestor destination of this entity, or None if it was not found.
        """

        if self.disney_data is None:
            self.disney_data = self.get_disney_data()
        try:
            return self._ancestor_destination_id
        except KeyError:
            logger.debug("No ancestor destination id found for %s", self.id)
            return None

    @ancestor_destination_id.setter
    def ancestor_destination_id(self, value: typing.Optional[str]):
        """
        Set the ancestor destination id

        Required for ThemeParkAPIMixin

        Args:
            value (typing.Optional[str]): Str to set ancestor_destination_id to
        """
        self.ancestor_destination_id = value

    @property
    def ancestor_park_ids(self) -> typing.Optional[list[str]]:
        """
        The ids of parks that are ancestors of this entity.

        Returns:
            (typing.Optional[list[str]]): A list of park ids that are ancestors of this entity, or None if no such ids are found.
        """
        if self.disney_data is None:
            self.disney_data = self.get_disney_data()
        try:
            return [
                i
                for i in self.disney_data["parkIds"]
                if any(j in i for j in ["theme-park", "water-park"])
            ]
        except KeyError:
            logger.debug("No ancestor park ids found for %s", self.id)
            return None

    @property
    def ancestor_resort_ids(self) -> typing.Optional[list[str]]:
        """
        The ids of resorts that are ancestors of this entity.

        Returns:
            (typing.Optional[list[str]]): A list of resort ids that are ancestors of this entity, or None if no such ids are found.
        """

        if self.disney_data is None:
            self.disney_data = self.get_disney_data()
        try:
            return [i for i in self.disney_data["parkIds"] if "resort" in i]
        except KeyError:
            logger.debug("No ancestor resort ids found for %s", self.id)
            return None

    @property
    def ancestor_land_id(self) -> typing.Optional[str]:
        """
        The id of the land that is an ancestor of this entity.

        Returns:
            (typing.Optional[str]): The id of the land that is an ancestor of this entity, or None if no such id is found.
        """
        if self.disney_data is None:
            self.disney_data = self.get_disney_data()
        try:
            return self.disney_data["landId"]
        except KeyError:
            logger.debug("No ancestor land id found for %s", self.id)
            return None

    @property
    def ancestor_resort_area_ids(self) -> typing.Optional[list[str]]:
        """
        The ids of resort areas that are ancestors of this entity.

        Returns:
            (typing.Optional[list[str]]): A list of resort area ids that are ancestors of this entity, or None if no such ids are found.
        """
        if self.disney_data is None:
            self.disney_data = self.get_disney_data()
        try:
            return [i for i in self.disney_data["parkIds"] if "resort-area" in i]
        except KeyError:
            logger.debug("No ancestor resort area ids found for %s", self.id)
            return None

    @property
    def ancestor_entertainment_venue_ids(self) -> typing.Optional[list[str]]:
        """
        The ids of entertainment venues that are ancestors of this entity.

        Returns:
            (typing.Optional[list[str]]): A list of entertainment venue ids that are ancestors of this entity, or None if no such ids are found.
        """
        if self.disney_data is None:
            self.disney_data = self.get_disney_data()
        try:
            return [
                i for i in self.disney_data["parkIds"] if "Entertainment-Venue" in i
            ]
        except KeyError:
            logger.debug("No ancestor entertainment venue ids found for %s", self.id)
            return None

    @property
    def ancestor_restaurant_ids(self) -> typing.Optional[list[str]]:
        """
        The ids of restaurants that are ancestors of this entity.

        Returns:
            (typing.Optional[list[str]]): A list of restaurant ids that are ancestors of this entity, or None if no such ids are found.
        """
        if self.disney_data is None:
            self.disney_data = self.get_disney_data()
        try:
            return [i["id"] for i in self.disney_data["restaurants"]]
        except KeyError:
            logger.debug("No ancestor restaurant ids found for %s", self.id)
            return None

    @property
    def time_zone(self) -> ZoneInfo:
        """
        The time zone of the entity.

        Returns:
            (ZoneInfo): The time zone of the entity.
        """

        if self.ancestor_destination_id == DestinationIds.WALT_DISNEY_WORLD:
            return ZoneInfo("America/New_York")
        elif self.ancestor_destination_id == DestinationIds.DISNEYLAND_RESORT:
            return ZoneInfo("America/Los_Angeles")
        else:
            return ZoneInfo("UTC")

    def details_simple_url(self) -> str:
        """
        Gets the simple details url for this entity

        Returns:
            (str): The simple details url

        Raises:
            AncestorDestinationMissing: If the ancestor destination id is not
                either Walt Disney World or Disneyland Resort
        """
        if self.ancestor_destination_id == DestinationIds.WALT_DISNEY_WORLD:
            dest_url_friendly_id = "wdw"
        elif self.ancestor_destination_id == DestinationIds.DISNEYLAND_RESORT:
            dest_url_friendly_id = "dlr"
        else:
            raise AncestorDestinationMissing
        return f"{ENTITY_DETAILS_SIMPLE_BASE_URL}/{dest_url_friendly_id}/{self.url_friendly_id}/{datetime.now().strftime('%Y-%m-%d')}"

    def status(self) -> typing.Optional[str]:
        """
        The current status of the entity.

        Returns:
            (typing.Optional[str]): The current status of the entity, or None if no such data exists.
        """

        live_data = self.get_entity_live_tp()
        try:
            return live_data["liveData"][0]["status"]
        except (KeyError, IndexError):
            logger.debug("No status found for %s", self.id)
            return None

    def wait_time(self) -> typing.Optional[int]:
        """
        The current wait time for the entity.

        Returns:
            (typing.Optional[int]): The current wait time for the entity, or None if no such data exists.
        """
        live_data = self.get_entity_live_tp()
        try:
            return live_data["liveData"][0]["queue"]["STANDBY"]["waitTime"]
        except (KeyError, IndexError):
            logger.debug("No wait time found for %s", self.id)
            return None

    def last_updated(self) -> typing.Optional[datetime]:
        """
        The last time the entity's data was updated.

        Returns:
            (typing.Optional[datetime]): The last time the entity's data was updated, or None if no such data exists.
        """
        live_data = self.get_entity_live_tp()
        try:
            return datetime.strptime(
                live_data["liveData"][0]["lastUpdated"], "%Y-%m-%dT%H:%M:%SZ"
            ).replace(tzinfo=ZoneInfo("UTC"))
        except (KeyError, IndexError):
            logger.debug("No last updated found for %s", self.id)
            return None

    def today_operating_hours(self) -> typing.Optional[dict[str, dict[str, datetime]]]:
        """
        The operating hours for today for the entity.

        Returns:
            (typing.Optional[dict[str, dict[str, datetime]]]): A dictionary of the operating hours for today, or None if no such data exists.
        """

        live_data = self.get_entity_live_tp()
        temp = {}

        try:
            for i in live_data["liveData"][0]["operatingHours"]:
                temp[i["type"]] = {
                    "start_time": datetime.strptime(
                        i["startTime"], "%Y-%m-%dT%H:%M:%S%z"
                    ).replace(tzinfo=self.time_zone),
                    "end_time": datetime.strptime(
                        i["endTime"], "%Y-%m-%dT%H:%M:%S%z"
                    ).replace(tzinfo=self.time_zone),
                }
        except (KeyError, IndexError):
            logger.debug("No operating hours found for %s", self.id)
            return None

        return temp

    def today_showtimes(self) -> typing.Optional[list[datetime]]:
        """
        The showtimes for today for the entity.

        Returns:
            (typing.Optional[list[datetime]]): A list of the showtimes for today, or None if no such data exists.
        """
        live_data = self.get_entity_live_tp()
        temp = []

        try:
            for i in live_data["liveData"][0]["showtimes"]:
                temp.append(
                    datetime.strptime(i["startTime"], "%Y-%m-%dT%H:%M:%S%z").replace(
                        tzinfo=self.time_zone
                    )
                )
        except (KeyError, IndexError):
            logger.debug("No showtimes found for %s", self.id)
            return None

        return temp

    def __str__(self) -> str:
        return f"{self.entity_type}: {self.name} ({self.id})"

    def __repr__(self) -> str:
        return f"Entity(id='{self.id}')"

    def __eq__(self, other) -> bool:
        if isinstance(other, Entity):
            return self.id == other.id
        return False

    # TODO virtual queue
