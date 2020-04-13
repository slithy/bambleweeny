class Equipment:
    def __init__(self, description: str, ev: float, count: int = 1):
        self.description = description
        self.ev = ev
        self.count = count

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
