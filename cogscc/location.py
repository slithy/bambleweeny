from recordtype import recordtype

from cogscc.models.errors import InvalidArgument

from cogscc.base_obj import BaseObj


class GHLocation(BaseObj):
    def __init__(self, name="new place", terrain="plains", latitude=40, altitude=0):
        self.name = name
        self.terrain = ""
        self.set_terrain(terrain)
        self.latitude = latitude
        self.altitude = altitude

    def __str__(self):
        return (
            f"location: `{self.name}`, terrain: {self.terrain}, latitude: {self.latitude}, altitude (feet): "
            f"{self.altitude}"
        )

    def set_terrain(self, terrain):
        if terrain in self._terrainData:
            self.terrain = terrain
        else:
            ter = ", ".join([i for i in self._terrainData])
            raise InvalidArgument(
                f"I do not recognize the terrain: {terrain}\nAvailable terrains: {ter}"
            )

    TerrainData = recordtype(
        "TerrainData",
        [
            ("precipitation", 0),
            ("T", lambda elevation: [-int(0.003 * elevation), -int(0.003 * elevation)]),
            ("windSpeed", 0),
            ("special", [[], []]),
        ],
    )
    _terrainData = _terrainData = {
        "rough": TerrainData(
            windSpeed=5, special=[[80, 100], ["windstorm", "earthquake"]]
        ),
        "hill": TerrainData(
            windSpeed=-5, special=[[80, 100], ["windstorm", "earthquake"]]
        ),
        "forest": TerrainData(
            T=lambda elevation: [
                -5 - int(0.003 * elevation),
                -5 - int(0.003 * elevation),
            ],
            windSpeed=-5,
            special=[[80, 100], ["quicksand", "earthquake"]],
        ),
        "jungle": TerrainData(
            precipitation=10,
            T=lambda elevation: [
                5 - int(0.003 * elevation),
                5 - int(0.003 * elevation),
            ],
            windSpeed=-10,
            special=[
                [5, 60, 80, 100],
                ["volcano", "Rain Forest Downpour", "quicksand", "earthquake"],
            ],
        ),
        "swamp": TerrainData(
            precipitation=5,
            T=lambda elevation: [
                5 - int(0.003 * elevation),
                5 - int(0.003 * elevation),
            ],
            windSpeed=-5,
            special=[[25, 80, 100], ["quicksand", "sun shower", "earthquake"]],
        ),
        "hot marsh": TerrainData(
            precipitation=5,
            T=lambda elevation: [
                5 - int(0.003 * elevation),
                5 - int(0.003 * elevation),
            ],
            windSpeed=-5,
            special=[[25, 80, 100], ["quicksand", "sun shower", "earthquake"]],
        ),
        "cold marsh": TerrainData(
            precipitation=5,
            T=lambda elevation: [
                -5 - int(0.003 * elevation),
                -5 - int(0.003 * elevation),
            ],
            windSpeed=-5,
            special=[[25, 80, 100], ["quicksand", "sun shower", "earthquake"]],
        ),
        "dust": TerrainData(
            precipitation=-25,
            T=lambda elevation: [
                -10 - int(0.003 * elevation),
                10 - int(0.003 * elevation),
            ],
            special=[
                [40, 70, 85, 100],
                ["flash flood", "dust dtorm", "tornado", "earthquake"],
            ],
        ),
        "plains": TerrainData(
            windSpeed=5,
            special=[[50, 100], ["windstorm", "earthquake"]],
        ),
        "desert": TerrainData(
            precipitation=-30,
            T=lambda elevation: [
                -10 - int(0.003 * elevation),
                10 - int(0.003 * elevation),
            ],
            windSpeed=5,
            special=[
                [25, 50, 65, 85, 100],
                ["flash flood", "sandstorm", "oasis", "mirage oasis", "earthquake"],
            ],

        ),
        "mountain": TerrainData(
            windSpeed=5,
            special=[
                [20, 50, 75, 80, 100],
                [
                    "Wind Storm",
                    "rock avalanche",
                    "snow avalanche",
                    "volcano",
                    "earthquake",
                ],
            ],
        ),
        "cold seacoast": TerrainData(
            precipitation=5,
            T=lambda elevation: [
                -5 - int(0.003 * elevation),
                -5 - int(0.003 * elevation),
            ],
            windSpeed=5,
            special=[[80, 94, 100], ["earthquake", "tsunami", "undersea volcano"]],
        ),
        "hot seacoast": TerrainData(
            precipitation=5,
            T=lambda elevation: [
                5 - int(0.003 * elevation),
                5 - int(0.003 * elevation),
            ],
            windSpeed=5,
            special=[[80, 94, 100], ["earthquake", "tsunami", "undersea volcano"]],
        ),
        "cold sea": TerrainData(
            precipitation=15,
            T=lambda elevation: [
                -10 - int(0.003 * elevation),
                -10 - int(0.003 * elevation),
            ],
            windSpeed=10,
            special=[
                [20, 40, 100],
                ["tsunami", "undersea volcano", "undersea earthquake"],
            ],
        ),
        "hot sea": TerrainData(
            precipitation=15,
            T=lambda elevation: [
                5 - int(0.003 * elevation),
                5 - int(0.003 * elevation),
            ],
            windSpeed=10,
            special=[
                [20, 40, 100],
                ["tsunami", "undersea volcano", "undersea earthquake"],
            ],
        ),
    }
