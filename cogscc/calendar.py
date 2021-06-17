from recordtype import recordtype
from bisect import bisect_left
from cogscc.funcs.dice import roll


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

    _weekDays = [
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
    _week2monthFest = [
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

    _monthFest2weeksPassed = [
        0,
        1,
        5,
        9,
        13,
        14,
        18,
        22,
        26,
        27,
        31,
        35,
        39,
        40,
        44,
        48,
    ]

    _monthFest2season = [0, 0, 1, 1, 1, 2, 2, 2, 3, 4, 4, 4, 5, 5, 5, 0]

    def __init__(self, day=0):
        self.day = day
        self.celene_calendar = MoonCalendar(91, 364 / 2)
        self.luna_calendar = MoonCalendar(28, 364 / 2)

    def __to_json__(self):
        return {"GHcalendar_day": self.day}

    @classmethod
    def __from_dict__(cls, d):
        return GHCalendar(d["GHcalendar_day"])

    def getYear(self):
        return int(self.day // 364)

    def getYearDay(self):
        return int(self.day % 364)

    def getYearWeek(self):
        return int(self.getYearDay() // 7)

    def _getWeekDay(self):
        return int(self.day % 7)

    def getWeekDay(self):
        return self._weekDays[self._getWeekDay()]

    def getMonthDay(self):
        return (
            7 * (self.getYearWeek() - self._monthFest2weeksPassed[self._getMonthFest()])
            + self._getWeekDay()
            + 1
        )

    def _getMonthFest(self):
        return self._week2monthFest[self.getYearWeek()]

    def getMonthFest(self):
        return self._monthFest[self._getMonthFest()]

    def _getSeason(self):
        return self._monthFest2season[self._getMonthFest()]

    def getSeason(self):
        return self._season[self._getSeason()]

    def getLunaPhase(self):
        return self.luna_calendar.getPhase(self.day)

    def getCelenePhase(self):
        return self.celene_calendar.getPhase(self.day)

    def getDate(self):
        return (
            f"**Date:**\n{self.getWeekDay()}, {self.getMonthDay()} {self.getMonthFest()} {self.getYear()}\n"
            f"Season: {self.getSeason()}\nLuna Phase: {self.getLunaPhase()}\n"
            f"Celene Phase: {self.getCelenePhase()}"
        )

    def addDays(self, days=1):
        self.day += days
        return f"{days} days have passed."


class GHWeather:

    MonthData = recordtype("MonthData", "T sky precipitation sunriseAndSunset")
    _monthData = {
        "Needfest": MonthData(
            [32.5, "1d10+2", "1d20"], [24, 50], 44, ["7:20", "17:48"]
        ),
        "Fireseek": MonthData([32, "1d10", "1d20"], [23, 50], 46, ["7:21", "17:01"]),
        "Readying": MonthData([34, "1d6+4", "1d10+4"], [25, 50], 40, ["6:55", "17:36"]),
        "Coldeven": MonthData([42, "1d8+4", "1d10+4"], [27, 54], 44, ["6:12", "18:09"]),
        "Growfest": MonthData([47, "1d9+5", "1d9+4"], [23, 54], 43, ["5:48", "18:24"]),
        "Planting": MonthData([52, "1d10+6", "1d8+4"], [20, 55], 42, ["5:24", "18:39"]),
        "Flocktime": MonthData(
            [63, "1d10+6", "1d10+6"], [20, 53], 42, ["4:45", "19:10"]
        ),
        "Wealsun": MonthData([71, "1d8+8", "1d6+6"], [20, 60], 36, ["4:32", "19:32"]),
        "Richfest": MonthData([74, "1d7+6", "1d6+6"], [21, 61], 34, ["4:38", "19:30"]),
        "Reaping": MonthData([77, "1d6+4", "1d6+6"], [22, 62], 33, ["4:45", "19:29"]),
        "Goodmonth": MonthData([75, "1d4+6", "1d6+6"], [25, 60], 33, ["5:13", "18:57"]),
        "Harvester": MonthData([68, "1d8+6", "1d8+6"], [33, 55], 33, ["5:42", "18:10"]),
        "Brewfest": MonthData(
            [62, "1d10+5", "1d10+5"], [34, 57], 34, ["5:57", "17:45"]
        ),
        "Patchwall": MonthData(
            [57, "1d10+5", "1d10+5"], [35, 60], 36, ["6:12", "17:21"]
        ),
        "Ready'reat": MonthData(
            [46, "1d10+6", "1d10+4"], [20, 50], 40, ["6:46", "16:45"]
        ),
        "Sunsebb": MonthData([33, "1d8+5", "1d20"], [25, 50], 43, ["7:19", "16:36"]),
    }
    TerrainData = recordtype(
        "TerrainData", "precipitation T windSpeed special forbidden"
    )
    _terrainData = {
        "Rough Terrain": TerrainData(
            0, 0, 5, [[80, 100], ["Windstorm", "Earthquake"]], []
        ),
        "Hill": TerrainData(0, [0], -5, [[80, 100], ["Windstorm", "Earthquake"]], []),
        "Forest": TerrainData(
            0, [-5], -5, [[80, 100], ["Quicksand", "Earthquake"]], []
        ),
        "Jungle": TerrainData(
            10,
            [5],
            -10,
            [
                [5, 60, 80, 100],
                ["Volcano", "Rain Forest Downpour", "Quicksand", "Earthquake"],
            ],
            [],
        ),
        "Swamp": TerrainData(
            5, [5], -5, {25: "Quicksand", 80: "Sun Shower", 100: "Earthquake"}, []
        ),
        "Marsh": TerrainData(
            5, [0], -5, {25: "Quicksand", 80: "Sun Shower", 100: "Earthquake"}, []
        ),
        "Dust": TerrainData(
            -25,
            [10, -10],
            0,
            {40: "Flash Flood", 70: "Dust Storm", 85: "Tornado", 100: "Earthquake"},
            ["Fog", "Gale", "Hurricane"],
        ),
        "Plains": TerrainData(
            0,
            [0],
            5,
            [[50, 100], ["Windstorm", "Earthquake"]],
            ["Monsoon", "Tropical Storm"],
        ),
        "Desert": TerrainData(
            -30,
            [10, -10],
            5,
            [
                [25, 50, 65, 85, 100],
                ["Flash Flood", "Sandstorm", "Oasis", "Mirage Oasis", "Earthquake"],
            ],
            [
                "Fog",
                "Mist",
                "Blizzard",
                "Monsoon",
                "Tropical Storm",
                "Gale",
                "Hurricane",
            ],
        ),
        "Mountain": TerrainData(
            0,
            [-3],
            5,
            [
                [20, 50, 75, 80, 100],
                [
                    "Wind Storm",
                    "Rock Avalanche",
                    "Snow Avalanche",
                    "Volcano",
                    "Earthquake",
                ],
            ],
            [],
        ),
        "Seacoast": TerrainData(
            5,
            [5, -5],
            5,
            [[80, 94, 100], ["Earthquake", "Tsunami", "Undersea Volcano"]],
            ["TODO duration of fog and mist doubled"],
        ),
        "Sea": TerrainData(
            15,
            [5, -10],
            10,
            [[20, 40, 100], ["Tsunami", "Undersea Volcano", "Undersea Earthquake"]],
            ["TODO duration of fog and mist doubled"],
        ),
    }
    _extremeT = [[1, 2, 4, 96, 98, 99, 100], range(-3, 4)]

    @staticmethod
    def _F2C(T):
        return int(10 * ((T - 32) * 5 / 9)) / 10

    def _correctForExtremeT(self, day):
        c = GHCalendar(day)
        k = bisect_left(self._extremeT[0], roll("1d100").total)
        m = self._extremeT[1][k]

        v = eval(self._monthData[c.getMonthFest()].T[1 + int(m < 0)].replace("1d", ""))
        return m*v


    def getTemperature(self, day, latitude, is_celsius=True):
        c = GHCalendar(day)
        T = self._monthData[c.getMonthFest()].T[0] + 2 * (
            40 - latitude
        )  # correct for latitude
        T += self._correctForExtremeT(day)

        T_max = T + roll(self._monthData[c.getMonthFest()].T[1]).total  # daily spread +
        T_min = T - roll(self._monthData[c.getMonthFest()].T[2]).total  # daily spread -
        return (self._F2C(T_min), self._F2C(T_max)) if is_celsius else (T_min, T_max)
