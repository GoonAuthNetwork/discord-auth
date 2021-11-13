import typing

from dispike import interactions
from dispike.creating.models.options import CommandOption, DiscordCommand, OptionTypes
from dispike.incoming.incoming_interactions import IncomingDiscordSlashInteraction
from dispike.response import DiscordResponse
from loguru import logger

from app.clients.discord_api.client import DiscordClient
from app.config import bot_settings
from app.commands.views import SetupView
from app.models.goon_server import GoonServer, ServerOption


class SetupCollection(interactions.EventCollection):
    def __init__(self, **kwargs) -> None:
        super().__init__()
        self.discord_api = DiscordClient(bot_settings.discord_bot_token)

    def command_schemas(
        self,
    ) -> typing.List[
        typing.Union[interactions.PerCommandRegistrationSettings, DiscordResponse]
    ]:
        commands = [
            DiscordCommand(
                name="setup",
                description=(
                    "Setup authentication for this server. "
                    "Only usable by the server owner."
                ),
                options=[
                    CommandOption(
                        name="authenticated-role",
                        description="The role to assign authenticated users.",
                        type=OptionTypes.ROLE,
                        required=True,
                    ),
                    CommandOption(
                        name="admin-notice-channel",
                        description=(
                            "The channel to send admin notifications to. "
                            "The bot user must have message create permissions."
                        ),
                        type=OptionTypes.CHANNEL,
                        required=True,
                    ),
                    CommandOption(
                        name="auth-notice-channel",
                        description=(
                            "Optional channel to send auth notifications to. "
                            "The bot user must have message create permissions."
                        ),
                        type=OptionTypes.CHANNEL,
                        required=False,
                    ),
                ],
            )
        ]

        names = ", ".join(map(lambda x: x.name, commands))
        logger.info(f"SetupCollection created {len(commands)} commands ({names})")
        return commands

    # TODO: Hide this command after setup
    @interactions.on("setup")
    async def about(
        self,
        ctx: IncomingDiscordSlashInteraction,
        **kwargs,
    ) -> DiscordResponse:
        auth_role = kwargs.get("authenticated-role")
        admin_channel = kwargs.get("admin-notice-channel")

        # TODO: Block, rate limit?
        if ctx.member.user.id != await self.__find_server_owner(ctx.guild_id):
            return SetupView.not_server_owner()

        server = await GoonServer.find_server(ctx.guild_id)

        if server is not None:
            return SetupView.already_set()

        server = await GoonServer.save_options(
            ctx.guild_id,
            {
                ServerOption.AUTH_ROLE: auth_role,
                ServerOption.NOTICE_CHANNEL_ADMIN: admin_channel,
                ServerOption.NOTICE_CHANNEL_AUTH: kwargs.get(
                    "auth-notice-channel", admin_channel
                ),
            },
        )

        return SetupView.setup_ok(server)

    async def __find_server_owner(self, serverId: int) -> typing.Optional[int]:
        guild = await self.discord_api.get_guild(serverId)
        if guild is None:
            return None

        return guild.owner_id
