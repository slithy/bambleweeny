from recordtype import recordtype
from bisect import bisect_left
from cogscc.funcs.dice import roll
from cogscc.funcs import utils
from cogscc.calendar import GHCalendar
from cogscc.location import GHLocation
from cogscc.base_obj import BaseObj


class GHWeatherReport(BaseObj):
    def __init__(self, day, T, sky, precipitation, specialPrecipitation):
        self.day = day
        self.T = T
        self.sky = sky
        self.precipitation = precipitation
        self.specialPrecipitation = specialPrecipitation

    def __str__(self):
        return self.__to_json__().__str__()

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

    PrecipitationData = recordtype(
        "PrecipitationData",
        [
            ("movementSpeed", ["normal", "normal", "normal"]),  # foot, horse, cart
            ("normalVisionRange", "normal"),
            ("ultraAndInfraVisionRange", "normal"),
            ("tracking", "normal"),
            ("gettingLost", "normal"),
            ("special", ""),
        ],
    )
    _precipitationData = {
        "heavy blizzard": PrecipitationData(
            movementSpeed=["12.5%", "25%", "0%"],
            normalVisionRange="2' radius",
            ultraAndInfraVisionRange="No",
            tracking="No",
            gettingLost="+50%",
            special="snowdrift up to 10'/h may accumulate on walls",
        ),
        "blizzard": PrecipitationData(
            movementSpeed=["25%", "25%", "25%"],
            normalVisionRange="10' radius",
            ultraAndInfraVisionRange="50%",
            tracking="+40%",
            gettingLost="+35%",
            special="snowdrift up to 5'/h may accumulate on walls",
        ),
        "heavy snowstorm": PrecipitationData(
            movementSpeed=["50%", "50%", "50%"],
            normalVisionRange="50%",
            ultraAndInfraVisionRange="50%",
            tracking="-25%",
            gettingLost="+20%",
            special="drifts of 1'/h if wind speed > 20 mph",
        ),
        "light snowstorm": PrecipitationData(
            movementSpeed=["75%", "normal", "normal"],
            normalVisionRange="75%",
            ultraAndInfraVisionRange="75%",
            tracking="-10%",
            gettingLost="+10%",
            special="drifts of 1'/h if wind speed > 20 mph",
        ),
        "sleet storm": PrecipitationData(
            movementSpeed=["75%", "50%", "50%"],
            normalVisionRange="75%",
            ultraAndInfraVisionRange="75%",
            tracking="-10%",
            gettingLost="+5%",
        ),
        "hailstorm": PrecipitationData(
            movementSpeed=["75%", "75%", "75%"],
            tracking="-10%",
            gettingLost="+10%",
            special="diameter: 1d2'. If higher than 1' assess 1 dmg/0.5' every turn for people with AC < 6. No "
            "protection from ring, bracers. Only magic armor",
        ),
        "heavy fog": PrecipitationData(
            movementSpeed=["25%", "25%", "25%"],
            normalVisionRange="2' radius",
            ultraAndInfraVisionRange="50%",
            tracking="-60%",
            gettingLost="+50%",
        ),
        "light fog": PrecipitationData(
            movementSpeed=["50%", "50%", "50%"],
            normalVisionRange="25%",
            ultraAndInfraVisionRange="75%",
            tracking="-30%",
            gettingLost="+30%",
        ),
        "mist": PrecipitationData(
            tracking="-5%",
        ),
        "dirzzle": PrecipitationData(
            tracking="-1%/turn",
        ),
        "light rainstorm": PrecipitationData(
            tracking="-10%/turn",
            special="a drop in temperature to 30 F (~ 0 C) or less after such storm may result in icy ground",
        ),
        "heavy rainstorm": PrecipitationData(
            movementSpeed=["75%", "normal", "75%"],
            normalVisionRange="75%",
            ultraAndInfraVisionRange="75%",
            tracking="-10%/turn",
            gettingLost="+10%",
            special="a drop in temperature to 30 F (~ 0 C) or less after such storm may result in icy ground",
        ),
        "thunderstorm": PrecipitationData(
            movementSpeed=["50%", "50%", "50%"],
            normalVisionRange="75%",
            ultraAndInfraVisionRange="75%",
            tracking="-10%/turn",
            gettingLost="+10% (+30% if horsed)",
            special="1 lighting stroke/10 mins. 1% probability that the party is hit. 10% if the party shelters under trees. Dmg: 6d6 with saving throw for half dmg",
        ),
        "tropical storm": PrecipitationData(
            movementSpeed=["25%", "25%", "no"],
            normalVisionRange="50%",
            ultraAndInfraVisionRange="50%",
            tracking="no",
            gettingLost="+30%",
            special="10% gust damage/3 turns if wind speed > 40 mph. Dmg: 1d6 for every full 10 mph above 40 mph",
        ),
        "monsoon": PrecipitationData(
            movementSpeed=["25%", "25%", "no"],
            normalVisionRange="25%",
            ultraAndInfraVisionRange="25%",
            tracking="no",
            gettingLost="+30%",
            special="10% gust damage/3 turns if wind speed > 40 mph. Dmg: 1d6 for every full 10 mph above 40 mph",
        ),
        "gale": PrecipitationData(
            movementSpeed=["25%", "25%", "no"],
            normalVisionRange="25%",
            ultraAndInfraVisionRange="25%",
            tracking="no",
            gettingLost="+20%",
            special="10% gust dmg/3 turns if wind speed > 40 mph. Dmg: 1d6 for every full 10 mph above 40 mph",
        ),
        "hurricane or typhoon": PrecipitationData(
            movementSpeed=["25%", "25%", "no"],
            normalVisionRange="25%",
            ultraAndInfraVisionRange="25%",
            tracking="no",
            gettingLost="+30%",
            special="1d6 wind dmg/3 turns to unprotected creatures. 1d4 structural dmg/turn to buildings",
        ),
    }


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
        self.ongoingPrecipitation = ongoingPrecipitation
        self.ongoingSpecialPrecipitation = ongoingSpecialPrecipitation

    def generate_weather(self, day, location, is_reset=False):
        self.reports = [i for i in self.reports if i.day >= day]
        while len(self.reports) < self._n_reports:
            self.reports.append(self.generate_day(day + len(self.reports), location))

    def generate_day(self, day, location):
        T = self.getTemperature(day, location, False)
        sky = self.getSkyConditions(day)
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

    def getTemperature(self, day, location, is_celsius=False):
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

    def getSkyConditions(self, day):
        c = GHCalendar(day)
        monthData = utils.smart_find(self._monthData, c.getMonthFest())
        k = bisect_left(monthData.sky, roll("1d100").total)
        return ["clear", "partly cloudy", "cloudy"][k]

    @staticmethod
    def _correctTforPrecipitation(T, pT):
        if T[0] <= pT[1] and T[1] >= pT[0]:
            T[0] = max(pT[0], T[0])
            T[1] = min(pT[1], T[1])
            return T, False
        else:
            return T, True

    def update_ongoingSpecialPrecipitation(self, day):
        self.ongoingSpecialPrecipitation = [
            i for i in self.ongoingSpecialPrecipitation if i[0] >= day
        ]

    def update_ongoingPrecipitation(self, day, terrain, T):
        self.ongoingPrecipitation = [
            i for i in self.ongoingPrecipitation if i[0] >= day
        ]
        if len(self.ongoingPrecipitation) != 0:
            return

        c = GHCalendar(day)
        monthData = utils.smart_find(self._monthData, c.getMonthFest())
        terrainData = utils.smart_find(GHLocation._terrainData, terrain)

        if roll("1d100").total > monthData.precipitation + terrainData.precipitation:
            return  # no precipitation

        cont = True
        while cont:
            k_prec = bisect_left(
                self._precipitationOccurranceData[0], roll("1d100").total
            )
            precipitation = self._precipitationOccurranceData[1][k_prec]
            if precipitation in terrainData.forbidden:
                continue

            if precipitation == "special":
                if len(self.ongoingSpecialPrecipitation) == 0:
                    self.ongoingSpecialPrecipitation.append(
                        [day + 1, f"{precipitation} TODO"]
                    )
                continue

            _, cont = self._correctTforPrecipitation(
                T, self._precipitationData[precipitation].T
            )

        cont = True
        duration = 0
        while cont:
            precipitationData = self._precipitationData[precipitation]

            cont = (
                roll("1d100").total <= precipitationData.continuing
            )  # needed immediately for rainbow

            duration += (roll(precipitationData.durationH).total / 24) * (
                1 + (terrain in terrainData.doubled)
            )
            amount = roll(precipitationData.amount).total
            area = roll(precipitationData.area).total
            windSpeed = max(
                roll(precipitationData.windSpeed).total + terrainData.windSpeed, 0
            )
            rainbow = None
            if not cont and roll("1d100").total <= precipitationData.rainbow:
                k = bisect_left(self._rainbowData[0], roll("1d100").total)
                rainbow = self._rainbowData[1][k]

            self.ongoingPrecipitation.append(
                [day + duration, precipitation, amount, windSpeed, rainbow, area]
            )

            morphing = roll("1d10").total
            if morphing == 1:
                k_prec = max(k_prec - 1, 0)
            if morphing == 10:
                k_prec = min(k_prec + 1, len(self._precipitationOccurranceData[1]) - 2)
            precipitation = self._precipitationOccurranceData[1][k_prec]

    def getPrecipitation(self, day, terrain, T):
        self.update_ongoingSpecialPrecipitation(day)
        self.update_ongoingPrecipitation(day, terrain, T)

        precipitation = [
            i
            for idx, i in enumerate(self.ongoingPrecipitation)
            if idx == 0 or self.ongoingPrecipitation[idx - 1][0] < day + 1
        ]
        specialPrecipitation = [
            i
            for idx, i in enumerate(self.ongoingSpecialPrecipitation)
            if idx == 0 or self.ongoingPrecipitation[idx - 1][0] < day + 1
        ]

        if len(precipitation) == 0:
            terrainData = utils.smart_find(GHLocation._terrainData, terrain)
            precipitation = [
                [
                    day,
                    "no precipitation",
                    0,
                    max(terrainData.windSpeed + roll("1d20-1").total, 0),
                    None,
                ]
            ]
        else:
            for i in precipitation:
                T, _ = self._correctTforPrecipitation(
                    T, self._precipitationData[i[1]].T
                )

        return precipitation, specialPrecipitation, T

    """Data Tables"""

    _rainbowData = [
        [89, 95, 98, 99, 100],
        [
            "single rainbow",
            "double rainbow (may be an omen)",
            "triple rainbow (" "almost cerainly an " "omen)",
            "bifrost bridge or coulds in the shape of rain deity",
            "rain deity or servant in the sky",
        ],
    ]

    _precipitationOccurranceData = [
        [2, 5, 10, 20, 25, 27, 30, 38, 40, 45, 60, 70, 84, 89, 94, 97, 99, 100],
        [
            "heavy blizzard",
            "blizzard",
            "heavy snowstorm",
            "light snowstorm",
            "sleet storm",
            "hailstorm",
            "heavy fog",
            "light fog",
            "mist",
            "dirzzle",
            "light rainstorm",
            "heavy rainstorm",
            "thunderstorm",
            "tropical storm",
            "monsoon",
            "gale",
            "hurricane or typhoon",
            "special",
        ],
    ]

    PrecipitationData = recordtype(
        "PrecipitationData",
        [
            ("T", [float("-inf"), float("inf")]),  # min, max
            ("continuing", 0),
            ("rainbow", 0),
            ("amount", "0"),
            ("durationH", "0"),
            ("windSpeed", "0"),
            ("area", "0"),
        ],
    )
    _precipitationData = {
        "heavy blizzard": PrecipitationData(
            T=[float("-inf"), 10],
            continuing=5,
            amount="2d10+10",
            durationH="3d8",
            windSpeed="6d8+40",
        ),
        "blizzard": PrecipitationData(
            T=[float("-inf"), 20],
            continuing=10,
            amount="2d8+8",
            durationH="3d10",
            windSpeed="3d8+36",
        ),
        "heavy snowstorm": PrecipitationData(
            T=[float("-inf"), 25],
            continuing=20,
            amount="2d8+2",
            durationH="4d6",
            windSpeed="3d10",
        ),
        "light snowstorm": PrecipitationData(
            T=[float("-inf"), 35],
            continuing=25,
            rainbow=1,
            amount="1d8",
            durationH="2d6",
            windSpeed="4d6",
        ),
        "sleet storm": PrecipitationData(
            T=[float("-inf"), 35],
            continuing=20,
            amount="1d2",
            durationH="1d6",
            windSpeed="3d10",
        ),
        "hailstorm": PrecipitationData(
            T=[float("-inf"), 65],
            continuing=10,
            durationH="1d4",
            windSpeed="4d10",
        ),
        "heavy fog": PrecipitationData(
            T=[20, 60],
            continuing=25,
            rainbow=1,
            durationH="1d12",
            windSpeed="1d20",
        ),
        "light fog": PrecipitationData(
            T=[30, float("inf")],
            continuing=30,
            rainbow=3,
            durationH="2d4",
            windSpeed="1d10",
        ),
        "mist": PrecipitationData(
            T=[30, float("inf")],
            continuing=15,
            rainbow=10,
            durationH="2d6",
            windSpeed="1d10",
        ),
        "dirzzle": PrecipitationData(
            T=[25, float("inf")],
            continuing=20,
            rainbow=5,
            amount="1",
            durationH="1d10",
            windSpeed="1d20",
        ),
        "light rainstorm": PrecipitationData(
            T=[25, float("inf")],
            continuing=45,
            rainbow=15,
            amount="1d3",
            durationH="1d12",
            windSpeed="1d20",
        ),
        "heavy rainstorm": PrecipitationData(
            T=[25, float("inf")],
            continuing=30,
            rainbow=20,
            amount="1d4+3",
            durationH="1d12",
            windSpeed="2d12+10",
        ),
        "thunderstorm": PrecipitationData(
            T=[30, float("inf")],
            continuing=15,
            rainbow=20,
            amount="1d8",
            durationH="1d4",
            windSpeed="4d10",
        ),
        "tropical storm": PrecipitationData(
            T=[40, float("inf")],
            continuing=20,
            rainbow=10,
            amount="1d6 [per day]",
            durationH="24*1d3",
            windSpeed="3d12+30",
        ),
        "monsoon": PrecipitationData(
            T=[55, float("inf")],
            continuing=30,
            rainbow=5,
            amount="1d8 [per day]",
            durationH="24*(1d6+6)",
            windSpeed="6d10",
        ),
        "gale": PrecipitationData(
            T=[40, float("inf")],
            continuing=15,
            rainbow=10,
            amount="1d8 [per day]",
            durationH="24*(1d3)",
            windSpeed="6d8+40",
        ),
        "hurricane or typhoon": PrecipitationData(
            T=[55, float("inf")],
            continuing=30,
            rainbow=5,
            amount="1d10 [per day]",
            durationH="24*(1d4)",
            windSpeed="7d10+70",
        ),
        "sand storm": PrecipitationData(
            durationH="1d8",
            windSpeed="5d10",
        ),
        "dust storm": PrecipitationData(
            durationH="1d8",
            windSpeed="5d10",
        ),
        "wind storm": PrecipitationData(
            durationH="1d10",
            windSpeed="8d10+20",
        ),
        "earthquake": PrecipitationData(
            durationH="1d10",
            windSpeed="1d20",
        ),
        "avalanche": PrecipitationData(
            amount="5d10",
            durationH="(1d10)/60",
            windSpeed="1d20",
        ),
        "volcano": PrecipitationData(
            amount="5d10",
            durationH="(1d10)/60",
            windSpeed="1d20",
        ),
        "tsunami": PrecipitationData(
            amount="10d20 [wave ht. feet]",
            durationH="1d2",
            windSpeed="5d10+10",
        ),
        "quicksand": PrecipitationData(
            area="1d20 [radius]",
            durationH="24",
            windSpeed="1d20",
        ),
        "flash flood": PrecipitationData(
            durationH="1d6+2",
            windSpeed="1d20",
        ),
        "rain forest downpour": PrecipitationData(
            amount="",
            durationH="3d4",
            windSpeed="1d20",
        ),
    }

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
