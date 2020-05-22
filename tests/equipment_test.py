import cogscc.equipment as eq
from cogscc.models.errors import AmbiguousMatch, CreditLimitExceeded, InvalidCoinType, InvalidContainerItem, \
    InvalidEquipmentAttribute, ItemNotFound, ItemNotWieldable, ItemNotWearable, NotWearingItem, \
    MissingArgument, NestedContainer, OutOfRange, UniqueItem

eqList = eq.EquipmentList()

eqList.add("The Necronomicon", {})
eqList.add("arrow", { 'count':20, 'ev':0.1})
eqList.add("arrowroot", {})
try:
    eqList.add("helium balloon", { 'ev': -1 })
except OutOfRange:
    print("helium balloon is too light")
try:
    eqList.add("dust", { 'ev': 0 })
except OutOfRange:
    print("dust is too light")
try:
    eqList.add("negative energy", { 'count': -1 })
except OutOfRange:
    print("negative energy is too negative")
try:
    eqList.add("no tea", { 'count': 0 })
except OutOfRange:
    print("you have no no tea")
print(eqList.getInventory())

print("List with EV")
print(eqList.getInventory('', ['ev']))

print("Dropping some stuff and getting new stuff")
eqList.drop("N")
try:
    eqList.drop("ar")
except AmbiguousMatch:
    print("ar is too ambiguous")
eqList.drop("arrow")
eqList.drop("arrow", 5)
eqList.add("Beetroot", {'count':2})
print(eqList.getInventory())

print("Valuables")
try:
  eqList.addCoin(0, "cp")
except OutOfRange:
    print("Can't add zero coins")
try:
  eqList.addCoin(-23, "cp")
except OutOfRange:
    print("Can't add negative coins")
try:
  eqList.addCoin(23, "pounds")
except InvalidCoinType:
    print("Can't add pounds")

try:
  eqList.dropCoin(0, "cp")
except OutOfRange:
    print("Can't drop zero coins")
try:
  eqList.dropCoin(-23, "cp")
except OutOfRange:
    print("Can't drop negative coins")
try:
  eqList.dropCoin(23, "pounds")
except InvalidCoinType:
    print("Can't drop pounds")
try:
  eqList.dropCoin(1, "cp")
except CreditLimitExceeded:
    print("Can't drop money you don't have")

print("Inventory with no coins")
print(eqList.add("golden snakeshead amulet with ruby eyes", { 'ev':0.1, 'value':500 }))
print(eqList.add("gleaming diamond", { 'count': 12, 'ev':0.01, 'value': 1000 }))
print(eqList.getInventory())

print("Inventory with coins")
print(eqList.addCoin(500, "cp"))
print(eqList.addCoin(500, "sp"))
print(eqList.addCoin(500, "ep"))
print(eqList.addCoin(500, "gp"))
print(eqList.addCoin(500, "pp"))
print(eqList.getInventory())
print(eqList.dropCoin(455, "pp"))
print(eqList.dropCoin(400, "gp"))
print(eqList.dropCoin(500, "ep"))
print(eqList.dropCoin(267, "sp"))
try:
    eqList.dropCoin(1000, "cp")
except CreditLimitExceeded:
    print("Can't drop money you don't have")

print("Inventory with coins and EV")
print(eqList.getInventory('', ['ev']))

print("Wearables")
print(eqList.addWearable("- Padded Armour", { 'ac':1, 'ev':2 }))
print(eqList.addWearable("Gold ring with snake sigil", { 'ev':0.01, 'value':1000 }))
print(eqList.addWearable("Crown of Lordly Might", { 'ac':5, 'ev':0.01, 'value':1000 }))
print(eqList.getInventory())
try:
    eqList.addWearable("Golden Snakeshead Amulet with ruby eyes", { 'ev':0.1, 'value':500 })
except UniqueItem:
    print("Can't create more than one instance of wearable items")
try:
    print(eqList.wear("Bill","Armour"))
except ItemNotFound:
    print("Can't wear items that you aren't carrying")
try:
    print(eqList.wear("Bill","Beetroot"))
