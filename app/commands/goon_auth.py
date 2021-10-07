import typing
from collections import OrderedDict
from dispike import interactions, IncomingDiscordSlashInteraction
from dispike.creating.models.options import (
    CommandChoice,
    CommandOption,
    DiscordCommand,
    OptionTypes,
)
from dispike.eventer import EventTypes
from dispike.helper import Embed, color
from dispike.incoming.incoming_interactions import IncomingDiscordButtonInteraction
from dispike.response import DiscordResponse

from app.clients.goon_auth_api import GoonAuthApi
from app.commands.responses.auth_responses import AuthResponseBuilder


# TODO: Use redis for this very ghetto cache
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


class AuthCollection(interactions.EventCollection):
    def __init__(self) -> None:
        super().__init__()

        self.in_progress_auths = LimitedSizeDict(4096)

        # TODO: Configurable api location
        self.auth_api = GoonAuthApi("http://127.0.0.1:8001", "")

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
        # TODO: Check if already authed in goon-files!

        # Get a challenge
        try:
            challenge = await self.auth_api.get_verification(username)
            if challenge is None:
                return AuthResponseBuilder.challenge_error(
                    "This error should not exist, "
                    "please tell your nearest GAN developer.",
                )
        except TypeError:
            return AuthResponseBuilder.challenge_error(
                "Invalid username, please try again."
            )

        # Save the username & discord is.
        # Maybe change to to only save the challenge & id?
        # Would require a rewrite of awful-auth.
        self.in_progress_auths[ctx.member.user.id] = username

        # Send response
        message = (
            "Please place the following hash anywhere in the "
            "**Additional Information** section of your Something Awful profile."
            f"\n\n**{challenge.hash}**\n\n"
            f"Note: The hash expires after **five minutes**\n\n"
            'Once finished, click the "Verify Hash" button below.'
        )

        return AuthResponseBuilder.challenge_ok(message)

    @interactions.on("auth.cancel", type=EventTypes.COMPONENT)
    async def auth_cancel(
        self, ctx: IncomingDiscordButtonInteraction
    ) -> DiscordResponse:
        # TODO: Delete from awful-auth. currently it'll time out after 5m

        # Cleanup in progress auth cache
        try:
            self.in_progress_auths.pop(ctx.member.user.id)
        except KeyError:
            pass

        # Send response
        return AuthResponseBuilder.auth_cancel()

    @interactions.on("auth.verify", type=EventTypes.COMPONENT)
    async def auth_verify(
        self, ctx: IncomingDiscordButtonInteraction
    ) -> DiscordResponse:
        author_id = ctx.member.user.id

        # Pull username from cache
        username = self.in_progress_auths.get(author_id)
        if username is None:
            return AuthResponseBuilder.verification_error(
                "Missing from the auth cache, please try again from /auth",
            )

        # Try to get the status of auth
        try:
            status = await self.auth_api.get_verification_update(username)
            if status is None:
                return AuthResponseBuilder.verification_error(
                    "This error should not exist, "
                    "please tell your nearest GAN developer.",
                )
        except ValueError:
            return AuthResponseBuilder.verification_error(
                "Please use the following command first: /auth",
            )
        except TypeError:
            return AuthResponseBuilder.verification_error(
                "Invalid username, please try again",
            )

        # In auth system but hash isn't on profile page
        if not status.validated:
            # TODO: verification_profile_hash_missing()
            # Leave Profile/Verify/Cancel buttons, etc
            return AuthResponseBuilder.verification_error(
                "Failed to validate, is the hash in your profile?"
            )

        # Handle valid user
        # goon-files.add()

        # Clean up
        try:
            self.in_progress_auths.pop(author_id)
        except KeyError:
            pass

        return AuthResponseBuilder.verification_ok()

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
