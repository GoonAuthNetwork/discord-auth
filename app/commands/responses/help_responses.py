from dispike.response import DiscordResponse


class HelpResponseBuilder:
    def help() -> DiscordResponse:
        # TODO: Help...
        return DiscordResponse(
            content=(
                "Help is on the way! Maybe... eventually... probably not. "
                "This command doesn't do anything currently."
            ),
            empherical=True,
        )
