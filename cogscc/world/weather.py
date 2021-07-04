from bisect import bisect_left
from cogscc.funcs.dice import roll
from cogscc.funcs import utils
from cogscc.world.calendar import GHCalendar
from cogscc.world.temperature import GHTemperature
from cogscc.world.weather_data import GHWeatherData
from cogscc.world.precipitation import GHPrecipitation
from cogscc.base_obj import BaseObj
from cogscc.models.errors import (
    InvalidArgument,
)


class GHWeatherReport(BaseObj):
    def __init__(self, day, T, sky, humidity, precipitation):
        self.day = day
        self.T = T
        self.sky = sky
        self.humidity = humidity
        self.precipitation = [
            GHPrecipitation.__from_dict__(i) if isinstance(i, dict) else i
            for i in precipitation
        ]

    def __str__(self):
        out = f"**Weather Report** date: {GHCalendar(self.day).__str__()}\n"
        out += f"T: {str(GHTemperature(self.T))} "
        if self.T[1] > 75:
            out += f"Rel. Humidity: {self.humidity}%\n"
            kTH = bisect_left(GHWeatherData.THData[0], self.humidity + self.T[1])
            TH = GHWeatherData.THData[1][kTH]
            if TH != "normal weather":
                THdata = GHWeatherData.TH_table_data[TH]
                std = GHWeatherData.TH_table_data["normal weather"]
                out += TH + ":\n"
                if std.movement_speed != THdata.movement_speed:
                    out += f"   movement speed (all types): {THdata.movement_speed}\n"
                if std.AC != THdata.AC:
                    out += f"   AC: {THdata.AC}\n"
                if std.BtH != THdata.BtH:
                    out += f"   BtH: {THdata.BtH}\n"
                if std.dex != THdata.dex:
                    out += f"   dex: {THdata.dex}\n"
                if std.vision != THdata.vision:
                    out += f"   vision (all types): {THdata.vision}\n"
                if std.rest_per_hour != THdata.rest_per_hour:
                    out += f"   rest needed per hour: {THdata.rest_per_hour}\n"
                if std.spell_failure_chance != THdata.spell_failure_chance:
                    out += f"   spell failure chance (if somatic): {THdata.spell_failure_chance}\n"
        out += f"Sky: {self.sky}\n"
        for i in self.precipitation:
            out += i.__str__(self.T)
        return out


class GHWeather(BaseObj):
    _n_reports = 14

    def __init__(
        self,
        reports=[],
        extreme_T_chain=[],
        precipitation_chain=[],
    ):
        self.reports = [
            GHWeatherReport.__from_dict__(i) if isinstance(i, dict) else i
            for i in reports
        ]
        self.extreme_T_chain = extreme_T_chain  # [endDay, modifier] or None
        self.precipitation_chain = [
            GHPrecipitation.__from_dict__(i) if isinstance(i, dict) else i
            for i in precipitation_chain
        ]

    def get_weather_report(self, day=0):
        if day < 0:
            raise InvalidArgument("I cannot forecast in the past!")
        if day >= len(self.reports):
            raise InvalidArgument(
                f"Either weather was not reset or you are trying to forecast too much in the "
                f"future!! Max possible forecast {len(self.reports)-1}"
            )
        return self.reports[day]

    def generate_weather(self, day, location):
        self.reports = [i for i in self.reports if i.day >= day]
        while len(self.reports) < self._n_reports:
            self.reports.append(self.generate_day(day + len(self.reports), location))

    def generate_day(self, day, location):
        T = self.get_temperature(day, location)
        sky = self.get_sky_conditions(day)
        humidity = self.get_humidity()
        precipitation, T = self.get_precipitation(day, location.terrain, T)

        return GHWeatherReport(day, T, sky, humidity, precipitation)

    def update_extreme_T_chain(self, day):
        self.extreme_T_chain = [i for i in self.extreme_T_chain if i[0] >= day]
        if len(self.extreme_T_chain) != 0:
            return

        c = GHCalendar(day)

        k = bisect_left(GHWeatherData.extreme_T_data.modifier[0], roll("1d100").total)
        multi = GHWeatherData.extreme_T_data.modifier[1][k]
        modifier = (
            eval(
                utils.smart_find(GHWeatherData.month_data, c.getMonthFest())
                .T[1 + int(multi < 0)]
                .replace("1d", "")
            )
            * multi
        )
        if modifier == 0:
            return

        k = bisect_left(GHWeatherData.extreme_T_data.duration[0], roll("1d20").total)
        duration = GHWeatherData.extreme_T_data.duration[1][k]
        self.extreme_T_chain.append([day + duration, modifier])

    def get_temperature(self, day, location):
        self.update_extreme_T_chain(day)

        T = GHTemperature.get_temperature(day, location)
        if len(self.extreme_T_chain) != 0:
            T[0] += self.extreme_T_chain[0][1]
            T[1] += self.extreme_T_chain[0][1]

        return T

    def get_sky_conditions(self, day):
        c = GHCalendar(day)
        monthData = utils.smart_find(GHWeatherData.month_data, c.getMonthFest())
        k = bisect_left(monthData.sky, roll("1d100").total)
        return ["clear", "partly cloudy", "cloudy"][k]

    def get_humidity(self):
        return roll("1d100").total

    def update_precipitation_chain(self, day, terrain, T):
        self.precipitation_chain = [
            i for i in self.precipitation_chain if i.end_time >= day
        ]
        if len(self.precipitation_chain) != 0:
            return

        c = GHCalendar(day)
        monthData = utils.smart_find(GHWeatherData.month_data, c.getMonthFest())
        terrainData = utils.smart_find(GHWeatherData.terrain_data, terrain)

        self.precipitation_chain = GHPrecipitation.get_precipitation_chain(
            day, T, terrain, monthData.precipitation + terrainData.precipitation
        )

        if (
            len(self.precipitation_chain) != 0
            and self.precipitation_chain[0].occurrence_idx() == -1
        ):
            self.precipitation_chain.extend(
                GHPrecipitation.get_precipitation_chain(
                    day, T, terrain, monthData.precipitation + terrainData.precipitation
                )
            )

    def get_precipitation(self, day, terrain, T):
        self.update_precipitation_chain(day, terrain, T)

        precipitation = [
            i for i in self.precipitation_chain if i.end_time - i.duration <= day + 1
        ]

        if len(precipitation) == 0:
            precipitation = [GHPrecipitation("no precipitation", day, terrain)]

        for i in precipitation:
            T = i.correct_T(T)

        return precipitation, T
