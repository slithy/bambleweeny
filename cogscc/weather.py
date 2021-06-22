from recordtype import recordtype
from bisect import bisect_left
from cogscc.funcs.dice import roll
from cogscc.funcs import utils
from cogscc.calendar import GHCalendar
from cogscc.location import GHLocation
from cogscc.precipitation import GHPrecipitation
from cogscc.base_obj import BaseObj



class GHWeatherReport(BaseObj):
    def __init__(self, day, T, sky, precipitation, specialPrecipitation):
        self.day = day
        self.T = T
        self.sky = sky
        self.precipitation = [GHPrecipitation.__from_dict__(i) if isinstance(i, dict) else i for i in precipitation]
        self.specialPrecipitation = [GHPrecipitation.__from_dict__(i) if isinstance(i, dict) else i for i in
                                     specialPrecipitation]

    def __str__(self):
        out = f"**Weather Report** date: {GHCalendar(self.day).__str__()} T: {utils.F2C(self.T[0])} C (min)" \
              f" {utils.F2C(self.T[1])} C (max) " \
              f"Sky: {self.sky}\n"
        for i in self.precipitation:
            out += str(i)
        for i in self.specialPrecipitation:
            out += str(i)
        return out

    def perceived_T(self):
        return [
            self._correctForWindChill(self.T[0]),
            self._correctForWindChill(self.T[1]),
        ]

    def _correctForWindChill(self, T):
        i_wind = int(abs(self.windSpeed) / 5)
        if i_wind > len(self._windChillData):
            i_wind = -1
        j_T = int((T + 20) / 5)
        if j_T < 0:
            j_T = 0
        if j_T >= len(self._windChillData[0]):
            return T

        delta = self._windChillData[i_wind][j_T] - self._windChillData[0][j_T]

        return T + delta

    # base Temperature -20 -15 -10 -5 0 5 10 15 20 25 30 35
    _windChillData = [
        [-20, -15, -10, -5, 0, 5, 10, 15, 20, 25, 30, 35],  # 0 mph
        [-28, -22, -15, -11, -6, 1, 7, 12, 16, 21, 27, 33],  # 5 mph
        [-43, -37, -31, -27, -22, -15, -9, -2, 2, 9, 16, 21],  # 10 mph
        [-58, -51, -45, -40, -33, -25, -18, -11, -6, 1, 11, 16],  # 15 mph
        [-64, -58, -52, -46, -40, -32, -24, -17, -9, -4, 3, 12],  # 20 mph
        [-72, -65, -58, -52, -45, -37, -29, -22, -15, -7, 0, 7],  # 25 mph
        [-78, -70, -63, -56, -49, -41, -33, -26, -18, -11, -2, 5],  # 30 mph
        [-82, -75, -67, -60, -52, -43, -35, -27, -20, -13, -4, 3],  # 35 mph
        [-83, -76, -69, -62, -54, 45, -36, -29, -22, -13, -4, 1],  # 40 mph
        [-84, -77, -70, -63, -55, 46, -38, -31, -24, -15, -4, 1],  # 45 mph
        [-85, -78, -71, -64, -56, 47, -38, -31, -24, -17, -7, 0],  # 50 mph
        [-86, -79, -72, -65, -57, -48, -39, -33, -25, -19, -8, -1],  # 55 mph
        [-87, -80, -73, -66, -58, -49, -40, -34, -27, -21, -10, -3],  # 60 mph
    ]




