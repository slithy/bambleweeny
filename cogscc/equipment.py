import gc
from copy import copy
from cogscc.models.errors import AmbiguousMatch, CreditLimitExceeded, InvalidCoinType, InvalidContainerItem, \
    InvalidEquipmentAttribute, ItemNotFound, ItemNotMutable, ItemNotWieldable, ItemNotWearable, \
    MissingArgument, NestedContainer, NotWearingItem, OutOfRange, UniqueItem


class Equipment:
    def __init__(self, description: str, count: int, ev: float, value: int):
        # 1 cp is 1/500 of an EV, that's the lightest thing that can be carried
        if ev < 0.002:
            raise OutOfRange("Items with no appreciable EV: treat the EV as 1 per 10 items carried (PHB p.46)")
        if count < 1:
            raise OutOfRange("Number of items must be a positive integer.")
        if value < 0:
            raise OutOfRange("Value must be a positive integer.")

        # Remove extra spaces
        self.description = " ".join(description.split())

        # Set article and plural
        self.article = ''
        for default_article in ['a','an','the','-']:
            if self.description.lower().startswith(default_article + ' '):
                self.article = default_article
                self.description = self.description[len(default_article)+1:]
        if not self.article:
            self.article = self.defaultArticle()
        self.plural = ''

        self.ev = ev
        self.count = count
        self.value = value
        self.gm_note = ''

    def __to_json__(self):
        # Save only non-default values
        d = { 'description': self.description }
        if self.article != self.defaultArticle():
            d['article'] = self.article
        if self.plural:
            d['plural'] = self.plural
        if self.count > 1:
            d['count'] = self.count
        if self.ev != 1.0:
            d['ev'] = self.ev
        if self.value != 0:
            d['value'] = self.value
        if self.gm_note:
            d['gm_note'] = self.gm_note
        return d

    @classmethod
    def __from_dict__(cls, d):
        ev = d.get('ev', 1)
        e = cls(d['description'], d.get('count', 1), ev if ev >= 0.002 else 1, d.get('value', 0))
        e.__from_dict_super__(d)
        return e

    def __from_dict_super__(e, d):
        e.article = d.get('article', e.defaultArticle())
        e.plural = d.get('plural', '')
        e.gm_note = d.get('gm_note', '')

    def defaultArticle(self):
        return 'an' if self.description[0].lower() in { 'a', 'e', 'i', 'o', 'u' } else 'a'

    def isEquipment(self):
        return self.value == 0

    def isPushable(self, e):
        return True if type(self) == type(e) and \
                          self.ev == e.ev and \
                       self.value == e.value else False

    def isWeapon(self):
        return False

    def isWielding(self):
        return False

    def isWearable(self):
        return False

    def isWearing(self):
        return False

    def isContainer(self):
        return False

    def isTreasure(self):
        return self.value > 0

    def getEV(self):
        return self.ev * self.count

    def findContainer(self):
        for ref in gc.get_referrers(self):
            for cl in gc.get_referrers(ref):
                if type(cl) is dict and 'capacity' in cl:
                    return (ref,cl)
        return None

    def isInContainer(self):
        return self.findContainer() != None

    def removeFromContainer(self):
        fc = self.findContainer()
        if fc != None:
            fc[0].remove(self)
            return fc[1]['description']

    def getDescription(self):
        number = ''
        desc = self.description
        if self.count > 1:
            number = f"{self.count} "
            if self.plural:
                desc = self.plural
            elif self.description.lower().endswith(('o','s','sh','ch','x','z')):
                desc = self.description + 'es'
            elif self.description.lower().endswith(('ay','ey','iy','oy','uy')):
                desc = self.description + 's'
            elif self.description.lower().endswith('y'):
                desc = self.description[:-1] + 'ies'
            else:
                desc = self.description + 's'
        elif self.article != '-':
            number = f"{self.article} "
        return f"{number}{desc}"

    def show(self, showEV: bool = False, showNotes: bool = False):
        detail = ''
        if self.value > 0:
            ev = f", EV {int(self.getEV() + 0.5)}" if showEV else ''
            detail = f" ({self.value * self.count} gp{ev})"
        elif showEV:
            detail = f" (EV {int(self.getEV() + 0.5)})"
        detail += ' :small_blue_diamond:' if showNotes and self.gm_note else ''
        return f"{self.getDescription()}{detail}"


