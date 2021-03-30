import gc
from copy import copy
from cogscc.models.errors import *


# Helper function to check if a dictionary is trying to change the value of an attribute in an existing item
def isAttrDifferent(d: dict, attr: str, itemattr):
    return attr in d.keys() and d.get(attr) != itemattr


class Equipment:
    def __init__(self, description: str, count: int, ev: float, value: int, plural: str):
        # 1 cp is 1/500 of an EV, that's the lightest thing that can be carried
        if ev < 0.002:
            raise OutOfRange("Items with no appreciable EV: treat the EV as 1 per 10 items carried (PHB p.46)")
        if count < 1:
            raise OutOfRange("Number of items must be a positive integer.")
        if value < 0:
            raise OutOfRange("Value must be zero or a positive integer.")

        self.rename(description, plural)
        self.ev = ev
        self.count = count
        self.value = value
        self.gm_note = ''
        self.addTags()

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
            d['ev'] = float(self.ev)
        if self.value != 0:
            d['value'] = self.value
        if self.gm_note:
            d['gm_note'] = self.gm_note
        return d

    def __str__(self):
        return self.__to_json__().__str__()

    @classmethod
    def __from_dict__(cls, d):
        ev = d.get('ev', 1)
        e = cls(d['description'], d.get('count', 1), ev if ev >= 0.002 else 1, d.get('value', 0), d.get('plural', ''))
        e.__from_dict_super__(d)
        return e

    def __from_dict_super__(e, d):
        e.article = d.get('article', e.defaultArticle())
        e.gm_note = d.get('gm_note', '')

    def isMarkedAsDropped(self):
        return self.description.find("[dropped]") != -1

    def addTags(self):
        self.tags = set()
        pass

    def lower(self):
        return self.description.lower()

    def hasTag(self, s: str):
        return s in self.tags

    def hasAnyTag(self, l: list):
        for i in l:
            if self.hasTag(i):
                return True
        return False

    def hasAllTags(self, l: list):
        for i in l:
            if not self.hasTag(i):
                return False
        return True

    def _anyInDescription(self, s: list):
        lowerDescription = self.lower()
        for i in s:
            if i in lowerDescription:
                return True
        return False

    def defaultArticle(self):
        return 'an' if self.description[0].lower() in { 'a', 'e', 'i', 'o', 'u' } else 'a'

    def isPushable(self, e):
        return True if type(self) == type(e) and \
                          self.ev == e.ev and \
                       self.value == e.value and \
                     self.gm_note == e.gm_note else False

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
        if not self.isContainer():
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
            elif self.lower().endswith(('o','s','sh','ch','x','z')):
                desc = self.description + 'es'
            elif self.lower().endswith(('ay','ey','iy','oy','uy')):
                desc = self.description + 's'
            elif self.lower().endswith('y'):
                desc = self.description[:-1] + 'ies'
            else:
                desc = self.description + 's'
        elif self.article != '-':
            number = f"{self.article} "
        return f"{number}{desc}"

    def rename(self, description: str, plural: str):
        # Remove extra spaces
        self.description = " ".join(description.split())

        # Set article and plural
        self.article = ''
        for default_article in ['a','an','the','-']:
            if self.lower().startswith(default_article + ' '):
                self.article = default_article
                self.description = self.description[len(default_article)+1:]
        if not self.article:
            self.article = self.defaultArticle()
        self.plural = plural

    def edit(self, d: dict):
        warning = ''
        d.pop('contents', None)
        if 'description' in d:
            self.rename(d['description'], d.get('plural',''))
            d.pop('description')
        if 'type' in d:
            warning += f"type cannot be edited\n"
            d.pop('type')
        for key,value in d.items():
            if key in self.__dict__:
                t = type(self.__dict__[key])
                self.__dict__[key] = t(value)
            else:
                warning += f"{key} is not a property of {type(self)}\n"
        return warning

    def showDetail(self):
        d = self.__to_json__()
        result = f"**{d['description']}** "
        d.pop('description', None)
        d.pop('contents', None)
        d.pop('gm_note', None)
        d['ev'] = d.get('ev', 1.0)
        for (key, value) in sorted(d.items()):
            result += f"{key}:{value} "
        return result

    def show(self, options: list = []):
        if 'detail' in options:
            return self.showDetail()
        ev = f", EV {int(self.getEV() + 0.5)}" if 'ev' in options else ''
        value = f" ({self.value * self.count} gp)" if self.value > 0 else ''
        gm_note = ' :small_blue_diamond:' if 'gm_note' in options and self.gm_note else ''
        return f"{self.getDescription()}{ev}{value}{gm_note}"


