import asyncio
import faulthandler
import logging
import os
import sys
import traceback

# this hooks a lot of weird things and needs to be imported early
import utils.newrelic

utils.newrelic.hook_all()
from utils import clustering, config

import aioredis
import discord
import motor.motor_asyncio
import sentry_sdk
from aiohttp import ClientOSError, ClientResponseError
from discord.errors import Forbidden, HTTPException, InvalidArgument, NotFound
from discord.ext import commands
from discord.ext.commands.errors import CommandInvokeError

from cogscc.models.errors import BambleweenyException, EvaluationError
from utils.help import help_command
from utils.redisIO import RedisIO

COGS = (
    "cogscc.dice", "cogscc.game", "cogsmisc.core"
)


async def get_prefix(the_bot, message):
    if not message.guild:
        return commands.when_mentioned_or(config.DEFAULT_PREFIX)(the_bot, message)
    guild_id = str(message.guild.id)
    if guild_id in the_bot.prefixes:
        gp = the_bot.prefixes.get(guild_id, config.DEFAULT_PREFIX)
    else:  # load from db and cache
        gp_obj = await the_bot.mdb.prefixes.find_one({"guild_id": guild_id})
        if gp_obj is None:
            gp = config.DEFAULT_PREFIX
        else:
            gp = gp_obj.get("prefix", config.DEFAULT_PREFIX)
        the_bot.prefixes[guild_id] = gp
    return commands.when_mentioned_or(gp)(the_bot, message)


class Avrae(commands.AutoShardedBot):
    def __init__(self, prefix, description=None, testing=False, **options):
        super(Avrae, self).__init__(prefix, help_command=help_command, description=description, **options)
        self.testing = testing
        self.state = "init"
        self.credentials = Credentials()
        if config.TESTING:
            self.mclient = motor.motor_asyncio.AsyncIOMotorClient(self.credentials.test_mongo_url)
        else:
            self.mclient = motor.motor_asyncio.AsyncIOMotorClient(config.MONGO_URL)
        self.mdb = self.mclient[config.MONGODB_DB_NAME]
        self.rdb = self.loop.run_until_complete(self.setup_rdb())
        self.prefixes = dict()
        self.muted = set()
        self.cluster_id = 0

        if config.SENTRY_DSN is not None:
            release = None
            if config.GIT_COMMIT_SHA:
                release = f"avrae-bot@{config.GIT_COMMIT_SHA}"
            sentry_sdk.init(dsn=config.SENTRY_DSN, environment=config.ENVIRONMENT.title(), release=release)

    async def setup_rdb(self):
        if config.TESTING:
            redis_url = self.credentials.test_redis_url
        else:
            redis_url = config.REDIS_URL
        return RedisIO(await aioredis.create_redis_pool(redis_url, db=config.REDIS_DB_NUM))

    async def get_server_prefix(self, msg):
        return (await get_prefix(self, msg))[-1]

    async def launch_shards(self):
        # set up my shard_ids
        await clustering.coordinate_shards(self)
        if self.shard_ids is not None:
            log.info(f"Launching {len(self.shard_ids)} shards! ({set(self.shard_ids)})")
        await super(Avrae, self).launch_shards()
        log.info(f"Launched {len(self.shards)} shards!")

        if self.is_cluster_0:
            await self.rdb.incr('build_num')

    @property
    def is_cluster_0(self):
        if self.cluster_id is None:  # we're not running in clustered mode anyway
            return True
        return self.cluster_id == 0

    @staticmethod
    def log_exception(exception=None, context: commands.Context = None):
        if config.SENTRY_DSN is None:
            return

        with sentry_sdk.push_scope() as scope:
            if context:
                # noinspection PyDunderSlots,PyUnresolvedReferences
                # for some reason pycharm doesn't pick up the attribute setter here
                scope.user = {"id": context.author.id, "username": str(context.author)}
                scope.set_tag("message.content", context.message.content)
                scope.set_tag("is_private_message", context.guild is None)
                scope.set_tag("channel.id", context.channel.id)
                scope.set_tag("channel.name", str(context.channel))
                if context.guild is not None:
                    scope.set_tag("guild.id", context.guild.id)
                    scope.set_tag("guild.name", str(context.guild))
            sentry_sdk.capture_exception(exception)


class Credentials:
    def __init__(self):
        try:
            import credentials
        except ImportError:
            raise Exception("Credentials not found.")
        self.token = credentials.officialToken
        self.test_redis_url = credentials.test_redis_url
        self.test_mongo_url = credentials.test_mongo_url
        if config.TESTING:
            self.token = credentials.testToken
        if config.ALPHA_TOKEN:
            self.token = config.ALPHA_TOKEN


