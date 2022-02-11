# import re


def valid_sa_name(name: str) -> bool:
    if name is None:
        return False
    # TODO: Fix name validation with userid alternative
    # Ghetto validation
    if len(name) < 3:
        return False

    if len(name) > 100:
        return False

    return True

    # matched = re.match("^[a-zA-Z0-9-_ ]{3,50}$", name)
    # return bool(matched)
