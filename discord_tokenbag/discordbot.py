#! /usr/bin/env python3
# Work with Python 3.10
# notes:
# Discord API: https://docs.pycord.dev/en/master/
#

import logging
import logging.handlers
import os

import discord
from discord.ext import bridge, commands

# load env vars
from dotenv import load_dotenv

load_dotenv("tipsytokens.env")


# setup logging
handler = logging.handlers.RotatingFileHandler(
    filename="logs/discord.log",
    mode="a",
    encoding="utf-8",
    maxBytes=32 * 1024 * 1024,  # 32 MiB
    backupCount=5,  # Rotate through 5 files
)
stdouthandler = logging.StreamHandler()
dt_fmt = "%Y-%m-%dZ%H:%M:%S"
formatter = logging.Formatter(
    "[{asctime}] [{levelname:<8}] {name}: {message}", dt_fmt, style="{"
)
handler.setFormatter(formatter)
stdouthandler.setFormatter(formatter)
logging.basicConfig(level=logging.INFO, handlers=[stdouthandler, handler])
logger_discord = logging.getLogger("discord")
# logger_discord.setLevel(logging.DEBUG)
logger_discord.setLevel(logging.ERROR)

token_logger = logging.getLogger("tokenbag")
token_logger.setLevel(logging.INFO)

logger = logging.getLogger("tipsyTokens")
# logger.setLevel(logging.DEBUG)
logger.setLevel(logging.INFO)

# setup Bot
Bot_Prefix = "!"
intents = discord.Intents.default()
# intents.message_content = True
intents.reactions = True

# 2147485760
BotServer = bridge.Bot(
    command_prefix=commands.when_mentioned_or(Bot_Prefix),
    owner_id=os.environ.get("ERROR_POC"),
    intents=intents,
    auto_sync_commands=True,
)
#    debug_guilds=[1004539730362376293],

# add Cogs
# FIXME: Get the cogs_list from a central place both here and in the Debug module
cogs_list = [
    "Debug",
    "TokenBag",
]


def load_cogs():
    # Load the ones that take no configuration
    # Pass out the list of loadable modules so Debug can find it
    # Load Debug always
    BotServer.load_extension("CommandList.Debug")
    logger.debug("Called to load Debug")

    for cog in cogs_list:
        if cog == 'Debug':
            continue
        BotServer.load_extension(f"CommandList.{cog}")
        logger.debug(f"Called to load {cog}")


DISCORD_TOKEN = os.environ.get("PROD_TOKEN")


@BotServer.event
async def on_ready():
    # logger.debug(f"Got in bgguser:{BGG_USERNAME} and token:{DISCORD_TOKEN}")
    logger.info("Ready!")


load_cogs()
BotServer.run(DISCORD_TOKEN)
