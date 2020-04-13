from cogscc.models.errors import AmbiguousMatch


class Equipment:
    def __init__(self, description: str, ev: float, count: int = 1):
        self.description = description
        self.ev = ev
        self.count = count

    def __to_json__(self):
        return { 'description': self.description, 'ev': self.ev, 'count': self.count }

    @classmethod
    def __from_dict__(cls, d):
        return cls(**d)

    def show(self):
        article = 'a'
        desc = self.description
        if self.count > 1:
            article = f"{self.count}"
            if desc[-1] == 'y':
                desc = self.description[:-1] + 'ies'
            elif desc[-1] != 's':
                desc += 's'
        elif self.description[0].lower() in ('a', 'e', 'i', 'o', 'u'):
            article = 'an'
        return f"{article} {desc}"


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


class TreasureItem(Equipment):
    def __init__(self, description: str, value: int, ev: float = 0.01, count: int = 1):
        self = Equipment(description, ev, count)
        self.value = value

class Treasure:
    # 1 EV = 500 cp = 300 sp = 150 gp
    def __init__(self):
        self.pp = 0
        self.gp = 0
        self.ep = 0
        self.sp = 0
        self.cp = 0
        self.valuables = []


class EquipmentList:
    def __init__(self):
        self.equipment = []

    def __to_json__(self):
        return self.equipment

    #@classmethod
    #def __from_dict__(cls, d):
        #return cls(**d)

    def add(self, description: str, ev: float, count: int):
        itemno = self.find(description, True)
        if itemno < 0:
            newitem = Equipment(description, ev, count)
            self.equipment.append(newitem)
            return f"gets {newitem.show()}."
        else:
            self.equipment[itemno].count += count 
            return f"now has {self.equipment[itemno].show()}."

    def drop(self, description: str, count: int):
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

    def find(self, description: str, exactMatch: bool = False):
        num_results = 0
        found_item = -1
        for item_no in range(len(self.equipment)):
            if self.equipment[item_no].description.lower() == description.lower() or \
               (not exactMatch and self.equipment[item_no].description.lower().startswith(description.lower())):
                num_results += 1
                found_item = item_no
        if num_results == 0:
            return -1
        elif num_results == 1:
            return found_item
        else:
            raise AmbiguousMatch(f"{description} matches more than one item, please be more specific.")

    def inventory(self):
        equip_list = ''
        if self.equipment:
            equip_list += "**Equipment**\n"
            for item in self.equipment:
                equip_list += f"{item.show()}\n"
        return equip_list

