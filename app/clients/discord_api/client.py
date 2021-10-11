from typing import Optional
from urllib.parse import quote

from httpx import AsyncClient, Response
from loguru import logger

from app.clients.discord_api.models.channel import Channel

from .constants import AuthType, HttpMethods, DiscordHeaders
from .endpoints import Api


defaultHeaders = {
    # TODO: Read this from somewhere, pyproject.toml?
    "user-agent": "DiscordBot (https://github.com/GoonAuthNetwork/discord-auth, v1.0)"
}


class RatelimitExceeded(Exception):
    def __init__(self, retry_after: int = None, *args: object) -> None:
        super().__init__(*args)
        self.retry_after = retry_after


class DiscordClient:
    def __init__(
        self,
        token: str = None,
        authType: AuthType = AuthType.BOT,
        errorOnRateLimit: bool = True,
    ) -> None:
        self.token = token
        self.authType = authType
        self.errorOnRateLimit = errorOnRateLimit

        self.client = AsyncClient(headers=defaultHeaders)

    def __token_formatted(self) -> str:
        if self.token is None:
            return ""

        return f"{self.authType.value} {self.token}"

    async def __request(
        self, path: str, method: HttpMethods = HttpMethods.GET, headers=None
    ) -> Response:
        _headers = {"Authorization": self.__token_formatted()}

        if headers is not None:
            _headers.update(headers)

        url = Api.BASE_PATH + path

        logger.debug(f"API REQUEST: {method.value} {url}")

        response = await self.client.request(
            method=method.value, url=url, headers=_headers
        )

        if self.errorOnRateLimit and response.status_code == 429:
            raise RatelimitExceeded(int(response.headers.get("Retry-After")))

        return response

    async def get_channel(self, channelId: int) -> Optional[Channel]:
        path = Api.CHANNEL.format(channelId=channelId)
        response = await self.__request(path, HttpMethods.GET)

        if response.status_code == 200:
            return Channel(**response.json())

        return None

    async def add_guild_member_role(
        self, guildId: int, userId: int, roleId: int, reason: str = None
    ) -> bool:
        headers = dict()
        if reason is not None:
            headers[DiscordHeaders.AUDIT_LOG_REASON.value] = quote(reason)

        path = Api.GUILD_MEMBER_ROLE.format(
            guildId=guildId, userId=userId, roleId=roleId
        )

        response = await self.__request(path, HttpMethods.PUT, headers)

        return response.status_code == 204

    async def remove_guild_member_role(
        self, guildId: int, userId: int, roleId: int, reason: str = None
    ) -> bool:
        headers = dict()
        if reason is not None:
            headers[DiscordHeaders.AUDIT_LOG_REASON.value] = quote(reason)

        path = Api.GUILD_MEMBER_ROLE.format(
            guildId=guildId, userId=userId, roleId=roleId
        )

        response = await self.__request(path, HttpMethods.DELETE, headers)

        return response.status_code == 204
