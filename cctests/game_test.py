import sys, os

rootpath = os.path.realpath(os.path.dirname(__file__) + "/..")
if rootpath not in sys.path:
    sys.path.append(rootpath)

import time
import json
import random
from os.path import basename
from discord.ext import commands
from cogscc.funcs.dice import roll
from cogscc.character import Character
from cogscc.monster import Monster
import cogscc.npc
from cogscc.models.errors import (
    AmbiguousMatch,
    CharacterNotFound,
    InvalidArgument,
    MissingArgument,
    NotAllowed,
)
from cogscc.world.world import GHWorld
from cogscc.world.location import GHLocation
from cogscc.base_obj import BaseObj


class ToJson(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, "__to_json__"):
            return obj.__to_json__()
        return json.JSONEncoder.default(self, obj)


class Game(BaseObj):
    gm_roles = ["Castle Keeper", "Game Master", "Dungeon Master"]

    def __init__(self):
        self.characters = {}
        self.monsters = []
        self.world = GHWorld()

    def saveJson(self, filename: str = "characters.json"):
        """Save characters to a file in JSON format."""
        with open(f"{basename(filename)}", "w") as f:
            json.dump(
                {"characters": self.characters, "world": self.world},
                f,
                cls=ToJson,
                indent=2,
                ensure_ascii=False,
            )
        ts = time.gmtime()
        timestamp = time.strftime("%Y%m%d%H%M%S", ts)
        filename_backup = f"{basename(filename)}.{timestamp}"
        with open(f"{filename_backup}", "w") as f:
            json.dump(
                {"characters": self.characters, "world": self.world}, f, cls=ToJson
            )

    def loadJson(self, filename: str = "characters.json"):
        """Load characters from a JSON-formatted file."""
        with open(f"{basename(filename)}", "r") as f:
            raw = json.load(f)
            if "world" not in raw:
                chars = raw
            else:
                chars = raw["characters"]
                self.world = GHWorld.__from_dict__(raw["world"])

            for player, character in chars.items():
                if character.get("type", ""):
                    self.characters[player] = Monster.__from_dict__(character)
                else:
                    self.characters[player] = Character.__from_dict__(character)


def test_save_load():
    g = Game()
    g.world.set_date(364 * 10.5)
    l = GHLocation("new town", "plains", 40, 0)
    g.world.add_location(l)
    g.world.reset_weather()
    filename = "characters.json"
    g.saveJson(filename)
    g2 = Game()
    g2.loadJson(filename)

    assert g2 == g

    with open(f"{basename(filename)}", "w") as f:
        json.dump({}, f, cls=ToJson, indent=2, ensure_ascii=False)
    g3 = Game()
    g3.loadJson(filename)

    assert g3 == Game()


test_save_load()
