from mousetools import ids


def test_destination_ids():
    assert ids.DestinationIds.WALT_DISNEY_WORLD == "80007798;entityType=destination"
    assert ids.DestinationIds.DISNEYLAND_RESORT == "80008297;entityType=destination"


def test_wdw_park_ids():
    assert ids.WaltDisneyWorldParkIds.MAGIC_KINGDOM == "80007944;entityType=theme-park"
    assert ids.WaltDisneyWorldParkIds.EPCOT == "80007838;entityType=theme-park"
    assert (
        ids.WaltDisneyWorldParkIds.HOLLYWOOD_STUDIOS == "80007998;entityType=theme-park"
    )
    assert ids.WaltDisneyWorldParkIds.ANIMAL_KINGDOM == "80007823;entityType=theme-park"
    assert ids.WaltDisneyWorldParkIds.TYPHOON_LAGOON == "80007981;entityType=water-park"
    assert ids.WaltDisneyWorldParkIds.BLIZZARD_BEACH == "80007834;entityType=water-park"


def test_disneyland_resort_park_ids():
    assert ids.DisneylandResortParkIds.DISNEYLAND == "330339;entityType=theme-park"
    assert (
        ids.DisneylandResortParkIds.CALIFORNIA_ADVENTURE
        == "336894;entityType=theme-park"
    )


def test_theme_park_api_ids():
    assert (
        ids.ThemeParkAPIIds.WALT_DISNEY_WORLD == "e957da41-3552-4cf6-b636-5babc5cbc4e5"
    )
    assert ids.ThemeParkAPIIds.MAGIC_KINGDOM == "75ea578a-adc8-4116-a54d-dccb60765ef9"
    assert ids.ThemeParkAPIIds.EPCOT == "47f90d2c-e191-4239-a466-5892ef59a88b"
    assert (
        ids.ThemeParkAPIIds.HOLLYWOOD_STUDIOS == "288747d1-8b4f-4a64-867e-ea7c9b27bad8"
    )
    assert ids.ThemeParkAPIIds.ANIMAL_KINGDOM == "1c84a229-8862-4648-9c71-378ddd2c7693"
    assert ids.ThemeParkAPIIds.TYPHOON_LAGOON == "b070cbc5-feaa-4b87-a8c1-f94cca037a18"
    assert ids.ThemeParkAPIIds.BLIZZARD_BEACH == "ead53ea5-22e5-4095-9a83-8c29300d7c63"
    assert (
        ids.ThemeParkAPIIds.DISNEYLAND_RESORT == "bfc89fd6-314d-44b4-b89e-df1a89cf991e"
    )
    assert ids.ThemeParkAPIIds.DISNEYLAND == "7340550b-c14d-4def-80bb-acdb51d49a6"
    assert (
        ids.ThemeParkAPIIds.CALIFORNIA_ADVENTURE
        == "832fcd51-ea19-4e77-85c7-75d5843b127c"
    )
