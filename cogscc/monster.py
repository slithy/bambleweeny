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

