from cogscc.funcs.dice import roll, DiceResult
from cogscc.character import Character
from cogscc.hitpoints import HP
import cogscc.equipment as eq
from cogscc.models.errors import *

import json

c = Character("Skullthrax Deathbane", "Human", "Cleric", 3)
c.assignStats(18,17,18,7,7,7,31)
c.setPrimes('str','dex','None')
eqList = eq.EquipmentList()
# eqList.addWeapon("bow", { 'damage': '1d8 + 1', "bth":"5", "range":40 })
# eqList.wield("Bill", "bow")
# eqList.addWeapon("Hammer", { 'damage': '1d8 + 1', "bth":"5" })
eqList.addWeapon("Hammer1", { 'damage': '1d8 + 1', "bth":"5"})
eqList.addWearable("Shield", { 'ac': '+1', "ev":"1"})
print(eqList.equipment[0].addTag("shoot"))
print(eqList.equipment[0].addTag("melee"))
print(eqList.equipment[0].addTag("baubau"))
# eqList.equipment[1].addTag("melee")
print(eqList.equipment[0].getTags())



# eqList.addWeapon("Sword2", { 'damage': '1d8 + 1', "bth":"5" })
# eqList.addWeapon("Throwing hammer", { 'damage': '1d8', "bth":"4" })
# eqList.wield("Bill", "1")
# eqList.wield("Bill", "2")
# eqList.wield("Bill", "Hammer2")
# eqList.addCoin(3, "gp")
# eqList.addCoin(4, "sp")

# c.setGod("Thor")
# print(c.getGod())
#
#
# c.equipment = eqList

# atks = c.getAtks(type="melee")


# for i in atks:
#     print(i)


# print(c.swapWeapons() )
# #
# atks = c.getAtks(type="melee")
# for i in atks:
#     print(i)

# atks = c.getAtks(type="throw", weapon='throwing')
#
# for i in atks:
#     print(i)
#
# print(c.showInventory())
# c.equipment.pickUp("throwing")
# print(c.showInventory())
# atks = c.getAtks(type="throw", weapon='throwing')


#
# print(c.equipment.pickUp("throwing") )
#
# atks = c.getAtks(type="throw", items=["throwing"])
# dmgs = c.getDmgs(type="throw", items=["throwing"])
#
# for i in atks:
#     print(i)
# for i in dmgs:
#     print(i)
#
# print(c.equipment.markAsDropped("throwing") )

#
# if len(atks) == 0:
#     raise NotWieldingItems

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
