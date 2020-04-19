import random
import time
import json
from os.path import basename
from discord.ext import commands
from cogscc.character import Character
from cogscc.monster import Monster
from cogscc.models.errors import AmbiguousMatch
from cogscc.models.errors import CharacterNotFound
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

    # Save, create and destroy characters

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
        Usage: !create "Character Name" <race> <class> [<level>]"""
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
            random_death = random.choice(["drinks poison and fails their saving throw",
                "is crushed by falling rocks", "opens a chest filled with poison gas",
                "is shot in the back by a comrade", "goes to explore the Tomb of Horrors and is never seen again", 
                "goes for a swim in a pool of acid", "didn't realise that the treasure chest was a mimic",
                "decides to split the party", "finds the cursed katana of seppuku",
                "decides to read the Necronomicon"])
            await ctx.send(f"{name} {random_death}. :skull:")
            await self.characters.get(player).showInventory(ctx)
            del self.characters[player]
        else:
            await ctx.send(f"{player} does not have a character.")

    @commands.command(name='assign')
    async def assignStats(self, ctx, strength: int, dexterity: int, constitution: int, intelligence: int, wisdom: int, charisma: int, hp: int = 0):
        """Assign character's stats and optionally hit points.
        Usage: !assign <str> <dex> <con> <int> <wis> <cha> [<hp>]"""
        player = str(ctx.author)
        if player in self.characters:
            self.characters.get(player).assignStats(strength, dexterity, constitution, intelligence, wisdom, charisma, hp)
            await self.characters.get(player).showCharacter(ctx)
        else:
            await ctx.send(f"{player} does not have a character.")

    @commands.command(name='prime')
    async def setPrimes(self, ctx, first_prime: str, second_prime: str = 'None', third_prime: str = 'None'):
        """Assign prime stats.
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

    @commands.command(name='alignment', aliases=['al'])
    async def setAlignment(self, ctx, alignment: str):
        """Sets character alignment.
        Characters can be Lawful, Neutral or Chaotic and Good, Neutral or Evil.
        Usage: !alignment <alignment>
               where alignment is one of: LG, LN, LE, NG, N, NE, CG, CN, CE"""
        player = str(ctx.author)
        if player in self.characters:
            self.characters.get(player).setAlignment(alignment)
            await ctx.send(f"{self.characters.get(player).name} is {self.characters.get(player).getAlignment()}")
        else:
            await ctx.send(f"{player} does not have a character.")

    # Display character sheet

    @commands.command(name='party')
    async def allCharacters(self, ctx, param: str = 'None'):
        """Show stats for all characters.
        Usage: !party [stats]"""
        for player, character in self.characters.items():
            if param == 'stats':
                await character.showCharacter(ctx, f"({player})")
            else:
                await character.showSummary(ctx, f"{player} is playing ")

    @commands.command(name='character', aliases=['char'])
    async def character(self, ctx, character: str = ''):
        """Show your character sheet."""
        if character == '':
            player = str(ctx.author)
            if player not in self.characters:
                await ctx.send(f"{player} does not have a character.")
                return
        else:
            self.gm_only(ctx)
            player = self.getPlayer(character)
        await self.characters.get(player).showCharacter(ctx)

    # Game mechanics

    @commands.command(name='check', aliases=['ck'])
    async def siegeCheck(self, ctx, stat: str, bonus: int = 0, cl: int = 0):
        """Make an ability check.
        Usage: !check <stat> [<bonus>] [<challenge level>]"""
        player = str(ctx.author)
        if player in self.characters:
            await self.characters.get(player).siegeCheck(ctx, stat, bonus, cl)
        else:
            await ctx.send(f"{player} does not have a character.")

    @commands.command(name='initiative', aliases=['init'])
    async def rollForInitiative(self, ctx):
        """Roll for initiative!"""
        initList = []
        for player, character in self.characters.items():
            if character.isActive():
                init = await character.rollForInitiative(ctx)
                initList.append((init, character.name))
            else:
                await character.inactiveStatus(ctx)
        for monster in self.monsters:
            init = await monster.rollForInitiative(ctx)
            initList.append((init, monster.name))
        initOrder = "**Initiative Order**\n"
        for i in sorted(initList, reverse=True):
            initOrder += f"{i[0]}\t{i[1]}\n"
        await ctx.send(initOrder)

    @commands.command(name='heal')
    async def heal(self, ctx, character: str, hp: str):
        """Heals the specified character.
        Usage: !heal <character> <healing_dice>"""
        player = self.getPlayer(character)
        await self.characters[player].heal(ctx, hp)

    @commands.command(name='first_aid', aliases=['firstaid','aid'])
    async def firstAid(self, ctx, character: str):
        """Perform first aid on the specified character.
        First aid does not restore any hit points, but can stop bleeding and restore unconscious characters to consciousness.
        Usage: !first_aid <character>"""
        player = self.getPlayer(character)
        await self.characters[player].first_aid(ctx)

    # Manage inventory

    @commands.command(name='inventory', aliases=['inv'])
    async def inventory(self, ctx, character: str = ''):
        """List your inventory."""
        if character == '':
            player = str(ctx.author)
            if player not in self.characters:
                await ctx.send(f"{player} does not have a character.")
                return
        else:
            self.gm_only(ctx)
            player = self.getPlayer(character)
        await self.characters.get(player).showInventory(ctx)

    @commands.command(name='equip', aliases=['pick','get'])
    async def addEquipment(self, ctx, description: str, count: int = 1, ev: float = 1, value: int = 0):
        """Add an item to your equipment list.
        Usage: !equip "Item Description" [<count>] [<ev>] [<value>]
               where count is the number of this item you are carrying (default: 1)
                     ev is the Encumbrance Value from the Player's Handbook (default: 1)
                     value is the value in gold pieces for gems, jewellery and other treasure (default: 0)"""
        player = str(ctx.author)
        if player in self.characters:
            await self.characters.get(player).addEquipment(ctx, description, count, ev, value)
        else:
            await ctx.send(f"{player} does not have a character.")

    @commands.command(name='equip.wearable', aliases=['wearable','equipw','pickw','getw'])
    async def addWearable(self, ctx, description: str, ac: int = 0, ev: float = 1, value: int = 0):
        """Add a wearable item to your equipment list.
        Usage: !equip.wearable "Item Description" [<ac>] [<ev>] [<value>]
               where ac is the armour class bonus of this item (default: 0)
                     ev is the Encumbrance Value from the Player's Handbook (default: 1)
                     value is the value in gold pieces for wearable treasure (jewellery, etc.) (default: 0)"""
        player = str(ctx.author)
        if player in self.characters:
            await self.characters.get(player).addWearable(ctx, description, ac, ev, value)
        else:
            await ctx.send(f"{player} does not have a character.")

    @commands.command(name='wear')
    async def wear(self, ctx, description: str, location: str = ''):
        """Wear an item you are carrying.
        Usage: !wear "Item Description" ["location"]
               where location is the optional location on your body
        Example: `wear ring "on left hand"` """
        player = str(ctx.author)
        if player in self.characters:
            await self.characters.get(player).wear(ctx, description, location)
        else:
            await ctx.send(f"{player} does not have a character.")

    @commands.command(name='take_off', aliases=['takeoff','take','remove'])
    async def takeOff(self, ctx, description: str):
        """Take off an item you are wearing
        Usage: !take_off "Item Description" """
        player = str(ctx.author)
        if player in self.characters:
            await self.characters.get(player).takeOff(ctx, description)
        else:
            await ctx.send(f"{player} does not have a character.")

    @commands.command(name='drop')
    async def dropEquipment(self, ctx, description: str, count: int = 9999999):
        """Remove an item from your equipment list.
        Usage: !drop "Item Description" [<count>]
               where count is the number of this item you want to drop (default: all)"""
        player = str(ctx.author)
        if player in self.characters:
            await self.characters.get(player).dropEquipment(ctx, description, count)
        else:
            await ctx.send(f"{player} does not have a character.")

    #async def addCoin(self, ctx, amount: int, denomination: str): 
    #async def dropCoin(self, ctx, amount: int, denomination: str): 

    ### GM-only commands ###

    @commands.command(name='load')
    async def loadJson(self, ctx, filename: str = 'characters.json'):
        """Load characters from a JSON-formatted file."""
        self.gm_only(ctx)
        with open(f"/save/{basename(filename)}", 'r') as f:
            chars = json.load(f)
            for player, character in chars.items():
                self.characters[player] = Character.__from_dict__(character)
        await ctx.send(f"Characters loaded from {filename}")

    def getPlayer(self, character_name: str):
        if character_name in self.characters:
            return character_name
        num_results = 0
        player_found: str
        for player, character in self.characters.items():
            if character.name.lower().startswith(character_name.lower()):
                num_results += 1
                player_found = player
        if num_results == 0:
            raise CharacterNotFound(f"No match found for {character_name}.")
        elif num_results == 1:
            return player_found
        else:
            raise AmbiguousMatch(f"{character_name} is ambiguous, be more specific or use the player ID.")

    @commands.command(name='damage', aliases=['dmg'])
    async def damage(self, ctx, character: str, dmg: str):
        """Does damage to the specified character.
        Usage: !damage <character> <damage_dice>"""
        self.gm_only(ctx)
        player = self.getPlayer(character)
        await self.characters[player].damage(ctx, dmg)

    @commands.command(name='rest')
    async def rest(self, ctx, duration: int = 1):
        """Rest for 1 or more days."""
        self.gm_only(ctx)
        duration_text = f"{duration} days have passed."
        if duration < 2:
            duration = 1
            duration_text = "1 day has passed."
        for player, character in self.characters.items():
            result = character.rest(duration)
            if result != '':
                await ctx.send(result)
        await ctx.send(duration_text)

    @commands.command(name='level_up',aliases=['levelup'])
    async def levelUp(self, ctx, character: str):
        """Levels up the specified character."""
        self.gm_only(ctx)
        player = self.getPlayer(character)
        await self.characters[player].levelUp(ctx)

    @commands.command(name='euthanise')
    async def deleteCharacter(self, ctx, player: str):
        """Ends the suffering of the character belonging to the specified player."""
        self.gm_only(ctx)
        del self.characters[player]
        await ctx.send(f"The suffering of {player}'s character has been ended.")

    @commands.command(name='monster_reset', aliases=['mr'])
    async def monsterReset(self, ctx):
        """Resets monsters at the start of a new combat."""
        self.gm_only(ctx)
        self.monsters = []
        await ctx.send(f"Monsters reset.")

    @commands.command(name='monster_add', aliases=['ma'])
    async def monsterAdd(self, ctx, name: str, init_mod: int = 0):
        """Adds a new monster to the combat."""
        self.gm_only(ctx)
        self.monsters.append(Monster(name, init_mod))
        await ctx.send(f"Added {name} to combat.")

def setup(bot):
    bot.add_cog(Game(bot))
