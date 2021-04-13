from discord.ext import commands
from discord_slash import cog_ext, SlashContext

from app.config import bot_settings


class GoonAuth(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @cog_ext.cog_slash(name="ping", guild_ids=bot_settings.guild_ids)
    async def _ping(self, ctx: SlashContext):
        await ctx.send(f"Pong! ({self.bot.latency*1000}ms)")


def setup(bot: commands.Bot):
    bot.add_cog(GoonAuth(bot))