except ItemNotWearable:
    print("Can't wear something that is not wearable")
print(eqList.addWearable("Indiana Jones hat", {}))
print(eqList.wear("Bill","Indiana","on head"))
print(eqList.wear("Bill","Padded","on body"))
print(eqList.getInventory('', ['ev']))
try:
    eqList.takeOff("Chiwawa")
except ItemNotFound:
    print("Can't take off an item you don't have.")
try:
    eqList.takeOff("Beetroot")
except NotWearingItem:
    print("Can't take off an item you aren't wearing.")
print(eqList.takeOff("Indiana"))
print(eqList.wear("Bill","Crown", "on head"))
print(eqList.getInventory())

print(f"AC bonus is {eqList.ac:+}")
print(eqList.takeOff("Crown"))
print(f"AC bonus is {eqList.ac:+}")

print("Weapons")
try:
    print(eqList.addWeapon("Club", {}))
except MissingArgument:
    print("damage was not specified")
try:
    print(eqList.addWeapon("Club", { 'ac':3 }))
except InvalidEquipmentAttribute:
    print("Only wearable items can take an AC.")
print(eqList.addWeapon("Sword", { 'damage': '1d8' }))
print(eqList.addWeapon("Two-handed Sword", { 'damage': '2d6', 'hands':2, 'ev':5 }))
try:
    print(eqList.addWeapon("Two-handed Sword", { 'damage': '3d6' }))
except UniqueItem:
    print("Can't add two of the same item")
print(eqList.addWearable("Shield, medium steel", { 'ac': 1, 'ev':3, 'hands':1 }))

print("Ranged Weapons")
print(eqList.addWeapon("Club, gold plated", { 'damage': '1d6+1', 'range':10, 'ev':2, 'value':100 }))
print(eqList.addWeapon("Longbow", { 'damage': '1d6', 'range':100, 'ev':2, 'hands':2 }))
print(eqList.addWeapon("Sling", { 'damage': '1d4', 'range':50, 'ev':1 }))
print(eqList.addWeapon("Magic Dagger +3", { 'bth': 3, 'damage': '1d4+3', 'range':10, 'ev':1 }))
print(eqList.getInventory())

print("Wielding Weapons")
print(eqList.wear("Bill","shield","on right arm"))
print(eqList.wear("Bill","shield","on left arm"))
print(eqList.wield("Bill","two"))
try:
    print(eqList.wield("Bill","shield"))
except ItemNotWieldable:
    print("Only weapons can be wielded")
try:
    print(eqList.wear("Bill","sword"))
except:
    print("Weapons cannot be worn.")
print(eqList.wield("Bill","sword"))
print(eqList.getInventory())

print(eqList.takeOff("sword"))
print(eqList.wield("Bill","dagger"))
print(eqList.wield("Bill","club"))
print(eqList.wield("Bill","bow"))
print(eqList.getInventory())

# Containers

print(eqList.addContainer("Large Sack made of silk", { 'ev': 2, 'capacity': 10, 'value': 50 }))
print(eqList.addContainer("Large Barrel", { 'ev': 9, 'capacity': 9 }))
print(eqList.addContainer("Backpack", { 'ev': 2, 'capacity': 8 }))
print(eqList.getInventory())

print(eqList.put("beet","backpack"))
print(eqList.put("beet","sack"))
print(eqList.put("beet","barrel"))
try:
    print(eqList.put("beet","barrel"))
except InvalidContainerItem:
    print("Can't put things in a container they are already in.")
print(eqList.put("armour","backpack"))
print(eqList.put("longbow","backpack"))
try:
    print(eqList.put("barrel","backpack"))
except NestedContainer:
    print("Containers cannot be nested.")
print(eqList.put("arrow","backpack"))
print(eqList.put("diamond","backpack"))

print(eqList.getInventory())
print(eqList.getInventory("blooby"))
print(eqList.getInventory("wear"))
print(eqList.getInventory("wield"))
print(eqList.getInventory("backpack"))
print(eqList.getInventory("sack"))
print(eqList.getInventory("barrel"))
print(eqList.getInventory("treas"))
print(eqList.getInventory("all"))

