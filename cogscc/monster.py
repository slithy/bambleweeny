from cogscc.funcs.dice import roll

class Monster:
    def __init__(self, name: str, init_mod: int):
        self.name = name
        self.init_mod = init_mod

    async def rollForInitiative(self, ctx):
        result = [roll(f"2d6{self.init_mod:+}", inline=True) for _ in range(1)]
        init = result[0].total
        await ctx.send(f":game_die: {self.name} rolls 2d6{self.init_mod:+} = {init}")
        return init
