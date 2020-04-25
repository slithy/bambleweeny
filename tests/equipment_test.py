import cogscc.equipment as eq
from cogscc.models.errors import AmbiguousMatch, CreditLimitExceeded, InvalidCoinType, \
    ItemNotFound, ItemNotWearable, NotWearingItem, OutOfRange, UniqueItem

eqList = eq.EquipmentList()

eqList.add("Necronomicon", {})
eqList.add("arrow", { 'count':20, 'ev':0.1})
eqList.add("arrowroot", {})
try:
    eqList.add("helium balloon", 1, -1)
except OutOfRange:
    print("helium balloon is invalid")
try:
    eqList.add("dust", 1, 0)
except OutOfRange:
    print("dust is invalid")
try:
    eqList.add("negative energy", -1, 1)
except OutOfRange:
    print("negative energy is invalid")
try:
    eqList.add("no tea", 0, 1)
except OutOfRange:
    print("no tea is invalid")
print(eqList.inventory())

print("List with EV")
print(eqList.inventory(True))

print("Dropping some stuff and getting new stuff")
eqList.drop("N")
try:
    eqList.drop("ar")
except AmbiguousMatch:
    print("ar is too ambiguous")
eqList.drop("arrow")
eqList.drop("arrow", 5)
eqList.add("Beetroot", 2, 1)
print(eqList.inventory())

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
print(eqList.add("golden snakeshead amulet with ruby eyes", 1, 0.1, 500))
print(eqList.add("gleaming diamond", 12, 0.01, 1000))
print(eqList.inventory())

print("Inventory with coins")
print(eqList.addCoin(500, "cp"))
print(eqList.addCoin(500, "sp"))
print(eqList.addCoin(500, "ep"))
print(eqList.addCoin(500, "gp"))
print(eqList.addCoin(500, "pp"))
print(eqList.inventory())
print(eqList.dropCoin(455, "pp"))
print(eqList.dropCoin(400, "gp"))
print(eqList.dropCoin(500, "ep"))
print(eqList.dropCoin(267, "sp"))
try:
    eqList.dropCoin(1000, "cp")
except CreditLimitExceeded:
    print("Can't drop money you don't have")

print("Inventory with coins and EV")
print(eqList.inventory(True))

print("Wearables")
print(eqList.addWearable("Padded Armour", 1, 2))
print(eqList.addWearable("Gold ring with snake sigil", 0, 0.01, 1000))
print(eqList.addWearable("Crown of Lordly Might", 5, 0.01, 1000))
print(eqList.inventory())
try:
    eqList.addWearable("Golden snakeshead amulet with ruby eyes", 0, 0.01, 1000)
except UniqueItem:
    print("Can't create more than one instance of wearable items")
try:
    print(eqList.wear("Armour"))
except ItemNotFound:
    print("Can't wear items that you aren't carrying")
try:
    print(eqList.wear("Beetroot"))
except NotWearableItem:
    print("Can't wear something that is not wearable")
print(eqList.addWearable("Indiana Jones hat", 0, 1))
print(eqList.wear("Indiana","on head"))
print(eqList.wear("Padded","on body"))
print(eqList.inventory(True))
try:
    eqList.takeOff("Chiwawa")
except ItemNotFound:
    print("Can't take off an item you don't have.")
try:
    eqList.takeOff("Beetroot")
except NotWearingItem:
    print("Can't take off an item you aren't wearing.")
print(eqList.takeOff("Indiana"))
print(eqList.wear("Crown", "on head"))
print(eqList.inventory())

print(f"AC bonus is {eqList.ac:+}")
print(eqList.takeOff("Crown"))
print(f"AC bonus is {eqList.ac:+}")

