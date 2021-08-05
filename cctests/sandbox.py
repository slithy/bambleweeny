import sys, os

rootpath = os.path.realpath(os.path.dirname(__file__) + "/..")
if rootpath not in sys.path:
    sys.path.append(rootpath)

import json
from cogscc.game import ToJson
from cogscc.world.world import GHWorld
from cogscc.world.calendar import GHCalendar
from cogscc.world.weather import GHWeather, GHWeatherReport
from cogscc.world.location import GHLocation

c = GHCalendar(364 / 2)
w = GHWorld()
l = GHLocation("home", "plains", 30, 200)
w.add_location(l)
w.advance_days(0)
for i in range(14):
    print(w.get_weather_report(i))
