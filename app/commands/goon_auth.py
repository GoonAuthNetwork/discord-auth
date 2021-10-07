import typing
from dispike import interactions, IncomingDiscordSlashInteraction
from dispike.creating.components import ActionRow, Button, ButtonStyles, LinkButton
from dispike.creating.models.options import (
    CommandChoice,
    CommandOption,
    DiscordCommand,
    OptionTypes,
)
from dispike.eventer import EventTypes
from dispike.helper import Embed, color
from dispike.response import DiscordResponse


class AuthCollection(interactions.EventCollection):
    def __init__(self) -> None:
        super().__init__()

    # region Schemas
    def command_schemas(
        self,
    ) -> typing.List[
        typing.Union[interactions.PerCommandRegistrationSettings, DiscordCommand]
    ]:
        return [
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

    # endregion

    # region Handlers
    @interactions.on("auth")
    async def auth(
        self, username: str, ctx: IncomingDiscordSlashInteraction
    ) -> DiscordResponse:
        hash = "v5tyhbw546ubj57jnhws578hw68k"
        embed = Embed(
            type="rich",
            title="Goon Authentication",
            description=(
                "Please place the following hash anywhere in the "
                "**Additional Information** section of your Something Awful profile."
                f"\n\n**{hash}**\n\n"
                f"Note: The hash expires after **five minutes**\n\n"
                'Once finished, click the "Verify Hash" button below.'
            ),
            colour=color.Color.teal(),
        )
        embed.add_field(
            name="\u200B",
            value=(
                "Powerd by the opened-sourced "
                "[Goon Auth Network](https://github.com/GoonAuthNetwork)"
            ),
        )

        action_row = ActionRow(
            components=[
                LinkButton(
                    label="SA Profile",
                    url=(
                        "https://forums.somethingawful.com/member.php?"
                        "action=editprofile"
                    ),
                ),
                Button(
                    label="Verify Hash",
                    style=ButtonStyles.SUCCESS,
                    custom_id="auth.verify",
                ),
            ]
        )

        return DiscordResponse(
            content=" ", embeds=[embed], action_row=action_row, empherical=True
        )

    @interactions.on("auth.verify", type=EventTypes.COMPONENT)
    async def auth_verify(
        self, ctx: IncomingDiscordSlashInteraction
    ) -> DiscordResponse:
        embed = Embed(
            type="rich",
            title="Goon Authentication",
            description=(
                "Your authentication has succeeded. "
                "Please enjoy your new found gooniness.\n\n"
                "If you would like to know more about the Goon Auth Network "
                "please click below!"
            ),
            color=color.Colour.green(),
        )

        action_row = ActionRow(
            components=[
                LinkButton(label="GAN Github", url="https://github.com/GoonAuthNetwork")
            ]
        )

        return DiscordResponse(
            update_message=True,
            content=" ",
            embeds=[embed],
            action_row=action_row,
            empherical=True,
        )

    @interactions.on("about")
    async def about(self, ctx: IncomingDiscordSlashInteraction) -> DiscordResponse:
        embed = Embed(
            type="rich",
            title="About GoonAuthNetwork",
            description=(
                "Insert some giant monologue on the "
                "ethics of discord goon authentication here."
            ),
            color=color.Colour.teal(),
        )
        # TODO: Change this to http://forums.somethingawful.com/member.php?
        #   action=getinfo&username=<insert_sa_username_here>
        # embed.add_field(name="\u200B", value="\u200B", inline=False)
        embed.add_field(
            name="Authenticated",
            value=(
                "[NotOats](https://forums.somethingawful.com/member.php?"
                "action=editprofile)"
            ),
            inline=True,
        )
        embed.add_field(name="On", value="10/7/2021", inline=True)
        embed.add_field(
            name="\u200B",
            value=(
                "Powerd by the opened-sourced "
                "[Goon Auth Network](https://github.com/GoonAuthNetwork)"
            ),
            inline=False,
        )

        return DiscordResponse(embeds=[embed], empherical=True)

    @interactions.on("help")
    async def help(self, ctx: IncomingDiscordSlashInteraction) -> DiscordResponse:
        return DiscordResponse(
            content=(
                "Help is on the way! Maybe... eventually... probably not. "
                "This command doesn't do anything currently."
            ),
            empherical=True,
        )

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
