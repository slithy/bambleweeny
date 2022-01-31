from recordtype import recordtype


class GHWeatherData:
    ExtremeTData = recordtype("ExtremeTData", "duration modifier")
    extreme_T_data = ExtremeTData(
        [[1, 3, 10, 14, 17, 19, 20], range(1, 8)],
        [[1, 2, 4, 96, 98, 99, 100], range(-3, 4)],
    )

    TerrainData = recordtype(
        "TerrainData",
        [
            ("precipitation", 0),
            ("T", lambda elevation: [-int(0.003 * elevation), -int(0.003 * elevation)]),
            ("wind_speed", 0),
            ("special", [[], []]),
        ],
    )
    terrain_data = {
        "rough": TerrainData(
            wind_speed=5, special=[[80, 100], ["windstorm", "earthquake"]]
        ),
        "hill": TerrainData(
            wind_speed=-5, special=[[80, 100], ["windstorm", "earthquake"]]
        ),
        "forest": TerrainData(
            T=lambda elevation: [
                -5 - int(0.003 * elevation),
                -5 - int(0.003 * elevation),
            ],
            wind_speed=-5,
            special=[[80, 100], ["quicksand", "earthquake"]],
        ),
        "jungle": TerrainData(
            precipitation=10,
            T=lambda elevation: [
                5 - int(0.003 * elevation),
                5 - int(0.003 * elevation),
            ],
            wind_speed=-10,
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
            wind_speed=-5,
            special=[[25, 80, 100], ["quicksand", "sun shower", "earthquake"]],
        ),
        "hot marsh": TerrainData(
            precipitation=5,
            T=lambda elevation: [
                5 - int(0.003 * elevation),
                5 - int(0.003 * elevation),
            ],
            wind_speed=-5,
            special=[[25, 80, 100], ["quicksand", "sun shower", "earthquake"]],
        ),
        "cold marsh": TerrainData(
            precipitation=5,
            T=lambda elevation: [
                -5 - int(0.003 * elevation),
                -5 - int(0.003 * elevation),
            ],
            wind_speed=-5,
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
            wind_speed=5,
            special=[[50, 100], ["windstorm", "earthquake"]],
        ),
        "desert": TerrainData(
            precipitation=-30,
            T=lambda elevation: [
                -10 - int(0.003 * elevation),
                10 - int(0.003 * elevation),
            ],
            wind_speed=5,
            special=[
                [25, 50, 65, 85, 100],
                ["flash flood", "sandstorm", "oasis", "mirage oasis", "earthquake"],
            ],
        ),
        "mountain": TerrainData(
            wind_speed=5,
            special=[
                [20, 50, 75, 80, 100],
                [
                    "windstorm",
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
            wind_speed=5,
            special=[[80, 94, 100], ["earthquake", "tsunami", "undersea volcano"]],
        ),
        "hot seacoast": TerrainData(
            precipitation=5,
            T=lambda elevation: [
                5 - int(0.003 * elevation),
                5 - int(0.003 * elevation),
            ],
            wind_speed=5,
            special=[[80, 94, 100], ["earthquake", "tsunami", "undersea volcano"]],
        ),
        "cold sea": TerrainData(
            precipitation=15,
            T=lambda elevation: [
                -10 - int(0.003 * elevation),
                -10 - int(0.003 * elevation),
            ],
            wind_speed=10,
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
            wind_speed=10,
            special=[
                [20, 40, 100],
                ["tsunami", "undersea volcano", "undersea earthquake"],
            ],
        ),
    }

    rainbow_data = [
        [89, 95, 98, 99, 100],
        [
            "single rainbow",
            "double rainbow (may be an omen)",
            "triple rainbow (" "almost cerainly an " "omen)",
            "bifrost bridge or coulds in the shape of rain deity",
            "rain deity or servant in the sky",
        ],
    ]

    precipitation_occurrence_data = [
        [2, 5, 10, 20, 25, 27, 30, 38, 40, 45, 60, 70, 84, 89, 94, 97, 99, 100],
        [
            "heavy blizzard",
            "blizzard",
            "heavy snowstorm",
            "light snowstorm",
            "sleet storm",
            "hailstorm",
            "heavy fog",
            "light fog",
            "mist",
            "dirzzle",
            "light rainstorm",
            "heavy rainstorm",
            "thunderstorm",
            "tropical storm",
            "monsoon",
            "gale",
            "hurricane or typhoon",
            "special",
        ],
    ]

    wind_speed_data = [
        [29, 44, 59, 74, float("inf")],
        [
            "normal wind",
            "strong wind",
            "very strong wind",
            "extremely strong wind",
            "tornado-like wind",
        ],
    ]
    WindSpeedTableData = recordtype(
        "WindSpeedTableData", "land sea air battle", default=""
    )
    wind_speed_table_data = {
        "normal wind": WindSpeedTableData(),
        "strong wind": WindSpeedTableData(
            land="All travel slowed by 25%; torches will be blown out",
            sea="Sailing difficult; rowing impossible",
            air="Creatures eagle-size and below can’t fly",
            battle="Missiles at half range and -1 to hit",
        ),
        "very strong wind": WindSpeedTableData(
            land="All travel slowed by 50%; torches and small fires will be blown out",
            sea="Minor ship damage (d4 structural points) may occur; wave ht. 3d6 ft",
            air="Man-sized creatures cannot fly",
            battle="Missiles at half range and -3 to hit",
        ),
        "extremely strong wind": WindSpeedTableData(
            land="Small trees are uprooted; all travel slowed by 75%; roofs may be torn off",
            sea="Ships are endangered (d10 structural damage) and blown off course; wave ht. d10+20 ft",
            air="No creatures can fly, except those from the Elemental Plane of Air",
            battle="No missile fire permitted; all non-magical weapon attacks are -1 to hit; dexterity bonuses to AC "
            "cancelled",
        ),
        "tornado-like wind": WindSpeedTableData(
            land="Only strong stone buildings will be undamaged; travel is impossible",
            sea="Ships are capsized and sunk; wave ht. d20+20 ft. or more",
            air="No creatures can fly, except those from the Elemental Plane of Air",
            battle="No missile fire permitted; all non-magical weapon attacks at -3 to hit; 20% chance per attack "
            "that any weapon will be tor from the wielder’s grip by the wind; dexterity bonuses to AC cancelled",
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
            ("wind_speed", "1d20-1"),
            ("area", "0"),
            ########## the rest is static ###############
            ("movement_speed", ["normal", "normal", "normal"]),  # foot, horse, cart
            ("normal_vision_range", "normal"),
            ("ultra_and_infra_vision_range", "normal"),
            ("tracking", "normal"),
            ("getting_lost", "normal"),
            ("add_info", ""),
            ("forbidden_terrain", []),
            ("double_duration_terrain", []),
        ],
    )
    precipitation_data = {
        "no precipitation": PrecipitationData(),
        "sandstorm": PrecipitationData(
            continuing=1,
            duration=["1d8", 24],
            wind_speed="5d10",
            movement_speed=["no", "no", "no"],
            normal_vision_range="no",
            ultra_and_infra_vision_range="No",
            tracking="No",
            getting_lost="+80%",
            add_info="50% chance of d4 damage every 3 turns, no saving throw, until shelter is found",
        ),
        "dust storm": PrecipitationData(
            continuing=1,
            duration=["1d8", 24],
            wind_speed="5d10",
            movement_speed=["no", "no", "no"],
            normal_vision_range="no",
            ultra_and_infra_vision_range="No",
            tracking="No",
            getting_lost="+80%",
            add_info="50% chance of d4 damage every 3 turns, no saving throw, until shelter is found",
        ),
        "windstorm": PrecipitationData(
            continuing=1,
            duration=["1d10", 24],
            wind_speed="8d10+20",
            movement_speed=["50%", "50%", "50%"],
            normal_vision_range="50%",
            ultra_and_infra_vision_range="75%",
            tracking="No",
            getting_lost="+30%",
            add_info="50% chance of 2d6 rock damage every 3 turns. (Characters must roll dexterity to "
            "save for half damage; monsters must save vs. petrification.)",
        ),
        "earthquake": PrecipitationData(
            continuing=1,
            duration=["1d10", 24],
            movement_speed=["25%", "25%", "no (may be overturned)"],
            tracking="-50%",
            getting_lost="+10% (+30% on horse)",
            add_info="Center is 1-100 miles away from party, with shock waves extending 1-100 miles. The first shock "
            "wave of the earthquake will be preceded by 1-4 mild tremors, which do no damage but cause "
            "untrained horses, cattle, and other animals to bolt in fear and run for open ground. After a "
            "delay of 1-6 rounds, the first shock wave reaches the party, and there are 1-6 shock waves in an earthquake. Roll d20 to determine the number of rounds between each of the shock waves. Each shock wave causes damage as the 7th level cleric spell Earthquake. If undersea, a tsunami occurs in 1d10 hours",
        ),
        "rock avalanche": PrecipitationData(
            amount="5d10",
            continuing=1,
            duration=["1d10", 24 * 60],
            movement_speed=["may be blocked", "may be blocked", "may be blocked"],
            tracking="-60%",
            getting_lost="+10% (if trail is covered)",
            add_info="Damage is 2d20 pts., with save (vs. dexterity or petrification, as for windstorm) for half "
            "damage. Victims taking more than 20 points of damage are buried and will suffocate in 6 rounds unless rescued.",
        ),
        "snow avalanche": PrecipitationData(
            amount="5d10",
            continuing=1,
            duration=["1d10", 24 * 60],
            movement_speed=["may be blocked", "may be blocked", "may be blocked"],
            tracking="-60%",
            getting_lost="+10% (if trail is covered)",
            add_info="Damage is 2d20 pts., with save (vs. dexterity or petrification, as for windstorm) for half "
            "damage. Victims taking more than 20 points of damage are buried and will suffocate in 6 rounds unless rescued.",
        ),
        "volcano": PrecipitationData(
            continuing=1,
            amount="1d8 [ashes per day]",
            duration=["1d10", 1],
            movement_speed=["50%", "50%", "50%"],
            normal_vision_range="75% (50% if undersea due to mist)",
            ultra_and_infra_vision_range="50%",
            tracking="-50%",
            getting_lost="+20% (40% on horse)",
            add_info="Ash burns: d4 damage every 3 turns, no save. Location: 0-7 (d8-1) miles from party. Lava flows "
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
            wind_speed="5d10+10",
            tracking="No",
            add_info="Save vs. dexterity/petrification or drown. If save is made, victim takes 1d20 "
            "damage.",
        ),
        "quicksand": PrecipitationData(
            continuing=1,
            area="1d20 [feet]",
            duration=["1 [permanent]", 1],
            movement_speed=[
                "normal (until entered)",
                "normal (until entered)",
                "normal (until entered)",
            ],
            tracking="No",
            getting_lost="+20% if skirted",
            add_info="An individual wearing no armor, leather armor, studded armor, elven chain, or magical armor will only sink up to the neck if he remains motionless, keeps his arms above the surface, and discards all heavy items. Other characters will be dragged under at the rate of 1 foot per round if motionless or 2 feet per round if attempting to escape. Drowning occurs 3 rounds after the head is submerged. If a victim is rescued after his head has been submerged, assess damage of d6 per round of submersion once character is resuscitated.",
        ),
        "flash flood": PrecipitationData(
            continuing=1,
            duration=["1d6+2", 24],
            movement_speed=["75%", "75%", "75%"],
            tracking="-5%/turn",
            getting_lost="+10%",
            add_info="A flash flood will begin with what appears to be a heavy rainstorm, with appropriate effects, "
            "during which 3 inches of rain will fall each hour. The rain will stop when 50% of the flood’s "
            "duration is over, at which point all low areas will be covered with running water to a depth "
            "which is triple the amount of rainfall. This water will remain for 6-10 turns, and then disappear at a rate of 3 inches per hour. The current will vary from 5-50 mph, increasing when water flows in narrow gullies.",
        ),
        "rain forest downpour": PrecipitationData(
            continuing=1,
            amount="1 [per hour]",
            duration=["3d4", 24],
            movement_speed=["50%", "50%", "no"],
            normal_vision_range="75%",
            ultra_and_infra_vision_range="75%",
            tracking="-5%/turn",
            getting_lost="+20%",
            wind_speed="1d6-1",
            add_info="The ground will absorb up to 6 inches of water; then mud will form, converting the area to a swamp for travel purposes.",
        ),
        "sun shower": PrecipitationData(
            continuing=1,
            amount="1",
            duration=["5+1d51", 24 * 60],
            rainbow=95,
        ),
        "tornado": PrecipitationData(
            continuing=1,
            amount="1 [per hour]",
            duration=["4+1d41", 24],
            movement_speed=["no", "no", "no"],
            normal_vision_range="75%",
            ultra_and_infra_vision_range="75%",
            tracking="no",
            getting_lost="+40%",
            wind_speed="300",
            add_info="10% chance party will be transported to the Ethereal Plane. Otherwise, treat as a "
            "triple-strength hurricane for damage.",
        ),
        "cyclone": PrecipitationData(
            continuing=1,
            amount="1 [per hour]",
            duration=["4+1d41", 24],
            movement_speed=["no", "no", "no"],
            normal_vision_range="75%",
            ultra_and_infra_vision_range="75%",
            tracking="no",
            getting_lost="+40%",
            wind_speed="300",
            add_info="10% chance party will be transported to the Ethereal Plane. Otherwise, treat as a "
            "triple-strength hurricane for damage.",
        ),
        "oasis": PrecipitationData(
            continuing=1,
            area="2+1d4 [feet]",
            duration=["1 [permanent]", 1],
            add_info="roll 1d20. A result of 1 or 2 indicates that the oasis is currently populated (determine "
            "population type via the Wilderness Encounter Charts in the DMG), while a 20 indicates that the last visitor has poisoned all the wells.",
        ),
        "mirage oasis": PrecipitationData(
            continuing=1,
            area="2+1d4 [feet]",
            duration=["1 [permanent]", 1],
            add_info="anyone who “drinks” must save vs. spell or take 1d6 damage from swallowed sand.",
        ),
        "heavy blizzard": PrecipitationData(
            T=[float("-inf"), 10],
            continuing=5,
            amount="2d10+10",
            duration=["3d8", 24],
            wind_speed="6d8+40",
            movement_speed=["12.5%", "25%", "no"],
            normal_vision_range="2' radius",
            ultra_and_infra_vision_range="No",
            tracking="No",
            getting_lost="+50%",
            add_info="snowdrift up to 10'/h may accumulate on walls",
            forbidden_terrain=["desert"],
        ),
        "blizzard": PrecipitationData(
            T=[float("-inf"), 20],
            continuing=10,
            amount="2d8+8",
            duration=["3d10", 24],
            wind_speed="3d8+36",
            movement_speed=["25%", "25%", "25%"],
            normal_vision_range="10' radius",
            ultra_and_infra_vision_range="50%",
            tracking="+40%",
            getting_lost="+35%",
            add_info="snowdrift up to 5'/h may accumulate on walls",
            forbidden_terrain=["desert"],
        ),
        "heavy snowstorm": PrecipitationData(
            T=[float("-inf"), 25],
            continuing=20,
            amount="2d8+2",
            duration=["4d6", 24],
            wind_speed="3d10",
            movement_speed=["50%", "50%", "50%"],
            normal_vision_range="50%",
            ultra_and_infra_vision_range="50%",
            tracking="-25%",
            getting_lost="+20%",
            add_info="drifts of 1'/h if wind speed > 20 mph",
        ),
        "light snowstorm": PrecipitationData(
            T=[float("-inf"), 35],
            continuing=25,
            rainbow=1,
            amount="1d8",
            duration=["2d6", 24],
            wind_speed="4d6",
            movement_speed=["75%", "normal", "normal"],
            normal_vision_range="75%",
            ultra_and_infra_vision_range="75%",
            tracking="-10%",
            getting_lost="+10%",
            add_info="drifts of 1'/h if wind speed > 20 mph",
        ),
        "sleet storm": PrecipitationData(
            T=[float("-inf"), 35],
            continuing=20,
            amount="1d2",
            duration=["1d6", 24],
            wind_speed="3d10",
            movement_speed=["75%", "50%", "50%"],
            normal_vision_range="75%",
            ultra_and_infra_vision_range="75%",
            tracking="-10%",
            getting_lost="+5%",
        ),
        "hailstorm": PrecipitationData(
            T=[float("-inf"), 65],
            continuing=10,
            duration=["1d4", 24],
            wind_speed="4d10",
            movement_speed=["75%", "75%", "75%"],
            tracking="-10%",
            getting_lost="+10%",
            add_info="diameter: 1d2'. If higher than 1' assess 1 dmg/0.5' every turn for people with AC < 6. No "
            "protection from ring, bracers. Only magic armor",
            forbidden_terrain=["desert", "dust"],
        ),
        "heavy fog": PrecipitationData(
            T=[20, 60],
            continuing=25,
            rainbow=1,
            duration=["1d12", 24],
            wind_speed="1d20",
            movement_speed=["25%", "25%", "25%"],
            normal_vision_range="2' radius",
            ultra_and_infra_vision_range="50%",
            tracking="-60%",
            getting_lost="+50%",
            forbidden_terrain=["desert", "dust"],
            double_duration_terrain=[
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
            wind_speed="1d10",
            movement_speed=["50%", "50%", "50%"],
            normal_vision_range="25%",
            ultra_and_infra_vision_range="75%",
            tracking="-30%",
            getting_lost="+30%",
            forbidden_terrain=["desert"],
            double_duration_terrain=[
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
            wind_speed="1d10",
            tracking="-5%",
            double_duration_terrain=[
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
            wind_speed="1d20",
            tracking="-1%/turn",
        ),
        "light rainstorm": PrecipitationData(
            T=[25, float("inf")],
            continuing=45,
            rainbow=15,
            amount="1d3",
            duration=["1d12", 24],
            wind_speed="1d20",
            tracking="-10%/turn",
            add_info="a drop in temperature to 30 F (~ 0 C) or less after such storm may result in icy ground",
        ),
        "heavy rainstorm": PrecipitationData(
            T=[25, float("inf")],
            continuing=30,
            rainbow=20,
            amount="1d4+3",
            duration=["1d12", 24],
            wind_speed="2d12+10",
            movement_speed=["75%", "normal", "75%"],
            normal_vision_range="75%",
            ultra_and_infra_vision_range="75%",
            tracking="-10%/turn",
            getting_lost="+10%",
            add_info="a drop in temperature to 30 F (~ 0 C) or less after such storm may result in icy ground",
        ),
        "thunderstorm": PrecipitationData(
            T=[30, float("inf")],
            continuing=15,
            rainbow=20,
            amount="1d8",
            duration=["1d4", 24],
            wind_speed="4d10",
            movement_speed=["50%", "50%", "50%"],
            normal_vision_range="75%",
            ultra_and_infra_vision_range="75%",
            tracking="-10%/turn",
            getting_lost="+10% (+30% if horsed)",
            add_info="1 lighting stroke/10 mins. 1% probability that the party is hit. 10% if the party shelters under trees. Dmg: 6d6 with saving throw for half dmg",
        ),
        "tropical storm": PrecipitationData(
            T=[40, float("inf")],
            continuing=20,
            rainbow=10,
            amount="1d6 [per day]",
            duration=["1d3", 1.0],
            wind_speed="3d12+30",
            movement_speed=["25%", "25%", "no"],
            normal_vision_range="50%",
            ultra_and_infra_vision_range="50%",
            tracking="no",
            getting_lost="+30%",
            add_info="10% gust damage/3 turns if wind speed > 40 mph. Dmg: 1d6 for every full 10 mph above 40 mph",
            forbidden_terrain=["desert", "plains"],
        ),
        "monsoon": PrecipitationData(
            T=[55, float("inf")],
            continuing=30,
            rainbow=5,
            amount="1d8 [per day]",
            duration=["1d6+6", 1.0],
            wind_speed="6d10",
            movement_speed=["25%", "25%", "no"],
            normal_vision_range="25%",
            ultra_and_infra_vision_range="25%",
            tracking="no",
            getting_lost="+30%",
            add_info="10% gust damage/3 turns if wind speed > 40 mph. Dmg: 1d6 for every full 10 mph above 40 mph",
            forbidden_terrain=["desert", "dust", "plains"],
        ),
        "gale": PrecipitationData(
            T=[40, float("inf")],
            continuing=15,
            rainbow=10,
            amount="1d8 [per day]",
            duration=["1d3", 1.0],
            wind_speed="6d8+40",
            movement_speed=["25%", "25%", "no"],
            normal_vision_range="25%",
            ultra_and_infra_vision_range="25%",
            tracking="no",
            getting_lost="+20%",
            add_info="10% gust dmg/3 turns if wind speed > 40 mph. Dmg: 1d6 for every full 10 mph above 40 mph",
            forbidden_terrain=["desert"],
        ),
        "hurricane or typhoon": PrecipitationData(
            T=[55, float("inf")],
            continuing=30,
            rainbow=5,
            amount="1d10 [per day]",
            duration=["1d4", 1.0],
            wind_speed="7d10+70",
            movement_speed=["25%", "25%", "no"],
            normal_vision_range="25%",
            ultra_and_infra_vision_range="25%",
            tracking="no",
            getting_lost="+30%",
            add_info="1d6 wind dmg/3 turns to unprotected creatures. 1d4 structural dmg/turn to buildings",
            forbidden_terrain=["desert", "dust"],
        ),
    }
    # base Temperature -20 -15 -10 -5 0 5 10 15 20 25 30 35
    windchill_data = [
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
    month_data = {
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

    THData = [
        [140, 160, 180, 200, float("inf")],
        [
            "normal weather",
            "hot weather",
            "very hot weather",
            "extremely hot weather",
            "inferno",
        ],
    ]
    THTableData = recordtype(
        "THTableData",
        [
            ("movement_speed", "normal"),
            ("AC", 0),
            ("BtH", 0),
            ("dex", 0),
            ("vision", "normal"),
            ("rest_per_hour", ""),
            ("spell_failure_chance", "0%"),
        ],
    )

    TH_table_data = {
        "normal weather": THTableData(),
        "hot weather": THTableData(
            dex=-1, rest_per_hour="2 turns", spell_failure_chance="5%"
        ),
        "very hot weather": THTableData(
            movement_speed="75%",
            BtH=-1,
            dex=-1,
            vision="75%",
            rest_per_hour="3 turns",
            spell_failure_chance="10%",
        ),
        "extremely hot weather": THTableData(
            movement_speed="50%",
            AC=-1,
            BtH=-2,
            dex=-2,
            vision="50%",
            rest_per_hour="4 turns",
            spell_failure_chance="15%",
        ),
        "inferno": THTableData(
            movement_speed="25%",
            AC=-2,
            BtH=-3,
            dex=-3,
            vision="25%",
            rest_per_hour="5 turns",
            spell_failure_chance="20%",
        ),
    }
