from recordtype import recordtype

from cogscc.models.errors import InvalidArgument

from cogscc.base_obj import BaseObj
from cogscc.world.weather_data import GHWeatherData
from cogscc.world.weather import GHWeather


class GHLocation(BaseObj):
    def __init__(
        self, name="new place", terrain="plains", latitude=40, altitude=0, weather={}
    ):

        self.name = name
        self.terrain = ""
        self.set_terrain(terrain)
        self.latitude = latitude
        self.altitude = altitude
        self.weather = (
            GHWeather.__from_dict__(weather) if isinstance(weather, dict) else weather
        )

    def __str__(self):
        return (
            f"location: `{self.name}`, terrain: {self.terrain}, latitude: {self.latitude}, altitude (feet): "
            f"{self.altitude}"
        )

    def set_terrain(self, terrain):
        if terrain in GHWeatherData.terrain_data:
            self.terrain = terrain
        else:
            ter = ", ".join([i for i in GHWeatherData.terrain_data])
            raise InvalidArgument(
                f"I do not recognize the terrain: {terrain}\nAvailable terrains: {ter}"
            )

    def reset_weather(self, day):
        self.weather = GHWeather()
        self.generate_weather(day)
        return f"Weather reset successfully"

    def generate_weather(self, day):
        self.weather.generate_weather(day, self)
        return f"Weather generated succesfully"
