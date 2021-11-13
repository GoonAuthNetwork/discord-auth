from typing import Optional

from dispike.helper import Embed, color
from dispike.response import DiscordResponse

from app import __version__
from app.clients.goon_files_api import User


class AboutView:
    def about(server_count: int, user: Optional[User]) -> DiscordResponse:
        # Generic about
        embed = Embed(
            title="About The Goon Authentication Network",
            description=(
                "The Goon Authentication Network is a replacement for the decommissioned GDN, built from the ground up to for privacy and transparency. "  # noqa: E501
                "It is my hope that the community joins in this endeavor and creates a large, drama free, authentication network for goons.\n\n"  # noqa: E501
                "If you would like to help, visit the project's [github](https://github.com/GoonAuthNetwork/) "  # noqa: E501
                "or join the [GAN Hub](https://discord.gg/AW63YNcaDf) discord!"
            ),
            color=color.Color.teal(),
        )
        embed.set_footer(text=f"Running Discord-Auth v{__version__}")

        # Current user if it exists
        if user is not None:
            # embed.add_field(name="\u200B", value="\u200B", inline=False)
            embed.add_field(
                name="Current User",
                value=(
                    f"[{user.userName}](https://forums.somethingawful.com/member.php?"
                    f"action=getinfo&userid={user.userId})"
                ),
                inline=True,
            )
            embed.add_field(
                name="Authenticated At",
                value=user.createdAt.strftime("%m/%d/%y %I:%M %p"),
                inline=True,
            )
            embed.add_field(name="\u200b", value="\u200b")

        # GAN stats
        embed.add_field(name="Servers powered by GAN", value=server_count, inline=True)

        return DiscordResponse(content=" ", embeds=[embed], empherical=True)
