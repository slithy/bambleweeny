import sys, os

rootpath = os.path.realpath(os.path.dirname(__file__) + "/..")
if rootpath not in sys.path:
    sys.path.append(rootpath)

from cogscc.weather import GHWeather
from cogscc.calendar import GHCalendar
from cogscc.location import GHLocation


def check_reports(c, w):
    assert len(w.reports) == w._n_reports
    for idx, i in enumerate(w.reports):
        assert i.day == idx + c.day


def test_generate_weather_days():
    c = GHCalendar(25)
    w = GHWeather()
    assert len(w.reports) == 0

    l = GHLocation("home", "hill", 30, 2500)
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


def test_correctTforPrecipitation():
    T, cont = GHWeather._correctTforPrecipitation([0, 5], [float("-inf"), 7])
    assert T == [0, 5]
    assert not cont
    T, cont = GHWeather._correctTforPrecipitation([0, 5], [float(-3), float("inf")])
    assert T == [0, 5]
    assert not cont
    T, cont = GHWeather._correctTforPrecipitation([0, 5], [1, 7])
    assert T == [1, 5]
    assert not cont
    T, cont = GHWeather._correctTforPrecipitation([0, 5], [1, 3])
    assert T == [1, 3]
    assert not cont
    T, cont = GHWeather._correctTforPrecipitation([0, 5], [-5, 3])
    assert T == [0, 3]
    assert not cont
    T, cont = GHWeather._correctTforPrecipitation([0, 5], [float("-inf"), -3])
    assert T == [0, 5]
    assert cont
    T, cont = GHWeather._correctTforPrecipitation([0, 5], [7, float("inf")])
    assert T == [0, 5]
    assert cont
    T, cont = GHWeather._correctTforPrecipitation([0, 5], [5, float("inf")])
    assert T == [5, 5]
    assert not cont
    T, cont = GHWeather._correctTforPrecipitation([0, 5], [float("-inf"), 0])
    assert T == [0, 0]
    assert not cont
