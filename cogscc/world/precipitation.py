from bisect import bisect_left

from cogscc.funcs.dice import roll

from cogscc.base_obj import BaseObj
from cogscc.world.temperature import GHTemperature
from cogscc.world.weather_data import GHWeatherData
from cogscc.funcs import utils
from cogscc.models.errors import ItemNotFound


class GHPrecipitation(BaseObj):
    def __init__(self, *args, **kwargs):
        if len(args) > 0:
            name, day, terrain = args
            self.name = name
            self.start_time = day
            self.terrain = terrain

            if self.name not in GHWeatherData.precipitation_data:
                l = ", ".join(list(GHWeatherData.precipitation_data.keys()))
                raise ItemNotFound(
                    f"The precipitation `{self.name}` does not exist! The available precipitations are:\n{l}"
                )

            pData = GHWeatherData.precipitation_data[self.name]

            self.duration = roll(pData.duration[0]).total / pData.duration[1]
            if terrain in pData.double_duration_terrain:
                self.duration *= 2
            self.end_time = self.duration + day

            self.amount = roll(pData.amount).consolidated()
            self.area = roll(pData.area).consolidated()
            terrainData = utils.smart_find(GHWeatherData.terrain_data, terrain)
            self.wind_speed = max(
                roll(pData.wind_speed).total + terrainData.wind_speed, 0
            )

            self.continuing = roll("1d100").total <= pData.continuing

            self.rainbow = None
            if not self.continuing and roll("1d100").total <= pData.rainbow:
                k = bisect_left(GHWeatherData.rainbow_data[0], roll("1d100").total)
                self.rainbow = GHWeatherData.rainbow_data[1][k]
        else:
            for k, v in kwargs.items():
                setattr(self, k, v)

        if self.name not in GHWeatherData.precipitation_data:
            l = ", ".join(list(GHWeatherData.precipitation_data.keys()))
            raise ItemNotFound(
                f"The precipitation `{self.name}` does not exist! The available precipitations are:\n{l}"
            )

    def occurrence_idx(self):
        try:
            return GHWeatherData.precipitation_occurrence_data[1].index(self.name)
        except ValueError:
            return -1

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
        out += f"wind speed: {self.wind_speed} [mph] \n"
        kws = bisect_left(GHWeatherData.wind_speed_data[0], self.wind_speed)
        wind_level = GHWeatherData.wind_speed_data[1][kws]

        if wind_level != GHWeatherData.wind_speed_data[1][0] or is_detailed:
            out += "wind effects:\n"
            wind_data = GHWeatherData.wind_speed_table_data[wind_level]
            for k in [
                i
                for i in dir(wind_data)
                if not i.startswith("_") and not callable(getattr(wind_data, i))
            ]:
                v = getattr(wind_data, k)
                out += f"   {k}: {v}\n"

        if T is not None:
            perceivedT = GHTemperature(T).perceived_T(self.wind_speed)
            if perceivedT != T:
                out += f"Perceived T: {str(GHTemperature(perceivedT))} \n"
        if is_detailed:
            out += f"continuing: {self.continuing} \n"
        if is_detailed or self.rainbow != std.rainbow:
            out += f"rainbow: {self.rainbow} \n"
        pData = GHWeatherData.precipitation_data[self.name]
        std = GHWeatherData.precipitation_data["no precipitation"]
        if is_detailed or pData.movement_speed != std.movement_speed:
            out += (
                f"movement speed: {pData.movement_speed[0]} [foot], {pData.movement_speed[1]} [horse], "
                f"{pData.movement_speed[2]} [cart] (or based on wind speed if worse)\n"
            )
        if is_detailed or pData.normal_vision_range != std.normal_vision_range:
            out += f"normal vision range: {pData.normal_vision_range}\n"
        if (
            is_detailed
            or pData.ultra_and_infra_vision_range != std.ultra_and_infra_vision_range
        ):
            out += f"ultra/infra vision range: {pData.ultra_and_infra_vision_range}\n"
        if is_detailed or pData.tracking != std.tracking:
            out += f"tracking: {pData.tracking}\n"
        if is_detailed or pData.getting_lost != std.getting_lost:
            out += f"chance of getting lost: {pData.getting_lost}\n"
        if is_detailed or pData.add_info != std.add_info:
            out += f"add. info: {pData.add_info}\n"
        return out

    def correct_T(self, T):
        pT = GHWeatherData.precipitation_data[self.name].T
        T[0] = max(pT[0], T[0])
        T[1] = min(pT[1], T[1])
        return T

    @staticmethod
    def get_precipitation_chain(day, T, terrain, precipitationChance, precipitation=""):
        pChain = []
        if roll("1d100").total > precipitationChance:
            return pChain

        while len(precipitation) == 0:
            r = roll("1d100").total
            k_prec = bisect_left(GHWeatherData.precipitation_occurrence_data[0], r)
            precipitation = GHWeatherData.precipitation_occurrence_data[1][k_prec]

            if precipitation == "special":
                tData = GHWeatherData.terrain_data[terrain]
                ks = bisect_left(tData.special[0], roll("1d100").total)
                precipitation = tData.special[1][ks]
                break

            pData = GHWeatherData.precipitation_data[precipitation]
            if terrain in pData.forbidden_terrain:
                precipitation = ""
            if not (T[0] <= pData.T[1] and T[1] >= pData.T[0]):
                precipitation = ""

        pChain.append(GHPrecipitation(precipitation, day, terrain))
        while pChain[-1].continuing:
            if pChain[-1].occurrence_idx() < 0:
                pChain.append(
                    GHPrecipitation(precipitation, pChain[-1].end_time, terrain)
                )
                continue

            k_prec = pChain[-1].occurrence_idx()
            morphing = int(roll("1d10").total)
            morphing = -int(morphing == 1) + int(morphing == 10)
            k_prec = (
                max(k_prec + morphing, 0)
                if morphing <= 0
                else min(
                    k_prec + 1, len(GHWeatherData.precipitation_occurrence_data[1]) - 2
                )
            )
            pData = GHWeatherData.precipitation_data[precipitation]
            if (terrain in pData.forbidden_terrain) or not (
                T[0] <= pData.T[1] and T[1] >= pData.T[0]
            ):
                k_prec = pChain[-1].occurrence_idx()

            precipitation = GHWeatherData.precipitation_occurrence_data[1][k_prec]
            pChain.append(GHPrecipitation(precipitation, pChain[-1].end_time, terrain))

        if pChain[-1].occurrence_idx() < 0:
            pChain.extend(
                GHPrecipitation.get_precipitation_chain(
                    pChain[-1].end_time, T, terrain, precipitationChance
                )
            )

        return pChain
