from cogscc.models.errors import InvalidItem
from cogscc.models.errors import AmbiguousMatch


class Equipment:
    def __init__(self, description: str, ev: float, count: int, value: int):
        # 1 cp is 1/500 of an EV, that's the lightest thing that can be carried
        if ev < 0.002:
            raise InvalidItem(f"EV cannot be zero. Items with no appreciable EV: treat the EV as 1 per 10 items carried (PHB p.46)")
        if count < 1:
            raise InvalidItem(f"Number of items must be a positive integer.")
        if value < 0:
            raise InvalidItem(f"Value must be a positive integer.")
        self.description = description
        self.ev = ev
        self.count = count
        self.value = value

    def __to_json__(self):
        return { 'description': self.description, 'ev': self.ev, 'count': self.count }

    @classmethod
    def __from_dict__(cls, d):
        return cls(**d)

    def getEV(self):
        return self.ev * self.count

    def show(self, showDetail: bool = False):
        article = 'a'
        detail = ''
        desc = self.description
        if self.count > 1:
            article = f"{self.count}"
            if desc.lower()[-5:] == "tooth":
                desc = desc[:-5] + "teeth"
            if desc.lower()[-2:] == "ch":
                desc = desc + "es"
            elif desc[-1] == 'y':
                desc = self.description[:-1] + 'ies'
            elif desc[-1] != 's':
                desc += 's'
        elif self.description[0].lower() in ('a', 'e', 'i', 'o', 'u'):
            article = 'an'
        if showDetail:
            valueS = ''
            if self.value > 0:
                valueS = f"{self.value} gp, "
            detail = f" ({valueS}EV {int(self.getEV() + 0.5)})"
        return f"{article} {desc}{detail}"


class Container:
    def __init__(self, description: str, ev: float, capacity: int):
        self = Equipment(description, ev, 1)
        self.capacity = capacity
        self.contents = []


class Wearable(Equipment):
    def __init__(self, description: str, ac: int, ev: float):
        self = Equipment(description, ev, 1)
        self.ac = ac
        self.save = 0
        if 'ring of protection' in description.lower():
            self.save = ac


class Weapon(Equipment):
    def __init__(self, description: str, dmg: str, range: int, ev: float):
        self = Equipment(description, ev, 1)
        self.dmg = dmg
        self.range = range
        self.ammo = ''
        if 'crossbow' in description.lower():
            self.ammo = 'bolt'
        elif bow in description.lower():
            self.ammo = 'arrow'
        elif 'sling' in description.lower():
            self.ammo = 'stone'


class Treasure:
    # 1 EV = 500 cp = 300 sp = 150 gp
    def __init__(self):
        self.pp = 0
        self.gp = 0
        self.ep = 0
        self.sp = 0
        self.cp = 0


class EquipmentList:
    def __init__(self):
        self.equipment = []

    def __to_json__(self):
        return { 'equipment': self.equipment }

    @classmethod
    def __from_dict__(cls, d):
        e = EquipmentList()
        for equipitem in d['equipment']:
            e.equipment.append(Equipment.__from_dict__(equipitem))
        return e

    def find(self, description: str, exactMatch: bool = False):
        num_results = 0
        found_item = -1
        # Search for exact matches first
        for item_no in range(len(self.equipment)):
            if self.equipment[item_no].description.lower() == description.lower():
                num_results = 1
                found_item = item_no
        # If we didn't find one, try partial matches
        if num_results == 0 and not exactMatch:
          for item_no in range(len(self.equipment)):
            if self.equipment[item_no].description.lower().startswith(description.lower()):
                num_results += 1
                found_item = item_no

        if num_results == 0:
            return -1
        elif num_results == 1:
            return found_item
        else:
            raise AmbiguousMatch(f"{description} matches more than one item, please be more specific.")

    def add(self, description: str, ev: float, count: int = 1, value: int = 0):
        itemno = self.find(description, True)
        if itemno < 0:
            newitem = Equipment(description, ev, count, value)
            self.equipment.append(newitem)
            return f"gets {newitem.show()}."
        else:
            self.equipment[itemno].count += count 
            return f"now has {self.equipment[itemno].show()}."

    def drop(self, description: str, count: int = 1):
        itemno = self.find(description)
        if itemno < 0:
            return f"doesn't have any {description}."
        elif count >= self.equipment[itemno].count:
            reply = f"drops {self.equipment[itemno].show()}"
            del self.equipment[itemno]
            return reply
        else:
            self.equipment[itemno].count -= count
            return f"now has {self.equipment[itemno].show()}."

    def inventory(self, showDetail: bool = False):
        equip_list = ''
        if self.equipment:
            equip_list += "**Equipment**\n"
            for item in self.equipment:
                equip_list += f"{item.show(showDetail)}\n"
        return equip_list

