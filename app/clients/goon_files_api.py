from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
from urllib import parse

from httpx import AsyncClient


class Service(str, Enum):
    DISCORD = "discord"
    OTHER = "other"


class ServiceToken:
    service: Service
    token: str
    info: Optional[str]

    def __init__(self, service: str, token: str, info: Optional[str] = None) -> None:
        self.service = Service(service)
        self.token = token
        self.info = info


class User:
    userId: int
    userName: str
    regDate: datetime
    permaBanned: Optional[datetime]
    services: Optional[List[ServiceToken]]
    createdAt: datetime

    def __init__(
        self,
        userId: int,
        userName: str,
        regDate: datetime,
        createdAt: datetime,
        permaBanned: Optional[datetime] = None,
        services: Optional[List[Dict[str, str]]] = None,
    ) -> None:
        self.userId = userId
        self.userName = userName
        self.createdAt = createdAt
        self.permaBanned = permaBanned

        if regDate is not None:
            self.regDate = datetime.fromisoformat(regDate)

        if services is not None:
            self.services = []
            for dict in services:
                self.services.append(ServiceToken(**dict))


class GoonFilesApi:
    def __init__(self, host: str, headers: Dict[str, str] = None) -> None:
        self.client = AsyncClient(base_url=host, headers=headers)

    async def find_user_by_service(
        self, service: Service, token: str
    ) -> Optional[User]:
        payload = {"service": parse.quote(service.value), "token": parse.quote(token)}
        response = await self.client.get("/user/", params=payload)

        # This shouldn't happen, but who knows...
        if response.status_code == 422:
            raise TypeError("Invalid query parameter")

        if response.status_code != 200:
            return None

        wrapped = response.json()
        return User(**wrapped)

    async def create_user(
        self,
        userId: int,
        userName: str,
        regDate: datetime,
        services: Optional[List[ServiceToken]] = None,
    ) -> Optional[User]:
        payload = {"userId": userId, "userName": userName, "regDate": regDate}
        if services is not None:
            payload["services"] = services

        response = await self.client.post("/user/", json=payload)

        if response.status_code == 422:
            raise TypeError("Invalid user parameter")

        if response.status_code != 200:
            return None

        wrapped = response.json()
        return User(**wrapped)
