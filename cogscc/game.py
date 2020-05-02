import random
import time
import json
from os.path import basename
from discord.ext import commands
from cogscc.funcs.dice import roll
from cogscc.character import Character
from cogscc.monster import Monster
import cogscc.npc
from cogscc.models.errors import AmbiguousMatch, CharacterNotFound, InvalidArgument, NotAllowed

def getArgDict(*args):
    argDict = {}
    for arg in args:
        s = arg.split(':', 1)
        if len(s) == 2:
            # Arguments should be key:value pairs
            try:
                argDict[s[0].lower()] = int(s[1])
            except ValueError:
                try:
                    argDict[s[0].lower()] = float(s[1])
                except ValueError:
                    argDict[s[0].lower()] = s[1]
        else:
            # Allow one integer and one string argument with default key
            try:
                count = int(s[0])
                if 'count' in argDict:
                    raise EvaluationError(f"I don't know what to do with {s[0]}.")
                else:
                    argDict['count'] = count
            except ValueError:
                if 'name' in argDict:
                    raise EvaluationError(f"I don't know what to do with {s[0]}.")
                else:
                    argDict['name'] = s[0]
    return argDict


class ToJson(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, "__to_json__"):
            return obj.__to_json__()
        return json.JSONEncoder.default(self, obj)