class Wearable(Equipment):
    def __init__(self, description: str, ac: int, hands: int, ev: float, value: int):
        super().__init__(description, 1, ev, value)
        self.ac = ac
        if hands < 0 or hands > 2:
            raise InvalidEquipmentAttribute(f"hands:{hands}")
        self.hands = hands
        self.is_worn = False
        self.location = ''

    def __to_json__(self):
        d = super().__to_json__()
        d['type'] = 'wearable'
        if self.ac != 0:
            d['ac'] = self.ac
        if self.hands != 0:
            d['hands'] = self.hands
        if self.is_worn:
            d['wearing'] = True
        if self.is_worn and self.location != '':
            d['location'] = self.location
        return d

    @classmethod
    def __from_dict__(cls, d):
        ev = d.get('ev', 1)
        e = cls(d['description'], d.get('ac', 0), d.get('hands', 0), ev if ev >= 0.002 else 1, d.get('value', 0))
        e.__from_dict_super__(d)
        e.is_worn = d.get('wearing', False)
        e.location = d.get('location', '')
        return e

    def isEquipment(self):
        return not self.is_worn and self.value == 0

    def isPushable(self, e):
        return False

    def isWearable(self):
        return True

    def isWearing(self):
        return self.is_worn

    def isTreasure(self):
        return not self.is_worn and self.value > 0

    def wear(self, location: str):
        self.removeFromContainer()
        self.is_worn = True
        self.location = location

    def takeOff(self):
        self.is_worn = False

    def show(self, showEV: bool = False, showNotes: bool = False):
        if not self.is_worn:
            return super().show(showEV, showNotes)
        else:
            loc = f", {self.location}" if self.location else ''
            ev = f" (EV {int(self.ev + 0.5)})" if showEV else ''
            ac = f", {self.ac:+} AC" if self.ac != 0 else ''
            notes = ' :small_blue_diamond:' if showNotes and self.gm_note else ''
            return f"{self.getDescription()}{loc}{ac}{ev}{notes}"


class Weapon(Equipment):
    def __init__(self, description: str, dmg: str, bth: int, hands: int, range: int, ev: float, value: int):
        super().__init__(description, 1, ev, value)
        self.dmg = dmg
        self.bth = bth
        if hands < 1 or hands > 2:
            raise InvalidEquipmentAttribute(f"hands:{hands}")
        self.hands = hands
        self.range = range
        self.is_wielding = False

    def __to_json__(self):
        d = super().__to_json__()
        d['type'] = 'weapon'
        d['dmg'] = self.dmg
        if self.bth != 0:
            d['bth'] = self.bth
        if self.hands != 1:
            d['hands'] = self.hands
        if self.range != 0:
            d['range'] = self.range
        if self.is_wielding:
            d['wielding'] = True
        return d

    @classmethod
    def __from_dict__(cls, d):
        ev = d.get('ev', 1)
        e = cls(d['description'], d['dmg'], d.get('bth', 0), d.get('hands', 1), d.get('range', 0), ev if ev >= 0.002 else 1, d.get('value', 0))
        e.__from_dict_super__(d)
        e.is_wielding = d.get('wielding', False)
        return e

    def isEquipment(self):
        return not self.is_wielding and self.value == 0

    def isPushable(self, e):
        return False

    def isWeapon(self):
        return True

    def isWielding(self):
        return self.is_wielding

    def wield(self):
        self.removeFromContainer()
        self.is_wielding = True

    def unwield(self):
        self.is_wielding = False

    def show(self, showEV: bool = False, showNotes: bool = False):
        if not self.is_wielding:
            return super().show(showEV, showNotes)
        else:
            dmg = f"{self.dmg} dmg" if self.bth == 0 else f"BtH {self.bth:+}, {self.dmg} dmg"
            range = f", range {self.range}'" if self.range > 0 else ""
            ev = f" (EV {int(self.ev + 0.5)})" if showEV else ''
            notes = ' :small_blue_diamond:' if showNotes and self.gm_note else ''
            return f"{self.getDescription()}, {dmg}{range}{ev}{notes}"


