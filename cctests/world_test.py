import sys, os

rootpath = os.path.realpath(os.path.dirname(__file__) + "/..")
if rootpath not in sys.path:
    sys.path.append(rootpath)

import json
from cogscc.game import ToJson
from cogscc.world.world import GHWorld
from cogscc.world.calendar import GHCalendar
from cogscc.world.weather import GHWeather, GHWeatherReport
from cogscc.world.location import GHLocation


def test_save_load():
    c = GHCalendar(25)
    w = GHWeather()
    l = GHLocation("new town", "plains", 40, 0)
    world = GHWorld(c, w, {l.name: l})
    d = json.dumps(world, cls=ToJson, indent=2, ensure_ascii=False)
    world_n = GHWorld.__from_dict__(json.loads(d))
    assert world == world_n


def test_locations():
    c = GHCalendar(25)
    w = GHWeather()
    l = GHLocation("new town", "plains", 40, 0)
    world = GHWorld(c, w, {"new town": l})
    assert world.get_current_location() == l
    l2 = GHLocation("graveyard", "hill", 30, 200)
    world.add_location(l2)
    assert world.get_current_location() != l2
    world.set_current_location("graveyard")
    assert world.get_current_location() == l2
    world.remove_location("new town")
    assert world.get_current_location() == l2
    world.remove_location("graveyard")
    l3 = GHLocation("home", "hill", 30, 200)
    world.add_location(l3)
    world.set_current_location("home")
    assert world.get_current_location() == l3
    assert len(world.locations) == 1


def test_fill_empty_world():
    w = GHWorld()
    w.calendar = GHCalendar(0)
    w.advance_days(0)
    l = GHLocation("graveyard", "hill", 30, 20000)
    w.add_location(l)
    w.advance_days(0)
    assert len(w.get_current_location().weather.reports) == GHWeather._n_reports


def test_get_locations():
    w = GHWorld()
    w.add_location(GHLocation("test", "hill", 40, 0))
    w.add_location(GHLocation("test2", "hill", 40, 0))
    w.reset_weather()
    assert len(w.locations) == 2
    for v in w.locations.values():
        assert len(v.weather.reports) == GHWeather._n_reports


#
# w = GHWorld()
# w.calendar = GHCalendar(364 / 2)
# w.advance_days(0)
# l = GHLocation("graveyard", "hill", 30, 100)
# w.add_location(l)
# w.advance_days(0)
# for i in w.get_precipitation_chain("light snowstorm"):
#     print(i)
