from typing import Optional, Tuple

from app.clients.goon_auth_api import GoonAuthApi, GoonAuthStatus, GoonAuthChallenge


async def get_verification(
    api: GoonAuthApi, name: str
) -> Tuple[Optional[GoonAuthChallenge], str]:
    try:
        challenge = await api.get_verification(name)
    except TypeError:
        return None, "Invalid username, please try again."

    if challenge is None:
        return (
            None,
            "This error should not exist, please tell your nearest GAN developer.",
        )

    message = (
        "Please place the following hash into your Something Awful profile."
        "Anywhere in the **Additional Information** section here "
        "https://forums.somethingawful.com/member.php?action=editprofile\n\n"
        f"**{challenge.hash}**\n\n"
        f"Note: The hash expires after **five minutes**\n\n"
        "Once finished, use the command /auth_check\n"
    )

    return challenge, message


async def check_verification(
    api: GoonAuthApi, name: str
) -> Tuple[Optional[GoonAuthStatus], str]:
    try:
        status = await api.get_verification_update(name)
    except ValueError:
        return None, "Please use the following command first: /auth"
    except TypeError:
        return None, "Invalid username, please try again."

    if status is None:
        return (
            None,
            "This error should not exist, please tell your nearest GAN developer.",
        )

    if not status.validated:
        return None, "Failed to validate, is the hash in your profile?"

    return status, None
