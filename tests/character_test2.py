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
# eqList.addWeapon("Hammer2", { 'damage': '1d8 + 1', "bth":"5" })
# eqList.addWeapon("Bow", { 'damage': '1d8 + 1', "bth":"5"})
# eqList.addAmmo("arrow", { 'damage': '1d3 + 1','count':10})
# eqList.addWeapon("Throwing Hammer2", { 'damage': '1d8 + 1', "bth":"5"})
# eqList.addWeapon("Throwing Hammer1", { 'damage': '1d8 + 1', "bth":"5"})
# eqList.addWearable("Shield", { 'ac': '+1', "ev":"1"})
# eqList.equipment[1].addTag("melee")
# c.setGod("Thor")

eqList.addWeapon("rod", {'damage': '1d8 +1', "bth":"5"})
eqList.addContainer("bag", {"capacity": 100, "ev":1})
eqList.addWeapon("rod2", {'damage': '1d8 +1', "bth":"5"})
eqList.addWeapon("rod3", {'damage': '1d8 +1', "bth":"5"})
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




# print(eqList.find("hammer"))

# eqList.wield("Bill", "Bow")



# eqList.addWeapon("Sword2", { 'damage': '1d8 + 1', "bth":"5" })
# eqList.addWeapon("Throwing hammer", { 'damage': '1d8', "bth":"4" })
# eqList.wield("Bill", "1")
# eqList.wield("Bill", "2")
# eqList.wield("Bill", "Hammer2")
# eqList.addCoin(3, "gp")
# eqList.addCoin(4, "sp")                                         # eqList.addTag("rod", "melee")
#
# c.equipment = eqList
#
# a = eqList.equipment[0].__to_json__()
#
# print(a)
#
# b = eq.Weapon.__from_dict__(a)
# print(b)


# c.setGod("Thor")
# print(c.getGod())
#
#
# c.equipment = eqList
#
# # print(c.showInventory())
#
#
# atks = c.getThrowAtk("2")
# print(atks)
# print(c.showInventory())
# c.equipment.pickUp("2")
# atks = c.getThrowAtk("2")
# print(atks)
# print(c.showInventory())
#
#
# eqList.wield("Bill", "bow")
# atks = c.getShootAtk("arrow")
# print(atks)
# print(c.showInventory())



# atks = c.getAtks(type="melee")
# print(atks)

# atks = c.getMeleeAtks("1")
# print(atks)



#
# print(f"{c.name}:\n{c.showHp()}")


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
