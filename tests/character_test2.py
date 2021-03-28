from cogscc.funcs.dice import roll, DiceResult
from cogscc.character import Character
from cogscc.hitpoints import HP
import cogscc.equipment as eq

import json

c = Character("Skullthrax Deathbane", "Human", "Barbarian", 3)
c.assignStats(18,17,18,7,7,7,31)
c.setPrimes('str','dex','None')
eqList = eq.EquipmentList()
eqList.addWeapon("Hammer", { 'damage': '1d8 + 1', "bth":"5" })
eqList.addWeapon("Sword", { 'damage': '1d8' })
eqList.wield("Bill", "Sword")
eqList.wield("Bill", "Hammer")
eqList.addCoin(3, "gp")
eqList.addCoin(4, "sp")
c.equipment = eqList
print(c.showSummary())

print(c.equipment)
c.swapWeapons()
print(c.equipment)

for d in c.getAttacks():
    print(d)
for d in c.getDmgs():
    print(d)