class Game(commands.Cog):
    gm_roles = [ 'Castle Keeper', 'Game Master', 'Dungeon Master' ]

    def __init__(self, bot):
        self.bot = bot
        self.characters = {}
        self.monsters = []

    def gm_only(self, ctx):
        for role in ctx.author.roles:
            if role.name in Game.gm_roles:
                return
        raise NotAllowed(f"Only the Game Master can do that!")

    def getGmList(self, ctx):
        gm_list = []
        for member in ctx.guild.members:
            for role in member.roles: 
                if role.name in Game.gm_roles:
                    gm_list.append(member)
        return gm_list

    def selfOrGm(self, ctx, character: str):
        if character:
            # Specified character name: if the caller is not a GM, it must be controlled by the player
            player = self.getPlayer(character)
            if not player.startswith(str(ctx.author)):
                self.gm_only(ctx)
        else:
            # Player's own character (if it exists)
            player = str(ctx.author)
            if player not in self.characters:
                raise CharacterNotFound(f"{player} does not have a character.")
        return player

    # Roll up a new character

    @commands.command(name='generate')
    async def genStats(self, ctx):
        """Randomly generate the six base stats for a new character."""
        rolls = [roll("4d6kh3", inline=True) for _ in range(6)]
        #self.stats.set(rolls[0].total, rolls[1].total, rolls[2].total, rolls[3].total, rolls[4].total, rolls[5].total)
        stat_summary = '\n:game_die: '.join(r.skeleton for r in rolls)
        total = sum([r.total for r in rolls])
        await ctx.send(f"{ctx.message.author.mention}\nGenerated random stats:\n:game_die: {stat_summary}\nTotal = `{total}`")

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

    @commands.command(name='create')
    async def create(self, ctx, name: str, race: str, xclass: str, level: int = 1):
        """Create a new character.
        Usage: !create "Character Name" <race> <class> [<level>]"""
        player = str(ctx.author)
        if player in self.characters:
            await ctx.send(self.characters.get(player).showSummary("You already have a character: "))
            return
        self.characters[player] = Character(name, race, xclass, level)
        await ctx.send(self.characters.get(player).showSummary(f"{player} is playing "))
        return

    @commands.command(name='suicide')
    async def suicide(self, ctx):
        """Kill your character (allowing you to create a new one)."""
        player = str(ctx.author)
        if player in self.characters:
            name = self.characters[player].getName()
            random_death = random.choice(["drinks poison and fails their saving throw",
                "is crushed by falling rocks", "opens a chest filled with poison gas",
                "is shot in the back by a comrade", "goes to explore the Tomb of Horrors and is never seen again", 
                "goes for a swim in a pool of acid", "didn't realise that the treasure chest was a mimic",
                "decides to split the party", "finds the cursed katana of seppuku",
                "decides to read the Necronomicon"])
            await ctx.send(f"{name} {random_death}. :skull:\n" + self.characters.get(player).showInventory())
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
            await ctx.send(self.characters.get(player).showCharacter())
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
            await ctx.send(self.characters.get(player).showCharacter())
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
            await ctx.send(f"{self.characters.get(player).getName()} is {self.characters.get(player).getAlignment()}")
        else:
            await ctx.send(f"{player} does not have a character.")

    # Display character sheet

    @commands.command(name='party')
    async def allCharacters(self, ctx, param: str = 'None'):
        """Show stats for all characters.
        Usage: !party [stats]"""
        party = ''
        for player, character in sorted(self.characters.items()):
            if param != 'stats':
                disabled = "**DISABLED** " if character.disabled else ''
                msg = f"{player} is playing" if type(character) is Character else "(NPC) "
                party += character.showSummary(f"\n{disabled}{msg} ")
            elif not character.disabled:
                party += '\n' + character.showCharacter(f"({player})")
            # Discord has a hard limit of 2000 chars/message
            if len(party) > 1500:
                await ctx.send(party)
                party = ''
        if party:
            await ctx.send(party)

    @commands.command(name='character', aliases=['char'])
    async def character(self, ctx, character: str = ''):
        """Show your character sheet."""
        player = self.selfOrGm(ctx, character)
        await ctx.send(self.characters.get(player).showCharacter())

    # Game mechanics

    @commands.command(name='check', aliases=['chk'])
    async def siegeCheck(self, ctx, stat: str, *args):
        """Make an ability check.
        Usage: !check <stat> [<bonus>] [CL:<challenge level>]"""
        argDict = getArgDict(*args)
        character = argDict.get('name', '')
        bonus = argDict.get('count', 0)
        cl = argDict.get('cl', 0)
        player = self.selfOrGm(ctx, character)
        await ctx.send(self.characters.get(player).siegeCheck(stat, bonus, cl))

    @commands.command(name='search', aliases=['listen','smell','track','traps'])
    async def search(self, ctx, bonus = 0):
        """Use a sense or skill to detect something or someone.
        Usage: !listen [+bonus]
               !search [+bonus]
               !smell [+bonus]
               !track [+bonus]
               !traps [+bonus]
        where bonus is the (positive or negative) modifier for the check. Racial bonuses are included
        automatically, so the bonus is for situational modifiers only. Examples:
            Listening through a stone wall carries a -10 penalty
            Dwarves get +4 to search checks and +2 to finding traps in stonework/structures"""
        player = str(ctx.author)
        if player in self.characters:
            (message, result) = self.characters.get(player).search(ctx.invoked_with, bonus)
            await ctx.send(message)
            for gm in self.getGmList(ctx):
                await gm.send(result)
        else:
            await ctx.send(f"{player} does not have a character.")

    # Combat

    @commands.command(name='initiative', aliases=['init'])
    async def rollForInitiative(self, ctx):
        """Roll for initiative!"""
        self.gm_only(ctx)
        initList = []
        initRolls = ''
        for player, character in sorted(self.characters.items()):
            if character.disabled:
                continue
            elif character.isActive():
                (init, dieRoll) = character.rollForInitiative()
                initList.append((init, character.getName()))
                initRolls += dieRoll
            else:
                initRolls += character.inactiveStatus()
        for monster in self.monsters:
            (init, dieRoll) = monster.rollForInitiative()
            initList.append((init, monster.getName()))
            initRolls += dieRoll
        await ctx.send(initRolls)
        initOrder = "**Initiative Order**\n"
        for i in sorted(initList, reverse=True):
            initOrder += f"{i[0]}\t{i[1]}\n"
        await ctx.send(initOrder)

    # Wounds and healing

    @commands.command(name='damage', aliases=['dmg'])
    async def damage(self, ctx, character: str, dmg: str):
        """Does damage to the specified character.
        Usage: !damage <character> <damage_dice>"""
        self.gm_only(ctx)
        player = self.getPlayer(character)
        await ctx.send(self.characters[player].damage(dmg))

    @commands.command(name='energy_drain')
    async def energyDrain(self, ctx, character: str, levels: int = 1):
        """Drains life energy level(s) from the specified character.
        Usage: !energy_drain <character> <no_levels>"""
        self.gm_only(ctx)
        player = self.getPlayer(character)
        await ctx.send(self.characters[player].energyDrain(levels))

    @commands.command(name='heal')
    async def heal(self, ctx, character: str, hp: str):
        """Heals the specified character.
        Usage: !heal <character> <healing_dice>"""
        player = self.getPlayer(character)
        await ctx.send(self.characters[player].heal(hp))

    @commands.command(name='first_aid', aliases=['firstaid','aid'])
    async def firstAid(self, ctx, character: str):
        """Perform first aid on the specified character.
        First aid does not restore any hit points, but can stop bleeding and restore unconscious characters to consciousness.
        Usage: !first_aid <character>"""
        player = self.getPlayer(character)
        await ctx.send(self.characters[player].first_aid())

    @commands.command(name='rest')
    async def rest(self, ctx, duration: int = 1):
        """Rest for 1 or more days."""
        self.gm_only(ctx)
        result = ''
        if duration < 2:
            duration = 1
            duration_text = "1 day has passed."
        for player, character in self.characters.items():
            result += character.rest(duration)
        result += f"\n{duration} days have passed."
        await ctx.send(result)

    # Manage inventory

    @commands.command(name='inventory', aliases=['inv'])
    async def inventory(self, ctx, character: str = ''):
        """List your inventory."""
        if character == '':
            player = str(ctx.author)
            if player not in self.characters:
                await ctx.send(f"{player} does not have a character.")
                return
            await ctx.send(self.characters.get(player).showInventory())
        else:
            self.gm_only(ctx)
            player = self.getPlayer(character)
            await ctx.send(self.characters.get(player).showInventory(True))

    @commands.command(name='equip', aliases=['pick','get'])
    async def addEquipment(self, ctx, description: str, *args):
        """Add an item to your equipment list.
        Usage: !equip "Item Description" [wearable|<count>] [<attributes>]
               where wearable means that you will be able to !wear this item
                     count is the number of this item you are carrying (default: 1)
                     attributes allow you to specify additional attributes of the item as a key-value pair:
                         ev:<number> is the Encumbrance Value from the Player's Handbook (default: 1)
                         value:<number> is the value in gold pieces for gems, jewellery and other treasure (default: 0)
                         ac:<number> is the Armour Class bonus that this item will give if you wear it (default: 0)
        Example: !equip "Mail Shirt" wearable ev:3 ac:4"""
        player = str(ctx.author)
        if player in self.characters:
            argDict = {}
            isWearable = False
            for arg in args:
                s = arg.split(':', 1)
                if len(s) == 2 and s[0].lower() == 'ev':
                    argDict['ev'] = float(s[1])
                elif len(s) == 2:
                    argDict[s[0].lower()] = int(s[1])
                elif s[0].isdigit() and not 'count' in argDict:
                    argDict['count'] = int(s[0])
                elif s[0].lower() == 'wearable':
                    isWearable = True
                else:
                    raise InvalidArgument(f"I don't know what you mean by {s[0]}.")

            if isWearable:
                await ctx.send(self.characters.get(player).addWearable(description, argDict))
            else:
                await ctx.send(self.characters.get(player).addEquipment(description, argDict))
        else:
            await ctx.send(f"{player} does not have a character.")

    @commands.command(name='give')
    async def give(self, ctx, *args):
        """Give an item to another character.
        Usage: !give [<number>] "Item Description" [to] <character>
               where <number> is the number of this item you want to give (default: 1)
                     <character> can be the character name or the Discord user ID."""
        player = str(ctx.author)
        if player in self.characters:
            try:
                argl = list(args)
                description = argl.pop(0)
                try:
                    count = int(description)
                    description = argl.pop(0)
                except ValueError:
                    count = 1
                recipient = argl.pop(0)
                if recipient == 'to':
                    recipient = argl.pop(0)
                if argl:
                    raise IndexError()
            except IndexError:
                raise InvalidArgument("Wrong number of arguments. Try: `!give <item> to <character>`")
            await ctx.send(self.characters.get(player).give(count, description, self.characters.get(self.getPlayer(recipient))))
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
            await ctx.send(self.characters.get(player).wear(description, location))
        else:
            await ctx.send(f"{player} does not have a character.")

    @commands.command(name='take_off', aliases=['takeoff','take','remove'])
    async def takeOff(self, ctx, description: str):
        """Take off an item you are wearing
        Usage: !take_off "Item Description" """
        player = str(ctx.author)
        if player in self.characters:
            await ctx.send(self.characters.get(player).takeOff(description))
        else:
            await ctx.send(f"{player} does not have a character.")

    @commands.command(name='drop')
    async def dropEquipment(self, ctx, description: str, count: int = 1):
        """Remove an item from your equipment list.
        Usage: !drop "Item Description" [<count>]
               where count is the number of this item you want to drop (default: 1)"""
        player = str(ctx.author)
        if player in self.characters:
            await ctx.send(self.characters.get(player).dropEquipment(description, count))
        else:
            await ctx.send(f"{player} does not have a character.")

    @commands.command(name='gp', aliases=['pp','ep','sp','cp'])
    async def managePurse(self, ctx, amount: int):
        """Add or remove coins from your purse.
        Usage: !gp +<amount> or !gp -<amount>
               There is a command for each coin type:
               !pp (platinum pieces)
               !gp (gold pieces)
               !ep (electrum pieces)
               !sp (silver pieces)
               !cp (copper pieces)"""
        player = str(ctx.author)
        if player in self.characters:
            await ctx.send(self.characters.get(player).managePurse(ctx.invoked_with, amount))
        else:
            await ctx.send(f"{player} does not have a character.")

    ### GM-only commands ###

    @commands.command(name='load')
    async def loadJson(self, ctx, filename: str = 'characters.json'):
        """Load characters from a JSON-formatted file."""
        self.gm_only(ctx)
        with open(f"/save/{basename(filename)}", 'r') as f:
            chars = json.load(f)
            for player, character in chars.items():
                self.characters[player] = Character.__from_dict__(character)
        await ctx.send(f"Characters loaded from {filename}.")

    @commands.command(name='load_npc')
    async def loadNPC(self, ctx):
        """Load new NPCs, animal companions, familiars, mounts, etc."""
        self.gm_only(ctx)
        npcs = cogscc.npc.load()
        for player, npc in npcs.items():
            self.characters[player] = npc
        await ctx.send(f"NPCs loaded.")

    def getPlayer(self, character_name: str):
        if character_name in self.characters:
            return character_name
        num_results = 0
        player_found: str
        for player, character in self.characters.items():
            if character.isMatchName(character_name):
                num_results += 1
                player_found = player
        if num_results == 0:
            raise CharacterNotFound(f"No match found for {character_name}.")
        elif num_results == 1:
            return player_found
        else:
            raise AmbiguousMatch(f"{character_name} is ambiguous, be more specific or use the player ID.")

    @commands.command(name='disable')
    async def disable(self, ctx, character: str):
        """Disables the specified character."""
        self.gm_only(ctx)
        player = self.getPlayer(character)
        self.characters[player].disabled = True
        await ctx.send(f"{player}'s character has been disabled for this session.")

    @commands.command(name='enable')
    async def enable(self, ctx, character: str):
        """Enables the specified character."""
        self.gm_only(ctx)
        player = self.getPlayer(character)
        self.characters[player].disabled = False
        await ctx.send(f"{player}'s character has been re-enabled.")

    @commands.command(name='gm_note', aliases=['ck_note','dm_note'])
    async def gmNote(self, ctx, character: str, item: str, description: str = ''):
        """Adds a secret note to an item or views the note.
        Usage: !gm_note <character> <item> [<description>]"""
        self.gm_only(ctx)
        player = self.getPlayer(character)
        await ctx.send(self.characters[player].gmNote(item, description))

    @commands.command(name='level_up',aliases=['levelup'])
    async def levelUp(self, ctx, character: str):
        """Levels up the specified character."""
        self.gm_only(ctx)
        player = self.getPlayer(character)
        await ctx.send(self.characters[player].levelUp())

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
    async def monsterAdd(self, ctx, name: str, *args):
        """Adds a new monster to the combat."""
        self.gm_only(ctx)
        argDict = {}
        for arg in args:
            s = arg.split(':', 1)
            if len(s) == 2:
                argDict[s[0].lower()] = int(s[1])
            elif s[0].isdigit() and not 'count' in argDict:
                argDict['count'] = int(s[0])
        if 'ac' not in argDict:
            argDict['ac'] = 10
        if 'hd' not in argDict:
            argDict['hd'] = 1
        self.monsters.append(Monster(name, argDict))
        await ctx.send(f"Added {name} to combat.")

def setup(bot):
    bot.add_cog(Game(bot))