class Wearable(Equipment):
    def __init__(self, description: str, ac: int, hands: int, ev: float, value: int):
        super().__init__(description, 1, ev, value, '')
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

    def isPushable(self, e):
        return False

    def isWearable(self):
        return True

    def isWearing(self):
        return self.is_worn

    def getEV(self):
        ev = self.ev-1 if self.is_worn else self.ev
        return ev if ev > 0 else 0

    def wear(self, location: str):
        self.removeFromContainer()
        self.is_worn = True
        self.location = location

    def takeOff(self):
        self.is_worn = False

    def show(self, options: list = []):
        if not self.is_worn or 'detail' in options:
            return super().show(options)
        else:
            loc = f", {self.location}" if self.location else ''
            ac = f", {self.ac:+} AC" if self.ac != 0 else ''
            ev = f", EV {int(self.getEV() + 0.5)}" if 'ev' in options else ''
            value = f" ({self.value} gp)" if self.value > 0 else ''
            notes = ' :small_blue_diamond:' if 'gm_note' in options and self.gm_note else ''
            return f"{self.getDescription()}{loc}{ac}{ev}{value}{notes}"


class Weapon(Equipment):
    def __init__(self, description: str, dmg: str, bth: int, hands: int, range: int, ev: float, value: int):
        super().__init__(description, 1, ev, value, '')
        self.damage = dmg
        self.bth = bth
        if hands < 1 or hands > 2:
            raise InvalidEquipmentAttribute(f"hands:{hands}")
        self.hands = hands
        self.range = range
        self.is_wielding = False


    def __to_json__(self):
        d = super().__to_json__()
        d['type'] = 'weapon'
        d['dmg'] = self.damage
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

    def addTags(self):
        super().addTags()

        if self._anyInDescription(["sword", "dagger", "club", "spear", "axe", "hammer"]):
            self.tags.add("melee")
        if self._anyInDescription(["dagger", "club", "spear", "hand axe", "throwing hammer", "javelin", "stone",
                                   "dart", "whip"]):
            self.tags.add("throw")
        if self._anyInDescription(["bow", "sling"]):
            self.tags.add("shoot")
        if self._anyInDescription(["arrow", "quarrel", "sling bullet"]):
            self.tags.add("ammo")

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

    def show(self, options: list = []):
        if not self.is_wielding or 'detail' in options:
            return super().show(options)
        else:
            dmg = f"{self.damage} dmg" if self.bth == 0 else f"BtH {self.bth:+}, {self.damage} dmg"
            range = f", range {self.range}'" if self.range > 0 else ""
            ev = f", EV {int(self.getEV() + 0.5)}" if 'ev' in options else ''
            value = f" ({self.value} gp)" if self.value > 0 else ''
            notes = ' :small_blue_diamond:' if 'gm_note' in options and self.gm_note else ''
            return f"{self.getDescription()}, {dmg}{range}{ev}{value}{notes}"


class Container(Equipment):
    def __init__(self, description: str, count: int, capacity: int, ev: float, value: int, plural: str):
        super().__init__(description, count, ev, value, plural)
        if capacity < 1:
            raise OutOfRange("Capacity must be a positive integer.")
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
    def __from_dict__(cls, equiplist, d):
        e = cls(d['description'], d.get('count', 1), d['capacity'], d.get('ev', 1.0), d.get('value', 0), d.get('plural', ''))
        e.__from_dict_super__(d)
        for equipitem in d.get('contents', []):
            EquipmentList.__from_dict_type__(e.contents, equipitem)
        equiplist.extend(e.contents)
        return e

    def __lt__(self, other):
        return self.description < other.description

    def isContainer(self):
        return True

    def isPushable(self, e):
        return False

    def put(self, item):
        if item.isContainer():
            raise NestedContainer(f"You try to put {item.show()} inside {self.show()}. This tears a hole in the fabric of space-time. You are sucked in and die. :skull:")
        elif item.getEV() > self.getCapacity():
            raise ContainerFull(f"{self.show()} does not have space for {item.show()}.")
        elif item.isWearing():
            item.takeOff()
        elif item.isWielding():
            item.unwield()
        elif item in self.contents:
            raise InvalidContainerItem(f"{item.show()} is already in {self.show()}.")
        else:
            item.removeFromContainer()
        self.contents.append(item)

    def getContents(self, options: list):
        return [ item.show(options) for item in self.contents ]

    def getCapacity(self):
        return self.capacity - sum([ item.ev for item in self.contents ])

    def getEV(self):
        return int(sum([ item.getEV() for item in self.contents ])/2) + (self.ev*self.count)

    def show(self, options: list = []):
        if 'detail' in options:
            return super().show(options)
        ev = f"  Capacity {self.capacity*self.count}, EV {int(self.getEV() + 0.5)}" if 'ev' in options else ''
        value = f" ({self.value * self.count} gp)" if self.value > 0 else ''
        gm_note = ' :small_blue_diamond:' if 'gm_note' in options and self.gm_note else ''
        bold = '**' if 'heading' in options else ''
        return f"{bold}{self.getDescription()}{bold}{ev}{value}{gm_note}"


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

    def __str__(self):
        return self.__to_json__().__str__()

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

    def show(self, options: list = []):
        total_ev = f" EV {int(self.getEV()+0.5)}" if 'ev' in options else ''
        coin = f"  :moneybag:{total_ev}\n"
        has_coin = False
        for den, amt in self.coin.items():
            if amt > 0:
                has_coin = True
                coin += f"  {amt} {den}"
        coin += '\n'
        return coin if has_coin else ''


