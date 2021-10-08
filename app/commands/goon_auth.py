import typing

from dispike import interactions, IncomingDiscordSlashInteraction
from dispike.creating.models.options import (
    CommandChoice,
    CommandOption,
    DiscordCommand,
    OptionTypes,
)
from dispike.eventer import EventTypes
from dispike.incoming.incoming_interactions import IncomingDiscordButtonInteraction
from dispike.response import DiscordResponse

from loguru import logger

from app.config import bot_settings
from app.clients.goon_auth_api import GoonAuthApi
from app.clients.goon_files_api import GoonFilesApi, Service
from app.commands.responses import (
    AboutResponseBuilder,
    HelpResponseBuilder,
)
from app.commands.handlers.auth_handler import AuthHandler


class AuthCollection(interactions.EventCollection):
    def __init__(self) -> None:
        super().__init__()

        logger.info(f"Using GoonAuthApi at {bot_settings.awful_auth_address}")
        self.auth_api = GoonAuthApi(bot_settings.awful_auth_address, "")

        logger.info(f"Using GoonFilesApi at {bot_settings.goon_files_address}")
        self.files_api = GoonFilesApi(bot_settings.goon_files_address, "")

        self.auth_handler = AuthHandler(self.auth_api, self.files_api)

    # region Schemas
    def command_schemas(
        self,
    ) -> typing.List[
        typing.Union[interactions.PerCommandRegistrationSettings, DiscordCommand]
    ]:
        commands = [
            DiscordCommand(
                name="auth",
                description=(
                    "Proof of gooniness, some say it's required in awful places."
                ),
                options=[
                    CommandOption(
                        name="username",
                        description="Your username on Something Awful",
                        type=OptionTypes.STRING,
                        required=True,
                    )
                ],
            ),
            DiscordCommand(
                name="about",
                description="Information about this bot and your auth status.",
            ),
            DiscordCommand(
                name="help", description="Use this if you need Goon Auth Network help."
            ),
            DiscordCommand(
                name="options",
                description=(
                    "Various options for the server owner to play with. "
                    "These apply to authing on **your** server only."
                ),
                options=[
                    CommandOption(
                        name="key",
                        description="The option to show/change.",
                        type=OptionTypes.STRING,
                        required=True,
                        choices=[
                            CommandChoice(name="Auth - Goon Role", value="goon-role"),
                            CommandChoice(
                                name="Auth - SA Account Age (in days)",
                                value="sa-account-age",
                            ),
                            CommandChoice(
                                name="Notifications - Auth Channel",
                                value="auth-info-chan",
                            ),
                            CommandChoice(
                                name="Notifications - Perma Ban Channel",
                                value="auth-info-chan",
                            ),
                        ],
                    ),
                    CommandOption(
                        name="value",
                        description="The option's value to set.",
                        type=OptionTypes.STRING,
                        required=False,
                    ),
                ],
            ),
        ]

        names = ", ".join(map(lambda x: x.name, commands))
        logger.info(f"AuthCollection created {len(commands)} commands ({names})")
        return commands

    # endregion

    # region Handlers
    @interactions.on("auth")
    async def auth(
        self, ctx: IncomingDiscordSlashInteraction, **kwargs
    ) -> DiscordResponse:
        return await self.auth_handler.process_auth(ctx, **kwargs)

    @interactions.on("auth.cancel", type=EventTypes.COMPONENT)
    async def auth_cancel(
        self, ctx: IncomingDiscordButtonInteraction
    ) -> DiscordResponse:
        return await self.auth_handler.process_auth_cancel(ctx)

    @interactions.on("auth.verify", type=EventTypes.COMPONENT)
    async def auth_verify(
        self, ctx: IncomingDiscordButtonInteraction
    ) -> DiscordResponse:
        return await self.auth_handler.process_auth_verify(ctx)

    @interactions.on("about")
    async def about(self, ctx: IncomingDiscordSlashInteraction) -> DiscordResponse:
        # Pull Auth records and choose a response
        user = await self.files_api.find_user_by_service(
            Service.DISCORD, ctx.member.user.id
        )
        if user is not None:
            return AboutResponseBuilder.about_authed(
                user.userName, user.userId, user.createdAt
            )

        return AboutResponseBuilder.about_anonymous()

    @interactions.on("help")
    async def help(self, ctx: IncomingDiscordSlashInteraction) -> DiscordResponse:
        return HelpResponseBuilder.help()

    @interactions.on("options")
    async def options(self, **kwargs) -> DiscordResponse:
        key = kwargs.get("key")
        value = kwargs.get("value")
        # ctx = kwargs.get("ctx")

        if value is None:
            value = "DEFAULT/EXISTING"
            update = False
        else:
            update = True

        return DiscordResponse(
            content=f"show_goon_role! - {key}:{value} - update: {update}",
            empherical=True,
        )

    # endregion

    async def check_goon_role(self, author_id: int, server_id: int) -> bool:
        """Checks if a goon has the specified role on the server

        Args:
            author_id (int): goon's discord id
            server_id (int): server's discord id

        Returns:
            bool: True if the goon has the role
        """

        return False

    async def grant_goon_role(self, author_id: int, server_id: int) -> bool:
        """Grants a goon the correct role for the server

        Args:
            author_id (int): goon's discord id
            server_id (int): server's discord id

        Returns:
            bool: True if the role was granted
        """
        # TODO: guild db with role info from /options
        logger.debug(f"Granting goon status - user: {author_id}, server: {server_id}")

        return True
