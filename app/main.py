import discord
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext
from loguru import logger

from app.config import bot_settings, logging_settings

logging_settings.setup_loguru()

client = commands.Bot(command_prefix="!", intents=discord.Intents.all())
slash = SlashCommand(client, sync_commands=True)


@client.event
async def on_ready():
    logger.info("Discord bot ready")


@slash.slash(name="ping", guild_ids=bot_settings.guild_ids)
async def _ping(ctx: SlashContext):
    await ctx.send(f"Pong! ({client.latency*1000}ms)")


client.run(bot_settings.discord_token)
