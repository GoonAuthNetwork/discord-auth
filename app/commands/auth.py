import typing

from dispike import interactions, IncomingDiscordSlashInteraction
from dispike.creating.models.options import (
    CommandOption,
    DiscordCommand,
    OptionTypes,
)
from dispike.eventer import EventTypes
from dispike.incoming.incoming_interactions import IncomingDiscordButtonInteraction
from dispike.response import DiscordResponse

from loguru import logger

from app.clients.goon_auth_api import GoonAuthApi
from app.clients.goon_files_api import GoonFilesApi
from app.commands.handlers.auth_handler import AuthHandler


class AuthCollection(interactions.EventCollection):
    def __init__(
        self,
        auth_api: GoonAuthApi,
        files_api: GoonFilesApi,
        **kwargs,
    ) -> None:
        super().__init__()

        self.auth_api = auth_api
        self.files_api = files_api

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
                        required=False,
                    )
                ],
            )
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

    # endregion
