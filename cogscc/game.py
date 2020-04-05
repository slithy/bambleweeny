import random
import time
import json
from os.path import basename
from discord.ext import commands
from cogscc.character import Character
from cogscc.monster import Monster
from cogscc.models.errors import NotAllowed


class ToJson(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, "__to_json__"):
            return obj.__to_json__()
        return json.JSONEncoder.default(self, obj)


class Game(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.gm_roles = [ 'Castle Keeper', 'Game Master', 'Dungeon Master' ]
        self.characters = {}
        self.monsters = []

    def gm_only(self, ctx):
        for role in ctx.author.roles:
            if role.name in self.gm_roles:
                return
        raise NotAllowed(f"Only the Game Master can do that!")

    @commands.command(name='load')
    async def loadJson(self, ctx, filename: str = 'characters.json'):
        """Load characters from a JSON-formatted file."""
        self.gm_only(ctx)
        with open(f"/save/{basename(filename)}", 'r') as f:
            chars = json.load(f)
            for player, character in chars.items():
                self.characters[player] = Character.__from_dict__(character)
        await ctx.send(f"Characters loaded from {filename}")

    @commands.command(name='save')
    async def saveJson(self, ctx, filename: str = 'characters.json'):
        """Save characters to a file in JSON format."""
        with open(f"/save/{basename(filename)}", 'w') as f:
            json.dump(self.characters, f, cls=ToJson)
        ts = time.gmtime()
        timestamp = time.strftime("%Y%m%d%H%M%S", ts)
        filename_backup = f"{basename(filename)}.{timestamp}"
        with open(f"/save/{filename_backup}", 'w') as f:
            json.dump(self.characters, f, cls=ToJson)
        await ctx.send(f"Characters saved as {filename_backup}")

    @commands.command(name='generate')
    async def genStats(self, ctx):
        """Randomly generate the six base stats for a new character."""
        await Character.genStats(ctx)

    @commands.command(name='create')
    async def create(self, ctx, name: str, race: str, xclass: str, level: int = 1):
        """Create a new character.
        Usage: !create 'Character Name' <race> <class> [<level>]"""
        player = str(ctx.author)
        if player in self.characters:
            await self.characters.get(player).showSummary(ctx, "You already have a character: ")
            return
        self.characters[player] = Character(name, race, xclass, level)
        await self.characters.get(player).showSummary(ctx, f"{player} is playing ")
        return

    @commands.command(name='suicide')
    async def suicide(self, ctx):
        """Kill your character (allowing you to create a new one)."""
        player = str(ctx.author)
        if player in self.characters:
            name = self.characters[player].name
            del self.characters[player]
            random_death = random.choice(["drinks poison and fails their saving throw",
                "is crushed by falling rocks", "opens a chest filled with poison gas",
                "is shot in the back by a comrade", "goes to explore the Tomb of Horrors and is never seen again", 
                "goes for a swim in a pool of acid", "didn't realise that the treasure chest was a mimic",
                "decides to split the party", "finds the cursed katana of seppuku",
                "decides to read the Necronomicon"])
            await ctx.send(f"{name} {random_death}. :skull:")
        else:
            await ctx.send(f"{player} does not have a character.")

    @commands.command(name='assign')
    async def assignStats(self, ctx, strength: int, dexterity: int, constitution: int, intelligence: int, wisdom: int, charisma: int):
        """Assign character's stats
        Usage: !assign <str> <dex> <con> <int> <wis> <cha>"""
        player = str(ctx.author)
        if player in self.characters:
            self.characters.get(player).assignStats(strength, dexterity, constitution, intelligence, wisdom, charisma)
            await self.characters.get(player).showCharacter(ctx)
        else:
            await ctx.send(f"{player} does not have a character.")

    @commands.command(name='prime')
    async def setPrimes(self, ctx, first_prime: str, second_prime: str = 'None', third_prime: str = 'None'):
        """Assign prime stats
        Humans have three prime attributes; non-humans have two. One prime attribute is
        determined by the character class and will be assigned automatically (it is
        not necessary to pass it to the command).
        Usage: !assign <first prime> [<second prime>]"""
        player = str(ctx.author)
        if player in self.characters:
            self.characters.get(player).setPrimes(first_prime, second_prime, third_prime)
            await self.characters.get(player).showCharacter(ctx)
        else:
            await ctx.send(f"{player} does not have a character.")

    @commands.command(name='character', aliases=['char'])
    async def character(self, ctx):
        """Show your character's stats"""
        player = str(ctx.author)
        if player in self.characters:
            await self.characters.get(player).showCharacter(ctx)
        else:
            await ctx.send(f"{player} does not have a character.")

    @commands.command(name='check', aliases=['ck'])
    async def siegeCheck(self, ctx, stat: str, bonus: int = 0, cl: int = 0):
        """Make an ability check
        Usage: !check <stat> [<bonus>] [<challenge level>]"""
        player = str(ctx.author)
        if player in self.characters:
            await self.characters.get(player).siegeCheck(ctx, stat, bonus, cl)
        else:
            await ctx.send(f"{player} does not have a character.")

    @commands.command(name='party')
    async def allCharacters(self, ctx, param: str = 'None'):
        """Show stats for all characters
        Usage: !party [stats]"""
        for player, character in self.characters.items():
            if param == 'stats':
                await character.showCharacter(ctx, f"({player})")
            else:
                await character.showSummary(ctx, f"{player} is playing ")

    @commands.command(name='initiative', aliases=['init'])
    async def rollForInitiative(self, ctx):
        initList = []
        for player, character in self.characters.items():
            init = await character.rollForInitiative(ctx)
            initList.append((init, character.name))
        for monster in self.monsters:
            init = await monster.rollForInitiative(ctx)
            initList.append((init, monster.name))
        initOrder = "**Initiative Order**\n"
        for i in sorted(initList, reverse=True):
            initOrder += f"{i[0]}\t{i[1]}\n"
        await ctx.send(initOrder)

    ### GM-only commands ###

    @commands.command(name='level_up')
    async def levelUp(self, ctx, player):
        """Levels up the character belonging to the specified player"""
        self.gm_only(ctx)
        await self.characters[player].levelUp(ctx)

    @commands.command(name='euthanise')
    async def deleteCharacter(self, ctx, player):
        """Ends the suffering of the character belonging to the specified player"""
        self.gm_only(ctx)
        del self.characters[player]
        await ctx.send(f"The suffering of {player}'s character has been ended.")

    @commands.command(name='monster_reset', aliases=['mr'])
    async def monsterReset(self, ctx):
        """Resets monsters at the start of a new combat"""
        self.gm_only(ctx)
        self.monsters = []
        await ctx.send(f"Monsters reset.")

    @commands.command(name='monster_add', aliases=['ma'])
    async def monsterAdd(self, ctx, name: str, init_mod = 0):
        """Adds a new monster to the combat"""
        self.gm_only(ctx)
        self.monsters.append(Monster(name, init_mod))
        await ctx.send(f"Added {name} to combat.")

def setup(bot):
    bot.add_cog(Game(bot))
