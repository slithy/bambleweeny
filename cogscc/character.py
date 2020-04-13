from enum import Enum
from math import ceil
from cogscc.funcs.dice import roll
from utils.constants import STAT_ABBREVIATIONS
from utils.constants import RACE_NAMES
from utils.constants import CLASS_NAMES
from cogscc.models.errors import InvalidArgument
from cogscc.models.errors import AmbiguousMatch
from cogscc.equipment import Equipment
from cogscc.equipment import Container
from cogscc.equipment import Wearable
from cogscc.equipment import Weapon


##### STATS #####

class BaseStats:
    def __init__(self, strength: int, dexterity: int, constitution: int,
                       intelligence: int, wisdom: int, charisma: int,
                       str_p: bool = False, dex_p: bool = False, con_p: bool = False,
                       int_p: bool = False, wis_p: bool = False, cha_p: bool = False):
        self.set(strength, dexterity, constitution, intelligence, wisdom, charisma)
        self.setPrimes(str_p, dex_p, con_p, int_p, wis_p, cha_p)

    @classmethod
    def __from_dict__(cls, d):
        return cls(**d)

    def __to_json__(self):
        return {
            "strength": self.strength, "dexterity": self.dexterity, "constitution": self.constitution,
            "intelligence": self.intelligence, "wisdom": self.wisdom, "charisma": self.charisma,
            "str_p": self.str_p, "dex_p": self.dex_p, "con_p": self.con_p,
            "int_p": self.int_p, "wis_p": self.wis_p, "cha_p": self.cha_p
        }

    # ---------- main funcs ----------
    def set(self, strength: int, dexterity: int, constitution: int, intelligence: int, wisdom: int, charisma: int):
        if strength < 1 or dexterity < 1 or constitution < 1 or \
           intelligence < 1 or wisdom < 1 or charisma < 1 or \
           strength > 19 or dexterity > 19 or constitution > 19 or \
           intelligence > 19 or wisdom > 19 or charisma > 19:
            raise InvalidArgument(f"The valid range for stats is 1-19.")
        self.strength = strength
        self.dexterity = dexterity
        self.constitution = constitution
        self.intelligence = intelligence
        self.wisdom = wisdom
        self.charisma = charisma

    def setPrimes(self, str_p: bool = False, dex_p: bool = False, con_p: bool = False,
                        int_p: bool = False, wis_p: bool = False, cha_p: bool = False):
        self.str_p = str_p
        self.dex_p = dex_p
        self.con_p = con_p
        self.int_p = int_p
        self.wis_p = wis_p
        self.cha_p = cha_p

    def setPrime(self, prime: str):
        if prime == 'str':
            self.str_p = True
        if prime == 'dex':
            self.dex_p = True
        if prime == 'con':
            self.con_p = True
        if prime == 'int':
            self.int_p = True
        if prime == 'wis':
            self.wis_p = True
        if prime == 'cha':
            self.cha_p = True

    def printPrime(self, is_prime):
        if is_prime:
            return ":small_blue_diamond:"
        else:
            return " "

    def getMod(self, stat: str):
        abbr_stat = stat.lower()[:3]
        if abbr_stat not in STAT_ABBREVIATIONS:
            raise InvalidArgument(f"{stat} is not a valid stat.")
        stat_val = {
            'str': self.strength, 'dex': self.dexterity,
            'con': self.constitution, 'int': self.intelligence,
            'wis': self.wisdom, 'cha': self.charisma
        }[abbr_stat]
        if stat_val < 2:
            return -4
        elif stat_val < 4:
            return -3
        elif stat_val < 6:
            return -2
        elif stat_val < 9:
            return -1
        elif stat_val < 13:
            return 0
        elif stat_val < 16:
            return 1
        elif stat_val < 18:
            return 2
        else:
            return 3

    def getPrime(self, stat: str):
        abbr_stat = stat.lower()[:3]
        if abbr_stat not in STAT_ABBREVIATIONS:
            raise InvalidArgument(f"{stat} is not a valid stat.")
        stat_prime = {
            'str': self.str_p, 'dex': self.dex_p,
            'con': self.con_p, 'int': self.int_p,
            'wis': self.wis_p, 'cha': self.cha_p
        }[abbr_stat]
        if stat_prime:
            return 6
        else:
            return 0

    def siegeCheck(self, name: str, level: int, stat: str, bonus: int, cl: int):
        cb = 18
        mod = self.getMod(stat)
        prime = self.getPrime(stat)
        all_mods = level + mod + prime + bonus
        result = [roll(f"1d20{all_mods:+}", inline=True) for _ in range(1)]
        total = result[0].total
        if total > cb and cl == 0:
            margin = total - cb
            success = f"Success against CL{margin}!"
        elif total > cb + cl:
            success = f"Success (CL{cl})! :grinning:"
        else:
            success = f"Failure! :scream:"

        known_cl = ''
        if cl != 0:
            known_cl = f"against challenge level {cl}"
        bonuses = f"{level:+} for level"
        if mod != 0:
            bonuses = bonuses + f", {mod:+} modifier"
        if prime != 0:
            bonuses = bonuses + f", {prime:+} for prime attribute"
        if bonus != 0:
            bonuses = bonuses + f", {bonus:+} bonus"
        return f"{name} makes a {stat.upper()} check {known_cl}\nBonuses are {bonuses} = {all_mods:+}\n:game_die: {result[0].skeleton}\n{success}"

    def __str__(self):
        return f"**STR**: {self.strength}{self.printPrime(self.str_p)}({self.getMod('str'):+})  " \
               f"**DEX**: {self.dexterity}{self.printPrime(self.dex_p)}({self.getMod('dex'):+})  " \
               f"**CON**: {self.constitution}{self.printPrime(self.con_p)}({self.getMod('con'):+})  " \
               f"**INT**: {self.intelligence}{self.printPrime(self.int_p)}({self.getMod('int'):+})  " \
               f"**WIS**: {self.wisdom}{self.printPrime(self.wis_p)}({self.getMod('wis'):+})  " \
               f"**CHA**: {self.charisma}{self.printPrime(self.cha_p)}({self.getMod('cha'):+})"


