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
async def test_find_by_service():
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


@pytest.mark.asyncio
async def test_find_user():
    test_user = random.choice(fake_users)

    # Add the user
    user = await client.create_user(**test_user)

    # Check the user
    assert user is not None
    assert user.userId == test_user["userId"]

    # Find it
    found = await client.find_user(test_user["userId"])

    assert found is not None
    assert found.userId == test_user["userId"]


@pytest.mark.asyncio
async def test_add_service():
    test_user = random.choice(fake_users)

    # Add the user
    user = await client.create_user(**test_user)

    # Check the user
    assert user is not None
    assert user.userId == test_user["userId"]
    assert user.userName == test_user["userName"]
    assert user.regDate == test_user["regDate"]

    # Add/Update Service
    updated_serverToken = ServiceToken(Service.DISCORD, "A new Token")

    updated_user = await client.add_service_token(user.userId, updated_serverToken)

    assert updated_user is not None
    assert updated_user.find_service(Service.DISCORD) is not None
    assert updated_user.find_service(Service.DISCORD).token == updated_serverToken.token


@pytest.mark.asyncio
async def test_create_or_update_user():
    test_user = random.choice(fake_users)
    test_service: ServiceToken = test_user["services"][0]

    # Create
    user = await client.create_or_update_user(
        test_user["userId"],
        test_user["userName"],
        test_user["regDate"],
        test_service,
    )

    assert user is not None
    assert user.find_service(test_service.service) is not None
    assert user.find_service(test_service.service).token == test_service.token

    # Update
    test_service = ServiceToken(Service.DISCORD, "A New Token")
    updated = await client.create_or_update_user(
        test_user["userId"],
        test_user["userName"],
        test_user["regDate"],
        test_service,
    )

    assert updated is not None
    assert updated.find_service(test_service.service) is not None
    assert updated.find_service(test_service.service).token == test_service.token
