# import json
# import ast
import logging

import discord
from discord import option
from discord.commands import SlashCommandGroup

# import random
from discord.ext import commands


class Debug(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cogs_list = [
            "Debug",
            "TokenBag",
        ]
        logger = logging.getLogger("tipsyTokens.Debug")
        logger.debug(f"Reloaded. Cogs List: {self.cogs_list}")

    debug_cmds = SlashCommandGroup(
        name="tokenbotdebug",
        description="TipsyToken bot Debug Commands",
        default_member_permissions=discord.Permissions(manage_guild=True),
        guild_only=True,
    )

    async def reload_cog(self, cog):
        message_log = ""
        isLoaded = False
        try:
            self.bot.unload_extension(f"CommandList.{cog}")
        except Exception as e:
            message_log = f"Error with unloading {cog}: {type(e).__name__}: {e};\n"

        try:
            self.bot.load_extension(f"CommandList.{cog}")
        except Exception as e:
            message_log += f"Error with loading {cog}: {type(e).__name__}: {e};\n"
        else:
            isLoaded = True
            # Clear any error in unloading if loading succeeded.
            message_log = ""
        return (isLoaded, message_log)

    # reload_cogs *****************************************************************
    @debug_cmds.command(
        name="reload",
        description="Reload cogs",
        default_member_permissions=discord.Permissions(manage_guild=True),
        guild_only=True,
    )
    @option(
        "module",
        description="Optional: Specify an individual cog to reload",
        default="",
    )
    async def reload_cogs(self, ctx, module: str):
        logger = logging.getLogger("tipsyTokens.Debug.reload_cogs")
        cogs = []
        message_log = ""
        try:
            cog_work_list = []
            if module is not None and module != "":
                cog_work_list.append(module)
            else:
                cog_work_list = self.cogs_list
            for cog in cog_work_list:
                (loaded, msgLog) = await self.reload_cog(cog.strip())
                message_log += msgLog
                if loaded:
                    cogs.append(cog.strip())

            logger.debug(f"Reloaded cogs: {', '.join(cogs)}\n{message_log}")
            await ctx.send_response(
                content=f"(Re)loaded cogs: {', '.join(cogs)}. {message_log}",
                ephemeral=True,
            )
        except Exception as e:
            logger.error(
                f"\nExperienced an error\n{type(e).__name__}: {e}"
                f"\n(Re)loaded cogs: {', '.join(cogs)}\nMessage_Log: {message_log}"
            )
            await ctx.send_response(
                content=f"Experienced an error\n{type(e).__name__}: {e}", ephemeral=True
            )

    # set_logging_level ***********************************************************
    @debug_cmds.command(
        name="logging",
        description="Change Logging level",
        default_member_permissions=discord.Permissions(manage_guild=True),
        guild_only=True,
    )
    @option(
        "level",
        description="Specify the new logging level",
        choices=["critical", "error", "warning", "info", "debug"],
    )
    @option(
        "module",
        description="Optional: Specify a specific log module to control",
        default="tipsyTokens",
    )
    async def set_logging_level(self, ctx, level, module: str):
        logger = logging.getLogger("tipsyTokens.Debug.set_logging_level")
        try:
            logger.info(f"Got in log level change request: {module.strip()} -> {level}")
            sublogger = logging.getLogger(module.strip())
            sublevel = logging.ERROR
            match level:
                case "critical":
                    sublevel = logging.CRITICAL
                case "error":
                    sublevel = logging.ERROR
                case "warning":
                    sublevel = logging.WARNING
                case "info":
                    sublevel = logging.INFO
                case "debug":
                    sublevel = logging.DEBUG
                case _:
                    sublevel = logging.ERROR
            sublogger.setLevel(sublevel)
            await ctx.send_response(
                content=f"Adjusted Log Level for {module.strip()} to {level}",
                ephemeral=True,
            )
        except Exception as e:
            logger.error(f"Experienced an error\n{type(e).__name__}: {e}")
            await ctx.send_response(
                content=f"Experienced an error\n{type(e).__name__}: {e}", ephemeral=True
            )


def setup(bot):
    bot.add_cog(Debug(bot))