##### HIT POINTS #####

class Wound(Enum):
    NORMAL = 1
    GRIEVOUS = 2
    MORTAL = 3
    DEAD = 4


class Bleeding(Enum):
    GRACE = 1
    BLEEDING = 2
    NOT_BLEEDING = 3


class HP:
    def __init__(self, max: int, current: int = 999, wound: Wound = Wound.NORMAL, bleeding = Bleeding.NOT_BLEEDING, conscious: bool = True):
        self.max = max
        self.current = max
        if current < max:
            self.current = current
        self.wound = wound
        self.bleeding = bleeding
        self.conscious = conscious

    @classmethod
    def __from_dict__(cls, d):
        hp = cls(**d)
        hp.wound = getattr(Wound, hp.wound)
        hp.bleeding = getattr(Bleeding, hp.bleeding)
        return hp

    def __to_json__(self):
        return {
            'max': self.max, 'current': self.current, 'wound': self.wound.name, 'bleeding': self.bleeding.name, 'conscious': self.conscious
        }

    # ---------- main funcs ----------
    def recover(self, name: str, hp: int):
        if self.current == self.max:
            return ''
        hp_text = f"{hp} hit points"
        if hp == 1:
           hp_text = "1 hit point"
        if self.current + hp <= self.max:
            self.current += hp
            return f"\n{name} recovers {hp_text}. :medical_symbol:  **HP**: {self.current}/{self.max}"
        else:
            self.current = self.max
            return f"\n{name} recovers to full strength. :medical_symbol:  **HP**: {self.current}/{self.max}"

    def rest(self, name: str, conMod: int, duration: int):
        if self.wound == Wound.DEAD:
            return f"{name} gets rigor mortis."
        result = ''
        if not self.conscious:
            self.conscious = True
            hours = [roll("1d6", inline=True) for _ in range(1)]
            result = f"{name} recovers consciousness after {hours[0].total} hours."
        if self.wound == Wound.MORTAL:
            self.wound = Wound.GRIEVOUS
            result += f"\n{name} is no longer mortally wounded."
            duration -= 1
        if duration > 0 and self.wound == Wound.GRIEVOUS:
            self.wound = Wound.NORMAL
            result += f"\n{name} is no longer greviously wounded."
            duration -= 1

        if duration > 0 and duration < 7:
            result += self.recover(name, duration)
            duration = 0
        elif duration > 0:
            result += self.recover(name, 7)
            duration -= 7

        if duration > 0:
            heal_rate = 1
            if conMod > 0:
                heal_rate += conMod
            result += self.recover(name, duration * heal_rate)

        return result

    def first_aid(self, name: str, status: str, success: bool):
        if self.wound == Wound.DEAD:
            return f"Unfortunately that doesn't really help. {name} is dead."
        if self.bleeding != Bleeding.NOT_BLEEDING and success:
            self.bleeding = Bleeding.NOT_BLEEDING
            return f"{status}\n{name} has stopped bleeding."
        elif self.bleeding != Bleeding.NOT_BLEEDING:
            return f"{status}\nFirst aid was unsuccessful. {name} is still bleeding."
        elif not self.conscious and success:
            self.conscious = True
            return f"{status}\n{name} has regained consciousness."
        elif not self.conscious:
            return f"{status}\nFirst aid was unsuccessful. {name} is still unconscious."
        else:
            return f"{name} is in a stable condition. Nothing more can be achieved with first aid."

    def heal(self, name: str, hp_healed: int):
        consequence = ''
        if self.wound == Wound.DEAD:
            consequence = f"Unfortunately that doesn't really help. {name} is dead."
        elif self.wound == Wound.MORTAL:
            if self.current + hp_healed > -6:
                hp_healed = -6 - self.current
            self.current += hp_healed
            consequence = f"{name} regains {hp_healed} hit points. :medical_symbol:  **HP**: {self.current}/{self.max}"
            if self.bleeding != Bleeding.NOT_BLEEDING:
                self.bleeding = Bleeding.NOT_BLEEDING
                consequence += f"\n{name} has stopped bleeding."
            if not self.conscious:
                self.conscious = True
                consequence += f"\n{name} regains consciousness."
            if self.current == -6:
                self.wound = Wound.GRIEVOUS
                consequence += f"\n{name} is grievously wounded."
        elif self.wound == Wound.GRIEVOUS:
            if self.current + hp_healed > 0:
                hp_healed = 0 - self.current
            self.current += hp_healed
            consequence = f"{name} regains {hp_healed} hit points. :medical_symbol:  **HP**: {self.current}/{self.max}"
            if not self.conscious:
                self.conscious = True
                consequence += f"\n{name} regains consciousness."
            if self.current == 0:
                self.wound = Wound.NORMAL
                consequence += f"\n{name} is no longer grievously wounded."
        elif self.current == self.max:
            consequence = f"{name} is already at full hit points."
            self.wound = Wound.NORMAL
            self.conscious = True
        else:
            if self.current + hp_healed > self.max:
                hp_healed = self.max - self.current
            self.current += hp_healed
            consequence = f"{name} regains {hp_healed} hit points. :medical_symbol:  **HP**: {self.current}/{self.max}"
            if not self.conscious:
                self.conscious = True
                consequence += f"\n{name} regains consciousness."
        return consequence

    def lose(self, name: str, dmg: int):
        dmgtxt = f"{dmg} points"
        if dmg < 1:
            return f"{name} takes no damage!"
        elif dmg == 1:
            dmgtxt = "1 point"
        self.current -= dmg
        consequence = f"{name} takes {dmgtxt} of damage! :scream:  **HP**: {self.current}/{self.max}"
        if self.wound == Wound.DEAD:
            consequence += f"\n{name} does not care because they are already dead."
        elif self.current < -9:
            consequence += f"\n{name} dies! :skull:"
            self.wound = Wound.DEAD
        elif self.current < -6 and self.wound != Wound.MORTAL:
            consequence += f"\n{name} is mortally wounded! :grimacing:"
            self.wound = Wound.MORTAL
            self.bleeding = Bleeding.GRACE
        elif self.current < 0 and self.wound == Wound.NORMAL:
            consequence += f"\n{name} is grievously wounded! :grimacing:"
            self.wound = Wound.GRIEVOUS
        if self.conscious and self.current < 1 and self.wound != Wound.DEAD:
            consequence += f"\n{name} loses consciousness! :dizzy_face:"
            self.conscious = False
        return consequence

    def bleed(self, name):
        status = ''
        if self.wound == Wound.DEAD:
            status = f"{name} is dead."
        elif self.conscious:
            status = f"{name} is conscious but too badly wounded to act."
        elif self.wound == Wound.MORTAL:
            status = f"{name} is mortally wounded, unconscious and bleeding out."
            if self.bleeding == Bleeding.GRACE:
                self.bleeding = Bleeding.BLEEDING
            elif self.bleeding == Bleeding.BLEEDING:
                self.current -= 1
                status += f"\n{name} loses 1 hit point. :scream:  **HP**: {self.current}/{self.max}"
            elif self.bleeding == Bleeding.NOT_BLEEDING:
                status = f"{name} is mortally wounded and unconscious but the bleeding has stopped."
            if self.current < -9:
                status += f"\n{name} dies! :skull:"
                self.wound = Wound.DEAD
        else:
            status = f"{name} is unconscious."
        return status

    def __str__(self):
        if self.conscious:
            unconscious = ':grimacing:'
        else:
            unconscious = '(unconscious) :dizzy_face:'
        if self.wound == Wound.NORMAL and not self.conscious:
            wounded = f"{unconscious}"
        elif self.wound == Wound.GRIEVOUS:
            wounded = f"Grievously wounded {unconscious}"
        elif self.wound == Wound.MORTAL:
            wounded = f"Mortally wounded {unconscious}"
        elif self.wound == Wound.DEAD:
            wounded = f"DEAD :skull:"
        else:
            wounded = ''
        return f"**HP**: {self.current}/{self.max} {wounded}"


