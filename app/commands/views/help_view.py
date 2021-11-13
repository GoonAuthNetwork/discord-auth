from dispike.helper import Embed, color
from dispike.response import DiscordResponse


class HelpView:
    def help() -> DiscordResponse:
        message = (
            "Hello user, this authentication bot is still fairly new. While it is "
            "improving rapidly you might run into some issues and/or bugs.\n\n"
            "For support please visit the [GAN Hub](https://discord.gg/AW63YNcaDf) and "
            "visit the `#auth-support` channel."
        )

        embed = Embed(
            type="rich",
            title="Help is on the way!",
            description=message,
            color=color.Color.teal(),
        )

        embed.add_field(
            name="\u200B",
            value=(
                "Powered by the open-source "
                "[Goon Auth Network](https://github.com/GoonAuthNetwork)"
            ),
            inline=False,
        )

        return DiscordResponse(content=" ", embeds=[embed], empherical=True)
