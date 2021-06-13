import math


class MoonCalendar:

    _phases = [
        "Full Moon :full_moon:",
        "Last Quarter :last_quarter_moon:",
        "New Moon :new_moon:",
        "First Quarter :first_quarter_moon:",
    ]
    _transition_phases = [
        "Waning Gibbous :waning_gibbous_moon:",
        "Waning Crescent :waning_crescent_moon:",
        "Waxing Crescent :waxing_crescent_moon:",
        "Waxing Gibbous :waxing_gibbous_moon:",
    ]

    def __init__(self, period, fullMoonDay):
        self.period = period
        self.fullMoonDay = fullMoonDay

    def getMoonPhase(self, day):
        day -= self.fullMoonDay
        return (day % self.period) / (self.period / 4)

    def getMoonPhase_name(self, day):
        mp = self.getMoonPhase(day)
        fmp = int(mp)
        cmp = math.ceil(mp) % 4
        if fmp == cmp:
            return self._phases[fmp]
        else:
            return f"{self._transition_phases[fmp]} ({self._phases[fmp]} -> {self._phases[cmp]})"


class GHCalendar:

    _week_days = [
        "Starday",
        "Sunday",
        "Moonday",
        "Godsday",
        "Waterday",
        "Earthday",
        "Freeday",
    ]
    _monthFest = [
        "Needfest",
        "Fireseek",
        "Readying",
        "Coldeven",
        "Growfest",
        "Planting",
        "Flocktime",
        "Wealsun",
        "Richfest",
        "Reaping",
        "Goodmonth",
        "Harvester",
        "Brewfest",
        "Patchwall",
        "Ready'reat",
        "Sunsebb",
    ]
    _season = ["Winter", "Spring", "Low Summer", "Mid Summer", "High Summer", "Autumn"]
    _week2monthfest = [
        0,
        *([1] * 4),
        *([2] * 4),
        *([3] * 4),
        4,
        *([5] * 4),
        *([6] * 4),
        *([7] * 4),
        8,
        *([9] * 4),
        *([10] * 4),
        *([11] * 4),
        12,
        *([13] * 4),
        *([14] * 4),
        *([15] * 4),
    ]
    _monthfest2season = [0, 0, 1, 1, 1, 2, 2, 2, 3, 4, 4, 4, 5, 5, 5, 0]

    def __init__(self, day=0):
        self.day = day
        self.CeleneCalendar = MoonCalendar(91, 3)
        self.LunaCalendar = MoonCalendar(28, 28 / 2)

    def getYear(self):
        return self.day // 364

    def getYearDay(self):
        return self.day % 364

    def getWeekDay(self):
        return self.day % 7

    def getYearWeek(self):
        return self.getYearDay() // 7

    def getMonthFest(self):
        return self._week2monthfest[self.getYearWeek()]

    def getSeason(self):
        return self._monthfest2season[self.getMonthFest()]

    def getWeekDay_name(self):
        return self._week_days[self.getWeekDay()]

    def getMonthFest_name(self):
        return self._monthFest[self.getMonthFest()]

    def getSeason_name(self):
        return self._season[self.getSeason()]
