from cogscc.monster import Monster
from cogscc.hitpoints import HP


def load():
    killer_frog_dict = {
        "ac": 12,
        "hd": "1d12",
        "hp": [8],
        "size": "S",
        "move": "15, 30 (jump)",
        "save": "P",
        "special": "Camouflage +5 to hide, +10 to surprise",
        "intelligence": "Animal",
        "alignment": "N",
        "type": "Animal",
        "xp": [9, 1],
        "attacks": [[2, "Talons", "1d2"], [1, "Bite", "1d4"]],
        "personal_name": "Froggo",
    }
    killer_frog = Monster("Giant Killer Frog", killer_frog_dict)

    # Return { 'user#id#num', Monster }
    return {}