desc = '''
Bambleweeny is Discord bot to generate random numbers for RPGs. It is a fork of [Avrae](https://github.com/avrae/avrae). The name is inspired by the Finite Improbability Generator from the _Hitchhikers Guide to the Galaxy_:

_The principle of generating small amounts of finite improbability by simply hooking the logic circuits of a Bambleweeny 57 Submeson Brain to an atomic vector plotter suspended in a strong Brownian Motion producer (say a nice hot cup of tea) were of course well understood—and such generators were often used to break the ice at parties by making all the molecules in the hostess's undergarments leap simultaneously one foot to the left, in accordance with the Theory of Indeterminacy._

_Many respectable physicists said that they weren't going to stand for this—partly because it was a debasement of science, but mostly because they didn't get invited to those sort of parties._

[Learn about Infinite Improbability](https://hitchhikers.fandom.com/wiki/Infinite_Improbability_Drive)
'''
bot = Avrae(prefix=get_prefix, description=desc, pm_help=True, testing=config.TESTING,
            activity=discord.Game(name=f'C&C | {config.DEFAULT_PREFIX}help'))

log_formatter = logging.Formatter('%(levelname)s:%(name)s: %(message)s')
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(log_formatter)
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(handler)
log = logging.getLogger('bot')


@bot.event
async def on_ready():
    log.info('Logged in as')
    log.info(bot.user.name)
    log.info(bot.user.id)
    log.info('------')


@bot.event
async def on_resumed():
    log.info('resumed.')


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return

    elif isinstance(error, BambleweenyException):
        return await ctx.send(str(error))

    elif isinstance(error, (commands.UserInputError, commands.NoPrivateMessage, ValueError)):
        return await ctx.send(
            f"Error: {str(error)}\nUse `{ctx.prefix}help " + ctx.command.qualified_name + "` for help.")

    elif isinstance(error, commands.CheckFailure):
        msg = str(error) or "You are not allowed to run this command."
        return await ctx.send(f"Error: {msg}")

    elif isinstance(error, commands.CommandOnCooldown):
        return await ctx.send("This command is on cooldown for {:.1f} seconds.".format(error.retry_after))

    elif isinstance(error, commands.MaxConcurrencyReached):
        return await ctx.send(f"Only {error.number} instance{'s' if error.number > 1 else ''} of this command per "
                              f"{error.per.name} can be running at a time.")

    elif isinstance(error, CommandInvokeError):
        original = error.original
        if isinstance(original, EvaluationError):  # PM an alias author tiny traceback
            e = original.original
            if not isinstance(e, BambleweenyException):
                tb = f"```py\nError when parsing expression {original.expression}:\n" \
                     f"{''.join(traceback.format_exception(type(e), e, e.__traceback__, limit=0, chain=False))}\n```"
                try:
                    await ctx.author.send(tb)
                except Exception as e:
                    log.info(f"Error sending traceback: {e}")
            return await ctx.send(str(original))

        elif isinstance(original, BambleweenyException):
            return await ctx.send(str(original))

        elif isinstance(original, Forbidden):
            try:
                return await ctx.author.send(
                    f"Error: I am missing permissions to run this command. "
                    f"Please make sure I have permission to send messages to <#{ctx.channel.id}>."
                )
            except HTTPException:
                try:
                    return await ctx.send(f"Error: I cannot send messages to this user.")
                except HTTPException:
                    return

        elif isinstance(original, NotFound):
            return await ctx.send("Error: I tried to edit or delete a message that no longer exists.")

        elif isinstance(original, (ClientResponseError, InvalidArgument, asyncio.TimeoutError, ClientOSError)):
            return await ctx.send("Error in Discord API. Please try again.")

        elif isinstance(original, HTTPException):
            if original.response.status == 400:
                return await ctx.send(f"Error: Message is too long, malformed, or empty.\n{original.text}")
            elif 499 < original.response.status < 600:
                return await ctx.send("Error: Internal server error on Discord's end. Please try again.")

        elif isinstance(original, OverflowError):
            return await ctx.send(f"Error: A number is too large for me to store.")

    # send error to sentry.io
    if isinstance(error, CommandInvokeError):
        bot.log_exception(error.original, ctx)
    else:
        bot.log_exception(error, ctx)

    await ctx.send(
        f"Error: {str(error)}\nUh oh, that wasn't supposed to happen! ")

    log.warning("Error caused by message: `{}`".format(ctx.message.content))
    for line in traceback.format_exception(type(error), error, error.__traceback__):
        log.warning(line)


@bot.event
async def on_message(message):
    if message.author.id in bot.muted:
        return
    await bot.process_commands(message)


@bot.event
async def on_command(ctx):
    try:
        log.debug(
            "cmd: chan {0.message.channel} ({0.message.channel.id}), serv {0.message.guild} ({0.message.guild.id}), "
            "auth {0.message.author} ({0.message.author.id}): {0.message.content}".format(
                ctx))
    except AttributeError:
        log.debug("Command in PM with {0.message.author} ({0.message.author.id}): {0.message.content}".format(ctx))


for cog in COGS:
    bot.load_extension(cog)

if __name__ == '__main__':
    faulthandler.enable()  # assumes we log errors to stderr, traces segfaults
    bot.state = "run"
    #bot.loop.create_task(compendium.reload_task(bot.mdb))
    bot.run(bot.credentials.token)
