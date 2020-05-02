from cogscc.character import Character
from cogscc.monster import Monster
from cogscc.hitpoints import HP
import cogscc.animals

c = Character("Skullthrax Deathbane", "Human", "Barbarian", 3)
c.assignStats(18,18,18,7,7,7,31)
c.setPrimes('str','dex','None')
print(c.showSummary())
print(c.showCharacter())
print(c.energyDrain())

d = { 'ac': 12, 'hd': '1d12', 'hp': [ HP(8,5) ], 'size': 'S', 'move': '15, 30 (jump)', 'save': 'P',
      'special': 'Camouflage +5 to hide, +10 to surprise', 'intelligence': 'Animal', 'alignment': 'N',
      'type': 'Animal', 'xp': [ 9, 1 ], 'attacks': [
          [ 2, 'Talons', '1d2' ],
          [ 1, 'Bite', '1d4' ]],
      'personal_name': 'Froggo' }

m = Monster('Giant Killer Frog', d)
print(m.statblock())
print(m.showSummary())
print(m.showCharacter())


animals = cogscc.animals.load()
characters = {}
for player, animal in animals.items():
    characters[player] = animal
