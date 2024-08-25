from mousetools import entities


def test_attraction():
    assert entities.Attraction(1).__repr__() == "Attraction(id='1')"


def test_destination():
    assert entities.Destination(1).__repr__() == "Destination(id='1')"


def test_park():
    assert entities.Park(1).__repr__() == "Park(id='1')"


def test_event():
    assert entities.Event(1).__repr__() == "Event(id='1')"


def test_restaurant():
    assert entities.Restaurant(1).__repr__() == "Restaurant(id='1')"


def test_resort():
    assert entities.Resort(1).__repr__() == "Resort(id='1')"


def test_entertainment():
    assert entities.Entertainment(1).__repr__() == "Entertainment(id='1')"


def test_entertainment_venue():
    assert entities.EntertainmentVenue(1).__repr__() == "EntertainmentVenue(id='1')"


def test_merchandise_facility():
    assert entities.MerchandiseFacility(1).__repr__() == "MerchandiseFacility(id='1')"


def test_dining_event():
    assert entities.DiningEvent(1).__repr__() == "DiningEvent(id='1')"


def test_dinner_show():
    assert entities.DinnerShow(1).__repr__() == "DinnerShow(id='1')"
