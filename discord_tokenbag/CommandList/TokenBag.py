import logging
import traceback

import discord
from discord import option
# from discord.commands import SlashCommandGroup

# import random
from discord.ext import commands

from tokenbag import TokenBag as bag


class TokenBag(commands.Cog):
    def __init__(self, bot):
        logger = logging.getLogger("tipsyTokens.TokenBag.init")
        self.bot = bot
        self.pool = bag(bool(logger.getEffectiveLevel() == logging.DEBUG), "")
        self.bag_config = {
            "Bag Pool": {
                "Base": {
                    "Config": {
                        "max_draws": 3,
                        "sums": False,
                        "hit_ceil": 3,
                        "hit_ceil_only_on_crit": False,
                        "hit_full": 2,
                        "hit_partial": 1,
                        "miss_ceil": 2,
                    },
                    "Specification": [
                        {
                            "Hit": 4,
                            "Bronze Flip": 4,
                            "Silver Flip": 2,
                            "Gold Flip": 2,
                            "Blank Red": 4,
                            "Miss": 3,
                            "Miss Bronze": 1,
                            "Miss Silver": 1,
                            "Miss Gold": 1,
                            "Gobstopper": 1,
                            "Gobstopper Miss": 2,
                        }
                    ],
                }
            },
            "Token Pool": {
                "Blank": {
                    "Sum Value": 0,
                    "Hit Value": 0,
                    "Can Be Stolen": False,
                    "Can Steal": False,
                    "Can Latch": False,
                    "Return to Bag": False,
                    "Min Rank": 0,
                    "Ends Draws": False,
                    "Can Flip": False,
                    "Flipped": {"Can Flip": False},
                    "Enable Crit": -4,
                },
                "Hit": {"Sum Value": 1, "Hit Value": 1, "Can Be Stolen": True},
                "Bronze Flip": {
                    "Sum Value": 1,
                    "Hit Value": 1,
                    "Min Rank": 1,
                    "Enable Crit": 1,
                    "Can Flip": True,
                    "Flipped": {"Sum Value": 1, "Hit Value": 1, "Min Rank": 0},
                },
                "Silver Flip": {
                    "Sum Value": 2,
                    "Hit Value": 1,
                    "Min Rank": 2,
                    "Enable Crit": 2,
                    "Can Flip": True,
                    "Flipped": {"Sum Value": 1, "Hit Value": 1, "Min Rank": 1},
                },
                "Gold Flip": {
                    "Sum Value": 3,
                    "Hit Value": 1,
                    "Min Rank": 3,
                    "Enable Crit": 3,
                    "Can Flip": True,
                    "Flipped": {"Sum Value": 1, "Hit Value": 1, "Min Rank": 2},
                },
                "Blank Red": {
                    "Sum Value": [-1, 0],
                    "Hit Value": [-1, 0],
                    "Can Be Stolen": True,
                    "Can Flip": True,
                    "Flipped": {
                        "Sum Value": 1,
                        "Hit Value": 0,
                        "Can Be Stolen": False,
                        "Min Rank": 0,
                    },
                },
                "Miss": {"Sum Value": -1, "Hit Value": -1},
                "Miss Bronze": {
                    "Hit Value": [-1, 1, 1, 1],
                    "Min Rank": 0,
                    "Can Flip": False,
                },
                "Miss Silver": {
                    "Hit Value": [-1, -1, 1, 1],
                    "Min Rank": 0,
                    "Can Flip": False,
                },
                "Miss Gold": {
                    "Hit Value": [-1, -1, -1, 1],
                    "Min Rank": 0,
                    "Can Flip": False,
                },
                "Gobstopper": {"Sum Value": -2, "Hit Value": -2, "Ends Draws": True},
                "Gobstopper Miss": {
                    "Sum Value": -2,
                    "Hit Value": -2,
                    "Ends Draws": False,
                    "Can Flip": True,
                    "Flipped": {
                        "Sum Value": 1,
                        "Hit Value": -1,
                        "Min Rank": 0,
                        "Ends Draws": False,
                    },
                },
            },
        }

        self.pool.import_config_json(self.bag_config, "Base", False)

        logger = logging.getLogger("tipsyTokens.TokenBag")
        logger.debug("(Re)loaded TokenBag")

    @discord.slash_command(description="Make a pull from the tokenbag!")
    @option(
        "rank",
        description="Specify the skill rank for the pull",
        choices=["Unranked", "Bronze", "Silver", "Gold"],
    )
    @option(
        "fortune",
        description="Will you spend a fortune on the pull?",
        choices=["yes", "no"],
    )
    async def pull(self, ctx, rank, fortune):
        logger = logging.getLogger("tipsyTokens.TokenBag.pull")
        logger.info("Trying a pull")
        try:
            logger.debug(f"Got in rank:{rank} and fortune:{fortune}")

            numberRank = 0
            match rank:
                case "Gold":
                    numberRank = 3
                case "Silver":
                    numberRank = 2
                case "Bronze":
                    numberRank = 1
                case _:
                    numberRank = 0
            if rank != "Unranked":
                rank += " Rank"

            tag = ""
            fortune_str = ""
            if fortune == "yes":
                tag = "fortune-"
                fortune_str = " with Fortune"

            # we want 'pull-order' and 'hits' 'misses' 'crit' 'full' 'partial' 'failure'
            # and the fortune- variants
            the_pull = self.pool.pull()
            logger.debug("The whole pull:")
            logger.debug(the_pull)

            logger.debug("The max pull:")
            logger.debug(the_pull[-1])

            logger.debug(f"Using tag:{tag} and nRank:{numberRank}. We got:")
            """
            hits=0
            misses=0
            result = "Failure"
            pull_list=["Fail"]
            """
            rPull = the_pull[-1]['ranks'][numberRank]
            logger.debug(rPull)
            pull_list = rPull[f'{tag}pull-order'] if f'{tag}pull-order' in rPull else rPull['pull-order']

            hits = rPull[tag + "hits"]
            misses = rPull[tag + "misses"]

            result = "Failure"
            if rPull[f"{tag}crit"]:
                result = "Critical Success"
            elif rPull[f"{tag}full"]:
                result = "Full Success"
            elif rPull[f"{tag}partial"]:
                result = "Difficult Success"
            await ctx.respond(
                f"At {rank}{fortune_str} you pulled a {result} from {hits} hits and {misses} misses with: {', '.join(pull_list)}"
            )
        except Exception as e:
            logger.error(
                f"Experienced an error\n{type(e).__name__}: {e}\n{traceback.format_exc()}"
            )
            await ctx.send_response(
                content=f"Experienced an error\n{type(e).__name__}: {e}", ephemeral=True
            )


def setup(bot):
    bot.add_cog(TokenBag(bot))
