import random
from discord.ext import commands
from cogscc.funcs.dice import roll
from utils.constants import STAT_ABBREVIATIONS
from utils.constants import RACE_NAMES
from utils.constants import CLASS_NAMES


class BaseStats:
    def __init__(self, strength: int, dexterity: int, constitution: int, intelligence: int, wisdom: int, charisma: int):
        self.strength = strength
        self.dexterity = dexterity
        self.constitution = constitution
        self.intelligence = intelligence
        self.wisdom = wisdom
        self.charisma = charisma
        self.str_p = False
        self.dex_p = False
        self.con_p = False
        self.int_p = False
        self.wis_p = False
        self.cha_p = False

    @classmethod
    def from_dict(cls, d):
        return cls(**d)

    def to_dict(self):
        return {
            "strength": self.strength, "dexterity": self.dexterity, "constitution": self.constitution,
            "intelligence": self.intelligence, "wisdom": self.wisdom, "charisma": self.charisma,
            "str_p": self.str_p, "dex_p": self.dex_p, "con_p": self.con_p,
            "int_p": self.int_p, "wis_p": self.wis_p, "cha_p": self.cha_p
        }

    # ---------- main funcs ----------
    def set(self, strength: int, dexterity: int, constitution: int, intelligence: int, wisdom: int, charisma: int):
        if strength < 1 or dexterity < 1 or constitution < 1 or intelligence < 1 or wisdom < 1 or charisma < 1 or strength > 19 or dexterity > 19 or constitution > 19 or intelligence > 19 or wisdom > 19 or charisma > 19:
            raise ValueError(f"The valid range for stats is 1-19.")
        self.strength = strength
        self.dexterity = dexterity
        self.constitution = constitution
        self.intelligence = intelligence
        self.wisdom = wisdom
        self.charisma = charisma

    def setPrime(self, str_p: bool, dex_p: bool, con_p: bool, int_p: bool, wis_p: bool, cha_p: bool):
        self.str_p = str_p
        self.dex_p = dex_p
        self.con_p = con_p
        self.int_p = int_p
        self.wis_p = wis_p
        self.cha_p = cha_p

    def printPrime(self, is_prime):
        if is_prime:
            return ":small_blue_diamond:"
        else:
            return " "

    def get_mod(self, stat: str):
        abbr_stat = stat.lower()[:3]
        if abbr_stat not in STAT_ABBREVIATIONS:
            raise ValueError(f"{stat} is not a valid stat.")
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

    def __str__(self):
        return f"**STR**: {self.strength}{self.printPrime(self.str_p)}({self.get_mod('str'):+})  " \
               f"**DEX**: {self.dexterity}{self.printPrime(self.dex_p)}({self.get_mod('dex'):+})  " \
               f"**CON**: {self.constitution}{self.printPrime(self.con_p)}({self.get_mod('con'):+})  " \
               f"**INT**: {self.intelligence}{self.printPrime(self.int_p)}({self.get_mod('int'):+})  " \
               f"**WIS**: {self.wisdom}{self.printPrime(self.wis_p)}({self.get_mod('wis'):+})  " \
               f"**CHA**: {self.charisma}{self.printPrime(self.cha_p)}({self.get_mod('cha'):+})"

class Character(commands.Cog):
    def __init__(self, name: str, race: str, xclass: str, level: int):
        self.name = name
        self.setRace(race)
        self.setClass(xclass)
        self.setLevel(level)
        self.stats = BaseStats(10,10,10,10,10,10)

    def setRace(self, race: str):
        if race.title() not in RACE_NAMES:
            raise ValueError(f"{race} is not a valid race.")
        self.race = race.title()
        return
        
    def setClass(self, xclass: str):
        if xclass.title() not in CLASS_NAMES:
            raise ValueError(f"{xclass} is not a valid class.")
        self.xclass = xclass.title()
        return

    def setLevel(self, level: int):
        self.level = level
        return

    def assignStats(self, strength: int, dexterity: int, constitution: int, intelligence: int, wisdom: int, charisma: int):
        self.stats.set(strength, dexterity, constitution, intelligence, wisdom, charisma)
        return

    def setPrime(self, first_prime: str, second_prime: str):
        prime_1 = first_prime.lower()[:3]
        prime_2 = second_prime.lower()[:3]
        if prime_1 not in STAT_ABBREVIATIONS:
            raise ValueError(f"{first_prime} is not a valid stat.")

        if self.race == 'Human':
            if second_prime == 'None':
                raise ValueError(f"Human characters need to specify two primes (in addition to class prime).")
            if prime_2 not in STAT_ABBREVIATIONS:
                raise ValueError(f"{second_prime} is not a valid stat.")
        elif second_prime != 'None':
            raise ValueError(f"Non-human characters must specify only one prime (in addition to class prime).")

        if self.xclass == 'Fighter' or self.xclass == 'Ranger':
            prime_3 = 'str'
        elif self.xclass == 'Rogue' or self.xclass == 'Assassin':
            prime_3 = 'dex'
        elif self.xclass == 'Barbarian' or self.xclass == 'Monk':
            prime_3 = 'con'
        elif self.xclass == 'Wizard' or self.xclass == 'Illusionist':
            prime_3 = 'int'
        elif self.xclass == 'Cleric' or self.xclass == 'Druid':
            prime_3 = 'wis'
        elif self.xclass == 'Knight' or self.xclass == 'Paladin' or self.xclass == 'Bard':
            prime_3 = 'cha'

        if prime_1 == prime_2 or prime_1 == prime_3:
            raise ValueError(f"{first_prime} was specified more than once!")
        elif prime_2 == prime_3:
            raise ValueError(f"{second_prime} was specified more than once!")

        str_p = False
        dex_p = False
        con_p = False
        int_p = False
        wis_p = False
        cha_p = False

        if prime_1 == 'str' or prime_2 == 'str' or prime_3 == 'str':
            str_p = True
        if prime_1 == 'dex' or prime_2 == 'dex' or prime_3 == 'dex':
            dex_p = True
        if prime_1 == 'con' or prime_2 == 'con' or prime_3 == 'con':
            con_p = True
        if prime_1 == 'int' or prime_2 == 'int' or prime_3 == 'int':
            int_p = True
        if prime_1 == 'wis' or prime_2 == 'wis' or prime_3 == 'wis':
            wis_p = True
        if prime_1 == 'cha' or prime_2 == 'cha' or prime_3 == 'cha':
            cha_p = True
        self.stats.setPrime(str_p, dex_p, con_p, int_p, wis_p, cha_p)

    async def showSummary(self, ctx, message: str = ""):
        await ctx.send(f"{message}{self.name} the {self.race} {self.xclass} Level {self.level}")
        return

    async def showCharacter(self, ctx):
        await ctx.send(f"{self.name}, {self.race} {self.xclass} Level {self.level}\n{self.stats}")
        return


