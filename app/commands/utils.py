import re


def valid_sa_name(name: str) -> bool:
    if name is None:
        return False

    matched = re.match("^[a-zA-Z0-9-_ ]{3,50}$", name)
    return bool(matched)
