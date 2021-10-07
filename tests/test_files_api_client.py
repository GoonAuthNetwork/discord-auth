import random
import pytest

from app.clients.goon_files_api import GoonFilesApi, Service, ServiceToken
from .utils import generate_username, generate_random_date

_host = "http://127.0.0.1:8002/"
client = GoonFilesApi(host=_host)
fake_users = [
    {
        "userId": random.randint(0, 100000),
        "userName": generate_username(),
        "regDate": generate_random_date(),
        "services": [
            ServiceToken(
                Service.DISCORD, f"{generate_username()}#{random.randint(0, 100000)}"
            )
        ],
    },
    {
        "userId": random.randint(0, 100000),
        "userName": generate_username(),
        "regDate": generate_random_date(),
        "services": [
            ServiceToken(
                Service.DISCORD, f"{generate_username()}#{random.randint(0, 100000)}"
            )
        ],
    },
    {
        "userId": random.randint(0, 100000),
        "userName": generate_username(),
        "regDate": generate_random_date(),
        "services": [
            ServiceToken(
                Service.DISCORD, f"{generate_username()}#{random.randint(0, 100000)}"
            )
        ],
    },
]


@pytest.mark.asyncio
async def test_add_user():
    pass


@pytest.mark.asyncio
async def test_check_user():
    pass


@pytest.mark.asyncio
async def test_add_check():
    test_user = random.choice(fake_users)

    # Add the user
    user = await client.create_user(**test_user)

    # Check the user
    assert user is not None
    assert user.userId == test_user["userId"]
    assert user.userName == test_user["userName"]
    assert user.regDate == test_user["regDate"]

    # Check services
    assert user.services is not None
    assert next(True for x in user.services if x.service == Service.DISCORD)

    # Query User
    token = test_user["services"][0].token
    queried = await client.find_user_by_service(Service.DISCORD, token)

    assert queried is not None
    assert queried.userId == test_user["userId"]
    assert queried.userName == test_user["userName"]
    assert queried.regDate == test_user["regDate"]
