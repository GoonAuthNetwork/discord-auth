from datetime import datetime
from typing import Union

from dispike.incoming.discord_types.member import Member
from dispike.incoming.incoming_interactions import (
    IncomingDiscordButtonInteraction,
    IncomingDiscordSlashInteraction,
)
from dispike.response import DiscordResponse

from loguru import logger

from app.config import bot_settings
from app.mongodb import db
from app.clients.goon_auth_api import GoonAuthApi, GoonAuthStatus
from app.clients.goon_files_api import GoonFilesApi, Service, ServiceToken, User
from app.commands.responses.auth_responses import AuthResponseBuilder
from app.commands.utils import valid_sa_name
from app.models.user_auth_request import UserAuthRequest


class AuthHandler:
    def __init__(
        self, auth_api: GoonAuthApi = None, files_api: GoonFilesApi = None
    ) -> None:
        if auth_api is None:
            logger.info(f"Using new GoonAuthApi at {bot_settings.awful_auth_address}")
            auth_api = GoonAuthApi(bot_settings.awful_auth_address, "")

        if files_api is None:
            logger.info(f"Using new GoonFilesApi at {bot_settings.goon_files_address}")
            files_api = GoonFilesApi(bot_settings.goon_files_address, "")

        self.auth_api = auth_api
        self.files_api = files_api

    async def process_auth(
        self, ctx: IncomingDiscordSlashInteraction, **kwargs
    ) -> DiscordResponse:
        username: str = kwargs.get("username")

        if not valid_sa_name(username):
            return AuthResponseBuilder.verification_error(
                "Invalid username, please try again"
            )

        user = await self.files_api.find_user_by_service(
            service=Service.DISCORD, token=ctx.member.user.id
        )

        if user is None:
            return await self.__auth_new(username, ctx)

        if user.userName.lower() != username.lower():
            return AuthResponseBuilder.verification_error("That's not your sa name!")

        return await self.__auth_existing(user, ctx)

    async def __auth_new(
        self, username: str, ctx: IncomingDiscordButtonInteraction
    ) -> DiscordResponse:
        """Auth a new user

        Args:
            username (str): Validated Something Awful username
            ctx (IncomingDiscordButtonInteraction): [description]
        """
        logger.debug(
            f"New auth request - guild: {ctx.guild_id}, "
            f"user: {ctx.member.user.id}, username: {username}"
        )

        try:
            challenge = await self.auth_api.get_verification(username)
            if challenge is None:
                logger.error(
                    "get_verification returned None - "
                    f"guild: {ctx.guild_id}, author: {ctx.member.user.id}, "
                    f"user: {username}"
                )
                return AuthResponseBuilder.challenge_error(
                    "Failed to get challenge hash, please contact a GAN admin."
                )
        except TypeError:
            return AuthResponseBuilder.verification_error(
                "Invald username, please try again!"
            )

        # Check for existing auth attempt with this hash
        existing_attempt = await db.engine.find_one(
            UserAuthRequest, UserAuthRequest.challengeHash == challenge.hash
        )

        if existing_attempt is not None:
            if existing_attempt.userDiscordId != ctx.member.user.id:
                # Someone is trying to auth in an existing attempt that isn't theirs
                return AuthResponseBuilder.challenge_error(
                    "Someone is already attemping to auth with that username. "
                    f"Are you sure you're `{username}`?"
                )

        # Delete any old auth requestrs for the discordId
        await self.__delete_auth_attempts(ctx.member.user.id)

        # Save the new one
        result = await db.engine.save(
            UserAuthRequest(
                userDiscordId=ctx.member.user.id,
                saName=username,
                challengeHash=challenge.hash,
                lastUpdated=datetime.now(),
            )
        )

        # Send response
        logger.debug(
            f"Generated challenge - hash: {result.challengeHash}, "
            f"user: {result.saName}, author: {result.userDiscordId}, "
            f"lastUpdated: {result.lastUpdated}, objId: {result.id}"
        )
        return AuthResponseBuilder.challenge_ok(challenge.hash)

    async def __auth_existing(
        self, user: User, ctx: IncomingDiscordButtonInteraction
    ) -> DiscordResponse:
        """Auth an existing user on this server

        Args:
            user (User): The currently stored user information
            ctx (IncomingDiscordButtonInteraction): [description]
        """
        logger.debug(
            f"Existing auth request - guild: {ctx.guild_id}, "
            f"user: {ctx.member.user.id}, user.userName: {user.userName}"
        )

        if await self.__check_user_auth_role(ctx.member, ctx.guild_id):
            return AuthResponseBuilder.verification_error(
                "You're already authenticated in this server."
            )

        # TODO: Return embed with ok/cancel to allow user to accept auth on server

        if await self.__grant_user_auth_role(ctx.member, ctx.guild_id):
            return AuthResponseBuilder.verification_ok(
                message=f"Welcome back {user.userName}, you're already "
                "authenticated so you get to skip the line!",
                update_message=False,
            )

        logger.error(
            f"Existing user failed to get role - guild: {ctx.guild_id}, "
            f"user: {ctx.member.user.id}"
        )
        return AuthResponseBuilder.verification_error(
            "Something went wrong, please contact a GAN admin."
        )

    async def process_auth_verify(
        self, ctx: IncomingDiscordButtonInteraction
    ) -> DiscordResponse:
        authRequest = await db.engine.find_one(
            UserAuthRequest, UserAuthRequest.userDiscordId == ctx.member.user.id
        )
        if authRequest is None:
            return AuthResponseBuilder.verification_error(
                "Your seem to be missing from the database. Did you wait too long?\n"
                "Please try again from /auth."
            )

        # TODO: Rate limit here
        authStatus = await self.__check_awful_auth_verification(authRequest)
        if authStatus is str:
            return AuthResponseBuilder.verification_error(authStatus)

        if not authStatus.validated:
            return AuthResponseBuilder.verification_profile_hash_missing()

        user = await self.files_api.create_or_update_user(
            userId=authStatus.user_id,
            userName=authStatus.user_name,
            regDate=authStatus.register_date,
            serviceToken=ServiceToken(Service.DISCORD, ctx.member.user.id),
        )
        if user is None:
            logger.error(
                "Failed to save auth to db - "
                f"discordId: {ctx.member.user.id}, saName: {authStatus.user_name}"
            )
            return AuthResponseBuilder.verification_error(
                "Failed to save auth to database, please see a GAN admin."
            )

        if not await self.__grant_user_auth_role(ctx.member, ctx.guild_id):
            logger.error(
                "Failed to save grant role - "
                f"discordId: {authRequest.userDiscordId}, "
                f"saName: {authRequest.saName}"
            )
            return AuthResponseBuilder.verification_error(
                "Failed to grant role, please see a GAN admin "
                "and/or your local server admin."
            )

        await self.__delete_auth_attempts(ctx.member.user.id)

        logger.debug(
            "Authed user - "
            f"guild: {ctx.guild_id}, discordId: {authRequest.userDiscordId}, "
            f"saName: {authRequest.saName}"
        )

        return AuthResponseBuilder.verification_ok()

    async def __check_awful_auth_verification(
        self, authRequest: UserAuthRequest
    ) -> Union[GoonAuthStatus, str]:
        """Checks a UserAuthRequest against the awful-auth api.
        Returned the auth status or an error message

        Returns:
            Union[GoonAuthStatus, str]: [description]
        """
        try:
            status = await self.auth_api.get_verification_update(authRequest.saName)
        except ValueError:
            return "Please use the following command first: /auth"
        except TypeError:
            return "Invalid username, please try again"

        if status is None:
            logger.error(
                "Challenge update returned None - "
                f"discordId: {authRequest.userDiscordId}, "
                f"saName: {authRequest.saName}"
            )
            return (
                "This error should not exist, "
                "please tell your nearest GAN developer.",
            )

        return status

    async def process_auth_cancel(
        self, ctx: IncomingDiscordButtonInteraction
    ) -> DiscordResponse:
        # TODO: Delete from awful-auth. currently it'll time out after 5m

        await self.__delete_auth_attempts(ctx.member.user.id)

        return AuthResponseBuilder.verification_cancel()

    async def __delete_auth_attempts(self, discordId: int) -> None:
        auth_requests = await db.engine.find(
            UserAuthRequest, UserAuthRequest.userDiscordId == discordId
        )

        for req in auth_requests:
            await db.engine.delete(req)

    async def process_auth_decline(
        self, ctx: IncomingDiscordButtonInteraction
    ) -> DiscordResponse:
        # TODO: process_auth_decline impl
        return DiscordResponse()

    async def __check_user_auth_role(self, member: Member, guild_id: int) -> bool:
        """Checks if a user has the authorized role in a guild.

        Args:
            member (Member): The user
            guild_id (int): The guild id

        Returns:
            bool: True if the user has the role
        """
        # TODO: __check_user_auth_role impl
        return False

    async def __grant_user_auth_role(self, member: Member, guild_id: int) -> bool:
        """Grants a user the correct authorized role in a guild.

        Args:
            member (Member): The user
            guild_id (int): The guild id

        Returns:
            bool: True if the role was granted, otherwise false.
        """
        # TODO: __grant_user_auth_role impl
        logger.debug(
            f"Granting goon status - user: {member.user.id}, server: {guild_id}"
        )

        return True
