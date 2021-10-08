import typing

from dispike import interactions
from dispike.creating.models.options import (
    CommandChoice,
    CommandOption,
    DiscordCommand,
    OptionTypes,
)
from dispike.response import DiscordResponse
from loguru import logger


class OptionsCollection(interactions.EventCollection):
    def __init__(self, **kwargs) -> None:
        super().__init__()

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
        logger.info(f"OptionsCollection created {len(commands)} commands ({names})")
        return commands

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
