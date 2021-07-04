import sys, os

rootpath = os.path.realpath(os.path.dirname(__file__) + "/..")
if rootpath not in sys.path:
    sys.path.append(rootpath)

from cogscc.world.weather import GHWeather
from cogscc.world.calendar import GHCalendar
from cogscc.world.location import GHLocation


def check_reports(c, w):
    assert len(w.reports) == w._n_reports
    for idx, i in enumerate(w.reports):
        assert i.day == idx + c.day


def test_generate_weather_days():
    c = GHCalendar(364 / 2)
    w = GHWeather()
    assert len(w.reports) == 0

    l = GHLocation("home", "hill", 0, 0)
    w.generate_weather(c.day, l)
    check_reports(c, w)

    c.advance(1)
    w.generate_weather(c.day, l)
    check_reports(c, w)

    c.advance(w._n_reports - 1)
    w.generate_weather(c.day, l)
    check_reports(c, w)

    c.advance(w._n_reports)
    w.generate_weather(c.day, l)
    check_reports(c, w)

    c.advance(w._n_reports + 1)
    w.generate_weather(c.day, l)
    check_reports(c, w)
