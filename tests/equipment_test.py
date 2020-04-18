import cogscc.equipment as eq
from cogscc.models.errors import AmbiguousMatch

eqList = eq.EquipmentList()

eqList.add("Necronomicon", 1, 1)
eqList.add("arrow", 0.1, 20)
eqList.add("arrowroot", 1, 1)
print(eqList.inventory())

print("Dropping some stuff and getting new stuff")
eqList.drop("N")
try:
  eqList.drop("ar")
except AmbiguousMatch:
  print("ar is too ambiguous")
eqList.drop("arrow")
eqList.add("Beetroot", 1, 2)
print(eqList.inventory())

