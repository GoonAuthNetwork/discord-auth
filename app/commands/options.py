import typing

from dispike import interactions, IncomingDiscordSlashInteraction
from dispike.creating.models.options import (
    CommandOption,
    DiscordCommand,
    OptionTypes,
)
from dispike.eventer import EventTypes
from dispike.main import Dispike
from dispike.response import DiscordResponse
from loguru import logger


class OptionHandler(typing.Protocol):
    def __call__(
        self, ctx: IncomingDiscordSlashInteraction, **kwargs: typing.Any
    ) -> DiscordResponse:
        ...


class OptionsCollection(interactions.EventCollection):
    def __init__(self, bot: Dispike, **kwargs) -> None:
        super().__init__()
        self.bot = bot

    def command_schemas(
        self,
    ) -> typing.List[
        typing.Union[interactions.PerCommandRegistrationSettings, DiscordResponse]
    ]:
        commands = [
            DiscordCommand(
                name="options",
                description=(
                    "Various options for the server owner to play with. "
                    "These apply to **your** server only."
                ),
                options=[
                    self.__create_option(
                        "authenticated_role",
                        "The role to give to authenticated users.",
                        self.__handle_authenticated_role,
                    ),
                    self.__create_option(
                        "auth_notification_channel",
                        "The channel to send notifications of authentications to.",
                        self.__handle_auth_notification_channel,
                    ),
                ],
            ),
        ]

        names = ", ".join(map(lambda x: x.name, commands))
        logger.info(f"OptionsCollection created {len(commands)} commands ({names})")
        return commands

    def __create_option(
        self,
        name: str,
        description: str,
        handler: OptionHandler,
        type: OptionTypes = OptionTypes.STRING,
    ) -> CommandOption:
        # Set handler
        self.bot.on(f"options.{name}", type=EventTypes.COMMAND, func=handler)

        # Create the option
        return CommandOption(
            name=name,
            description=description,
            type=OptionTypes.SUB_COMMAND,
            options=[
                CommandOption(
                    name="set",
                    description="Value to change this option to.",
                    type=type,
                    required=False,
                )
            ],
        )

    async def __handle_authenticated_role(
        self, ctx: IncomingDiscordSlashInteraction, **kwargs
    ) -> DiscordResponse:
        return DiscordResponse("HANDLE AUTHENTICATED ROLE", empherical=True)

    async def __handle_auth_notification_channel(
        self, ctx: IncomingDiscordSlashInteraction, **kwargs
    ) -> DiscordResponse:
        return DiscordResponse("HANDLE AUTH NOTIFICATION CHANNEL", empherical=True)

    # This has to exist for dumb dispike EventCollection registering reasons
    @interactions.on("options.authenticated_role")
    async def options(self, **kwargs) -> DiscordResponse:
        return DiscordResponse("HANDLE AUTHENTICATED ROLE - STATIC", empherical=True)
