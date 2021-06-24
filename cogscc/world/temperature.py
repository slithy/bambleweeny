from cogscc.funcs import utils
from cogscc.world.calendar import GHCalendar
from cogscc.world.location import GHLocation
from cogscc.world.weather_data import GHWeatherData

from cogscc.funcs.dice import roll


class GHTemperature:
    def __init__(self, T):
        self.T = T

    def perceived_T(self, wind_speed):
        return [
            self._correct_for_windchill(self.T[0], wind_speed),
            self._correct_for_windchill(self.T[1], wind_speed),
        ]

    def F2C(self):
        return [utils.F2C(self.T[0]), utils.F2C(self.T[1])]

    def __str__(self, is_celsius=True):
        if is_celsius:
            T = self.F2C()
            return f"{T[0]}:{T[1]} C (min:max)"
        else:
            return f"{self.T[0]}:{self.T[1]} F (min:max)"

    @staticmethod
    def _correct_for_windchill(T, ws):

        i_wind = int(abs(ws) / 5)
        if i_wind >= len(GHWeatherData.windchill_data):
            i_wind = -1
        j_T = int((T + 20) / 5)
        if j_T < 0:
            j_T = 0
        if j_T >= len(GHWeatherData.windchill_data[0]):
            return T

        delta = (
            GHWeatherData.windchill_data[i_wind][j_T]
            - GHWeatherData.windchill_data[0][j_T]
        )

        return T + delta

    @staticmethod
    def get_temperature(day, location):
        c = GHCalendar(day)
        monthData = utils.smart_find(GHWeatherData.month_data, c.getMonthFest())
        baseT = monthData.T[0]
        # correct for latitude
        T = baseT + 2 * (40 - location.latitude)

        # terrain
        terrainData = utils.smart_find(GHWeatherData.terrain_data, location.terrain)
        terrainTmod = terrainData.T(location.altitude)

        # daily spread -
        T_min = T + roll(monthData.T[1]).total + terrainTmod[0]
        # daily spread +
        T_max = T + roll(monthData.T[2]).total + terrainTmod[1]

        return [T_min, T_max]
