from cogscc.world.calendar import GHCalendar
from cogscc.world.weather_data import GHWeatherData
from cogscc.world.precipitation import GHPrecipitation
from cogscc.world.location import GHLocation
from cogscc.models.errors import ItemNotFound
from cogscc.base_obj import BaseObj
from cogscc.funcs import utils


class GHWorld(BaseObj):
    def __init__(
        self,
        calendar={},
        weather={},
        locations={},
        currentLocation=None,
    ):
        self.calendar = (
            GHCalendar.__from_dict__(calendar)
            if isinstance(calendar, dict)
            else calendar
        )
        self.locations = {
            k: GHLocation.__from_dict__(v) if isinstance(v, dict) else v
            for k, v in locations.items()
        }
        self.currentLocation = None
        self.set_current_location(currentLocation)

    # Date
    def set_date(self, days):
        self.calendar = GHCalendar(days)
        self.advance_days(0)

    # Location
    def add_location(self, l):
        k = l.name
        out = f"Location {k} {'replaced' if k in self.locations else 'added'}"
        self.locations[k] = l
        if len(self.locations) == 1:
            out += f"\n{self.set_current_location(k)}"
        return out

    def remove_location(self, k):
        if self.currentLocation == k:
            self.currentLocation = None
        if k not in self.locations:
            return f"Location {k} was not inserted!"
        del self.locations[k]
        return f"Location {k} successfully removed"

    def get_current_location(self):
        if self.currentLocation is None:
            return "Current location is not set!"

        return self.locations[self.currentLocation]

    def get_locations(self):
        out = ""
        for i in self.locations.values():
            out += str(i) + "\n"
        return out

    def set_current_location(self, k):
        if len(self.locations) == 0:
            self.currentLocation = None
            return self.get_current_location()

        if k is None:
            self.currentLocation = list(self.locations.keys())[0]
            return self.get_current_location()

        if k in self.locations:
            self.currentLocation = k
            return self.get_current_location()

        loc = ", ".join([i for i in self.locations])
        raise ItemNotFound(f"Location {k} not found in [{loc}]")

    # Weather
    def reset_weather(self):
        for v in self.locations.values():
            v.reset_weather(self.calendar.day)
        return f"Weather reset successfully"

    def get_weather_report(self, day=0):
        return self.get_current_location().weather.get_weather_report(day)

    def get_precipitation_chain(self, precipitation, day=0):
        wr = self.get_weather_report(day)

        c = GHCalendar(day)
        monthData = utils.smart_find(GHWeatherData.month_data, c.getMonthFest())
        terrainData = utils.smart_find(
            GHWeatherData.terrain_data, self.get_current_location().terrain
        )

        return GHPrecipitation.get_precipitation_chain(
            wr.day,
            wr.T,
            self.get_current_location().terrain,
            monthData.precipitation + terrainData.precipitation,
            precipitation,
        )

    def advance_days(self, days=1):
        self.calendar.advance(days)
        for v in self.locations.values():
            v.generate_weather(self.calendar.day)

        return str(self.calendar)
