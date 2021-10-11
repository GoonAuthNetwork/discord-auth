from dispike.helper import Embed, color
from dispike.response import DiscordResponse

from app.models.goon_server import GoonServer


class SetupResponseBuilder:
    def not_server_owner() -> DiscordResponse:
        message = (
            "You're not the server owner! I think setup would be best left to them."
        )

        embed = Embed(
            type="rich",
            title="New Server Setup",
            description=message,
            color=color.Color.red(),
        )
        embed.add_field(
            name="\u200B",
            value=(
                "Powerd by the opened-sourced "
                "[Goon Auth Network](https://github.com/GoonAuthNetwork)"
            ),
        )

        return DiscordResponse(content=" ", embeds=[embed], empherical=True)

    def already_set() -> DiscordResponse:
        message = (
            "The server was already setup."
            " To change configuration options please use `/config`."
        )

        embed = Embed(
            type="rich",
            title="New Server Setup",
            description=message,
            color=color.Color.red(),
        )
        embed.add_field(
            name="\u200B",
            value=(
                "Powerd by the opened-sourced "
                "[Goon Auth Network](https://github.com/GoonAuthNetwork)"
            ),
        )

        return DiscordResponse(content=" ", embeds=[embed], empherical=True)

    def setup_ok(server: GoonServer) -> DiscordResponse:
        message = (
            "Congratulations, you now have stairs in your server!\n"
            "If you need any help with the bot please visit the GAN discord "
            "which can be found (here)[https://discord.gg/AW63YNcaDf].\n\n"
            "The server was setup with the following options, "
            "to change them please type `/config`."
        )

        embed = Embed(
            type="rich",
            title="New Server Setup",
            description=message,
            color=color.Color.green(),
        )

        for opt, value in server.options.items():
            value = opt.format_value_for_mention(value)

            embed.add_field(
                name=opt.value.replace("_", " ").title(), value=f"{value}", inline=True
            )

        embed.add_field(
            name="\u200B",
            value=(
                "Powerd by the opened-sourced "
                "[Goon Auth Network](https://github.com/GoonAuthNetwork)"
            ),
            inline=False,
        )

        return DiscordResponse(content=" ", embeds=[embed], empherical=True)
