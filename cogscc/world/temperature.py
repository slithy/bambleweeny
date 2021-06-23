from cogscc.funcs import utils
from cogscc.world.calendar import GHCalendar
from cogscc.world.location import GHLocation
from cogscc.world.weather_data import GHWeatherData

from cogscc.funcs.dice import roll


class GHTemperature:
    def __init__(self, T):
        self.T = T

    def perceived_T(self, windSpeed):
        return [
            self._correctForWindChill(self.T[0], windSpeed),
            self._correctForWindChill(self.T[1], windSpeed),
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
    def _correctForWindChill(T, ws):
        i_wind = int(abs(ws) / 5)
        if i_wind > len(GHWeatherData._windChillData):
            i_wind = -1
        j_T = int((T + 20) / 5)
        if j_T < 0:
            j_T = 0
        if j_T >= len(GHWeatherData._windChillData[0]):
            return T

        delta = (
            GHWeatherData._windChillData[i_wind][j_T]
            - GHWeatherData._windChillData[0][j_T]
        )

        return T + delta

    @staticmethod
    def get_temperature(day, location):
        c = GHCalendar(day)
        monthData = utils.smart_find(GHWeatherData._monthData, c.getMonthFest())
        baseT = monthData.T[0]
        # correct for latitude
        T = baseT + 2 * (40 - location.latitude)

        # terrain
        terrainData = utils.smart_find(GHWeatherData._terrainData, location.terrain)
        terrainTmod = terrainData.T(location.altitude)

        # daily spread -
        T_min = T + roll(monthData.T[1]).total + terrainTmod[0]
        # daily spread +
        T_max = T + roll(monthData.T[2]).total + terrainTmod[1]

        return [T_min, T_max]
