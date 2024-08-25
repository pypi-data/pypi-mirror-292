from mousetools.entities.base import Entity
from zoneinfo import ZoneInfo
from datetime import datetime


def test_attraction_entity():
    btm_entity = Entity("80010110;entityType=Attraction")

    assert btm_entity.id == "80010110;entityType=Attraction"
    assert btm_entity.entity_type == "Attraction"
    assert btm_entity.entity_type_name == "attractions"
    assert btm_entity.name == "Big Thunder Mountain Railroad"
    assert btm_entity.url_friendly_id == "big-thunder-mountain-railroad"
    assert btm_entity.coordinates == {"lat": 28.4199638504, "lng": -81.5846422864}
    assert btm_entity.ancestor_destination_id == "80007798;entityType=destination"
    assert btm_entity.ancestor_park_ids == ["80007944;entityType=theme-park"]
    assert btm_entity.ancestor_land_id == "80007922;entityType=land"
    assert btm_entity.ancestor_resort_ids == []
    assert btm_entity.ancestor_resort_area_ids == []
    assert btm_entity.ancestor_entertainment_venue_ids == []
    assert btm_entity.ancestor_restaurant_ids is None
    assert (
        btm_entity.details_simple_url()
        == f"https://disneyworld.disney.go.com/finder/api/v1/explorer-service/details-entity-simple/wdw/big-thunder-mountain-railroad/{datetime.now().strftime('%Y-%m-%d')}"
    )
    assert btm_entity.time_zone == ZoneInfo("America/New_York")
    status = btm_entity.status()
    assert isinstance(status, str) or status is None
    wait_time = btm_entity.wait_time()
    assert isinstance(wait_time, int) or wait_time is None

    assert (
        btm_entity.__str__()
        == "Attraction: Big Thunder Mountain Railroad (80010110;entityType=Attraction)"
    )
    assert btm_entity.__repr__() == "Entity(id='80010110;entityType=Attraction')"

    # TODO test expected keys
    assert isinstance(btm_entity.get_extended_disney_data(), dict)

    assert isinstance(btm_entity.last_updated(), datetime)

    assert "Operating" in btm_entity.today_operating_hours()

    assert btm_entity.today_showtimes() is None
