from dispike.creating.components import ActionRow, Button, ButtonStyles, LinkButton
from dispike.helper import Embed, color
from dispike.response import DiscordResponse


class AuthResponseBuilder:
    def challenge_ok(hash: str) -> DiscordResponse:
        message = (
            "Please place the following hash anywhere in the "
            "**Additional Information** section of your Something Awful profile."
            f"\n\n**{hash}**\n\n"
            f"Note: The hash expires after **five minutes**\n\n"
            'Once finished, click the "Verify Hash" button below.'
        )
        embed = Embed(
            type="rich",
            title="Goon Authentication",
            description=message,
            colour=color.Color.teal(),
        )
        embed.add_field(
            name="\u200B",
            value=(
                "Powered by the open-sourced "
                "[Goon Auth Network](https://github.com/GoonAuthNetwork)"
            ),
        )

        action_row = ActionRow(
            components=[
                LinkButton(
                    label="SA Profile",
                    url=(
                        "https://forums.somethingawful.com/member.php?"
                        "action=editprofile"
                    ),
                ),
                Button(
                    label="Verify Hash",
                    style=ButtonStyles.SUCCESS,
                    custom_id="auth.verify",
                ),
                Button(
                    label="Cancel", style=ButtonStyles.DANGER, custom_id="auth.cancel"
                ),
            ]
        )

        return DiscordResponse(
            content=" ", embeds=[embed], action_row=action_row, empherical=True
        )

    def challenge_error(message: str) -> DiscordResponse:
        embed = Embed(
            type="rich",
            title="Goon Authentication",
            description=message,
            colour=color.Color.red(),
        )
        embed.add_field(
            name="\u200B",
            value=(
                "Powered by the open-sourced "
                "[Goon Auth Network](https://github.com/GoonAuthNetwork)"
            ),
        )

        return DiscordResponse(content=" ", embeds=[embed], empherical=True)

    def verification_cancel() -> DiscordResponse:
        embed = Embed(
            type="rich",
            title="Goon Authentication",
            description=(
                "We're sad to see you go, feel free to auth again later!\n\n"
                "If you would like to know more about the Goon Auth Network "
                "please click below!"
            ),
            color=color.Colour.red(),
        )

        action_row = ActionRow(
            components=[
                LinkButton(label="GAN Github", url="https://github.com/GoonAuthNetwork")
            ]
        )

        return DiscordResponse(
            update_message=True,
            content=" ",
            embeds=[embed],
            action_row=action_row,
            empherical=True,
        )

    def verification_ok(
        message: str = None, update_message: bool = True
    ) -> DiscordResponse:
        if message is None:
            message = (
                "You're finally validated! "
                "Please enjoy your new found gooniness.\n\n"
                "If you would like to know more about the Goon Auth Network "
                "please click below!"
            )

        embed = Embed(
            type="rich",
            title="Goon Authentication",
            description=message,
            color=color.Colour.green(),
        )

        action_row = ActionRow(
            components=[
                LinkButton(label="GAN Github", url="https://github.com/GoonAuthNetwork")
            ]
        )

        return DiscordResponse(
            update_message=update_message,
            content=" ",
            embeds=[embed],
            action_row=action_row,
            empherical=True,
        )

    def verification_error(
        message: str, update_message: bool = True
    ) -> DiscordResponse:
        embed = Embed(
            type="rich",
            title="Goon Authentication",
            description=(
                f"{message}\n\n"
                "If you would like to know more about the Goon Auth Network "
                "please click below!"
            ),
            color=color.Colour.red(),
        )

        action_row = ActionRow(
            components=[
                LinkButton(label="GAN Github", url="https://github.com/GoonAuthNetwork")
            ]
        )

        return DiscordResponse(
            update_message=update_message,
            content=" ",
            embeds=[embed],
            action_row=action_row,
            empherical=True,
        )

    def verification_profile_hash_missing() -> DiscordResponse:
        embed = Embed(
            type="rich",
            title="Goon Authentication",
            description=("Failed to validate. Is the **hash** in your **profile**?"),
            color=color.Colour.red(),
        )

        return DiscordResponse(
            embeds=[embed],
            empherical=True,
        )
