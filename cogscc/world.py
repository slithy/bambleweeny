from cogscc.calendar import GHCalendar
from cogscc.weather import GHWeather
from cogscc.location import GHLocation
from cogscc.models.errors import ItemNotFound, InvalidArgument
from cogscc.base_obj import BaseObj


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
        self.weather = (
            GHWeather.__from_dict__(weather) if isinstance(weather, dict) else weather
        )
        self.locations = {
            k: GHLocation.__from_dict__(v) if isinstance(v, dict) else v
            for k, v in locations.items()
        }
        self.currentLocation = None
        self.set_current_location(currentLocation)

        self.advance_days(0)


# Weather
    def reset_weather(self):
        self.weather = GHWeather()
        self.advance_days(0)
        return f"Weather reset successfully"

    def get_weather_report(self, day=0):
        return self.weather.reports[day]


# Date
    def set_date(self, days):
        self.calendar = GHCalendar(days)
        self.advance_days(0)

    def advance_days(self, days=1):
        self.calendar.advance(days)
        if self.currentLocation is not None:
            self.weather.generate_weather(
                self.calendar.day, self.get_current_location()
            )
            return str(self.calendar)
        else:
            return f"Missing location. Weather not set!\n{str(self.calendar)}"

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
            return None

        return self.locations[self.currentLocation]

    def get_locations(self):
        out = ""
        for i in self.locations:
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

