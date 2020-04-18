import cogscc.equipment as eq
from cogscc.models.errors import AmbiguousMatch
from cogscc.models.errors import CreditLimitExceeded
from cogscc.models.errors import InvalidCoinType
from cogscc.models.errors import OutOfRange

eqList = eq.EquipmentList()

eqList.add("Necronomicon", 1, 1)
eqList.add("arrow", 0.1, 20)
eqList.add("arrowroot", 1, 1)
try:
    eqList.add("helium balloon", -1, 1)
except OutOfRange:
    print("helium balloon is invalid")
try:
    eqList.add("dust", 0, 1)
except OutOfRange:
    print("dust is invalid")
try:
    eqList.add("negative energy", 1, -1)
except OutOfRange:
    print("negative energy is invalid")
try:
    eqList.add("no tea", 1, 0)
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
eqList.add("Beetroot", 1, 2)
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
eqList.add("golden snakeshead amulet with ruby eyes", 0.1, 1, 500)
eqList.add("gleaming diamond", 0.01, 12, 1000)
print(eqList.inventory())

print("Inventory with coins")
eqList.addCoin(500, "cp")
eqList.addCoin(500, "sp")
eqList.addCoin(500, "ep")
eqList.addCoin(500, "gp")
eqList.addCoin(500, "pp")
print(eqList.inventory())
eqList.dropCoin(455, "pp")
eqList.dropCoin(400, "gp")
eqList.dropCoin(500, "ep")
eqList.dropCoin(267, "sp")
try:
    eqList.dropCoin(1000, "cp")
except CreditLimitExceeded:
    print("Can't drop money you don't have")

print("Inventory with coins and EV")
print(eqList.inventory(True))

