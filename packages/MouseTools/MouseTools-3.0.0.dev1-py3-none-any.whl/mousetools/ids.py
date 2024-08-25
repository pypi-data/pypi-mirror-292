from datetime import datetime
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
from mousetools.auth import auth_obj
from mousetools.urls import ANCESTOR_ENTITIES_BASE_URL
import requests
import logging

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class DestinationIds:
    WALT_DISNEY_WORLD: str = "80007798;entityType=destination"
    """The destination id for Walt Disney World."""
    DISNEYLAND_RESORT: str = "80008297;entityType=destination"
    """The destination id for Disneyland Resort."""


@dataclass(frozen=True)
class WaltDisneyWorldParkIds:
    MAGIC_KINGDOM: str = "80007944;entityType=theme-park"
    """The Park id for Magic Kingdom."""
    EPCOT: str = "80007838;entityType=theme-park"
    """The Park id for Epcot."""
    HOLLYWOOD_STUDIOS: str = "80007998;entityType=theme-park"
    """The Park id for Hollywood Studios."""
    ANIMAL_KINGDOM: str = "80007823;entityType=theme-park"
    """The Park id for Animal Kingdom."""
    TYPHOON_LAGOON: str = "80007981;entityType=water-park"
    """The Park id for Typhoon Lagoon."""
    BLIZZARD_BEACH: str = "80007834;entityType=water-park"
    """The Park id for Blizzard Beach."""


@dataclass(frozen=True)
class DisneylandResortParkIds:
    DISNEYLAND: str = "330339;entityType=theme-park"
    """The Park id for Disneyland."""
    CALIFORNIA_ADVENTURE: str = "336894;entityType=theme-park"
    """The Park id for California Adventure."""


@dataclass(frozen=True)
class ThemeParkAPIIds:
    WALT_DISNEY_WORLD: str = "e957da41-3552-4cf6-b636-5babc5cbc4e5"
    """The ThemeParks.Wiki id for Walt Disney World."""
    MAGIC_KINGDOM: str = "75ea578a-adc8-4116-a54d-dccb60765ef9"
    """The ThemeParks.Wiki id for Magic Kingdom."""
    EPCOT: str = "47f90d2c-e191-4239-a466-5892ef59a88b"
    """The ThemeParks.Wiki id for Epcot."""
    HOLLYWOOD_STUDIOS: str = "288747d1-8b4f-4a64-867e-ea7c9b27bad8"
    """The ThemeParks.Wiki id for Hollywood Studios."""
    ANIMAL_KINGDOM: str = "1c84a229-8862-4648-9c71-378ddd2c7693"
    """The ThemeParks.Wiki id for Animal Kingdom."""
    TYPHOON_LAGOON: str = "b070cbc5-feaa-4b87-a8c1-f94cca037a18"
    """The ThemeParks.Wiki id for Typhoon Lagoon."""
    BLIZZARD_BEACH: str = "ead53ea5-22e5-4095-9a83-8c29300d7c63"
    """The ThemeParks.Wiki id for Blizzard Beach."""

    DISNEYLAND_RESORT: str = "bfc89fd6-314d-44b4-b89e-df1a89cf991e"
    """The ThemeParks.Wiki id for Disneyland Resort."""
    DISNEYLAND: str = "7340550b-c14d-4def-80bb-acdb51d49a6"
    """The ThemeParks.Wiki id for Disneyland."""
    CALIFORNIA_ADVENTURE: str = "832fcd51-ea19-4e77-85c7-75d5843b127c"
    """The ThemeParks.Wiki id for California Adventure."""


def ancestor_entities(dest_id: str):
    if dest_id == DestinationIds.WALT_DISNEY_WORLD:
        destination = "wdw"
    elif dest_id == DestinationIds.DISNEYLAND_RESORT:
        destination = "dlr"

    results = []

    today_str = datetime.now().strftime("%Y-%m-%d")
    base_url = f"{ANCESTOR_ENTITIES_BASE_URL}/{destination}/{dest_id}/{today_str}"
    entity_names = ["/entertainment", "/dining", "/shops", "/resorts"]
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(requests.get, f"{base_url}{i}", headers=auth_obj.get_headers(), timeout=300) for i in entity_names]
        for future in as_completed(futures):
            try:
                response = future.result()
                response.raise_for_status()
                results += response.json()["results"]
            except Exception as e:
                logger.warning("Error getting ancestor entities: %s", e)

    return results
