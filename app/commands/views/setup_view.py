from dispike.helper import Embed, color
from dispike.response import DiscordResponse

from app.models.goon_server import GoonServer
from .utils import create_response


class SetupView:
    def not_server_owner() -> DiscordResponse:
        embed = Embed(
            title="New Server Setup",
            description=(
                "You're not the server owner! I think setup would be best left to them."
            ),
            color=color.Color.red(),
        )

        return create_response(embed)

    def already_set() -> DiscordResponse:
        embed = Embed(
            title="New Server Setup",
            description=(
                "The server was already setup."
                " To change configuration options please use `/config`."
            ),
            color=color.Color.red(),
        )

        return create_response(embed)

    def setup_ok(server: GoonServer) -> DiscordResponse:
        embed = Embed(
            title="New Server Setup",
            description=(
                "Congratulations, you now have stairs in your server!\n"
                "If you need any help with the bot please visit the GAN discord "
                "which can be found (here)[https://discord.gg/AW63YNcaDf].\n\n"
                "The server was setup with the following options, "
                "to change them please type `/config`."
            ),
            color=color.Color.green(),
        )

        for opt, value in server.options.items():
            value = opt.format_value_for_mention(value)

            embed.add_field(
                name=opt.value.replace("_", " ").title(), value=f"{value}", inline=True
            )

        return create_response(embed)
