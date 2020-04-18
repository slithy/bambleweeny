from cogscc.models.errors import AmbiguousMatch, CreditLimitExceeded, InvalidCoinType, OutOfRange, UniqueItem


class Equipment:
    def __init__(self, description: str, count: int, ev: float, value: int):
        # 1 cp is 1/500 of an EV, that's the lightest thing that can be carried
        if ev < 0.002:
            raise OutOfRange(f"Items with no appreciable EV: treat the EV as 1 per 10 items carried (PHB p.46)")
        if count < 1:
            raise OutOfRange(f"Number of items must be a positive integer.")
        if value < 0:
            raise OutOfRange(f"Value must be a positive integer.")
        self.description = description
        self.article = 'an' if description[0].lower() in { 'a', 'e', 'i', 'o', 'u' } else 'a'
        self.ev = ev
        self.count = count
        self.value = value

    def __to_json__(self):
        return { 'description': self.description, 'ev': self.ev, 'count': self.count }

    @classmethod
    def __from_dict__(cls, d):
        return cls(**d)

    def isEquipment(self):
        return self.value == 0

    def isTreasure(self):
        return self.value > 0

    def getEV(self):
        return self.ev * self.count

    def show(self, showEV: bool = False):
        number = ''
        desc = self.description
        detail = ''
        if self.count > 1:
            number = f"{self.count} "
            if desc.lower()[-5:] == "tooth":
                desc = desc[:-5] + "teeth"
            if desc.lower()[-2:] == "ch":
                desc = desc + "es"
            elif desc[-1] == 'y':
                desc = self.description[:-1] + 'ies'
            elif desc[-1] != 's':
                desc += 's'
        elif self.article:
            number = f"{self.article} "

        if self.value > 0:
            ev = f", EV {int(self.getEV() + 0.5)}" if showEV else ''
            detail = f" ({self.value} gp{ev})"
        elif showEV:
            detail = f" (EV {int(self.getEV() + 0.5)})"
        return f"{number}{desc}{detail}"


class Wearable(Equipment):
    def __init__(self, description: str, ac: int, ev: float, value: int):
        super().__init__(description, 1, ev, value)
        self.ac = ac
        self.is_worn = False
        self.location = ''


class Weapon(Equipment):
    def __init__(self, description: str, dmg: str, range: int, ev: float, value: int):
        self = Equipment(description, 1, ev, value)
        self.dmg = dmg
        self.range = range
        self.ammo = ''
        if 'crossbow' in description.lower():
            self.ammo = 'bolt'
        elif bow in description.lower():
            self.ammo = 'arrow'
        elif 'sling' in description.lower():
            self.ammo = 'stone'


class Container:
    def __init__(self, description: str, ev: float, capacity: int):
        self = Equipment(description, 1, ev, 0)
        self.capacity = capacity
        self.contents = []


class Coin:
    # 1 EV = 500 cp = 300 sp = 150 gp
    coin_ev = {
        'pp': 0.00740, # 1 EV = 135 pp
        'gp': 0.00666, # 1 EV = 150 gp
        'ep': 0.00444, # 1 EV = 225 ep
        'sp': 0.00333, # 1 EV = 300 sp
        'cp': 0.00200  # 1 EV = 500 cp
    }

    def __init__(self):
        self.coin = {
            'pp': 0,
            'gp': 0,
            'sp': 0,
            'ep': 0,
            'cp': 0
        }

    def empty(self):
        return self.coin['pp'] + self.coin['gp'] + self.coin['ep'] + self.coin['sp'] + self.coin['cp'] == 0

    def add(self, amount: int, denomination: str):
        if denomination not in self.coin:
            raise InvalidCoinType(f"{denomination} is not recognised as coinage.")
        if amount < 1:
            raise OutOfRange("Coin value must be a positive integer.")
        self.coin[denomination] += amount

    def drop(self, amount: int, denomination: str):
        if denomination not in self.coin:
            raise InvalidCoinType(f"{denomination} is not recognised as coinage.")
        if amount < 1:
            raise OutOfRange("Coin value must be a positive integer.")
        if self.coin[denomination] == 0:
            raise CreditLimitExceeded(f"You look in your purse but find no {denomination}")
        elif self.coin[denomination] < amount:
            raise CreditLimitExceeded(f"Your purse contains only {self.coin[denomination]} {denomination}")
        else:
            self.coin[denomination] -= amount

    def getEV(self, denomination: str = '', amount: int = 0):
        if denomination == '':
            ev = 0
            for den, amt in self.coin.items():
                ev += amt * Coin.coin_ev[den]
            return ev
        elif denomination not in Coin.coin_ev:
            raise InvalidCoinType()
        if amount > 0:
            return amount * Coin.coin_ev[denomination]
        else:
            return self.coin[denomination] * Coin.coin_ev[denomination]

    def current(self, denomination: str):
        if denomination not in Coin.coin_ev:
            raise InvalidCoinType()
        return f"{self.coin[denomination]} {denomination}"

    def show(self, showEV: bool = False):
        total_ev = f" (EV {int(self.getEV()+0.5)})" if showEV else ''
        coin = f"**Coin{total_ev}:**"
        has_coin = False
        for den, amt in self.coin.items():
            if amt > 0:
                has_coin = True
                ev = f" (EV {int(self.getEV(den)+0.5)})" if showEV else ''
                coin += f"  {amt} {den}{ev}"
        coin += '\n'
        return coin if has_coin else ''


class EquipmentList:
    def __init__(self):
        self.equipment = []
        self.coin = Coin()

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

    def add(self, description: str, count: int = 1, ev: float = 0, value: int = 0):
        itemno = self.find(description, True)
        if itemno < 0:
            newitem = Equipment(description, count, ev, value)
            self.equipment.append(newitem)
            return f"gets {newitem.show()}."
        else:
            self.equipment[itemno].count += count 
            return f"now has {self.equipment[itemno].show()}."

    def addWearable(self, description: str, ac: int = 0, ev: float = 0, value: int = 0):
        itemno = self.find(description, True)
        if itemno < 0:
            newitem = Wearable(description, ac, ev, value)
            self.equipment.append(newitem)
            return f"gets {newitem.show()}."
        else:
            raise UniqueItem(f"Wearable items are unique and you already have {self.equipment[itemno].show()}.")

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

    def addCoin(self, amount: int, denomination: str):
        self.coin.add(amount, denomination)
        return f"has {self.coin.current(denomination)}."

    def dropCoin(self, amount: int, denomination: str):
        self.coin.drop(amount, denomination)
        return f"has {self.coin.current(denomination)}."

    def inventory(self, showEV: bool = False):
        equip_list = "**Equipment**\n"
        has_equipment = False
        treasure_list = "**Treasure**\n"
        has_treasure = False

        for item in self.equipment:
            if item.isEquipment():
                has_equipment = True
                equip_list += f"{item.show(showEV)}\n"
            elif item.isTreasure():
                has_treasure = True
                treasure_list += f"{item.show(showEV)}\n"
        if not self.coin.empty():
            has_treasure = True
            treasure_list += f"{self.coin.show(showEV)}\n"
        inventory = (equip_list if has_equipment else '') + \
                    (treasure_list if has_treasure else '')
        return inventory

