from cogscc.funcs.dice import roll

class BaseCharacter:
    def getName(self):
        return self.name

    def getLevel(self):
        return self.level

    def getHp(self):
        return self.hp

    def isMatchName(self, name: str):
        return self.name.lower().startswith(name.lower())

    def isActive(self):
        return self.getHp().current > 0

    def inactiveStatus(self):
        return f"{self.getHp().bleed(self.getName())}\n"

    # Game mechanics

    def siegeCheck(self, stat: str, bonus: int, cl: int):
        return self.stats.siegeCheck(self.getName(), self.getLevel(), stat, bonus, cl)

    # Combat

    def rollForInitiative(self):
        dex_mod = self.stats.getMod('dex')
        result = [roll(f"2d6{dex_mod:+}", inline=True) for _ in range(1)]
        init = result[0].total
        return (init, f":game_die: {self.getName()} rolls 2d6{dex_mod:+} = {init}\n")

    # Wounds and healing

    def damage(self, dmg: str):
        dmg_roll = ''
        dmg_amt: int
        try:
            int(dmg)
            dmg_amt = int(dmg)
        except ValueError:
            result = [roll(f"{dmg}", inline=True) for _ in range(1)]
            dmg_amt = result[0].total
            dmg_roll = f":game_die: {result[0].skeleton}\n"
        return f"{dmg_roll}{self.getHp().lose(self.getName(), dmg_amt)}"

    def heal(self, heal: str):
        heal_roll = ''
        heal_amt: int
        try:
            int(heal)
            heal_amt = int(heal)
        except ValueError:
            result = [roll(f"{heal}", inline=True) for _ in range(1)]
            heal_amt = result[0].total
            heal_roll = f":game_die: {result[0].skeleton}\n"
        return f"{heal_roll}{self.getHp().heal(self.getName(), heal_amt)}"

    def first_aid(self):
        all_mods = self.getLevel() + self.stats.getMod('con') + self.stats.getPrime('con')
        result = [roll(f"1d20{all_mods:+}", inline=True) for _ in range(1)]
        total = result[0].total
        success = total > 18
        check = f"{self.getName()} makes a Constitution check.\n:game_die: {result[0].skeleton}"
        return self.getHp().first_aid(self.getName(), check, success)

    def rest(self, duration: int):
        return self.getHp().rest(self.getName(), self.stats.getMod('con'), duration)

