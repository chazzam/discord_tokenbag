import logging
import traceback

import discord
from discord import option
# from discord.commands import SlashCommandGroup

# import random
from discord.ext import commands

from tokenbag import TokenBag as bag
from tokenbag import PullType


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
                    "Ends Draws": True,
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
        "pull_type",
        description="What type of pull is this?",
        choices=["Action", "Resistance", "Befell"],
    )
    async def pull(self, ctx, rank, pull_type):
        logger = logging.getLogger("tipsyTokens.TokenBag.pull")
        logger.info("Trying a pull")
        try:
            logger.debug(f"Got in rank:{rank} and pull type:{pull_type}")

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

            ptype = PullType.Action
            if pull_type == "Resistance":
                ptype = PullType.Resistance
            elif pull_type == "Befell":
                ptype = PullType.Befell

            # we want 'pull-order' and 'hits' 'misses' 'crit' 'full' 'partial' 'failure'
            # and the fortune- variants
            the_pull_list = self.pool.pull_one(numberRank, ptype)
            logger.debug("The whole pull:")
            logger.debug(the_pull_list)

            logger.debug(f"Using type:{ptype} and nRank:{numberRank}.")
            result = ""

            if ptype == PullType.Befell:
                the_pull = the_pull_list[0]
                bHits = the_pull["hits"]
                bResult = (
                    "**Poor Outcomes** (enough information to know where to look, "
                    "a highly ephemeral version of something, Desperate Positioning.)"
                )
                if bHits >= 3:
                    bResult = (
                        "**Incredible Outcomes** (unbelievably useful information, exquisite "
                        "version of something from the rucksack, Controlled Positioning)"
                    )
                elif bHits >= 2:
                    bResult = (
                        "**Very Good Outcomes** (actionable and useful information, exceptional "
                        "version of something, Controlled Positioning)"
                    )
                elif bHits >= 1:
                    bResult = (
                        "**Mediocre Outcomes** (actionable information, a usable version of "
                        "something, Risky Positioning)"
                    )

                result = (
                    f"You did a {pull_type} pull at {rank} and "
                    f"drew {bHits} hits via:\n*{', '.join(the_pull['pull-order'])}*.\n\n"
                    f"This results in {bResult}\n"
                )
            elif ptype == PullType.Resistance:
                the_pull = the_pull_list[0]
                result = (
                    f"You did a {pull_type} pull at {rank} and "
                    f"drew:\n*{', '.join(the_pull['pull-order'])}*.\n"
                    f"This results in:\n"
                    f"- Losing {the_pull['costs']['lost']} fortune.\n"
                    f"- Taking {the_pull['costs']['taken']} fortune and"
                    " converting it into your own Karma.\n"
                    f"- With up to {the_pull['costs']['mitigated']} of any lost fortune able to be spent from Karma instead of the Fortune pool."
                )
                if the_pull["costs"]["mitigated"] >= 3:
                    result = (
                        f"You did a {pull_type} pull at {rank} and "
                        f"drew:\n*{', '.join(the_pull['pull-order'])}*.\n"
                        f"This results in:\n"
                        "- ***Three Hits!*** One Fortune is returned to the game as your Karma!"
                    )
            else:
                result = f"You did an Action pull at {rank}:\n"
                spoiler_begin = ""
                spoiler_end = ""
                for the_pull in the_pull_list:
                    bHits = the_pull["hits"]
                    bMisses = the_pull["misses"]
                    bResult = "Failure"
                    if the_pull["crit"]:
                        bResult = "Critical Success"
                    elif the_pull["full"]:
                        bResult = "Success"
                    elif the_pull["partial"]:
                        bResult = "Success with Consequences"

                    fHits = the_pull["fortune-hits"]
                    fMisses = the_pull["fortune-misses"]
                    fResult = "Failure"
                    if the_pull["fortune-crit"]:
                        fResult = "Critical Success"
                    elif the_pull["fortune-full"]:
                        fResult = "Success"
                    elif the_pull["fortune-partial"]:
                        fResult = "Success with Consequences"

                    result += (
                        "~~                                               ~~\n"
                        f"{spoiler_begin}"
                        f"- Without Fortune you drew: *{', '.join(the_pull['pull-order'])}*. "
                        f"This results in a **{bResult}** from {bHits} hits and {bMisses} misses.\n"
                        f"- With Fortune you drew: *{', '.join(the_pull['fortune-pull-order'])}*. "
                        f"This results in a **{fResult}** from {fHits} hits and {fMisses} misses."
                        f"{spoiler_end}\n"
                    )
                    spoiler_begin = "Draw Again?:\n||"
                    spoiler_end = "||"

            await ctx.respond(result)
        except Exception as e:
            logger.error(
                f"Experienced an error\n{type(e).__name__}: {e}\n{traceback.format_exc()}"
            )
            await ctx.send_response(
                content=f"Experienced an error\n{type(e).__name__}: {e}", ephemeral=True
            )


def setup(bot):
    bot.add_cog(TokenBag(bot))
