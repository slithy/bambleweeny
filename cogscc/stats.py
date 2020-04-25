from cogscc.funcs.dice import roll
from utils.constants import STAT_ABBREVIATIONS
from cogscc.models.errors import InvalidArgument


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
            success = f"Success against CL{total-cb}!"
        elif total > cb + cl:
            success = f"Success (CL{cl})! :grinning:"
        else:
            success = f"Failure ({total-cb})" if name == 'secret_check' else "Failure! :scream:"

        # Abbreviated result, used for secret GM checks
        if name == 'secret_check':
            return f"{success}"

        # Long-form result for normal checks
        known_cl = f"against challenge level {cl}" if cl > 0 else ''
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

