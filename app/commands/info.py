import typing

from dispike import interactions, IncomingDiscordSlashInteraction
from dispike.creating.models.options import DiscordCommand
from dispike.response import DiscordResponse
from loguru import logger

from app.clients.goon_files_api import GoonFilesApi, Service
from app.commands.views import AboutView, HelpView


class InfoCollection(interactions.EventCollection):
    def __init__(self, files_api: GoonFilesApi, **kwargs) -> None:
        super().__init__()

        self.files_api = files_api

    def command_schemas(
        self,
    ) -> typing.List[
        typing.Union[interactions.PerCommandRegistrationSettings, DiscordResponse]
    ]:
        commands = [
            DiscordCommand(
                name="about",
                description="Information about this bot and your auth status.",
            ),
            DiscordCommand(
                name="help", description="Use this if you need Goon Auth Network help."
            ),
        ]

        names = ", ".join(map(lambda x: x.name, commands))
        logger.info(f"InfoCollection created {len(commands)} commands ({names})")
        return commands

    @interactions.on("about")
    async def about(self, ctx: IncomingDiscordSlashInteraction) -> DiscordResponse:
        # Pull Auth records and choose a response
        user = await self.files_api.find_user_by_service(
            Service.DISCORD, ctx.member.user.id
        )
        if user is not None:
            return AboutView.about_authed(user.userName, user.userId, user.createdAt)

        return AboutView.about_anonymous()

    @interactions.on("help")
    async def help(self, ctx: IncomingDiscordSlashInteraction) -> DiscordResponse:
        return HelpView.help()
