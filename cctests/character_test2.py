from cogscc.funcs.dice import roll, DiceResult
from cogscc.character import Character
from cogscc.hitpoints import HP
import cogscc.equipment as eq
from cogscc.models.errors import *

import json

c = Character("Skullthrax Deathbane", "Human", "Cleric", 3)
c.assignStats(18, 17, 18, 7, 7, 7, 31)
c.setPrimes("str", "dex", "None")
eqList = eq.EquipmentList()
# eqList.addWeapon("bow", { 'damage': '1d8 + 1', "bth":"5", "range":40 })
# eqList.wield("Bill", "bow")
# eqList.addWeapon("Hammer2", { 'damage': '1d8 + 1', "bth":"5" })
# eqList.addWeapon("Bow", { 'damage': '1d8 + 1', "bth":"5"})
# eqList.addAmmo("arrow", { 'damage': '1d3 + 1','count':10})
# eqList.addWeapon("Throwing Hammer2", { 'damage': '1d8 + 1', "bth":"5"})
# eqList.addWeapon("Throwing Hammer1", { 'damage': '1d8 + 1', "bth":"5"})
# eqList.addWearable("Shield", { 'ac': '+1', "ev":"1"})
# eqList.equipment[1].addTag("melee")
# c.setGod("Thor")

eqList.addWeapon("rod", {'damage': '1d8 +1', "bth":"5"})
eqList.addTag("rod", "melee")

c.equipment = eqList

a = eqList.equipment[0].__to_json__()

print(a)

b = eq.Weapon.__from_dict__(a)
print(b)
=======
eqList.addWeapon("rod", {"damage": "1d8 +1", "bth": "5"})
eqList.addContainer("bag", {"capacity": 100, "ev": 1})
eqList.addWeapon("rod2", {"damage": "1d8 +1", "bth": "5"})
eqList.addWeapon("rod3", {"damage": "1d8 +1", "bth": "5"})
eqList.put("rod2", "bag")
eqList.put("rod3", "bag")
print(eqList.getInventory())
# eqList.addTag("rod", "melee")
#
# c.equipment = eqList
#
# a = eqList.equipment[0].__to_json__()
#
# print(a)
#
# b = eq.Weapon.__from_dict__(a)
# print(b)

