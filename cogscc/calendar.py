class MoonCalendar:

    _phases = [
        "Full Moon :full_moon:",
        "Waning Gibbous :waning_gibbous_moon:",
        "Last Quarter :last_quarter_moon:",
        "Waning Crescent :waning_crescent_moon:",
        "New Moon :new_moon:",
        "Waxing Crescent :waxing_crescent_moon:",
        "First Quarter :first_quarter_moon:",
        "Waxing Gibbous :waxing_gibbous_moon:",
    ]

    def __init__(self, period, midFullMoonDay):
        self.period = period
        self.startFullMoonDay = midFullMoonDay - self.period / 16

    def _getPhase(self, day):
        day -= self.startFullMoonDay
        return (day % self.period) / (self.period / 8)

    def getPhase(self, day):
        return self._phases[int(self._getPhase(day))]


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
        self.celene_calendar = MoonCalendar(91, 364 / 2)
        self.luna_calendar = MoonCalendar(28, 364 / 2)

    def __to_json__(self):
        return {"GHcalendar_days": self.days}

    @classmethod
    def __from_dict__(cls, d):
        return GHCalendar(d["GHcalendar_days"])

    def getYear(self):
        return self.day // 364

    def getYearDay(self):
        return self.day % 364

    def getYearWeek(self):
        return self.getYearDay() // 7

    def _getWeekDay(self):
        return self.day % 7

    def getWeekDay(self):
        return self._week_days[self._getWeekDay()]

    def _getMonthFest(self):
        return self._week2monthfest[self.getYearWeek()]

    def getMonthFest(self):
        return self._monthFest[self._getMonthFest()]

    def _getSeason(self):
        return self._monthfest2season[self._getMonthFest()]

    def getSeason(self):
        return self._season[self._getSeason()]

    def getLunaPhase(self):
        return self.luna_calendar.getPhase(self.day)

    def getCelenePhase(self):
        return self.celene_calendar.getPhase(self.day)

    def getDate(self):
        return (
            f"**Date:**\nYear: {self.getYear()}\nYear Week: {self.getYearWeek()}\nWeek Day: {self.getWeekDay()}\n"
            f"Month (or Fest): {self.getMonthFest()}\nSeason: {self.getSeason()}\nLuna Phase: {self.getLunaPhase()}\n"
            f"Celene Phase: {self.getCelenePhase()}"
        )
