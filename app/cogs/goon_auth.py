from collections import OrderedDict
from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from loguru import logger


from app.clients.goon_auth_api import GoonAuthApi, GoonAuthStatus
from app.config import bot_settings


class LimitedSizeDict(OrderedDict):
    def __init__(self, max_size: int) -> None:
        super().__init__()
        self.max_size = max_size

    def __setitem__(self, k, v) -> None:
        super().__setitem__(k, v)
        self._check_size_limit()

    def _check_size_limit(self):
        while len(self) > self.max_size:
            self.popitem(last=False)


class GoonAuth(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

        # Auth Cache of discord users
        self.auth_attempts = LimitedSizeDict(2048)

        # Initialize clients here
        self.auth_api = GoonAuthApi("http://127.0.0.1:8001/", "")

    @cog_ext.cog_slash(name="ping", guild_ids=bot_settings.guild_ids)
    async def _ping(self, ctx: SlashContext):
        await ctx.send(f"Pong! ({self.bot.latency*1000}ms)")

    @cog_ext.cog_slash(
        name="auth",
        guild_ids=bot_settings.guild_ids,
        description="Proof of gooniness, required on some awful servers",
        options=[
            {
                "name": "username",
                "description": "Your username on Something Awful",
                "type": 3,
                "required": True,
            }
        ],
    )
    async def _auth_start(self, ctx: SlashContext, username: str):
        try:
            challenge = await self.auth_api.get_verification(username)
        except TypeError:
            await ctx.send("Invalid username, please try again.", hidden=True)
            return

        if challenge is None:
            await ctx.send(
                "This error should not exist, please tell your nearest GAN developer.",
                hidden=True,
            )
            return

        message = (
            "Please place the following hash into your Something Awful profile."
            "Anywhere in the **Additional Information** section here "
            "https://forums.somethingawful.com/member.php?action=editprofile\n\n"
            f"**{challenge.hash}**\n\n"
            f"Note: The hash expires after **five minutes**\n\n"
            "Once finished, use the command /auth_check\n"
        )

        await ctx.send(message, hidden=True)

        # Save sa username for this discord id for use in /auth_check
        self.auth_attempts[ctx.author_id] = username

    @cog_ext.cog_slash(
        name="auth_check",
        guild_ids=bot_settings.guild_ids,
        description="Check on your auth status. "
        "Only use after putting the hash in your profile.",
    )
    async def _auth_check(self, ctx: SlashContext):
        user_name = self.auth_attempts.get(ctx.author_id)
        if user_name is None:
            await ctx.send("Please use the following command first: /auth", hidden=True)
            return

        try:
            status = await self.auth_api.get_verification_update(user_name)
        except ValueError:
            await ctx.send("Please use the following command first: /auth", hidden=True)
            return
        except TypeError:
            await ctx.send("Invalid username, please try again.", hidden=True)
            return

        if status is None:
            await ctx.send(
                "This error should not exist, please tell your nearest GAN developer.",
                hidden=True,
            )
            return

        if status.validated:
            # Handle a valid user, include guild_id to update roles if needed
            await self.handle_valid_user(status, ctx.guild_id)
            await ctx.send("Validation succeeded, welcome to the Goon Auth Network")

            # Clean up the cache, we don't care if the key no longer exists
            try:
                self.auth_attempts.pop(ctx.author_id)
            except KeyError:
                pass
        else:
            await ctx.send(
                "Failed to validate, is the hash in your profile?", hidden=True
            )

    async def handle_valid_user(self, status: GoonAuthStatus, guild_id: int) -> None:
        logger.info(
            f"Authed: {status.user_name} | "
            f"id: {status.user_id} | "
            f"reg: {status.register_date} | "
            f"gid: {guild_id}"
        )


def setup(bot: commands.Bot):
    bot.add_cog(GoonAuth(bot))