class Characters(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.characters = {}

    @commands.command(name='generate')
    async def randStats(self, ctx):
        """Randomly generate the six base stats for a new character."""
        rolls = [roll("4d6kh3", inline=True) for _ in range(6)]
        #self.stats.set(rolls[0].total, rolls[1].total, rolls[2].total, rolls[3].total, rolls[4].total, rolls[5].total)
        stat_summary = '\n'.join(r.skeleton for r in rolls)
        total = sum([r.total for r in rolls])
        await ctx.send(f"{ctx.message.author.mention}\nGenerated random stats:\n{stat_summary}\nTotal = `{total}`")
        return

    @commands.command(name='create')
    async def create(self, ctx, name: str, race: str, xclass: str, level: int = 1):
        """Create a new character.
        Usage: !create 'Character Name' <race> <class> [<level>]"""
        if ctx.author in self.characters:
            await self.characters.get(ctx.author).showSummary(ctx, "You already have a character: ")
            return
        self.characters[ctx.author] = Character(name, race, xclass, level)
        await self.characters.get(ctx.author).showSummary(ctx, f"{ctx.author} is playing ")
        return

    @commands.command(name='suicide')
    async def suicide(self, ctx):
        """Kill your character (allowing you to create a new one)."""
        if ctx.author in self.characters:
            name = self.characters[ctx.author].name
            del self.characters[ctx.author]
            random_death = random.choice(["drinks poison and fails their saving throw",
                "is crushed by falling rocks", "opens a chest filled with poison gas",
                "is shot in the back by a comrade", "goes to explore the Tomb of Horrors and is never seen again", 
                "goes for a swim in a pool of acid", "didn't realise that the treasure chest was a mimic",
                "decides to split the party", "finds the cursed katana of seppuku",
                "decides to read the Necronomicon"])
            await ctx.send(f"{name} {random_death}. :skull:")
        else:
            await ctx.send(f"{ctx.author} does not have a character.")

    @commands.command(name='assign')
    async def assignStats(self, ctx, strength: int, dexterity: int, constitution: int, intelligence: int, wisdom: int, charisma: int):
        """Assign character's stats
        Usage: !assign <str> <dex> <con> <int> <wis> <cha>"""
        if ctx.author in self.characters:
            self.characters.get(ctx.author).assignStats(strength, dexterity, constitution, intelligence, wisdom, charisma)
            await self.characters.get(ctx.author).showCharacter(ctx)
        else:
            await ctx.send(f"{ctx.author} does not have a character.")

    @commands.command(name='prime')
    async def setPrime(self, ctx, first_prime: str, second_prime: str = 'None'):
        """Assign prime stats
        Usage: !assign <first prime> [<second prime>]"""
        if ctx.author in self.characters:
            self.characters.get(ctx.author).setPrime(first_prime, second_prime)
            await self.characters.get(ctx.author).showCharacter(ctx)
        else:
            await ctx.send(f"{ctx.author} does not have a character.")

    @commands.command(name='character')
    async def character(self, ctx):
        """Show your character's stats"""
        if ctx.author in self.characters:
            await self.characters.get(ctx.author).showCharacter(ctx)
        else:
            await ctx.send(f"{ctx.author} does not have a character.")

def setup(bot):
    bot.add_cog(Characters(bot))

