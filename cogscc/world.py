from cogscc.calendar import GHCalendar
from cogscc.weather import GHWeather
from cogscc.location import GHLocation
from cogscc.models.errors import ItemNotFound, InvalidArgument


class GHWorld:
    def __init__(
        self,
        calendar=GHCalendar(),
        weather=GHWeather(),
        locations={},
        currentLocation=None,
    ):
        if not isinstance(locations, dict):
            currentLocation = locations.name
            locations = {locations.name: locations}

        self.calendar = calendar
        self.weather = weather
        self.locations = locations
        self.currentLocation = None

        self.set_current_location(currentLocation)

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
        del self.locations[k]
        return f"Location {k} successfully removed"

    def get_current_location(self):
        if self.currentLocation is None:
            raise InvalidArgument("Current location not set!")

        return self.locations[self.currentLocation]

    def set_current_location(self, k):
        if k in self.locations or not None:
            self.currentLocation = k
        else:
            loc = ", ".join([i for i in self.locations])
            raise ItemNotFound(f"Location {k} not found in [{loc}]")

    def __to_json__(self):
        return {
            i: getattr(self, i)
            for i in dir(self)
            if not i.startswith("_") and not callable(getattr(self, i))
        }

    @classmethod
    def __from_dict__(cls, d):
        calendar = GHCalendar.__from_dict__(d.get("calendar", {}))
        weather = GHWeather.__from_dict__(d["weather"])
        if "locations" in d:
            locations = {
                k: GHLocation.__from_dict__(v) for k, v in d["locations"].items()
            }
        else:
            locations = {}
        currentLocation = d.get("currentLocation", None)
        return GHWorld(calendar, weather, locations, currentLocation)

    def __eq__(self, other):
        return (
            isinstance(other, type(self)) and self.__to_json__() == other.__to_json__()
        )
