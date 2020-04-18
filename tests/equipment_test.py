import cogscc.equipment as eq
from cogscc.models.errors import InvalidItem
from cogscc.models.errors import AmbiguousMatch

eqList = eq.EquipmentList()

eqList.add("Necronomicon", 1, 1)
eqList.add("arrow", 0.1, 20)
eqList.add("arrowroot", 1, 1)
try:
    eqList.add("helium balloon", -1, 1)
except InvalidItem:
    print("helium balloon is invalid")
try:
    eqList.add("dust", 0, 1)
except InvalidItem:
    print("dust is invalid")
try:
    eqList.add("negative energy", 1, -1)
except InvalidItem:
    print("negative energy is invalid")
try:
    eqList.add("no tea", 1, 0)
except InvalidItem:
    print("no tea is invalid")
print(eqList.inventory())

print("Detailed list")
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

