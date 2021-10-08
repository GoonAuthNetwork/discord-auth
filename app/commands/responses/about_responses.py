from datetime import datetime

from dispike.helper import Embed, color
from dispike.response import DiscordResponse


class AboutResponseBuilder:
    about_ethics = (
        "Insert some giant monologue on the "
        "ethics of discord goon authentication here."
    )

    def about_authed(
        username: str, user_id: int, auth_date: datetime
    ) -> DiscordResponse:
        embed = Embed(
            type="rich",
            title="About GoonAuthNetwork",
            description=AboutResponseBuilder.about_ethics,
            color=color.Colour.teal(),
        )

        embed.add_field(
            name="Authenticated",
            value=(
                f"[{username}](https://forums.somethingawful.com/member.php?"
                f"action=getinfo&userid={user_id})"
            ),
            inline=True,
        )
        embed.add_field(
            name="At", value=auth_date.strftime("%m/%d/%y %I:%M %p"), inline=True
        )

        embed.add_field(
            name="\u200B",
            value=(
                "Powerd by the opened-sourced "
                "[Goon Auth Network](https://github.com/GoonAuthNetwork)"
            ),
            inline=False,
        )

        return DiscordResponse(embeds=[embed], empherical=True)

    def about_anonymous() -> DiscordResponse:
        embed = Embed(
            type="rich",
            title="About GoonAuthNetwork",
            description=AboutResponseBuilder.about_ethics,
            color=color.Colour.teal(),
        )
        embed.add_field(
            name="\u200B",
            value=(
                "Powerd by the opened-sourced "
                "[Goon Auth Network](https://github.com/GoonAuthNetwork)"
            ),
            inline=False,
        )

        return DiscordResponse(embeds=[embed], empherical=True)
