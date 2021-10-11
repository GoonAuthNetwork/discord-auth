import typing
import odmantic

from enum import Enum
from loguru import logger

from app.mongodb import db


class ServerOption(str, Enum):
    AUTH_ROLE = "auth_role"
    NOTICE_CHANNEL_AUTH = "auth_notice_channel"
    NOTICE_CHANNEL_ADMIN = "admin_notice_channel"


class GoonServer(odmantic.Model):
    serverId: int = odmantic.Field(..., title="The discord server's id")
    options: typing.Optional[typing.Dict[ServerOption, str]] = odmantic.Field(
        description="The server's options", default=None
    )

    @staticmethod
    async def find_server(serverId: int) -> typing.Optional["GoonServer"]:
        return await db.engine.find_one(GoonServer, GoonServer.serverId == serverId)

    @staticmethod
    async def find_option(serverId: int, option: ServerOption) -> typing.Optional[str]:
        server = await GoonServer.find_server(serverId)
        if server is None or server.options is None:
            logger.error(
                "Searching for non existant option or server - "
                f"serverId:{serverId}, opt: {option.value}"
            )

            return None

        return server.options.get(option, None)

    @staticmethod
    async def save_options(
        server: typing.Union[int, "GoonServer"],
        options: typing.Dict[ServerOption, str],
    ) -> "GoonServer":
        if isinstance(server, int):
            serverId = server

            server = await GoonServer.find_server(serverId)
            if server is None:
                server = GoonServer(serverId=serverId)

        if server.options is None:
            server.options = dict()

        server.options.update(options)

        await db.engine.save(server)

        return server
