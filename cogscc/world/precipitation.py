from recordtype import recordtype
from bisect import bisect_left

from cogscc.funcs.dice import roll

from cogscc.base_obj import BaseObj
from cogscc.world.location import GHLocation
from cogscc.world.temperature import GHTemperature
from cogscc.world.weather_data import GHWeatherData
from cogscc.funcs import utils


class GHPrecipitation(BaseObj):
    def __init__(self, *args, **kwargs):
        if len(args) > 0:
            name, day, terrain = args
            self.name = name
            self.start_time = day
            self.terrain = terrain

            pData = GHWeatherData._precipitationData[self.name]

            self.duration = roll(pData.duration[0]).total / pData.duration[1]
            if terrain in pData.doubleDurationTerrain:
                self.duration *= 2
            self.end_time = self.duration + day

            self.amount = roll(pData.amount).consolidated()
            self.area = roll(pData.area).consolidated()
            terrainData = utils.smart_find(GHWeatherData._terrainData, terrain)
            self.windSpeed = max(roll(pData.windSpeed).total + terrainData.windSpeed, 0)

            self.continuing = roll("1d100").total <= pData.continuing

            self.rainbow = None
            if not self.continuing and roll("1d100").total <= pData.rainbow:
                k = bisect_left(self._rainbowData[0], roll("1d100").total)
                self.rainbow = self._rainbowData[1][k]
        else:
            for k, v in kwargs.items():
                setattr(self, k, v)

    def __str__(self, T=None, is_detailed=False):
        std = GHPrecipitation("no precipitation", self.start_time, self.terrain)
        out = f"**{self.name}**: \n"
        if is_detailed or self.duration != std.duration:
            t = utils.d2std_time(self.duration)
            out += f"duration: {t[2]}m:{t[1]}h:{t[0]}d \n"
        if is_detailed or self.amount != std.amount:
            out += f"amount: {self.amount} [inches] \n"
        if is_detailed or self.area != std.area:
            out += f"area: {self.area} [feet] "
        out += f"wind speed: {self.windSpeed} [mph] \n"
        if T is not None:
            perceivedT = GHTemperature(T).perceived_T(self.windSpeed)
            if perceivedT != T:
                out += f"Perceived T: {str(GHTemperature(perceivedT))} \n"
        if is_detailed:
            out += f"continuing: {self.continuing} \n"
        if is_detailed or self.rainbow != std.rainbow:
            out += f"rainbow: {self.rainbow} \n"
        pData = GHWeatherData._precipitationData[self.name]
        std = GHWeatherData._precipitationData["no precipitation"]
        if is_detailed or pData.movementSpeed != std.movementSpeed:
            out += (
                f"movement speed: {pData.movementSpeed[0]} [foot], {pData.movementSpeed[1]} [horse], "
                f"{pData.movementSpeed[2]} [cart]\n"
            )
        if is_detailed or pData.normalVisionRange != std.normalVisionRange:
            out += f"normal vision range: {pData.normalVisionRange}\n"
        if (
            is_detailed
            or pData.ultraAndInfraVisionRange != std.ultraAndInfraVisionRange
        ):
            out += f"ultra/infra vision range: {pData.ultraAndInfraVisionRange}\n"
        if is_detailed or pData.tracking != std.tracking:
            out += f"tracking: {pData.tracking}\n"
        if is_detailed or pData.gettingLost != std.gettingLost:
            out += f"chance of getting lost: {pData.gettingLost}\n"
        if is_detailed or pData.special != std.special:
            out += f"special: {pData.special}\n"
        return out

    def correct_T(self, T):
        pT = GHWeatherData._precipitationData[self.name].T
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
            if precipitation == "special":
                continue
            pData = GHWeatherData._precipitationData[precipitation]
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
                k_prec = min(
                    k_prec + 1, len(GHPrecipitation._precipitationOccurranceData[1]) - 2
                )
            precipitation = GHPrecipitation._precipitationOccurranceData[1][k_prec]
            pData = GHWeatherData._precipitationData[precipitation]
            if (terrain in pData.forbiddenTerrain) or not (
                T[0] <= pData.T[1] and T[1] >= pData.T[0]
            ):
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