class Container(Equipment):
    def __init__(self, description: str, capacity: int, ev: float, value: int):
        super().__init__(description, 1, ev, value)
        self.capacity = capacity
        self.contents = []

    def __to_json__(self):
        d = super().__to_json__()
        d['type'] = 'container'
        d['capacity'] = self.capacity
        if self.contents:
            d['contents'] = self.contents
        return d

    @classmethod
    def __from_dict__(cls, d):
        e = cls(d['description'], d['capacity'], d.get('ev', 1.0), d.get('value', 0))
        e.__from_dict_super__(d)
        e.contents = d.get('contents', [])
        return e

    def __lt__(self, other):
        return self.description < other.description

    def isContainer(self):
        return True

    def put(self, item):
        if item.isContainer():
            raise NestedContainer(f"You try to put {item.show()} inside {self.show()}. This tears a hole in the fabric of space-time. You are sucked in and die. :skull:")
        elif item.isWearing():
            item.takeOff()
        elif item.isWielding():
            item.unwield()
        elif item in self.contents:
            raise InvalidContainerItem(f"{item.show()} is already in {self.show()}.")
        else:
            item.removeFromContainer()
        self.contents.append(item)

    def showContents(self, showEV: bool = False, showNotes: bool = False):
        detail = ''
        if self.value > 0:
            ev = f", EV {int(self.getEV() + 0.5)}" if showEV else ''
            detail = f" ({self.value * self.count} gp{ev})"
        elif showEV:
            detail = f" (EV {int(self.getEV() + 0.5)})"
        detail += ' :small_blue_diamond:' if showNotes and self.gm_note else ''
        equip_list = f"**{self.description}**{detail} Capacity {self.capacity}\n"
        for item in self.contents:
            equip_list += f"  {item.show(showEV, showNotes)}\n"
        return equip_list


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

    def __to_json__(self):
        d = {}
        for den,amt in self.coin.items():
            if amt > 0:
                d[den] = amt
        return { 'coin': d }

    @classmethod
    def __from_dict__(cls, d):
        c = Coin()
        for den,amt in d.items():
            c.coin[den] = amt
        return c

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
        coin = f"  :moneybag:{total_ev}\n"
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
        self.ac = 0

    def __to_json__(self):
        return { 'items': self.equipment, 'coin': self.coin.coin }

    @classmethod
    def __from_dict__(cls, d):
        e = EquipmentList()
        for equipitem in d['items']:
            type = equipitem.get('type', 'normal')
            if type == 'wearable':
                e.equipment.append(Wearable.__from_dict__(equipitem))
            elif type == 'weapon':
                e.equipment.append(Weapon.__from_dict__(equipitem))
            elif type == 'container':
                e.equipment.append(Container.__from_dict__(equipitem))
            else:
                e.equipment.append(Equipment.__from_dict__(equipitem))
        e.coin = Coin.__from_dict__(d.get('coin'))
        e.recalculateAC()
        return e

    def find(self, description: str, exactMatch: bool = False):
        num_results = 0
        found_item = -1
        # Search for exact matches first
        for item_no in range(len(self.equipment)):
            if self.equipment[item_no].description.lower() == description.lower():
                num_results = 1
                found_item = item_no
        # If we didn't find one, try partial matches at the start of the string
        if num_results == 0 and not exactMatch:
          for item_no in range(len(self.equipment)):
            if self.equipment[item_no].description.lower().startswith(description.lower()):
                num_results += 1
                found_item = item_no
        # If we still didn't find one, try partial matches anywhere in the string
        if num_results == 0 and not exactMatch:
          for item_no in range(len(self.equipment)):
            if description.lower() in self.equipment[item_no].description.lower():
                num_results += 1
                found_item = item_no

        if num_results == 0:
            return -1
        elif num_results == 1:
            return found_item
        else:
            raise AmbiguousMatch(f"{description} matches more than one item, please be more specific.")

    def recalculateAC(self):
        self.ac = 0
        for item_no in range(len(self.equipment)):
            if self.equipment[item_no].isWearing():
                self.ac += self.equipment[item_no].ac

    def freeHands(self, hands: int, name: str):
        free_hands = 2
        reply = ''
        for item_no in range(len(self.equipment)):
            if self.equipment[item_no].isWearing() or self.equipment[item_no].isWielding():
                free_hands -= self.equipment[item_no].hands
        if free_hands >= hands:
            return reply
        for item_no in range(len(self.equipment)):
            if self.equipment[item_no].isWielding():
                self.equipment[item_no].unwield()
                free_hands += self.equipment[item_no].hands
                reply += f"{name} puts away {self.equipment[item_no].show()}\n"
                if free_hands >= hands:
                    return reply
        for item_no in range(len(self.equipment)):
            if self.equipment[item_no].isWearing() and self.equipment[item_no].hands > 0:
                self.equipment[item_no].takeOff()
                free_hands += self.equipment[item_no].hands
                reply += f"{name} takes off {self.equipment[item_no].show()}\n"
                if free_hands >= hands:
                    return reply

    def add(self, description: str, d: dict):
        for key in d.keys():
            if key == 'name':
                raise InvalidEquipmentAttribute(d['name'])
            if key not in ['count','ev','value']:
                raise InvalidEquipmentAttribute(key)
        count = d.get('count', 1)
        if count != int(count) or count < 1:
            raise OutOfRange("count must be a positive integer")

        itemno = self.find(description, True)
        if itemno < 0:
            newitem = Equipment(description, count, float(d.get('ev',1)), int(d.get('value',0)))
            self.equipment.append(newitem)
            return f"gets {newitem.show()}."
        elif type(self.equipment[itemno]) is not Equipment:
            raise UniqueItem(f"You already have a {self.equipment[itemno].show()} and this type of item is unique.")
        elif 'ev' in d.keys() and d.get('ev') != self.equipment[itemno].ev:
            raise ItemNotMutable(f"EV:{d.get('ev')} is different from the EV of {self.equipment[itemno].show(True)}")
        elif 'value' in d.keys() and d.get('value') != self.equipment[itemno].value:
            raise ItemNotMutable(f"Value:{d.get('value')} is different from the value of {self.equipment[itemno].show()}")
        else:
            self.equipment[itemno].count += count 
            return f"now has {self.equipment[itemno].show()}."

    def gmNote(self, item, description = ''):
        itemno = self.find(item)
        if itemno < 0:
            raise ItemNotFound(f"{item} not found.")
        if description:
            self.equipment[itemno].gm_note = description
            return f"{self.equipment[itemno].show()}"
        elif self.equipment[itemno].gm_note:
            return self.equipment[itemno].gm_note
        else:
            return f"{self.equipment[itemno].show()} has no secret note."

    def push(self, e):
        itemno = self.find(e.description, True)
        if itemno < 0:
            self.equipment.append(e)
        elif not self.equipment[itemno].isPushable(e):
            raise UniqueItem()
        else:
            self.equipment[itemno].count += e.count 

    def addWeapon(self, description: str, d: dict):
        for key in d.keys():
            if key not in ['name','count','ev','value','damage','bth','hands','range']:
                raise InvalidEquipmentAttribute(key)
        count = d.get('count', 1)
        if count != 1:
            raise UniqueItem("Weapons are unique (count must be 1)")
        if not d.get('damage',''):
            raise MissingArgument(f"You need to specify the damage for {description}.")

        itemno = self.find(description, True)
        if itemno < 0:
            newitem = Weapon(description, d['damage'], int(d.get('bth',0)), int(d.get('hands',1)),
                int(d.get('range',0)), float(d.get('ev',1)), int(d.get('value',0)))
            self.equipment.append(newitem)
            return f"gets {newitem.show()}."
        else:
            raise UniqueItem(f"Weapons are unique and you already have {self.equipment[itemno].show()}.")

    def wield(self, name: str, description: str):
        itemno = self.find(description)
        if itemno < 0:
            raise ItemNotFound(f"You don't have any {description}.")
        elif not self.equipment[itemno].isWeapon():
            raise ItemNotWieldable(f"{self.equipment[itemno].show()} is not something you can wield.")
        else:
            reply = self.freeHands(self.equipment[itemno].hands, name)
            reply += f"{name} is wielding {self.equipment[itemno].show()}."
            self.equipment[itemno].wield()
            self.recalculateAC()
            return reply

    def addWearable(self, description: str, d: dict):
        for key in d.keys():
            if key not in ['name','count','ev','value','ac','hands']:
                raise InvalidEquipmentAttribute(key)
        count = d.get('count', 1)
        if count != 1:
            raise UniqueItem("Wearable items are unique (count must be 1)")

        # Shields require 1 hand by default
        if d.get('hands',99) == 99 and 'shield' in description.lower():
            d['hands'] = 1

        itemno = self.find(description, True)
        if itemno < 0:
            newitem = Wearable(description, int(d.get('ac',0)), int(d.get('hands',0)), float(d.get('ev',1)), int(d.get('value',0)))
            self.equipment.append(newitem)
            return f"gets {newitem.show()}."
        else:
            raise UniqueItem(f"Wearable items are unique and you already have {self.equipment[itemno].show()}.")

    def wear(self, name: str, description: str, location: str = ''):
        itemno = self.find(description)
        if itemno < 0:
            raise ItemNotFound(f"You don't have any {description}.")
        elif not self.equipment[itemno].isWearable():
            raise ItemNotWearable(f"{self.equipment[itemno].show()} is not something you can wear.")
        else:
            reply = self.freeHands(self.equipment[itemno].hands, name)
            reply += f"{name} is wearing {self.equipment[itemno].show()}."
            self.equipment[itemno].wear(location)
            self.recalculateAC()
            return reply

    def takeOff(self, description: str):
        itemno = self.find(description)
        if itemno < 0:
            raise ItemNotFound(f"You don't have any {description}.")
        elif self.equipment[itemno].isWearing():
            self.equipment[itemno].takeOff()
            self.recalculateAC()
            reply = f"takes off {self.equipment[itemno].show()}."
            return reply
        elif self.equipment[itemno].isWielding():
            self.equipment[itemno].unwield()
            reply = f"puts away {self.equipment[itemno].show()}."
            return reply
        else:
            raise NotWearingItem(f"You are not bearing {self.equipment[itemno].show()}.")

    def addContainer(self, description: str, d: dict):
        for key in d.keys():
            if key not in ['name','count','capacity','ev','value']:
                raise InvalidEquipmentAttribute(key)
        count = d.get('count', 1)
        if count != 1:
            raise UniqueItem("Containers are unique (count must be 1)")
        if not d.get('ev',''):
            raise MissingArgument(f"You need to specify the Encumbrance Value (EV) for {description}.")
        if not d.get('capacity',''):
            raise MissingArgument(f"You need to specify the capacity for {description}.")

        itemno = self.find(description, True)
        if itemno < 0:
            newitem = Container(description, int(d['capacity']), float(d['ev']), int(d.get('value',0)))
            self.equipment.append(newitem)
            return f"gets {newitem.show()}."
        else:
            raise UniqueItem(f"Containers are unique and you already have {self.equipment[itemno].show()}.")

    def put(self, description: str, container: str):
        itemno = self.find(description)
        if itemno < 0:
            raise ItemNotFound(f"You don't have any {description}.")
        contno = self.find(container)
        if contno < 0:
            raise ItemNotFound(f"You don't have any {container}.")
        self.equipment[contno].put(self.equipment[itemno])
        return f"puts {self.equipment[itemno].show()} into {self.equipment[contno].show()}"

    def takeOut(self, description: str):
        itemno = self.find(description)
        if itemno < 0:
            raise ItemNotFound(f"You don't have any {description}.")
        contdesc = self.equipment[itemno].removeFromContainer()
        contno = self.find(contdesc)
        return f"removes {self.equipment[itemno].show()} from {self.equipment[contno].show()}"

    def pop(self, description: str, count: int = 1):
        itemno = self.find(description)
        if itemno < 0:
            raise ItemNotFound(f"You don't have any {description}.")
        elif count >= self.equipment[itemno].count:
            reply = ''
            if self.equipment[itemno].isWearing():
                self.equipment[itemno].takeOff()
                self.recalculateAC()
            e = copy(self.equipment[itemno])
            del self.equipment[itemno]
        else:
            e = copy(self.equipment[itemno])
            self.equipment[itemno].count -= count
            e.count = count
        return e

    def drop(self, description: str, count: int = 1):
        itemno = self.find(description)
        if itemno < 0:
            raise ItemNotFound(f"You don't have any {description}.")
        elif count >= self.equipment[itemno].count:
            reply = ''
            if self.equipment[itemno].isWearing():
                self.equipment[itemno].takeOff()
                self.recalculateAC()
            reply = f"drops {self.equipment[itemno].show()}."
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

    def getInventory(self, showEV: bool = False, showNotes: bool = False):
        wear_list = "**Wearing**\n"
        has_wear = False
        wield_list = "**Wielding**\n"
        has_wield = False
        equip_list = "**Carrying**\n"
        has_equipment = False
        treasure_list = "**Treasure**\n"
        has_treasure = False
        container_list = []

        for item in self.equipment:
            if item.isWearing():
                has_wear = True
                wear_list += f"  {item.show(showEV, showNotes)}\n"
            if item.isWielding():
                has_wield = True
                wield_list += f"  {item.show(showEV, showNotes)}\n"
            elif item.isContainer():
                container_list.append(item)
            elif item.isEquipment():
                has_equipment = True
                equip_list += f"  {item.show(showEV, showNotes)}\n"
            elif item.isTreasure():
                has_treasure = True
                treasure_list += f"  {item.show(showEV, showNotes)}\n"
        if not self.coin.empty():
            has_treasure = True
            treasure_list += f"{self.coin.show(showEV)}\n"
        inventory = (wear_list if has_wear else '') + \
                    (wield_list if has_wield else '')
        container_list.sort()
        for item in container_list:
            inventory += item.showContents()
        inventory += (equip_list if has_equipment else '') + \
                     (treasure_list if has_treasure else '')
        return inventory

