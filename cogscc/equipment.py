class Equipment:
    def __init__(self, description: str, ev: int, count: int = 1):
        self.description = description
        self.ev = ev
        self.count = count

class Container:
    def __init__(self, description: str, ev: int, capacity: int):
        self = Equipment(description, ev, 1)
        self.capacity = capacity
        self.contents = []

class Wearable(Equipment):
    def __init__(self, description: str, ac: int, ev: int):
        self = Equipment(description, ev, 1)
        self.ac = ac
        self.save = 0
        if 'ring of protection' in description.lower():
            self.save = ac

class Weapon(Equipment):
    def __init__(self, description: str, dmg: str, range: int, ev: int):
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
