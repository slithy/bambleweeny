from math import ceil
from utils.constants import STAT_ABBREVIATIONS
from utils.constants import RACE_NAMES
from utils.constants import CLASS_NAMES
from cogscc.base_character import BaseCharacter
from cogscc.stats import BaseStats
from cogscc.hitpoints import HP, Wound
from cogscc.equipment import EquipmentList
from cogscc.funcs.dice import roll
from cogscc.models.errors import InvalidArgument


class Character(BaseCharacter):
    def __init__(self, name: str, race: str, xclass: str, level: int):
        self.name = name
        self.setRace(race)
        self.setClass(xclass)
        self.setLevel(level)
        self.setAlignment('XX')
        self.stats = BaseStats(10,10,10,10,10,10)
        self.stats.setPrime(self.getClassPrime())
        self.hp = HP(1)
        self.equipment = EquipmentList()
        self.disabled = False

    def __to_json__(self):
        return { 'Name': self.name, 'Race': self.race, 'Class': self.xclass, 'Level': self.level,
                 'Alignment': self.alignment, 'HP': self.hp, 'Stats': self.stats, 'Equipment': self.equipment }

    @classmethod
    def __from_dict__(cls, d):
        c = Character(d['Name'], d['Race'], d['Class'], d['Level'])
        c.alignment = d['Alignment']
        c.hp = HP.__from_dict__(d['HP'])
        c.stats = BaseStats.__from_dict__(d['Stats'])
        c.equipment = EquipmentList.__from_dict__(d['Equipment'])
        c.disabled = False
        return c

    # Character generation

    def setRace(self, race: str):
        if race.title() not in RACE_NAMES:
            raise InvalidArgument(f"{race} is not a valid race.")
        self.race = race.title()
        
    def setClass(self, xclass: str):
        if xclass.title() not in CLASS_NAMES:
            raise InvalidArgument(f"{xclass} is not a valid class.")
        self.xclass = xclass.title()

    def setLevel(self, level: int):
        self.level = level

    def setAlignment(self, alignment: str):
        if alignment == 'XX':
            if self.xclass == 'Paladin':
                alignment = 'LG'
            elif self.xclass == 'Monk':
                alignment = 'LN'
            else:
                alignment = 'NN'
        elif alignment.upper() == 'N':
            alignment = 'NN'
        if len(alignment) != 2:
            raise InvalidArgument(f"Alignment must be specified as two letters: [L]awful/[N]eutral/[C]haotic + [G]ood/[N]eutral/[E]vil")
        law_axis = alignment[0].upper()
        evil_axis = alignment[1].upper()
        if law_axis != 'L' and law_axis != 'N' and law_axis != 'C':
            raise InvalidArgument("First letter of alignment must be [L]awful/[N]eutral/[C]haotic")
        if evil_axis != 'G' and evil_axis != 'N' and evil_axis != 'E':
            raise InvalidArgument("Second letter of alignment must be [G]ood/[N]eutral/[E]vil")
        if self.xclass == 'Assassin' and evil_axis == 'G':
            raise InvalidArgument("Assassins cannot be Good")
        if self.xclass == 'Monk' and law_axis != 'L':
            raise InvalidArgument("Monks must be Lawful")
        if self.xclass == 'Druid' and (law_axis != 'N' or evil_axis != 'N'):
            raise InvalidArgument("Druids must be Neutral")
        if self.xclass == 'Paladin' and (law_axis != 'L' or evil_axis != 'G'):
            raise InvalidArgument("Paladins must be Lawful Good")
        self.alignment = law_axis + evil_axis

    def getAlignment(self):
        if self.alignment == 'NN':
            return 'Neutral'
        law_axis = 'Neutral'
        evil_axis = 'Neutral'
        if self.alignment[0] == 'L':
            law_axis = 'Lawful'
        elif self.alignment[0] == 'C':
            law_axis = 'Chaotic'
        if self.alignment[1] == 'G':
            evil_axis = 'Good'
        elif self.alignment[1] == 'E':
            evil_axis = 'Evil'
        return law_axis + ' ' + evil_axis

    def assignStats(self, strength: int, dexterity: int, constitution: int, intelligence: int, wisdom: int, charisma: int, hp: int):
        self.stats.set(strength, dexterity, constitution, intelligence, wisdom, charisma)
        if hp != 0:
            self.hp = HP(hp)

    def getClassPrime(self):
        if self.xclass == 'Fighter' or self.xclass == 'Ranger':
            return 'str'
        elif self.xclass == 'Rogue' or self.xclass == 'Assassin':
            return 'dex'
        elif self.xclass == 'Barbarian' or self.xclass == 'Monk':
            return 'con'
        elif self.xclass == 'Wizard' or self.xclass == 'Illusionist':
            return 'int'
        elif self.xclass == 'Cleric' or self.xclass == 'Druid':
            return 'wis'
        elif self.xclass == 'Knight' or self.xclass == 'Paladin' or self.xclass == 'Bard':
            return 'cha'

    def setPrimes(self, first_prime: str, second_prime: str, third_prime: str):
        prime_1 = first_prime.lower()[:3]
        prime_2 = second_prime.lower()[:3]
        prime_3 = third_prime.lower()[:3]
        if prime_1 not in STAT_ABBREVIATIONS:
            raise InvalidArgument(f"{first_prime} is not a valid stat.")

        if self.race == 'Human':
            if second_prime == 'None':
                raise InvalidArgument(f"Human characters must specify two primes (in addition to class prime).")
            if prime_2 not in STAT_ABBREVIATIONS:
                raise InvalidArgument(f"{second_prime} is not a valid stat.")
            if third_prime == 'None':
                prime_3 = self.getClassPrime()
            elif prime_3 not in STAT_ABBREVIATIONS:
                raise InvalidArgument(f"{third_prime} is not a valid stat.")
        else:
            if second_prime == 'None':
                prime_2 = self.getClassPrime()
            elif prime_2 not in STAT_ABBREVIATIONS:
                raise InvalidArgument(f"{second_prime} is not a valid stat.")
            if third_prime != 'None':
                raise InvalidArgument(f"Non-human characters must specify one prime (in addition to class prime).")

        if prime_1 != self.getClassPrime() and prime_2 != self.getClassPrime() and prime_3 != self.getClassPrime():
            raise InvalidArgument(f"One of your primes must be your class prime ({self.getClassPrime()})")

        if prime_1 == prime_2 or prime_1 == prime_3 or prime_2 == prime_3:
            raise InvalidArgument(f"Can't set primes for a {self.race} {self.xclass} to {prime_1} {prime_2} {prime_3}")

        self.stats.setPrimes()
        self.stats.setPrime(prime_1)
        self.stats.setPrime(prime_2)
        self.stats.setPrime(prime_3)

    # Game mechanics

    def getAC(self):
        if self.xclass == 'Monk':
            try:
                ac = [ 10,11,12,12,13,13,13,14,14,14,14,15,15,15,15,16,16,16,16,16,17,17,17,17,17 ][self.level]
            except IndexError:
                # Level 24 is the max in CKG
                ac = 17
        else:
            ac = 10
        ac += self.equipment.ac + self.stats.getMod('dex')
        # Half-Orcs get +1 to AC if they are not wearing armour. This is a simplification which assumes
        # that only characters who cannot wear armour will not be wearing armour:
        if self.race == 'Half-Orc' and (self.xclass in { 'Monk', 'Wizard', 'Illusionist' }):
            ac += 1
        return ac

    def getBtH(self):
        if self.xclass == 'Fighter':
            return self.level
        elif self.xclass == 'Ranger' or self.xclass == 'Barbarian' or self.xclass == 'Monk' \
          or self.xclass == 'Knight' or self.xclass == 'Paladin'   or self.xclass == 'Bard':
            return self.level-1
        elif self.xclass == 'Cleric' or self.xclass == 'Druid':
            return ceil((self.level-1)/2)
        elif self.xclass == 'Rogue' or self.xclass == 'Assassin':
            return ceil((self.level-1)/3)
        elif self.xclass == 'Wizard' or self.xclass == 'Illusionist':
            return ceil((self.level-1)/4)
        else:
            raise InvalidArgument(f"{self.xclass} is not a valid class.")

    def levelUp(self):
        """Level up and roll new hit points."""
        hd: int
        if self.xclass == 'Barbarian' or self.xclass == 'Monk':
            hd = 12
        elif self.xclass == 'Fighter' or self.xclass == 'Ranger' or self.xclass == 'Knight' \
          or self.xclass == 'Paladin' or self.xclass == 'Bard':
            hd = 10
        elif self.xclass == 'Cleric' or self.xclass == 'Druid':
            hd = 8
        elif self.xclass == 'Rogue' or self.xclass == 'Assassin':
            hd = 6
        elif self.xclass == 'Wizard' or self.xclass == 'Illusionist':
            hd = 4
        else:
            raise InvalidArgument(f"{self.xclass} is not a valid class.")
        con_mod = self.stats.getMod('con')
        result = [roll(f"1d{hd}{con_mod:+}", inline=True) for _ in range(1)]
        total = result[0].total
        if total < 1:
            total = 1
        self.hp.max += total
        self.hp.current += total
        self.level += 1
        hptxt = 'hit points'
        if total == 1:
            hptxt = 'hit point'
        return f"{self.name} levels up! :partying_face:\n" + \
               f":game_die: {result[0].skeleton}\n" + \
               f"{self.name} advances to level {self.level} and gains {total} {hptxt} (total hp: {self.hp.max})."

    def energyDrain(self, num_levels: int = 1):
        new_hp = int((self.hp.max*(self.level-num_levels)/self.level)+0.5)
        self.hp.max = new_hp
        if self.hp.current > new_hp:
            self.hp.current = new_hp
        self.level -= num_levels
        if self.level < 1:
            self.hp.wound = Wound.DEAD
            return f"All of {self.name}'s life energy has been drained! :scream:\n{self.name} is a dead withered husk. :skull:"
        else:
            return f"{self.name}'s life energy has been drained! :scream:\n{self.name} is reduced to level {self.level}. {self.hp}"

    def search(self, check, bonus):
        level = 0
        bonus = 0
        stat = 'wis'
        message = ''
        if check == 'search':
            message = f"{self.name} searches the area."
            level = self.level
            if self.race == 'Elf':
                bonus = 2
        elif check == 'listen':
            message = f"{self.name} listens attentively."
            if self.xclass in [ 'Rogue', 'Assassin' ]:
                level = self.level
            if self.race in [ 'Elf', 'Half-Elf' ]:
                bonus = 2
            elif self.race == 'Gnome':
                bonus = 3
        elif check == 'smell':
            message = f"{self.name} sniffs the air."
            stat = 'con'
            if self.race == 'Half-Orc':
                level = self.level
                bonus = 2
        elif check == 'traps':
            message = f"{self.name} searches for traps."
            if self.xclass in [ 'Rogue', 'Assassin' ]:
                level = self.level
                stat = 'int'
            elif self.xclass == 'Ranger':
                level = self.level
            if self.race in [ 'Elf', 'Half-Elf' ]:
                bonus = 2
        elif check == 'track':
            message = f"{self.name} searches for tracks."
            if self.xclass == 'Ranger':
                level = self.level
            if self.race == 'Half-Orc':
                bonus = 2
        else:
            raise InvalidArgument(f"{self.name} doesn't know how to {check}")
        result = self.stats.siegeCheck('secret_check', level, stat, bonus, 0)
        return (message,f"{self.name} makes a {check} check: {result}")

    # Show character

    def showShortSummary(self):
        return f"{self.name}     **AC:** {self.getAC()} {self.hp}"

    def showSummary(self, message: str = ""):
        return f"{message}{self.name} the {self.race} {self.xclass} Level {self.level}"

    def showCharacter(self, message: str = ""):
        return f"{self.name}, {self.race} {self.xclass}, {self.getAlignment()}, Level {self.level} {message}\n" + \
               f"**AC:** {self.getAC()}  **BtH:** {self.getBtH():+}  {self.hp}\n" + \
               f"{self.stats}"

    def showHp(self):
        num_moons = int(self.hp.max/4 + 0.75)
        current = 0 if self.hp.current < 0 else self.hp.current
        moons = ''
        for i in range(num_moons):
            if current == 0:
                moons += ':new_moon:'
            elif current == 1:
                moons += ':waning_crescent_moon:'
                current = 0
            elif current == 2:
                moons += ':last_quarter_moon:'
                current = 0
            elif current == 3:
                moons += ':waning_gibbous_moon:'
                current = 0
            else:
                moons += ':full_moon:'
                current -= 4
        return f"{self.hp}\n{moons}"

    # Manage inventory

    def showInventory(self, showNotes: bool = False):
        inventory = self.equipment.getInventory(False, showNotes)
        return inventory if inventory else f"{self.name} is not carrying anything."

    def addEquipment(self, description: str, d: dict):
        return f"{self.name} {self.equipment.add(description, d)}"

    def addWeapon(self, description: str, d: dict):
        return f"{self.name} {self.equipment.addWeapon(description, d)}"

    def wield(self, description: str):
        return f"{self.equipment.wield(self.name, description)}"

    def addWearable(self, description: str, d: dict):
        return f"{self.name} {self.equipment.addWearable(description, d)}"

    def wear(self, description: str, location: str = ''):
        return f"{self.equipment.wear(self.name, description, location)}"

    def takeOff(self, description: str):
        return f"{self.name} {self.equipment.takeOff(description)}"

    def addContainer(self, description: str, d: dict):
        return f"{self.name} {self.equipment.addContainer(description, d)}"

    def give(self, count: int, description: str, recipient):
        if recipient is self:
            return "Only crazy people give things to themselves."
        else:
            e = self.equipment.pop(description, count)
            try:
                recipient.equipment.push(e)
            except UniqueItem:
                self.equipment.push(e)
                return f"{recipient.name} already has an item like {e.show()} with different properties"
            return f"{self.name} gives {e.show()} to {recipient.name}"

    def dropEquipment(self, description: str, count: int):
        return f"{self.name} {self.equipment.drop(description, count)}"

    def managePurse(self, denomination: str, amount: int):
        if amount == 0:
            return f"{self.name} gets out their purse, then changes their mind and puts it away again."
        elif amount > 0:
            return f"{self.name} {self.equipment.addCoin(amount, denomination)}"
        else:
            return f"{self.name} {self.equipment.dropCoin(-amount, denomination)}"

    def gmNote(self, item, description):
        if description:
            return f"The Castle Keeper adds a secret note to {self.equipment.gmNote(item, description)}"
        else:
            return f"{self.equipment.gmNote(item)}"

