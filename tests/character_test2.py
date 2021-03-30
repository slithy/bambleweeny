from cogscc.funcs.dice import roll, DiceResult
from cogscc.character import Character
from cogscc.hitpoints import HP
import cogscc.equipment as eq
from cogscc.models.errors import *

import json

c = Character("Skullthrax Deathbane", "Human", "Barbarian", 3)
c.assignStats(18,17,18,7,7,7,31)
c.setPrimes('str','dex','None')
eqList = eq.EquipmentList()
# eqList.addWeapon("bow", { 'damage': '1d8 + 1', "bth":"5", "range":40 })
# eqList.wield("Bill", "bow")
eqList.addWeapon("Hammer", { 'damage': '1d8 + 1', "bth":"5" })
eqList.addWeapon("Throwing hammer", { 'damage': '1d8', "bth":"4" })
# eqList.wield("Bill", "Throwing hammer")
# eqList.wield("Bill", "Hammer")
eqList.addCoin(3, "gp")
eqList.addCoin(4, "sp")
c.equipment = eqList
print(c.showSummary())

atks = c.getAtks(isRanged = True)
dmgs = c.getDmgs(isRanged = True)


for i in atks:
    r = roll(i)
    print(f"{r.__str__()}: {r.result}")
for i in dmgs:
    r = roll(i)
    print(f"{r.__str__()}: {r.result}")

if len(atks) == 0:
    raise NotWieldingItems

# c.swapWeapons()
# print(c.equipment.equipment[0])
# print(c.equipment.equipment[0].hasTag("melee"))
# print(c.equipment.equipment[0].hasTag("throw"))
# print(c.equipment.equipment[0].hasAllTags(["throw", "melee"]))


# print(c.equipment)
# c.swapWeapons()
# print(c.equipment)

# for d in c.getAttacks():
#     print(d)
# for d in c.getDmgs():
#     print(d)
