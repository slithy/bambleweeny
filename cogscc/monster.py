from cogscc.funcs.dice import roll
from cogscc.stats import BaseStats
from cogscc.hitpoints import HP


class Monster:
    def __init__(self, name: str, d: dict):
        # Name
        self.name = name
        # AC
        self.ac = int(d.pop('ac'))
        # HD
        try:
            self.hd = f"{int(d['hd'])}d8"
            del d['hd']
        except ValueError:
            self.hd = d.pop('hd')
        self.count = d.pop('count', 1)
        # hp
        hp_list = d.pop('hp', [])
        if type(hp_list) == int:
            hp_list = [hp_list] * self.count
        elif len(hp_list) > self.count:
            del hp_list[self.count:]
        elif len(hp_list) < self.count:
            hp_list += self.rollHp(len(hp_list))
        self.hp = [ hp if type(hp) == HP else HP(hp) for hp in hp_list ]
        # Saves
        self.save = d.pop('save','P')
        self.getInt(d)
        self.stats = BaseStats(d.pop('str',10),d.pop('dex',10),d.pop('con',10), \
                               d.pop('int',10),d.pop('wis',10),d.pop('cha',10))
        if self.save.lower() == 'p':
            self.stats.setPrime('str')
            self.stats.setPrime('dex')
            self.stats.setPrime('con')
        elif self.save.lower() == 'm':
            self.stats.setPrime('int')
            self.stats.setPrime('wis')
            self.stats.setPrime('cha')
        # Everything else
        self.optional_stats = d

    def rollHp(self, already_rolled: int = 0):
        result = [roll(f"{self.hd}", inline=True) for _ in range(self.count-already_rolled)]
        for hp in result:
            print(f"{hp.skeleton}")
        return [hp.total for hp in result]

    def getInt(self, d: dict):
        # Specifying an intelligence value overrides the general range
        if 'int' in d:
            del d['intelligence']
        # Otherwise map the range to a value
        elif 'intelligence' in d:
            d['int'] = {
                'Animal': 1,
                'Inferior': 4,
                'Low': 7,
                'Average': 10,
                'High': 14,
                'Superior': 16,
                'Genius': 18,
                'Supra-Genius': 23,
                'Deific': 26
           }[d['intelligence']]

    def show(self):
        number = f"{self.count} "
        if self.count == 1:
            desc = self.name
            number = ""
        elif 'plural_name' in self.optional_stats:
            desc = self.optional_stats.get('plural_name')
        elif self.name.lower().endswith(('o','s','sh','ch','x','z')):
            desc = self.name + 'es'
        elif self.name.lower().endswith(('ay','ey','iy','oy','uy')):
            desc = self.name + 's'
        elif self.name.lower().endswith('y'):
            desc = self.name[:-1] + 'ies'
        else:
            desc = self.name + 's'
        return f"{number}{desc}"

    def statblock(self):
        statblock = self.show()
        statblock += f": **AC** {self.ac}, **HD** {self.hd}, **hp** "
        if self.count == 1:
            statblock += f"{self.hp[0].brief()},"
        else:
            for hp in self.hp:
                statblock += f"{hp.current},"
        if 'move' in self.optional_stats:
            statblock += f" **MV** {self.optional_stats['move']},"
        if 'attacks' in self.optional_stats:
            statblock += " **Attack**"
            for attack in self.optional_stats['attacks']:
                num = f"{attack[0]}× " if attack[0] > 1 else ""
                statblock += f" {num}{attack[1]} ({attack[2]}),"
        if 'special' in self.optional_stats:
            statblock += f" **Special** {self.optional_stats['special']},"
        statblock += f" **Save** {self.save},"
        if 'type' in self.optional_stats:
            statblock += f" **Type** {self.optional_stats['type']},"
        if 'size' in self.optional_stats:
            statblock += f" **Size** {self.optional_stats['size']},"
        if 'intelligence' in self.optional_stats:
            statblock += f" **Int** {self.optional_stats['intelligence']},"
        if 'alignment' in self.optional_stats:
            statblock += f" **AL** {self.optional_stats['alignment']},"
        if 'xp' in self.optional_stats:
            statblock += f" **XP** "
            xp_base = self.optional_stats['xp'][0]
            xp_hp = self.optional_stats['xp'][1]
            for hp in self.hp:
                statblock += f"{xp_base + (hp.max * xp_hp)},"
        statblock = statblock[:-1]
        return statblock

#    def __to_json__(self):
#        return { 'Name': self.name, 'Race': self.race, 'Class': self.xclass, 'Level': self.level,
#                 'Alignment': self.alignment, 'HP': self.hp, 'Stats': self.stats, 'Equipment': self.equipment }
#
#    @classmethod
#    def __from_dict__(cls, d):
#        c = Character(d['Name'], d['Race'], d['Class'], d['Level'])
#        c.alignment = d['Alignment']
#        c.hp = HP.__from_dict__(d['HP'])
#        c.stats = BaseStats.__from_dict__(d['Stats'])
#        c.equipment = EquipmentList.__from_dict__(d['Equipment'])
#        c.disabled = False
#        return c
#
#    def isActive(self):
#        return self.hp.current > 0
#
#    async def inactiveStatus(self, ctx):
#        await ctx.send(f"{self.hp.bleed(self.name)}")
#
#    async def damage(self, ctx, dmg: str):
#        dmg_roll = ''
#        dmg_amt: int
#        try:
#            int(dmg)
#            dmg_amt = int(dmg)
#        except ValueError:
#            result = [roll(f"{dmg}", inline=True) for _ in range(1)]
#            dmg_amt = result[0].total
#            dmg_roll = f":game_die: {result[0].skeleton}\n"
#        await ctx.send(f"{dmg_roll}{self.hp.lose(self.name, dmg_amt)}")
#
#    async def heal(self, ctx, heal: str):
#        heal_roll = ''
#        heal_amt: int
#        try:
#            int(heal)
#            heal_amt = int(heal)
#        except ValueError:
#            result = [roll(f"{heal}", inline=True) for _ in range(1)]
#            heal_amt = result[0].total
#            heal_roll = f":game_die: {result[0].skeleton}\n"
#        await ctx.send(f"{heal_roll}{self.hp.heal(self.name, heal_amt)}")
#
#    async def first_aid(self, ctx):
#        all_mods = self.level + self.stats.getMod('con') + self.stats.getPrime('con')
#        result = [roll(f"1d20{all_mods:+}", inline=True) for _ in range(1)]
#        total = result[0].total
#        success = total > 18
#        check = f"{self.name} makes a Constitution check.\n:game_die: {result[0].skeleton}"
#        result = self.hp.first_aid(self.name, check, success)
#        await ctx.send(f"{result}")
#
#    def rest(self, duration: int):
#        return self.hp.rest(self.name, self.stats.getMod('con'), duration)
#
#    async def siegeCheck(self, ctx, stat: str, bonus: int, cl: int):
#        await ctx.send(self.stats.siegeCheck(self.name, self.level, stat, bonus, cl))
#
#    async def rollForInitiative(self, ctx):
#        dex_mod = self.stats.getMod('dex')
#        result = [roll(f"2d6{dex_mod:+}", inline=True) for _ in range(1)]
#        init = result[0].total
#        await ctx.send(f":game_die: {self.name} rolls 2d6{dex_mod:+} = {init}")
#        return init
#