class GHWeather(BaseObj):
    _n_reports = 14

    def __init__(
        self,
        reports=[],
        ongoingExtremeT=[],
        ongoingPrecipitation=[],
        ongoingSpecialPrecipitation=[],
    ):
        self.reports = [
            GHWeatherReport.__from_dict__(i) if isinstance(i, dict) else i
            for i in reports
        ]
        self.ongoingExtremeT = ongoingExtremeT  # [endDay, modifier] or None
        self.ongoingPrecipitation = [GHPrecipitation.__from_dict__(i) if isinstance(i, dict) else i for i in ongoingPrecipitation]
        self.ongoingSpecialPrecipitation = [GHPrecipitation.__from_dict__(i) if isinstance(i, dict) else i for i in
                                            ongoingSpecialPrecipitation]

    def generate_weather(self, day, location, is_reset=False):
        self.reports = [i for i in self.reports if i.day >= day]
        while len(self.reports) < self._n_reports:
            self.reports.append(self.generate_day(day + len(self.reports), location))

    def generate_day(self, day, location):
        T = self.get_temperature(day, location, False)
        sky = self.get_sky_conditions(day)
        precipitation, specialPrecipitation, T = self.getPrecipitation(
            day, location.terrain, T
        )
        return GHWeatherReport(day, T, sky, precipitation, specialPrecipitation)

    def update_ongoingExtremeT(self, day):
        self.ongoingExtremeT = [i for i in self.ongoingExtremeT if i[0] >= day]
        if len(self.ongoingExtremeT) != 0:
            return

        c = GHCalendar(day)

        k = bisect_left(self._extremeTdata.modifier[0], roll("1d100").total)
        multi = self._extremeTdata.modifier[1][k]
        modifier = (
            eval(
                utils.smart_find(self._monthData, c.getMonthFest())
                .T[1 + int(multi < 0)]
                .replace("1d", "")
            )
            * multi
        )
        if modifier == 0:
            return

        k = bisect_left(self._extremeTdata.duration[0], roll("1d20").total)
        duration = self._extremeTdata.duration[1][k]
        self.ongoingExtremeT.append([day + duration, modifier])

    def get_temperature(self, day, location, is_celsius=False):
        c = GHCalendar(day)
        monthData = utils.smart_find(self._monthData, c.getMonthFest())
        baseT = monthData.T[0]
        # correct for latitude
        T = baseT + 2 * (40 - location.latitude)
        # correct for extreme effects
        self.update_ongoingExtremeT(day)
        if len(self.ongoingExtremeT) != 0:
            T += self.ongoingExtremeT[0][1]

        # terrain
        terrainData = utils.smart_find(GHLocation._terrainData, location.terrain)
        terrainTmod = terrainData.T(location.altitude)

        # daily spread -
        T_min = T + roll(monthData.T[1]).total + terrainTmod[0]
        # daily spread +
        T_max = T + roll(monthData.T[2]).total + terrainTmod[1]

        return [utils.F2C(T_min), utils.F2C(T_max)] if is_celsius else [T_min, T_max]

    def get_sky_conditions(self, day):
        c = GHCalendar(day)
        monthData = utils.smart_find(self._monthData, c.getMonthFest())
        k = bisect_left(monthData.sky, roll("1d100").total)
        return ["clear", "partly cloudy", "cloudy"][k]



    def update_ongoingSpecialPrecipitation(self, day):
        self.ongoingSpecialPrecipitation = [
            i for i in self.ongoingSpecialPrecipitation if i[0] >= day
        ]

    def update_ongoingPrecipitation(self, day, terrain, T):
        self.ongoingPrecipitation = [
            i for i in self.ongoingPrecipitation if i.end_time >= day
        ]
        if len(self.ongoingPrecipitation) != 0:
            return

        c = GHCalendar(day)
        monthData = utils.smart_find(self._monthData, c.getMonthFest())
        terrainData = utils.smart_find(GHLocation._terrainData, terrain)

        if roll("1d100").total <= monthData.precipitation + terrainData.precipitation:
            self.ongoingPrecipitation.extend(GHPrecipitation.get_precipitation(day, T, terrain))




    def getPrecipitation(self, day, terrain, T):
        self.update_ongoingSpecialPrecipitation(day)
        self.update_ongoingPrecipitation(day, terrain, T)

        precipitation = [
            i
            for idx, i in enumerate(self.ongoingPrecipitation)
            if idx == 0 or self.ongoingPrecipitation[idx - 1].end_time < day + 1
        ]
        specialPrecipitation = [
            i
            for idx, i in enumerate(self.ongoingSpecialPrecipitation)
            if idx == 0 or self.ongoingPrecipitation[idx - 1][0] < day + 1
        ]

        if len(precipitation) == 0:
            precipitation = [GHPrecipitation("no precipitation", day, terrain)]

        for i in precipitation:
            T = i.correct_T(T)

        return precipitation, specialPrecipitation, T

    """Data Tables"""
    MonthData = recordtype("MonthData", "T sky precipitation sunriseAndSunset")
    _monthData = {
        "needfest": MonthData(
            [32.5, "-1d20", "1d10+2"], [24, 50, 100], 44, ["7:20", "17:48"]
        ),
        "fireseek": MonthData([32, "-1d20", "1d10"], [23, 50], 46, ["7:21", "17:01"]),
        "readying": MonthData(
            [34, "-1d10-4", "1d6+4"], [25, 50], 40, ["6:55", "17:36"]
        ),
        "coldeven": MonthData(
            [42, "-1d10-4", "1d8+4"], [27, 54], 44, ["6:12", "18:09"]
        ),
        "growfest": MonthData([47, "-1d9-4", "1d9+5"], [23, 54], 43, ["5:48", "18:24"]),
        "planting": MonthData(
            [52, "-1d8-4", "1d10+6"], [20, 55], 42, ["5:24", "18:39"]
        ),
        "flocktime": MonthData(
            [63, "-1d10-6", "1d10+6"], [20, 53], 42, ["4:45", "19:10"]
        ),
        "wealsun": MonthData([71, "-1d6-6", "1d8+8"], [20, 60], 36, ["4:32", "19:32"]),
        "richfest": MonthData([74, "-1d6-6", "1d7+6"], [21, 61], 34, ["4:38", "19:30"]),
        "reaping": MonthData([77, "-1d6-6", "1d6+4"], [22, 62], 33, ["4:45", "19:29"]),
        "goodmonth": MonthData(
            [75, "-1d6-6", "1d4+6"], [25, 60], 33, ["5:13", "18:57"]
        ),
        "harvester": MonthData(
            [68, "-1d8-6", "1d8+6"], [33, 55], 33, ["5:42", "18:10"]
        ),
        "brewfest": MonthData(
            [62, "-1d10-5", "1d10+5"], [34, 57], 34, ["5:57", "17:45"]
        ),
        "patchwall": MonthData(
            [57, "-1d10-5", "1d10+5"], [35, 60], 36, ["6:12", "17:21"]
        ),
        "ready'reat": MonthData(
            [46, "-1d10-4", "1d10+6"], [20, 50], 40, ["6:46", "16:45"]
        ),
        "sunsebb": MonthData([33, "-1d20", "1d8+5"], [25, 50], 43, ["7:19", "16:36"]),
    }

    ExtremeTData = recordtype("ExtremeTData", "duration modifier")
    _extremeTdata = ExtremeTData(
        [[1, 3, 10, 14, 17, 19, 20], range(1, 8)],
        [[1, 2, 4, 96, 98, 99, 100], range(-3, 4)],
    )