##### CHARACTER #####

class Character:
    def __init__(self, name: str, race: str, xclass: str, level: int):
        self.name = name
        self.setRace(race)
        self.setClass(xclass)
        self.setLevel(level)
        self.setAlignment('XX')
        self.stats = BaseStats(10,10,10,10,10,10)
        self.stats.setPrime(self.getClassPrime())
        self.hp = HP(1)
        self.equipment = []
        self.wearing = []

    def __to_json__(self):
        return { 'Name': self.name, 'Race': self.race, 'Class': self.xclass, 'Level': self.level,
                 'Alignment': self.alignment, 'HP': self.hp, 'Stats': self.stats }

    @classmethod
    def __from_dict__(cls, d):
        c = Character(d['Name'], d['Race'], d['Class'], d['Level'])
        c.alignment = d['Alignment']
        c.hp = HP.__from_dict__(d['HP'])
        c.stats = BaseStats.__from_dict__(d['Stats'])
        return c

    @classmethod
    async def genStats(cls, ctx):
        """Randomly generate the six base stats for a new character."""
        rolls = [roll("4d6kh3", inline=True) for _ in range(6)]
        #self.stats.set(rolls[0].total, rolls[1].total, rolls[2].total, rolls[3].total, rolls[4].total, rolls[5].total)
        stat_summary = '\n:game_die: '.join(r.skeleton for r in rolls)
        total = sum([r.total for r in rolls])
        await ctx.send(f"{ctx.message.author.mention}\nGenerated random stats:\n:game_die: {stat_summary}\nTotal = `{total}`")

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

    async def levelUp(self, ctx):
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
        await ctx.send(f"{self.name} levels up! :partying_face:\n:game_die: {result[0].skeleton}\n{self.name} advances to level {self.level} and gains {total} {hptxt} (total hp: {self.hp.max}).")

    def isActive(self):
        return self.hp.current > 0

    async def inactiveStatus(self, ctx):
        await ctx.send(f"{self.hp.bleed(self.name)}")

    async def damage(self, ctx, dmg: str):
        dmg_roll = ''
        dmg_amt: int
        try:
            int(dmg)
            dmg_amt = int(dmg)
        except ValueError:
            result = [roll(f"{dmg}", inline=True) for _ in range(1)]
            dmg_amt = result[0].total
            dmg_roll = f":game_die: {result[0].skeleton}\n"
        await ctx.send(f"{dmg_roll}{self.hp.lose(self.name, dmg_amt)}")

    async def heal(self, ctx, heal: str):
        heal_roll = ''
        heal_amt: int
        try:
            int(heal)
            heal_amt = int(heal)
        except ValueError:
            result = [roll(f"{heal}", inline=True) for _ in range(1)]
            heal_amt = result[0].total
            heal_roll = f":game_die: {result[0].skeleton}\n"
        await ctx.send(f"{heal_roll}{self.hp.heal(self.name, heal_amt)}")

    async def first_aid(self, ctx):
        all_mods = self.level + self.stats.getMod('con') + self.stats.getPrime('con')
        result = [roll(f"1d20{all_mods:+}", inline=True) for _ in range(1)]
        total = result[0].total
        success = total > 18
        check = f"{self.name} makes a Constitution check.\n:game_die: {result[0].skeleton}"
        result = self.hp.first_aid(self.name, check, success)
        await ctx.send(f"{result}")

    def rest(self, duration: int):
        return self.hp.rest(self.name, self.stats.getMod('con'), duration)

    async def siegeCheck(self, ctx, stat: str, bonus: int, cl: int):
        await ctx.send(self.stats.siegeCheck(self.name, self.level, stat, bonus, cl))

    def findEquipment(self, description: str, exactMatch: bool = False):
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
            return item_no
        else:
            raise AmbiguousMatch(f"{description} matches more than one item, please be more specific.")

    async def addEquipment(self, ctx, description: str, ev: float, count: int):
        itemno = self.findEquipment(description, True)
        if itemno < 0:
            newitem = Equipment(description, ev, count)
            self.equipment.append(newitem)
            await ctx.send(f"{self.name} gets {newitem.show()}.")
        else:
            self.equipment[itemno].count += count 
            await ctx.send(f"{self.name} now has {self.equipment[itemno].show()}.")

    async def dropEquipment(self, ctx, description: str, count: int):
        itemno = self.findEquipment(description)
        if itemno < 0:
            await ctx.send(f"{self.name} doesn't have any {description}.")
        elif count >= self.equipment[itemno].count:
            await ctx.send(f"{self.name} drops {self.equipment[itemno].show()}")
            del self.equipment[itemno]
        else:
            self.equipment[itemno].count -= count
            await ctx.send(f"{self.name} now has {self.equipment[itemno].show()}.")

    async def showSummary(self, ctx, message: str = ""):
        await ctx.send(f"{message}{self.name} the {self.race} {self.xclass} Level {self.level}")

    async def showCharacter(self, ctx, message: str = ""):
        await ctx.send(f"{self.name}, {self.race} {self.xclass}, {self.getAlignment()}, Level {self.level} {message}\n**BtH:** {self.getBtH():+}  {self.hp}\n{self.stats}")

    async def showInventory(self, ctx):
        if self.equipment:
            equip_list = "**Equipment**\n"
            for item in self.equipment:
                equip_list += f"{item.show()}\n"
            await ctx.send(equip_list)

    async def rollForInitiative(self, ctx):
        dex_mod = self.stats.getMod('dex')
        result = [roll(f"2d6{dex_mod:+}", inline=True) for _ in range(1)]
        init = result[0].total
        await ctx.send(f":game_die: {self.name} rolls 2d6{dex_mod:+} = {init}")
        return init
