"""
Created on Dec 26, 2016

@author: andrew
"""
import random
import time
from datetime import datetime, timedelta
from math import floor, isnan

import discord
import psutil
from discord.ext import commands

from cogsmisc.stats import Stats


class Core(commands.Cog):
    """
    Core utilty and general commands.
    """

    def __init__(self, bot):
        self.bot = bot
        self.start_time = time.monotonic()

    @commands.command(hidden=True)
    async def avatar(self, ctx, user: discord.Member = None):
        """Gets a user's avatar.
        Usage: !avatar <USER>"""
        if user is None:
            user = ctx.message.author
        if user.avatar_url != "":
            await ctx.send(user.avatar_url)
        else:
            await ctx.send(user.display_name + " is using the default avatar.")

    @commands.command()
    async def ping(self, ctx):
        """Checks the ping time to the bot."""
        now = datetime.utcnow()
        pong = await ctx.send("Pong.")
        delta = datetime.utcnow() - now
        httping = floor(delta.total_seconds() * 1000)
        wsping = floor(self.bot.latency * 1000) if not isnan(self.bot.latency) else "Unknown"
        await pong.edit(content=f"Pong.\nHTTP Ping = {httping} ms.\nWS Ping = {wsping} ms.")

    #@commands.command()
    #async def invite(self, ctx):
        #"""Prints a link to invite Avrae to your server."""
        #await ctx.send(
            #"You can invite Avrae to your server here:\n"
            #"<https://invite.avrae.io>")

    #@commands.command()
    #async def changelog(self, ctx):
        #"""Prints a link to the official changelog."""
        #await ctx.send("You can check out the latest patch notes at "
                       #"https://github.com/avrae/avrae/releases/latest, and a list of all releases at "
                       #"<https://github.com/avrae/avrae/releases>!")

    @commands.command(aliases=['stats', 'info'])
    async def about(self, ctx):
        """Information about the bot."""
        stats = {}
        statKeys = ("dice_rolled_life", "spells_looked_up_life", "monsters_looked_up_life", "commands_used_life",
                    "items_looked_up_life", "rounds_init_tracked_life", "turns_init_tracked_life")
        for k in statKeys:
            stats[k] = await Stats.get_statistic(ctx, k)

        embed = discord.Embed(description='The Bambleweeny 57 Submeson Brain, a bot to generate random numbers. Just add an atomic vector plotter and some hot tea. Now with added Castles & Crusades integration!')
        embed.title = "Bambleweeny, the best in Finite Improbability!"
        embed.url = "https://www.starthinker.fr"
        embed.colour = 0x7289da
        total_members = sum(1 for _ in self.bot.get_all_members())
        unique_members = len(self.bot.users)
        members = '%s total\n%s unique' % (total_members, unique_members)
        embed.add_field(name='Members (Cluster)', value=members)
        embed.add_field(name='Uptime', value=str(timedelta(seconds=round(time.monotonic() - self.start_time))))
        motd = random.choice(["May the RNG be with you", "You have no tea",
                              "Will give higher rolls for tea", "The answer is 42",
                              "Does anyone even read these?"])
        embed.set_footer(
            text=f'{motd} | Build {await self.bot.rdb.get("build_num")} | Cluster {self.bot.cluster_id}')

        #commands_run = "{commands_used_life} total\n{dice_rolled_life} dice rolled\n" \
        #               "{spells_looked_up_life} spells looked up\n{monsters_looked_up_life} monsters looked up\n" \
        #               "{items_looked_up_life} items looked up\n" \
        #               "{rounds_init_tracked_life} rounds of initiative tracked ({turns_init_tracked_life} turns)" \
        commands_run = "{commands_used_life} total\n{dice_rolled_life} dice rolled" \
            .format(**stats)
        embed.add_field(name="Commands Run", value=commands_run)
        embed.add_field(name="Servers", value=f"{len(self.bot.guilds)} on this cluster\n"
                                              f"{await Stats.get_guild_count(self.bot)} total")
        memory_usage = psutil.Process().memory_full_info().uss / 1024 ** 2
        embed.add_field(name='Memory Usage', value='{:.2f} MiB'.format(memory_usage))
        embed.add_field(name='About', value='Forked from Avrae by slithy#7856 for the CERN Games Club', inline=False)

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Core(bot))
