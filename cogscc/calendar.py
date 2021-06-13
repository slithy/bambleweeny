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
