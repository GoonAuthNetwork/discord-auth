from dispike.helper import Embed
from dispike.response import DiscordResponse


def create_response(
    embed: Embed, ephemeral=True, add_powered_by=True
) -> DiscordResponse:
    """
    Creates a DiscordResponse for the specified embed.
    Optionally adds a powered_by_field to the embed.
    """
    if add_powered_by:
        powered_by_field(embed)

    # Empty content string is to fix a current dispike bug
    return DiscordResponse(content=" ", embeds=[embed], empherical=ephemeral)


def powered_by_field(embed: Embed) -> None:
    """Adds the generic "powered by" field to the specified embed"""
    embed.add_field(
        name="\u200B",
        value=(
            "Powered by the open-source "
            "[Goon Auth Network](https://github.com/GoonAuthNetwork)"
        ),
        inline=False,
    )
