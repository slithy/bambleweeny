from cogscc.monster import Monster
from cogscc.hitpoints import HP, Wound, Bleeding
#from cogscc.models.errors import AmbiguousMatch, CreditLimitExceeded, InvalidCoinType, \
    #ItemNotFound, NotWearableItem, NotWearingItem, OutOfRange, UniqueItem

try:
    m = Monster()
except TypeError:
    print("Missing positional arguments")
try:
    m = Monster('Orc')
except TypeError:
    print("Missing positional argument")
try:
    m = Monster('Orc', {})
except KeyError:
    print("Missing AC")
try:
    m = Monster('Orc', { 'ac':20 })
except KeyError:
    print("Missing HD")
try:
    m = Monster('Orc', { 'ac':'invalid', 'hd':4 })
except ValueError:
    print("AC must be an integer")
try:
    m = Monster('Orc', { 'ac':'invalid', 'hd':'splat' })
except ValueError:
    print("HD must be a valid die roll or an integer")

# Minimum stats for a monster
m = Monster('Ogre', { 'hd':4, 'ac':20 })
print(m.statblock())

# Multiple monsters
m = Monster('Orc', { 'hd':1, 'ac':20, 'count':10 })
print(m.showSummary())
print(m.statblock())

m = Monster('Octopus', { 'hd':4, 'ac':20, 'count':5, 'plural_name': 'Octopodes' })
print(m.statblock())

m = Monster('Goblin', { 'hd':'1d6', 'ac':13, 'count':5, 'hp': 3 })
print(m.statblock())

m = Monster('Goblin', { 'hd':'1d6', 'ac':13, 'count':5, 'hp': [ 1, 2 ] })
print(m.statblock())

m = Monster('Goblin', { 'hd':'1d6', 'ac':13, 'count':5, 'hp': [ 1, 2, 3, 4, 5, 6, 7, 8, 9, 10 ], 'xp': [ 5, 1 ] })
print(m.statblock())

hp = HP(8,5)
d = { 'ac': 12, 'hd': '1d12', 'hp': [ hp.__to_json__() ], 'size': 'S', 'move': '15, 30 (jump)', 'save': 'P',
      'special': 'Camouflage +5 to hide, +10 to surprise', 'intelligence': 'Animal', 'alignment': 'N',
      'type': 'Animal', 'xp': [ 9, 1 ], 'attacks': [
          [ 2, 'talons', '1d2' ],
          [ 1, 'bite', '1d4' ]] }

m = Monster('Giant Killer Frog', d)
print(m.statblock())

