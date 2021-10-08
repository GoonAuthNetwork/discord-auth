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
from dispike.incoming.incoming_interactions import IncomingDiscordButtonInteraction
from dispike.response import DiscordResponse

from loguru import logger

from app.config import api_settings
from app.clients.goon_auth_api import GoonAuthApi
from app.clients.goon_files_api import GoonFilesApi, Service, ServiceToken
from app.commands.responses import (
    AboutResponseBuilder,
    AuthResponseBuilder,
    HelpResponseBuilder,
)


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

        logger.info(f"Using GoonAuthApi at {api_settings.awful_auth_address}")
        self.auth_api = GoonAuthApi(api_settings.awful_auth_address, "")

        logger.info(f"Using GoonFilesApi at {api_settings.goon_files_address}")
        self.files_api = GoonFilesApi(api_settings.goon_files_address, "")

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
        self, username: str, ctx: IncomingDiscordSlashInteraction
    ) -> DiscordResponse:
        author_id = ctx.member.user.id

        # Check if already authed in goon-files!
        user = await self.files_api.find_user_by_service(
            Service.DISCORD, ctx.member.user.id
        )
        if user is not None:
            logger.debug(
                "Previously authed - "
                f"guild: {ctx.guild_id}, author: {author_id}, user: {user.userName}"
            )

            # Previously auth'd give role
            if await self.grant_goon_role(author_id, ctx.guild_id):
                return AuthResponseBuilder.verification_ok(update_message=False)

            # Either already have the role or something went wrong
            # TODO: handle something went wrong
            else:
                return AuthResponseBuilder.challenge_error(
                    f"You're already authed as ({user.userName})"
                    "[https://forums.somethingawful.com/member.php?"
                    f"action=getinfo&userId={user.userId}]!"
                )

        # Get a challenge
        try:
            challenge = await self.auth_api.get_verification(username)
            if challenge is None:
                logger.error(
                    "Challenge is empty while getting verification - "
                    f"guild: {ctx.guild_id}, author: {author_id}, user: {username}"
                )
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

        logger.debug(
            f"Generated challenge - hash: {challenge.hash}, "
            f"user: {challenge.user_name}, author: {author_id}"
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

        logger.debug(f"Cancelled auth - author: {ctx.member.user.id}")

        # Send response
        return AuthResponseBuilder.verification_cancel()

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
                logger.error(
                    "Challenge update returned None - "
                    f"guild: {ctx.guild_id}, author: {author_id}, user: {username}"
                )
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
            # This prints a new message with the error to ensure
            # the original hash/verify/cancel buttons remain
            # TODO: Rate limit here
            return AuthResponseBuilder.verification_profile_hash_missing()

        # By this point we're authed, clean up & handle the rest
        try:
            self.in_progress_auths.pop(author_id)
        except KeyError:
            pass

        # Create or update the user in goon-files
        user = await self.files_api.create_or_update_user(
            userId=status.user_id,
            userName=status.user_name,
            regDate=status.register_date,
            serviceToken=ServiceToken(Service.DISCORD, author_id),
        )

        # Something went wrong...
        if user is None:
            logger.error(
                "Failed to save auth to db - "
                f"guild: {ctx.guild_id}, author: {author_id}, user: {username}"
            )
            return AuthResponseBuilder.verification_error(
                "Failed to save auth to database, please see a GAN admin."
            )

        # Update goon with role
        if not await self.grant_goon_role(author_id, ctx.guild_id):
            logger.error(
                "Failed to save grant role - "
                f"guild: {ctx.guild_id}, author: {author_id}, user: {username}"
            )
            return AuthResponseBuilder.verification_error(
                "Failed to grant role, please see a GAN admin "
                "and/or your local server admin."
            )

        logger.debug(
            "Authed user - "
            "guild: {ctx.guild_id}, author: {author_id}, user: {username}"
        )

        return AuthResponseBuilder.verification_ok()

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

    async def grant_goon_role(self, author_id: int, server_id: int) -> bool:
        # TODO: guild db with role info from /options
        logger.debug(f"Granting goon status - user: {author_id}, server: {server_id}")

        return True