class EquipmentList:
    def __init__(self):
        self.equipment = []
        self.coin = Coin()
        self.ac = 0

    def __to_json__(self):
        saveList = [ item for item in self.equipment if not item.isInContainer() ]
        return { 'items': saveList, 'coin': self.coin.coin }

    def __str__(self):
        out = f"coin: {self.coin}\nac: {self.ac}\n"
        for item in self.equipment:
            out += item.__str__() + "\n"
        return out


    @classmethod
    def __from_dict__(cls, d):
        e = EquipmentList()
        for equipitem in d['items']:
            EquipmentList.__from_dict_type__(e.equipment, equipitem)
        e.coin = Coin.__from_dict__(d.get('coin'))
        e.recalculateAC()
        return e

    @classmethod
    def __from_dict_type__(cls, equiplist: list, equipitem: dict):
        type = equipitem.get('type', 'normal')
        if type == 'wearable':
            equiplist.append(Wearable.__from_dict__(equipitem))
        elif type == 'weapon':
            equiplist.append(Weapon.__from_dict__(equipitem))
        elif type == 'container':
            equiplist.append(Container.__from_dict__(equiplist, equipitem))
        else:
            equiplist.append(Equipment.__from_dict__(equipitem))

    def find(self, description: str, exactMatch: bool = False, inlist: list = []):
        if not inlist:
            inlist = self.equipment
        num_results = 0
        found_item = -1
        # Search for exact matches first
        for item_no in range(len(inlist)):
            if inlist[item_no].lower() == description.lower():
                num_results = 1
                found_item = item_no
        # If we didn't find one, try partial matches at the start of the string
        if num_results == 0 and not exactMatch:
          for item_no in range(len(inlist)):
            if inlist[item_no].lower().startswith(description.lower()):
                num_results += 1
                found_item = item_no
        # If we still didn't find one, try partial matches anywhere in the string
        if num_results == 0 and not exactMatch:
          for item_no in range(len(inlist)):
            if description.lower() in inlist[item_no].lower():
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

    def getWieldedItems(self):
        out = []
        for item_no in range(len(self.equipment)):
            if self.equipment[item_no].isWielding():
                out.append(self.equipment[item_no])
        return out

    def swapWeapons(self):
        wi = self.getWieldedItems()
        if (len(wi)) != 2:
            raise NotAllowed("You are not wielding 2 weapons. I cannot swap them")
        idx0 = wi[0][1]
        idx1 = wi[1][1]
        self.equipment[idx1], self.equipment[idx0] = self.equipment[idx0], self.equipment[idx1]


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
        newitem = Equipment(description, count, float(d.get('ev',1)), int(d.get('value',0)), d.get('plural',''))
        if itemno < 0:
            self.equipment.append(newitem)
            return f"gets {newitem.show()}."
        elif not self.equipment[itemno].isPushable(newitem):
            raise UniqueItem(f"You already have {self.equipment[itemno].show()} but the type of item is different.")
        elif self.equipment[itemno].isInContainer():
            self.equipment[itemno].removeFromContainer()
        self.equipment[itemno].count += count
        return f"now has {self.equipment[itemno].show()}."

    def showDetail(self, description: str):
        itemno = self.find(description)
        if itemno < 0:
            raise ItemNotFound(f"{description} not found.")
        return self.equipment[itemno].showDetail()

    def edit(self, description: str, d: dict):
        itemno = self.find(description)
        if itemno < 0:
            raise ItemNotFound(f"{description} not found.")
        # Range checking
        if float(d.get('ev','1.0')) < 0.002:
            raise OutOfRange("ev must be a positive number.")
        if int(d.get('count','1')) < 1:
            raise OutOfRange("count must be a positive integer.")
        if int(d.get('value','0')) < 0:
            raise OutOfRange("value must be zero or a positive integer.")
        if int(d.get('capacity','1')) < 1:
            raise OutOfRange("capacity must be a positive integer.")
        if not 0 <= int(d.get('hands','1')) <= 2:
            raise OutOfRange(f"hands must be an integer between 0 and 2")
        w = self.equipment[itemno].edit(d)
        return f"{w}{self.equipment[itemno].showDetail()}"

    def rename(self, description: str, new_description: str, plural: str):
        itemno = self.find(description)
        if itemno < 0:
            raise ItemNotFound(f"{description} not found.")
        new_itemno = self.find(new_description)
        if new_itemno >= 0:
            raise UniqueItem(f"{self.equipment[new_itemno].show()} already exists.")
        oldname = self.equipment[itemno].show()
        self.equipment[itemno].rename(new_description,plural)
        return f"{oldname} shall henceforth be known as {self.equipment[itemno].show()}"

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

    def isPushable(self, description: str, e):
        itemno_src = self.find(description)
        if itemno_src < 0:
            raise ItemNotFound(f"You don't have any {description}.")
        itemno_dest = e.find(self.equipment[itemno_src].description, True)
        return itemno_dest < 0 or self.equipment[itemno_src].isPushable(self.equipment[itemno_dest])

    def push(self, e):
        itemno = self.find(e.description, True)
        if itemno < 0:
            self.equipment.append(e)
        elif not self.equipment[itemno].isPushable(e):
            raise UniqueItem()
        else:
            self.equipment[itemno].count += e.count 

    def pop(self, description: str, count: int = 1):
        itemno = self.find(description)
        if itemno < 0:
            raise ItemNotFound(f"You don't have any {description}.")
        elif count >= self.equipment[itemno].count:
            reply = ''
            if self.equipment[itemno].isWearing():
                self.equipment[itemno].takeOff()
                self.recalculateAC()
            elif self.equipment[itemno].isWielding():
                self.equipment[itemno].unwield()
            else:
                self.equipment[itemno].removeFromContainer()
            e = copy(self.equipment[itemno])
            del self.equipment[itemno]
        else:
            e = copy(self.equipment[itemno])
            self.equipment[itemno].count -= count
            e.count = count
        return e

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
        elif self.equipment[itemno].isWielding():
            self.equipment[itemno].unwield()
            reply = f"puts away {self.equipment[itemno].show()}."
        elif self.equipment[itemno].isInContainer():
            contdesc = self.equipment[itemno].removeFromContainer()
            contno = self.find(contdesc)
            reply = f"removes {self.equipment[itemno].show()} from {self.equipment[contno].show()}."
        else:
            raise NotWearingItem(f"You are not bearing {self.equipment[itemno].show()}.")
        return reply

    def addContainer(self, description: str, d: dict):
        for key in d.keys():
            if key not in ['name','count','capacity','ev','value','plural']:
                raise InvalidEquipmentAttribute(key)

        itemno = self.find(description, True)
        if itemno < 0:
            if not d.get('ev',''):
                raise MissingArgument(f"You need to specify the Encumbrance Value (EV) for {description}.")
            if not d.get('capacity',''):
                raise MissingArgument(f"You need to specify the capacity for {description}.")
            newitem = Container(description, d.get('count',1), int(d['capacity']), float(d['ev']), int(d.get('value',0)), d.get('plural',''))
            self.equipment.append(newitem)
            return f"gets {newitem.show()}."
        elif isAttrDifferent(d, 'capacity', self.equipment[itemno].capacity):
            raise ItemNotMutable(f"Capacity:{d.get('capacity')} is different from the capacity of {self.equipment[itemno].show()}")
        elif isAttrDifferent(d, 'ev', self.equipment[itemno].ev):
            raise ItemNotMutable(f"EV:{d.get('ev')} is different from the EV of {self.equipment[itemno].show(['ev'])}")
        elif isAttrDifferent(d, 'value', self.equipment[itemno].value):
            raise ItemNotMutable(f"Value:{d.get('value')} is different from the value of {self.equipment[itemno].show()}")
        else:
            self.equipment[itemno].count += d.get('count',1)
            return f"now has {self.equipment[itemno].show()}."

    def put(self, description: str, container: str):
        itemno = self.find(description)
        if itemno < 0:
            raise ItemNotFound(f"You don't have any {description}.")
        contno = self.find(container)
        if contno < 0:
            raise ItemNotFound(f"You don't have any {container}.")
        self.equipment[contno].put(self.equipment[itemno])
        return f"puts {self.equipment[itemno].show()} into {self.equipment[contno].show()}"

    def drop(self, description: str, count: int = 1):
        itemno = self.find(description)
        if itemno < 0:
            raise ItemNotFound(f"You don't have any {description}.")
        elif count >= self.equipment[itemno].count:
            reply = ''
            if self.equipment[itemno].isWearing():
                self.equipment[itemno].takeOff()
                self.recalculateAC()
            else:
                self.equipment[itemno].removeFromContainer()
            reply = f"drops {self.equipment[itemno].show()}."
            del self.equipment[itemno]
            return reply
        else:
            self.equipment[itemno].count -= count
            return f"now has {self.equipment[itemno].show()}."

    def markAsDropped(self, description: str):
        """This is useful when you throw an item and you do not want to completely drop it"""
        itemno = self.find(description)
        if itemno < 0:
            raise ItemNotFound(f"You don't have any {description}.")
        elif not self.equipment[itemno].isMarkedAsDropped():
            self.equipment[itemno].description += " [dropped]"
            if self.equipment[itemno].isWearing():
                self.equipment[itemno].takeOff()
                self.recalculateAC()
            elif self.equipment[itemno].isWielding():
                self.equipment[itemno].unwield()

            return f"leaves {self.equipment[itemno].show()} temporarily on the ground."
        else:
            raise ItemNotFound(f"{self.equipment[itemno].show()} was already dropped.")

    def pickUp(self, description: str):
        itemno = self.find(description)
        if itemno < 0:
            raise ItemNotFound(f"yo do not have any {description}.")
        elif not self.equipment[itemno].isMarkedAsDropped():
            raise ItemNotFound(f"{self.equipment[itemno].show()} is not temporarily dropped.")
        else:
            self.equipment[itemno].description = self.equipment[itemno].description.replace(" [dropped]", "")
            return f"re-equips {self.equipment[itemno].show()}."



    def addCoin(self, amount: int, denomination: str):
        self.coin.add(amount, denomination)
        return f"has {self.coin.current(denomination)}."

    def dropCoin(self, amount: int, denomination: str):
        self.coin.drop(amount, denomination)
        return f"has {self.coin.current(denomination)}."

    def getInventory(self, section: str = "", options: list = []):
        section_list = [ 'Wearing', 'Wielding' ]
        section_list.extend(sorted([item.description for item in self.equipment if item.isContainer()]))
        section_list.append('Carrying')

        if section and section.lower() != 'all':
            section_list.append('Treasure')
            sectionno = self.find(section, False, section_list)
            if sectionno < 0:
                raise InventorySectionNotFound(f"I don't know what you mean by \"{section}\" (not a container).")
            section_list = [section_list[sectionno]]
        section_dict = { key : list([]) for key in section_list }
        section_desc = { key : f"**{key}**\n" for key in section_list }

        for item in self.equipment:
            if item.isWearing() and 'Wearing' in section_dict:
                section_dict['Wearing'].append(item.show(options))
            elif item.isWielding() and 'Wielding' in section_dict:
                section_dict['Wielding'].append(item.show(options))
            elif not item.isWearing() and not item.isWielding() and not item.isContainer() and not item.isInContainer() and 'Carrying' in section_dict:
                section_dict['Carrying'].append(item.show(options))
            elif item.isContainer() and item.description in section_dict:
                section_desc[item.description] = f"{item.show(options + ['heading'])}\n"
                if section:
                    section_dict[item.description] = item.getContents(options)
            if item.isTreasure() and 'Treasure' in section_dict:
                section_dict['Treasure'].append(item.show(options))

        inventory = ''
        for section_key, item_list in section_dict.items():
            if not item_list:
                if len(section_dict) > 1 and section_key in [ 'Wearing','Wielding','Carrying','Treasure' ]:
                    continue
                elif section_key == 'Treasure' and not self.coin.empty():
                    continue
                elif section:
                    item_list.append('(Empty)')
            inventory += section_desc[section_key]
            for item in item_list:
                inventory += f"  {item}\n"

        if not self.coin.empty() and (not section or section.lower() == 'all' or 'Treasure' in section_dict):
            inventory += self.coin.show(options)

        return inventory
