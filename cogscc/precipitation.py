from recordtype import recordtype
from bisect import bisect_left

from cogscc.funcs.dice import roll

from cogscc.base_obj import BaseObj
from cogscc.location import GHLocation
from cogscc.funcs import utils


class GHPrecipitation(BaseObj):
    def __init__(self, *args, **kwargs):
        if len(args) > 0:
            name, day, terrain = args
            self.name = name
            self.start_time = day
            self.terrain = terrain

            pData = self._precipitationData[self.name]

            self.duration = roll(pData.duration[0]).total / pData.duration[1]
            if terrain in pData.doubleDurationTerrain:
                self.duration *= 2
            self.end_time = self.duration + day

            self.amount = roll(pData.amount).consolidated()
            self.area = roll(pData.area).consolidated()
            terrainData = utils.smart_find(GHLocation._terrainData, terrain)
            self.windSpeed = max(roll(pData.windSpeed).total + terrainData.windSpeed, 0)

            self.continuing = roll("1d100").total <= pData.continuing

            self.rainbow = None
            if not self.continuing and roll("1d100").total <= pData.rainbow:
                k = bisect_left(self._rainbowData[0], roll("1d100").total)
                self.rainbow = self._rainbowData[1][k]
        else:
            for k, v in kwargs.items():
                setattr(self, k, v)

    def __str__(self, is_detailed=False):
        std = GHPrecipitation("no precipitation", self.start_time, self.terrain)
        out = f"**{self.name}**: "
        if is_detailed or self.duration != std.duration:
            out += f"duration: {self.duration} [days] "
        if is_detailed or self.amount != std.amount:
            out += f"amount: {self.amount} [inches] "
        if is_detailed or self.area != std.area:
            out += f"area: {self.area} [feet] "
        out += f"wind speed: {self.windSpeed} [mph] "
        if is_detailed:
            out += f"continuing: {self.continuing} "
        if is_detailed or self.rainbow != std.rainbow:
            out += f"rainbow: {self.rainbow} "
        pData = self._precipitationData[self.name]
        std = self._precipitationData["no precipitation"]
        out += "\n"
        if is_detailed or pData.movementSpeed != std.movementSpeed:
            out += f"movement speed: {pData.movementSpeed[0]} [foot], {pData.movementSpeed[1]} [horse], " \
                   f"{pData.movementSpeed[2]} [cart]\n"
        if is_detailed or pData.normalVisionRange != std.normalVisionRange:
            out += f"normal vision range: {pData.normalVisionRange}\n"
        if is_detailed or pData.ultraAndInfraVisionRange != std.ultraAndInfraVisionRange:
            out += f"ultra/infra vision range: {pData.ultraAndInfraVisionRange}\n"
        if is_detailed or pData.tracking != std.tracking:
            out += f"tracking: {pData.tracking}\n"
        if is_detailed or pData.gettingLost != std.gettingLost:
            out += f"chance of getting lost: {pData.gettingLost}\n"
        if is_detailed or pData.special != std.special:
            out += f"special: {pData.special}\n"
        return out



    def correct_T(self, T):
        pT = GHPrecipitation._precipitationData[self.name].T
        T[0] = max(pT[0], T[0])
        T[1] = min(pT[1], T[1])
        return T

    @staticmethod
    def get_precipitation(day, T, terrain):

        out = []
        while True:
            k_prec = bisect_left(
                GHPrecipitation._precipitationOccurranceData[0], roll("1d100").total
            )
            precipitation = GHPrecipitation._precipitationOccurranceData[1][k_prec]
            if precipitation =="special":
                continue
            pData = GHPrecipitation._precipitationData[precipitation]
            if terrain in pData.forbiddenTerrain:
                continue
            if not (T[0] <= pData.T[1] and T[1] >= pData.T[0]):
                continue
            break

        out.append(GHPrecipitation(precipitation, day, terrain))
        day = out[-1].end_time
        while out[-1].continuing:
            morphing = roll("1d10").total
            old_k = k_prec
            if morphing == 1:
                k_prec = max(k_prec - 1, 0)
            if morphing == 10:
                k_prec = min(k_prec + 1, len(GHPrecipitation._precipitationOccurranceData[1]) - 2)
            precipitation = GHPrecipitation._precipitationOccurranceData[1][k_prec]
            pData = GHPrecipitation._precipitationData[precipitation]
            if (terrain in pData.forbiddenTerrain) or not (T[0] <= pData.T[1] and T[1] >= pData.T[0]):
                precipitation = GHPrecipitation._precipitationOccurranceData[1][old_k]

            out.append(GHPrecipitation(precipitation, day, terrain))
            day = out[-1].end_time

        return out


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
            ("duration", ["0", 1.0]), #[roll, multiplier (because roll() returns an integer and not float]
            ("windSpeed", "1d20-1"),
            ("area", "0"),
            ########## the rest is static ###############
            ("movementSpeed", ["normal", "normal", "normal"]),  # foot, horse, cart
            ("normalVisionRange", "normal"),
            ("ultraAndInfraVisionRange", "normal"),
            ("tracking", "normal"),
            ("gettingLost", "normal"),
            ("special", ""),
            ("forbiddenTerrain",[]),
            ("doubleDurationTerrain", []),
        ],
    )
    _precipitationData = {
        "no precipitation": PrecipitationData(),
        "heavy blizzard": PrecipitationData(
            T=[float("-inf"), 10],
            continuing=5,
            amount="2d10+10",
            duration=["3d8", 24],
            windSpeed="6d8+40",
            movementSpeed=["12.5%", "25%", "0%"],
            normalVisionRange="2' radius",
            ultraAndInfraVisionRange="No",
            tracking="No",
            gettingLost="+50%",
            special="snowdrift up to 10'/h may accumulate on walls",
            forbiddenTerrain=["desert"]
        ),
        "blizzard": PrecipitationData(
            T=[float("-inf"), 20],
            continuing=10,
            amount="2d8+8",
            duration=["3d10",24],
            windSpeed="3d8+36",
            movementSpeed=["25%", "25%", "25%"],
            normalVisionRange="10' radius",
            ultraAndInfraVisionRange="50%",
            tracking="+40%",
            gettingLost="+35%",
            special="snowdrift up to 5'/h may accumulate on walls",
            forbiddenTerrain=["desert"]
        ),
        "heavy snowstorm": PrecipitationData(
            T=[float("-inf"), 25],
            continuing=20,
            amount="2d8+2",
            duration=["4d6", 24],
            windSpeed="3d10",
            movementSpeed=["50%", "50%", "50%"],
            normalVisionRange="50%",
            ultraAndInfraVisionRange="50%",
            tracking="-25%",
            gettingLost="+20%",
            special="drifts of 1'/h if wind speed > 20 mph",
        ),
        "light snowstorm": PrecipitationData(
            T=[float("-inf"), 35],
            continuing=25,
            rainbow=1,
            amount="1d8",
            duration=["2d6", 24],
            windSpeed="4d6",
            movementSpeed=["75%", "normal", "normal"],
            normalVisionRange="75%",
            ultraAndInfraVisionRange="75%",
            tracking="-10%",
            gettingLost="+10%",
            special="drifts of 1'/h if wind speed > 20 mph",
        ),
        "sleet storm": PrecipitationData(
            T=[float("-inf"), 35],
            continuing=20,
            amount="1d2",
            duration=["1d6", 24],
            windSpeed="3d10",
            movementSpeed=["75%", "50%", "50%"],
            normalVisionRange="75%",
            ultraAndInfraVisionRange="75%",
            tracking="-10%",
            gettingLost="+5%",
        ),
        "hailstorm": PrecipitationData(
            T=[float("-inf"), 65],
            continuing=10,
            duration=["1d4",24],
            windSpeed="4d10",
            movementSpeed=["75%", "75%", "75%"],
            tracking="-10%",
            gettingLost="+10%",
            special="diameter: 1d2'. If higher than 1' assess 1 dmg/0.5' every turn for people with AC < 6. No "
            "protection from ring, bracers. Only magic armor",
            forbiddenTerrain=["desert", "dust"]
        ),
        "heavy fog": PrecipitationData(
            T=[20, 60],
            continuing=25,
            rainbow=1,
            duration=["1d12",24],
            windSpeed="1d20",
            movementSpeed=["25%", "25%", "25%"],
            normalVisionRange="2' radius",
            ultraAndInfraVisionRange="50%",
            tracking="-60%",
            gettingLost="+50%",
            forbiddenTerrain=["desert", "dust"],
            doubleDurationTerrain=["cold seacoast", "hot seacoast", "cold sea", "hot sea"]
        ),
        "light fog": PrecipitationData(
            T=[30, float("inf")],
            continuing=30,
            rainbow=3,
            duration=["2d4",24],
            windSpeed="1d10",
            movementSpeed=["50%", "50%", "50%"],
            normalVisionRange="25%",
            ultraAndInfraVisionRange="75%",
            tracking="-30%",
            gettingLost="+30%",
            forbiddenTerrain=["desert"],
            doubleDurationTerrain = ["cold seacoast", "hot seacoast", "cold sea", "hot sea"]
        ),
        "mist": PrecipitationData(
            T=[30, float("inf")],
            continuing=15,
            rainbow=10,
            duration=["2d6",24],
            windSpeed="1d10",
            tracking="-5%",
            doubleDurationTerrain=["cold seacoast", "hot seacoast", "cold sea", "hot sea"]
        ),
        "dirzzle": PrecipitationData(
            T=[25, float("inf")],
            continuing=20,
            rainbow=5,
            amount="1",
            duration=["1d10",24],
            windSpeed="1d20",
            tracking="-1%/turn",
        ),
        "light rainstorm": PrecipitationData(
            T=[25, float("inf")],
            continuing=45,
            rainbow=15,
            amount="1d3",
            duration=["1d12",24],
            windSpeed="1d20",
            tracking="-10%/turn",
            special="a drop in temperature to 30 F (~ 0 C) or less after such storm may result in icy ground",
        ),
        "heavy rainstorm": PrecipitationData(
            T=[25, float("inf")],
            continuing=30,
            rainbow=20,
            amount="1d4+3",
            duration=["1d12",24],
            windSpeed="2d12+10",
            movementSpeed=["75%", "normal", "75%"],
            normalVisionRange="75%",
            ultraAndInfraVisionRange="75%",
            tracking="-10%/turn",
            gettingLost="+10%",
            special="a drop in temperature to 30 F (~ 0 C) or less after such storm may result in icy ground",
        ),
        "thunderstorm": PrecipitationData(
            T=[30, float("inf")],
            continuing=15,
            rainbow=20,
            amount="1d8",
            duration=["1d4",24],
            windSpeed="4d10",
            movementSpeed=["50%", "50%", "50%"],
            normalVisionRange="75%",
            ultraAndInfraVisionRange="75%",
            tracking="-10%/turn",
            gettingLost="+10% (+30% if horsed)",
            special="1 lighting stroke/10 mins. 1% probability that the party is hit. 10% if the party shelters under trees. Dmg: 6d6 with saving throw for half dmg",
        ),
        "tropical storm": PrecipitationData(
            T=[40, float("inf")],
            continuing=20,
            rainbow=10,
            amount="1d6 [per day]",
            duration=["1d3", 1.0],
            windSpeed="3d12+30",
            movementSpeed=["25%", "25%", "no"],
            normalVisionRange="50%",
            ultraAndInfraVisionRange="50%",
            tracking="no",
            gettingLost="+30%",
            special="10% gust damage/3 turns if wind speed > 40 mph. Dmg: 1d6 for every full 10 mph above 40 mph",
            forbiddenTerrain=["desert", "plains"]
        ),
        "monsoon": PrecipitationData(
            T=[55, float("inf")],
            continuing=30,
            rainbow=5,
            amount="1d8 [per day]",
            duration=["1d6+6",1.0],
            windSpeed="6d10",
            movementSpeed=["25%", "25%", "no"],
            normalVisionRange="25%",
            ultraAndInfraVisionRange="25%",
            tracking="no",
            gettingLost="+30%",
            special="10% gust damage/3 turns if wind speed > 40 mph. Dmg: 1d6 for every full 10 mph above 40 mph",
            forbiddenTerrain=["desert", "dust", "plains"]
        ),
        "gale": PrecipitationData(
            T=[40, float("inf")],
            continuing=15,
            rainbow=10,
            amount="1d8 [per day]",
            duration=["1d3", 1.0],
            windSpeed="6d8+40",
            movementSpeed=["25%", "25%", "no"],
            normalVisionRange="25%",
            ultraAndInfraVisionRange="25%",
            tracking="no",
            gettingLost="+20%",
            special="10% gust dmg/3 turns if wind speed > 40 mph. Dmg: 1d6 for every full 10 mph above 40 mph",
            forbiddenTerrain=["desert"]
        ),
        "hurricane or typhoon": PrecipitationData(
            T=[55, float("inf")],
            continuing=30,
            rainbow=5,
            amount="1d10 [per day]",
            duration=["1d4", 1.0],
            windSpeed="7d10+70",
            movementSpeed=["25%", "25%", "no"],
            normalVisionRange="25%",
            ultraAndInfraVisionRange="25%",
            tracking="no",
            gettingLost="+30%",
            special="1d6 wind dmg/3 turns to unprotected creatures. 1d4 structural dmg/turn to buildings",
            forbiddenTerrain=["desert", "dust"]
        ),
    }