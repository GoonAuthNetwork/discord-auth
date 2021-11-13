from dispike.helper import Embed, color
from dispike.response import DiscordResponse

from .utils import create_response


class HelpView:
    def help() -> DiscordResponse:
        embed = Embed(
            title="Help is on the way!",
            description=(
                "Hello user, this authentication bot is still fairly new. While it is improving rapidly you might run into some issues and/or bugs.\n\n"  # noqa: E501
                "For support please visit the [GAN Hub](https://discord.gg/AW63YNcaDf) and visit the `#auth-support` channel."  # noqa: E501
            ),
            color=color.Color.teal(),
        )

        return create_response(embed)
