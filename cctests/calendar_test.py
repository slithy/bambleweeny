import sys, os

sys.path.append(os.path.realpath(os.path.dirname(__file__) + "/.."))

from cogscc.calendar import GHCalendar, MoonCalendar


def test_getYear():
    c = GHCalendar(370)
    assert c.getYear() == 1
    c = GHCalendar(213)
    assert c.getYear() == 0


def test_getYearDay():
    c = GHCalendar(364 + 3)
    assert c.getYearDay() == 3


def test_getYearWeek():
    c = GHCalendar(364 + 3 + 7 * 20)
    assert c.getYearWeek() == 20
    c = GHCalendar(6 + 7 * 54)
    assert c.getYearWeek() == 2


def test_getWeekDay_name():
    c = GHCalendar(364 + 3)
    assert c.getWeekDay_name() == "Godsday"
    c = GHCalendar(1)
    assert c.getWeekDay_name() == "Sunday"


def test_getMonthFest_name():
    c = GHCalendar(3)
    assert c.getMonthFest_name() == "Needfest"
    c = GHCalendar(7 + 28 * 2 - 1)
    assert c.getMonthFest_name() == "Readying"
    c = GHCalendar(7 + 28 * 2)
    assert c.getMonthFest_name() == "Coldeven"
    c = GHCalendar(364 + 3)
    assert c.getMonthFest_name() == "Needfest"
    c = GHCalendar(364 - 1)
    assert c.getMonthFest_name() == "Sunsebb"


def test_getSeason_name():
    c = GHCalendar(3)
    assert c.getSeason_name() == "Winter"
    c = GHCalendar(364 - 2)
    assert c.getSeason_name() == "Winter"
    c = GHCalendar(364 + 3)
    assert c.getSeason_name() == "Winter"
    c = GHCalendar(28 * 6 + 7 * 2 + 2)
    assert c.getSeason_name() == "Mid Summer"
    c = GHCalendar(28 * 9 + 7 * 3 + 2)
    assert c.getSeason_name() == "Autumn"
    c = GHCalendar(28 * 9 + 7 * 3 - 1)
    assert c.getSeason_name() == "High Summer"
    c = GHCalendar(28 * 9 + 7 * 3)
    assert c.getSeason_name() == "Autumn"


def count_freq_over_period(p, s):
    mc = MoonCalendar(p, s)
    out = {}
    for i in range(p):
        v = mc.getMoonPhase_name(i)
        if v in out:
            out[v] += 1
        else:
            out[v] = 1
    return out


def test_getMoonPhase_name():
    f = count_freq_over_period(28, 0)
    l = len(set([i for i in f.values()]))
    assert l >= 1
    assert l <= 2
    f = count_freq_over_period(91, 0)
    l = len(set([i for i in f.values()]))
    assert l >= 1
    assert l <= 2
    f = count_freq_over_period(16, 0)
    l = len(set([i for i in f.values()]))
    assert l == 1
