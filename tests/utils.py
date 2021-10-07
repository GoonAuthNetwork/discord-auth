from datetime import datetime
import random
import string
from typing import Any, Dict


def generate_username() -> str:
    """Creates a random valid sa user name

    Returns:
        str: [description]
    """
    return "".join(random.choices(string.ascii_letters + string.digits, k=15))


def generate_random_date(start: datetime = None, end: datetime = None) -> datetime:
    if start is None:
        start = datetime(2000, 1, 1)
    if end is None:
        end = datetime.now()

    start_stamp = datetime.timestamp(start)
    end_stamp = datetime.timestamp(end)

    rand_stamp = random.uniform(start_stamp, end_stamp)

    return datetime.fromtimestamp(rand_stamp).replace(microsecond=0)


def is_sub_dict(main: Dict[str, Any], sub: Dict[str, Any]) -> bool:
    """Check if sub dict is in main dict

    Args:
        main (Dict[str, Any]): [description]
        sub (Dict[str, Any]): [description]

    Returns:
        bool: [description]
    """
    return all(main.get(key, None) == val for key, val in sub.items())
