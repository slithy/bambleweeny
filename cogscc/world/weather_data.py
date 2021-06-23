from recordtype import recordtype


class GHWeatherData:

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
                ["volcano", "rain forest downpour", "quicksand", "earthquake"],
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

    PrecipitationData = recordtype(
        "PrecipitationData",
        [
            ("T", [float("-inf"), float("inf")]),  # min, max
            ("continuing", 0),
            ("rainbow", 0),
            ("amount", "0"),
            (
                "duration",
                ["0", 1.0],
            ),  # [roll, multiplier (because roll() returns an integer and not float]
            ("windSpeed", "1d20-1"),
            ("area", "0"),
            ########## the rest is static ###############
            ("movementSpeed", ["normal", "normal", "normal"]),  # foot, horse, cart
            ("normalVisionRange", "normal"),
            ("ultraAndInfraVisionRange", "normal"),
            ("tracking", "normal"),
            ("gettingLost", "normal"),
            ("special", ""),
            ("forbiddenTerrain", []),
            ("doubleDurationTerrain", []),
        ],
    )
    _precipitationData = {
        "no precipitation": PrecipitationData(),
        "sand storm": PrecipitationData(
            continuing=1,
            duration=["1d8", 24],
            windSpeed="5d10",
            movementSpeed=["no", "no", "no"],
            normalVisionRange="no",
            ultraAndInfraVisionRange="No",
            tracking="No",
            gettingLost="+80%",
            special="50% chance of d4 damage every 3 turns, no saving throw, until shelter is found",
        ),
        "dust storm": PrecipitationData(
            continuing=1,
            duration=["1d8", 24],
            windSpeed="5d10",
            movementSpeed=["no", "no", "no"],
            normalVisionRange="no",
            ultraAndInfraVisionRange="No",
            tracking="No",
            gettingLost="+80%",
            special="50% chance of d4 damage every 3 turns, no saving throw, until shelter is found",
        ),
        "wind storm": PrecipitationData(
            continuing=1,
            duration=["1d10", 24],
            windSpeed="8d10+20",
            movementSpeed=["50%", "50%", "50%"],
            normalVisionRange="50%",
            ultraAndInfraVisionRange="75%",
            tracking="No",
            gettingLost="+30%",
            special="50% chance of 2d6 rock damage every 3 turns. (Characters must roll dexterity to "
            "save for half damage; monsters must save vs. petrification.)",
        ),
        "earthquake": PrecipitationData(
            continuing=1,
            duration=["1d10", 24],
            movementSpeed=["25%", "25%", "no (may be overturned)"],
            tracking="-50%",
            gettingLost="+10% (+30% on horse)",
            special="Center is 1-100 miles away from party, with shock waves extending 1-100 miles. The first shock "
            "wave of the earthquake will be preceded by 1-4 mild tremors, which do no damage but cause "
            "untrained horses, cattle, and other animals to bolt in fear and run for open ground. After a "
            "delay of 1-6 rounds, the first shock wave reaches the party, and there are 1-6 shock waves in an earthquake. Roll d20 to determine the number of rounds between each of the shock waves. Each shock wave causes damage as the 7th level cleric spell Earthquake. If undersea, a tsunami occurs in 1d10 hours",
        ),
        "rock avalanche": PrecipitationData(
            amount="5d10",
            continuing=1,
            duration=["1d10", 24 * 60],
            movementSpeed=["may be blocked", "may be blocked", "may be blocked"],
            tracking="-60%",
            gettingLost="+10% (if trail is covered)",
            special="Damage is 2d20 pts., with save (vs. dexterity or petrification, as for wind storm) for half "
            "damage. Victims taking more than 20 points of damage are buried and will suffocate in 6 rounds unless rescued.",
        ),
        "snow avalanche": PrecipitationData(
            amount="5d10",
            continuing=1,
            duration=["1d10", 24 * 60],
            movementSpeed=["may be blocked", "may be blocked", "may be blocked"],
            tracking="-60%",
            gettingLost="+10% (if trail is covered)",
            special="Damage is 2d20 pts., with save (vs. dexterity or petrification, as for wind storm) for half "
            "damage. Victims taking more than 20 points of damage are buried and will suffocate in 6 rounds unless rescued.",
        ),
        "volcano": PrecipitationData(
            continuing=1,
            amount="1d8 [ashes per day]",
            duration=["1d10", 1],
            movementSpeed=["50%", "50%", "50%"],
            normalVisionRange="75% (50% if undersea due to mist)",
            ultraAndInfraVisionRange="50%",
            tracking="-50%",
            gettingLost="+20% (40% on horse)",
            special="Ash burns: d4 damage every 3 turns, no save. Location: 0-7 (d8-1) miles from party. Lava flows "
            "at d10 mph, does damage as a salamander’s tail. For every day a volcano continues to erupt, "
            "the base temperature will rise 1 degree F in a 60-mile-diameter area. This overheating will "
            "lapse after 7-12 months, as particles of ash in the air bring the temperature back down, "
            "but the chance of clear skies in the area will be cut by 50% for an additional 1-6 months "
            "thereafter. If undersea, an island will be formed after 2d6 days",
        ),
        "tsunami": PrecipitationData(
            continuing=1,
            amount="10d20 [ht. feet]",
            duration=["1d2", 24],
            windSpeed="5d10+10",
            tracking="No",
            special="Save vs. dexterity/petrification or drown. If save is made, victim takes 1d20 "
            "damage.",
        ),
        "quicksand": PrecipitationData(
            continuing=1,
            area="1d20 [feet]",
            duration=["1 [permanent]"],
            movementSpeed=[
                "normal (until entered)",
                "normal (until entered)",
                "normal (until entered)",
            ],
            tracking="No",
            gettingLost="+20% if skirted",
            special="An individual wearing no armor, leather armor, studded armor, elven chain, or magical armor will only sink up to the neck if he remains motionless, keeps his arms above the surface, and discards all heavy items. Other characters will be dragged under at the rate of 1 foot per round if motionless or 2 feet per round if attempting to escape. Drowning occurs 3 rounds after the head is submerged. If a victim is rescued after his head has been submerged, assess damage of d6 per round of submersion once character is resuscitated.",
        ),
        "flash flood": PrecipitationData(
            continuing=1,
            duration=["1d6+2", 24],
            movementSpeed=["75%", "75%", "75%"],
            tracking="-5%/turn",
            gettingLost="+10%",
            special="A flash flood will begin with what appears to be a heavy rainstorm, with appropriate effects, "
            "during which 3 inches of rain will fall each hour. The rain will stop when 50% of the flood’s "
            "duration is over, at which point all low areas will be covered with running water to a depth "
            "which is triple the amount of rainfall. This water will remain for 6-10 turns, and then disappear at a rate of 3 inches per hour. The current will vary from 5-50 mph, increasing when water flows in narrow gullies.",
        ),
        "rain forest downpour": PrecipitationData(
            continuing=1,
            amount="1 [per hour]",
            duration=["3d4", 24],
            movementSpeed=["50%", "50%", "no"],
            normalVisionRange="75%",
            ultraAndInfraVisionRange="75%",
            tracking="-5%/turn",
            gettingLost="+20%",
            windSpeed="1d6-1",
            special="The ground will absorb up to 6 inches of water; then mud will form, converting the area to a swamp for travel purposes.",
        ),
        "sun shower": PrecipitationData(
            continuing=1,
            amount=["1", 2],
            duration=["5+1d51", 24 * 60],
            rainbow=95,
        ),
        "tornado": PrecipitationData(
            continuing=1,
            amount="1 [per hour]",
            duration=["4+1d41", 24],
            movementSpeed=["no", "no", "no"],
            normalVisionRange="75%",
            ultraAndInfraVisionRange="75%",
            tracking="no",
            gettingLost="+40%",
            windSpeed="300",
            special="10% chance party will be transported to the Ethereal Plane. Otherwise, treat as a "
            "triple-strength hurricane for damage.",
        ),
        "cyclone": PrecipitationData(
            continuing=1,
            amount="1 [per hour]",
            duration=["4+1d41", 24],
            movementSpeed=["no", "no", "no"],
            normalVisionRange="75%",
            ultraAndInfraVisionRange="75%",
            tracking="no",
            gettingLost="+40%",
            windSpeed="300",
            special="10% chance party will be transported to the Ethereal Plane. Otherwise, treat as a "
            "triple-strength hurricane for damage.",
        ),
        "oasis": PrecipitationData(
            continuing=1,
            area=["2+1d4 [feet]", 1],
            duration=["1 [permanent]", 1],
            special="roll 1d20. A result of 1 or 2 indicates that the oasis is currently populated (determine "
            "population type via the Wilderness Encounter Charts in the DMG), while a 20 indicates that the last visitor has poisoned all the wells.",
        ),
        "mirage oasis": PrecipitationData(
            continuing=1,
            area=["2+1d4 [feet]", 1],
            duration=["1 [permanent]", 1],
            special="anyone who “drinks” must save vs. spell or take 1d6 damage from swallowed sand.",
        ),
        "heavy blizzard": PrecipitationData(
            T=[float("-inf"), 10],
            continuing=5,
            amount="2d10+10",
            duration=["3d8", 24],
            windSpeed="6d8+40",
            movementSpeed=["12.5%", "25%", "no"],
            normalVisionRange="2' radius",
            ultraAndInfraVisionRange="No",
            tracking="No",
            gettingLost="+50%",
            special="snowdrift up to 10'/h may accumulate on walls",
            forbiddenTerrain=["desert"],
        ),
        "blizzard": PrecipitationData(
            T=[float("-inf"), 20],
            continuing=10,
            amount="2d8+8",
            duration=["3d10", 24],
            windSpeed="3d8+36",
            movementSpeed=["25%", "25%", "25%"],
            normalVisionRange="10' radius",
            ultraAndInfraVisionRange="50%",
            tracking="+40%",
            gettingLost="+35%",
            special="snowdrift up to 5'/h may accumulate on walls",
            forbiddenTerrain=["desert"],
        ),
        "heavy snowstorm": PrecipitationData(
            T=[float("-inf"), 25],
            continuing=20,
            amount="2d8+2",
            duration=["4d6", 24],
            windSpeed="3d10",
            movementSpeed=["50%", "50%", "50%"],
            normalVisionRange="50%",
            ultraAndInfraVisionRange="50%",
            tracking="-25%",
            gettingLost="+20%",
            special="drifts of 1'/h if wind speed > 20 mph",
        ),
        "light snowstorm": PrecipitationData(
            T=[float("-inf"), 35],
            continuing=25,
            rainbow=1,
            amount="1d8",
            duration=["2d6", 24],
            windSpeed="4d6",
            movementSpeed=["75%", "normal", "normal"],
            normalVisionRange="75%",
            ultraAndInfraVisionRange="75%",
            tracking="-10%",
            gettingLost="+10%",
            special="drifts of 1'/h if wind speed > 20 mph",
        ),
        "sleet storm": PrecipitationData(
            T=[float("-inf"), 35],
            continuing=20,
            amount="1d2",
            duration=["1d6", 24],
            windSpeed="3d10",
            movementSpeed=["75%", "50%", "50%"],
            normalVisionRange="75%",
            ultraAndInfraVisionRange="75%",
            tracking="-10%",
            gettingLost="+5%",
        ),
        "hailstorm": PrecipitationData(
            T=[float("-inf"), 65],
            continuing=10,
            duration=["1d4", 24],
            windSpeed="4d10",
            movementSpeed=["75%", "75%", "75%"],
            tracking="-10%",
            gettingLost="+10%",
            special="diameter: 1d2'. If higher than 1' assess 1 dmg/0.5' every turn for people with AC < 6. No "
            "protection from ring, bracers. Only magic armor",
            forbiddenTerrain=["desert", "dust"],
        ),
        "heavy fog": PrecipitationData(
            T=[20, 60],
            continuing=25,
            rainbow=1,
            duration=["1d12", 24],
            windSpeed="1d20",
            movementSpeed=["25%", "25%", "25%"],
            normalVisionRange="2' radius",
            ultraAndInfraVisionRange="50%",
            tracking="-60%",
            gettingLost="+50%",
            forbiddenTerrain=["desert", "dust"],
            doubleDurationTerrain=[
                "cold seacoast",
                "hot seacoast",
                "cold sea",
                "hot sea",
            ],
        ),
        "light fog": PrecipitationData(
            T=[30, float("inf")],
            continuing=30,
            rainbow=3,
            duration=["2d4", 24],
            windSpeed="1d10",
            movementSpeed=["50%", "50%", "50%"],
            normalVisionRange="25%",
            ultraAndInfraVisionRange="75%",
            tracking="-30%",
            gettingLost="+30%",
            forbiddenTerrain=["desert"],
            doubleDurationTerrain=[
                "cold seacoast",
                "hot seacoast",
                "cold sea",
                "hot sea",
            ],
        ),
        "mist": PrecipitationData(
            T=[30, float("inf")],
            continuing=15,
            rainbow=10,
            duration=["2d6", 24],
            windSpeed="1d10",
            tracking="-5%",
            doubleDurationTerrain=[
                "cold seacoast",
                "hot seacoast",
                "cold sea",
                "hot sea",
            ],
        ),
        "dirzzle": PrecipitationData(
            T=[25, float("inf")],
            continuing=20,
            rainbow=5,
            amount="1",
            duration=["1d10", 24],
            windSpeed="1d20",
            tracking="-1%/turn",
        ),
        "light rainstorm": PrecipitationData(
            T=[25, float("inf")],
            continuing=45,
            rainbow=15,
            amount="1d3",
            duration=["1d12", 24],
            windSpeed="1d20",
            tracking="-10%/turn",
            special="a drop in temperature to 30 F (~ 0 C) or less after such storm may result in icy ground",
        ),
        "heavy rainstorm": PrecipitationData(
            T=[25, float("inf")],
            continuing=30,
            rainbow=20,
            amount="1d4+3",
            duration=["1d12", 24],
            windSpeed="2d12+10",
            movementSpeed=["75%", "normal", "75%"],
            normalVisionRange="75%",
            ultraAndInfraVisionRange="75%",
            tracking="-10%/turn",
            gettingLost="+10%",
            special="a drop in temperature to 30 F (~ 0 C) or less after such storm may result in icy ground",
        ),
        "thunderstorm": PrecipitationData(
            T=[30, float("inf")],
            continuing=15,
            rainbow=20,
            amount="1d8",
            duration=["1d4", 24],
            windSpeed="4d10",
            movementSpeed=["50%", "50%", "50%"],
            normalVisionRange="75%",
            ultraAndInfraVisionRange="75%",
            tracking="-10%/turn",
            gettingLost="+10% (+30% if horsed)",
            special="1 lighting stroke/10 mins. 1% probability that the party is hit. 10% if the party shelters under trees. Dmg: 6d6 with saving throw for half dmg",
        ),
        "tropical storm": PrecipitationData(
            T=[40, float("inf")],
            continuing=20,
            rainbow=10,
            amount="1d6 [per day]",
            duration=["1d3", 1.0],
            windSpeed="3d12+30",
            movementSpeed=["25%", "25%", "no"],
            normalVisionRange="50%",
            ultraAndInfraVisionRange="50%",
            tracking="no",
            gettingLost="+30%",
            special="10% gust damage/3 turns if wind speed > 40 mph. Dmg: 1d6 for every full 10 mph above 40 mph",
            forbiddenTerrain=["desert", "plains"],
        ),
        "monsoon": PrecipitationData(
            T=[55, float("inf")],
            continuing=30,
            rainbow=5,
            amount="1d8 [per day]",
            duration=["1d6+6", 1.0],
            windSpeed="6d10",
            movementSpeed=["25%", "25%", "no"],
            normalVisionRange="25%",
            ultraAndInfraVisionRange="25%",
            tracking="no",
            gettingLost="+30%",
            special="10% gust damage/3 turns if wind speed > 40 mph. Dmg: 1d6 for every full 10 mph above 40 mph",
            forbiddenTerrain=["desert", "dust", "plains"],
        ),
        "gale": PrecipitationData(
            T=[40, float("inf")],
            continuing=15,
            rainbow=10,
            amount="1d8 [per day]",
            duration=["1d3", 1.0],
            windSpeed="6d8+40",
            movementSpeed=["25%", "25%", "no"],
            normalVisionRange="25%",
            ultraAndInfraVisionRange="25%",
            tracking="no",
            gettingLost="+20%",
            special="10% gust dmg/3 turns if wind speed > 40 mph. Dmg: 1d6 for every full 10 mph above 40 mph",
            forbiddenTerrain=["desert"],
        ),
        "hurricane or typhoon": PrecipitationData(
            T=[55, float("inf")],
            continuing=30,
            rainbow=5,
            amount="1d10 [per day]",
            duration=["1d4", 1.0],
            windSpeed="7d10+70",
            movementSpeed=["25%", "25%", "no"],
            normalVisionRange="25%",
            ultraAndInfraVisionRange="25%",
            tracking="no",
            gettingLost="+30%",
            special="1d6 wind dmg/3 turns to unprotected creatures. 1d4 structural dmg/turn to buildings",
            forbiddenTerrain=["desert", "dust"],
        ),
    }
    # base Temperature -20 -15 -10 -5 0 5 10 15 20 25 30 35
    _windChillData = [
        [-20, -15, -10, -5, 0, 5, 10, 15, 20, 25, 30, 35],  # 0 mph
        [-28, -22, -15, -11, -6, 1, 7, 12, 16, 21, 27, 33],  # 5 mph
        [-43, -37, -31, -27, -22, -15, -9, -2, 2, 9, 16, 21],  # 10 mph
        [-58, -51, -45, -40, -33, -25, -18, -11, -6, 1, 11, 16],  # 15 mph
        [-64, -58, -52, -46, -40, -32, -24, -17, -9, -4, 3, 12],  # 20 mph
        [-72, -65, -58, -52, -45, -37, -29, -22, -15, -7, 0, 7],  # 25 mph
        [-78, -70, -63, -56, -49, -41, -33, -26, -18, -11, -2, 5],  # 30 mph
        [-82, -75, -67, -60, -52, -43, -35, -27, -20, -13, -4, 3],  # 35 mph
        [-83, -76, -69, -62, -54, 45, -36, -29, -22, -13, -4, 1],  # 40 mph
        [-84, -77, -70, -63, -55, 46, -38, -31, -24, -15, -4, 1],  # 45 mph
        [-85, -78, -71, -64, -56, 47, -38, -31, -24, -17, -7, 0],  # 50 mph
        [-86, -79, -72, -65, -57, -48, -39, -33, -25, -19, -8, -1],  # 55 mph
        [-87, -80, -73, -66, -58, -49, -40, -34, -27, -21, -10, -3],  # 60 mph
    ]
    MonthData = recordtype("MonthData", "T sky precipitation sunriseAndSunset")
    _monthData = {
        "needfest": MonthData(
            [32.5, "-1d20", "1d10+2"], [24, 50, 100], 44, ["7:20", "17:48"]
        ),
        "fireseek": MonthData([32, "-1d20", "1d10"], [23, 50], 46, ["7:21", "17:01"]),
        "readying": MonthData(
            [34, "-1d10-4", "1d6+4"], [25, 50], 40, ["6:55", "17:36"]
        ),
        "coldeven": MonthData(
            [42, "-1d10-4", "1d8+4"], [27, 54], 44, ["6:12", "18:09"]
        ),
        "growfest": MonthData([47, "-1d9-4", "1d9+5"], [23, 54], 43, ["5:48", "18:24"]),
        "planting": MonthData(
            [52, "-1d8-4", "1d10+6"], [20, 55], 42, ["5:24", "18:39"]
        ),
        "flocktime": MonthData(
            [63, "-1d10-6", "1d10+6"], [20, 53], 42, ["4:45", "19:10"]
        ),
        "wealsun": MonthData([71, "-1d6-6", "1d8+8"], [20, 60], 36, ["4:32", "19:32"]),
        "richfest": MonthData([74, "-1d6-6", "1d7+6"], [21, 61], 34, ["4:38", "19:30"]),
        "reaping": MonthData([77, "-1d6-6", "1d6+4"], [22, 62], 33, ["4:45", "19:29"]),
        "goodmonth": MonthData(
            [75, "-1d6-6", "1d4+6"], [25, 60], 33, ["5:13", "18:57"]
        ),
        "harvester": MonthData(
            [68, "-1d8-6", "1d8+6"], [33, 55], 33, ["5:42", "18:10"]
        ),
        "brewfest": MonthData(
            [62, "-1d10-5", "1d10+5"], [34, 57], 34, ["5:57", "17:45"]
        ),
        "patchwall": MonthData(
            [57, "-1d10-5", "1d10+5"], [35, 60], 36, ["6:12", "17:21"]
        ),
        "ready'reat": MonthData(
            [46, "-1d10-4", "1d10+6"], [20, 50], 40, ["6:46", "16:45"]
        ),
        "sunsebb": MonthData([33, "-1d20", "1d8+5"], [25, 50], 43, ["7:19", "16:36"]),
    }
